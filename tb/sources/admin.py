import telegram
import hashlib
from time import time


class AdminReview:
	def __init__(self, db):
		self.db = db

	def active(self):
		return self.db.get('active_review', False)


class ReviewIsOut:
	def __init__(self, actual, reviews_id):
		self.actual = actual
		self.reviews_id = reviews_id

	def __iter__(self):
		return (
			id
			for id in [self.actual.active()]
			if id and id not in self.reviews_id
		)


class AcAdminReviewIsOut:
	def __init__(self, review_id, chat_id):
		self.review_id = review_id
		self.chat_id = chat_id

	def send(self, transport):
		transport.sendMessage(
			self.chat_id,
			text='GERRIT: Review %s is Out' % self.review_id
		)

	def save(self, db):
		db.set('active_review', False, 'admin')


class AcReviewForAdmin:
	def __init__(self, review, chat_id):
		self.review = review
		self.chat_id = chat_id

	def send(self, transport):
		# @todo #46 Сейчас сообщение о ревью не достаточно информативно.
		#  Нужно дополнить его текстом из сабжекта вместо этой абракадабры
		review_id_hash = hashlib.md5(self.review['id'].encode('ascii')).hexdigest()
		transport.sendMessage(
			self.chat_id,
			text='GERRIT: Update review %s, (%s, %s)' % (
				self.review['id'],
				self.review['revision'][:7],
				self.review['verify']
			),
			reply_markup=telegram.InlineKeyboardMarkup([[
				telegram.InlineKeyboardButton(
					'Approve',
					callback_data='approve %s' % review_id_hash
				),
				telegram.InlineKeyboardButton(
					'Reject',
					callback_data='reject %s' % review_id_hash
				),
				telegram.InlineKeyboardButton(
					'Ignore',
					callback_data='ignore %s' % review_id_hash
				)
			]])
		)

	def save(self, db):
		db.set('active_review', self.review['id'], 'admin')


class SoAdminReviewIsOut:
	def __init__(self, reviews_id, chat_id):
		self.reviews_id = reviews_id
		self.chat_id = chat_id

	def actions(self):
		return [
			AcAdminReviewIsOut(review_id, self.chat_id)
			for review_id in self.reviews_id
		]


class SoReviewForAdmin:
	def __init__(self, reviews, chat_id):
		self.reviews = reviews
		self.chat_id = chat_id

	def actions(self):
		return [
			AcReviewForAdmin(review, self.chat_id)
			for review in self.reviews
		]


class AdminCommands:
	def __init__(self, db):
		self.db = db

	def __iter__(self):
		return iter(self.db.all(table='commands'))


class AdminIgnoreCommands:
	def __init__(self, commands):
		self.commands = commands

	def __iter__(self):
		return (s for s in self.commands if s['action'] == 'ignore')


class AcIgnoreReview:
	def __init__(self, command):
		self.command = command

	def send(self, transport):
		pass

	def save(self, db):
		db.update(self.command['review_id'], {
			'status': 'ignore',
			'time': int(time())
		}, 'gerrit')
		db.delete(self.command.doc_id, 'admin', 'commands')


class SoIgnoreReview:
	def __init__(self, commands):
		self.commands = commands

	def actions(self):
		return [AcIgnoreReview(c) for c in self.commands]
