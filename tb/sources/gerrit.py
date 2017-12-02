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
		# @todo #12 Хранилище у нас абстрактное и не знает,
		#  что эту информацию нужно класть в БД геррита.
		#  Может быть нам сделать некий токен первым параметром у insert и у set?
		#  Или наоборот, пусть БД представляется, когда сейвит action? Это проще.
		db.insert({
			'id': self.id,
			'verify': None,
			'review': None,
			'revision': None
		})
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
	def __init__(self, **kwargs):
		if 'controlled_ids' in kwargs:
			self.controlled_ids = kwargs['controlled_ids']
		else:
			self.controlled_ids = ReviewUnderControl(
				TinyDataBase(
					kwargs.get('config').value('gerrit.db')
				)
			)
		if 'remote_ids' in kwargs:
			self.remote_ids = kwargs['remote_ids']
		else:
			self.remote_ids = ReviewOnServer(kwargs.get('config'))

	def actions(self):
		return [AcNewReview(id) for id in set(self.remote_ids) - set(self.controlled_ids)]


class SoNewReviewTest(TestCase):
	def testNewFromClean(self):
		so = SoNewReview(controlled_ids=[], remote_ids=[1, 2, 3])
		self.assertEqual(len(so.actions()), 3)

	def testNewWithExists(self):
		so = SoNewReview(controlled_ids=[1, 2], remote_ids=[1, 2, 3])
		self.assertEqual(len(so.actions()), 1)
