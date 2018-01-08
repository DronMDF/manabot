import telegram
import hashlib
from time import time


class ReviewAdmin:
	def __init__(self, id):
		self.id = id

	def __getitem__(self, name):
		return self.__dict__[name]


class ReviewListAdmin:
	def __init__(self, db):
		self.db = db

	def __iter__(self):
		return (
			ReviewAdmin(i)
			for i in [self.db.get('active_review', False)]
			if i
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
	def __init__(self, reviews, chat_id):
		self.reviews = reviews
		self.chat_id = chat_id

	def actions(self):
		return [
			AcAdminReviewIsOut(r, self.chat_id)
			for r in self.reviews
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
		# @todo #64 Необходимо использовать идентификатор записи ревью в БД,
		#  для этого необходимо отфильтровать список ревью на основании команды
		#  Или просто все команды странслировать в ревью. Может быть мне стоит делать
		#  два независимых экшина, чтобы не смешивать два дела в одном?
		#  возможно я могу прикопать идентификатор записи при создании команды?
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
