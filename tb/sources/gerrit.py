from pygerrit2.rest import GerritRestAPI
from requests.auth import HTTPDigestAuth
from unittest import TestCase
from tb.storage import TinyDataBase


class GerritReview:
	def __init__(self, change):
		self.change = change
		self.doc_id = None

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
	def __init__(self, added):
		self.added = added

	def actions(self):
		return [AcNewReview(r['id']) for r in self.added]


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
	def __init__(self, review):
		self.review = review

	def send(self, transport):
		pass

	def save(self, db):
		db.update(
			self.review.doc_id,
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
	def __init__(self, updated):
		self.updated = updated

	def actions(self):
		return [AcUpdateReview(r) for r in self.updated]
