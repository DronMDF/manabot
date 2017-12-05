from pygerrit2.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from unittest import TestCase
from tb.storage import TinyDataBase


class AcNewReview:
	def __init__(self, id):
		self.id = id

	def send(self, transport):
		pass

	def save(self, db):
		db.insert({
			'id': self.id,
			'verify': None,
			'review': None,
			'revision': None
		}, 'gerrit')
		print('GERRIT: New review', self.id)


class ReviewUnderControl:
	def __init__(self, db):
		self.db = db

	def __iter__(self):
		return (i['id'] for i in self.db.all())


class ReviewOnServer:
	def __init__(self, config):
		self.config = config

	def __iter__(self):
		# @todo #18 Возможно мы можем написать декоратор для Auth
		#  Потому что у меня возникло желание вынести это в функцию,
		#  что не правильно.
		if self.config.value('gerrit.auth') == 'digest':
			auth = HTTPDigestAuth(
				self.config.value('gerrit.user'),
				self.config.value('gerrit.password')
			)
		else:
			auth = None
		return (
			i['id'] for i in GerritRestAPI(
				url=self.config.value('gerrit.url'),
				auth=auth
			).get('/changes/')
		)


class SoNewReview:
	def __init__(self, controlled_ids, remote_ids):
		self.controlled_ids = controlled_ids
		self.remote_ids = remote_ids

	def actions(self):
		return [
			AcNewReview(id)
			for id in set(self.remote_ids) - set(self.controlled_ids)
		]


class SoNewReviewTest(TestCase):
	def testNewFromClean(self):
		so = SoNewReview(controlled_ids=[], remote_ids=[1, 2, 3])
		self.assertEqual(len(so.actions()), 3)

	def testNewWithExists(self):
		so = SoNewReview(controlled_ids=[1, 2], remote_ids=[1, 2, 3])
		self.assertEqual(len(so.actions()), 1)


class AcOutReview:
	def __init__(self, id):
		self.id = id

	def send(self, transport):
		pass

	def save(self, db):
		db.delete(self.id, 'gerrit')
		print('GERRIT: Out review', self.id)


class SoOutReview:
	def __init__(self, controlled_ids, remote_ids):
		self.controlled_ids = controlled_ids
		self.remote_ids = remote_ids

	def actions(self):
		return [
			AcOutReview(id)
			for id in set(self.controlled_ids) - set(self.remote_ids)
		]


class SoOutReviewTest(TestCase):
	def testOut(self):
		so = SoOutReview(controlled_ids=[1, 2, 3], remote_ids=[2, 3, 4])
		self.assertEqual(len(so.actions()), 1)
