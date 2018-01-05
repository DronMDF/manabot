from pygerrit2.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from unittest import TestCase
from tb.storage import TinyDataBase
from .review import ReviewIds, ReviewById


class GerritReview:
	def __init__(self, change):
		self.change = change

	def __getitem__(self, key):
		if key == 'verify':
			return 'approved' in self.change.get('labels', {}).get('Verified', {})
		elif key == 'revision':
			return self.change['current_revision']
		else:
			return self.change[key]


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
			GerritReview(i)
			for i in GerritRestAPI(
				url=self.config.value('gerrit.url'),
				auth=auth
			).get('/changes/?o=LABELS&o=CURRENT_REVISION')
		)


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
	def __init__(self, review):
		self.review = review

	def send(self, transport):
		pass

	def save(self, db):
		db.delete(self.review.doc_id, 'gerrit')
		print('GERRIT: Out review', self.review['id'])


class SoOutReview:
	def __init__(self, removed):
		self.removed = removed

	def actions(self):
		return [AcOutReview(r) for r in self.removed]


class AcUpdateReview:
	def __init__(self, updating, review):
		self.updating = updating
		self.review = review

	def send(self, transport):
		pass

	def save(self, db):
		db.update(
			self.updating.value().doc_id,
			{
				'id': self.review['id'],
				'revision': self.review['revision'],
				'verify': self.review['verify']
			},
			'gerrit'
		)
		print(
			'GERRIT: Update review %s, (%s, %s)' % (
				self.review['id'],
				self.review['revision'][:7],
				self.review['verify']
			)
		)


class SoUpdateReview:
	def __init__(self, remote, controlled):
		# @todo #67 Здесь на вход необходимо подавать умный список ревью,
		#  Элементы которого будут иметь идентифкатор БД и данные для обновления
		self.remote = remote
		self.controlled = controlled

	def needUpdate(self, review):
		local = next((l for l in self.controlled if l['id'] == review['id']), None)
		return local is not None and not all((
			local['revision'] == review['revision'],
			local['verify'] == review['verify']
		))

	def actions(self):
		return [
			AcUpdateReview(ReviewById(self.controlled, v['id']), v)
			for v in self.remote if self.needUpdate(v)
		]
