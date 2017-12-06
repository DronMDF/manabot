from pygerrit2.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from unittest import TestCase
from tb.storage import TinyDataBase


class ReviewUnderControl:
	def __init__(self, db):
		self.db = db

	def __iter__(self):
		return iter(self.db.all())


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


class ReviewIds:
	def __init__(self, reviews):
		self.reviews = reviews

	def __iter__(self):
		return (i['id'] for i in self.reviews)


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


class AcVerifiedReview:
	def __init__(self, chat_id, review):
		self.chat_id = chat_id
		self.review = review

	def send(self, transport):
		# @todo #38 Нет необходимости на каждое изменение слать уведомления.
		#  Нужно выбрать одно из них и начать диалог с овнером о том,
		#  что с ним делать.
		#  И пока овнер в диалоге - новых уведомлений не городить (таймаут)
		#  И вероятно это должен быть отдельный соурс,
		#  который будет работать постфактом
		transport.sendMessage(
			self.chat_id,
			text='GERRIT: Update review %s, (%s, %s)' % (
				self.review['id'],
				self.review['revision'][:7],
				self.review['verify']
			)
		)

	def save(self, db):
		db.update(
			self.review['id'],
			{
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


class SoVerifiedReview:
	def __init__(self, verified, controlled, chat_id):
		self.verified = verified
		self.controlled = controlled
		self.chat_id = chat_id

	def needUpdate(self, review):
		local = next((l for l in self.controlled if l['id'] == review['id']), None)
		return local is not None and not all((
			local['revision'] == review['revision'],
			local['verify'] == review['verify']
		))

	def actions(self):
		return [
			AcVerifiedReview(self.chat_id, v)
			for v in self.verified
			if self.needUpdate(v)
		]
