import hashlib
import telegram


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
	def __init__(self, review, chat_id):
		self.review = review
		self.chat_id = chat_id

	def send(self, transport):
		# @todo #78: Единственно доступная здесь информация -
		#  это review id, который хранится в БД администратора.
		#  Хотя хотелось бы видеть сабжект от ревью,
		#  но в БД геррита этого ревью уже нет.
		transport.sendMessage(
			self.chat_id,
			text='Review is Out: %s' % self.review['id']
		)

	def save(self, db):
		db.set('active_review', False, 'admin')


class SoAdminReviewIsOut:
	def __init__(self, reviews, chat_id):
		self.reviews = reviews
		self.chat_id = chat_id

	def actions(self):
		return [
			AcAdminReviewIsOut(r, self.chat_id)
			for r in self.reviews
		]


class AcReviewForAdmin:
	def __init__(self, review, chat_id):
		self.review = review
		self.chat_id = chat_id

	def send(self, transport):
		review_id_hash = hashlib.md5(self.review['id'].encode('ascii')).hexdigest()
		transport.sendMessage(
			self.chat_id,
			text='Review is ready: %s %s' % (
				self.review['revision'][:7],
				self.review['subject']
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


class SoReviewForAdmin:
	def __init__(self, reviews, chat_id):
		self.reviews = reviews
		self.chat_id = chat_id

	def actions(self):
		return [
			AcReviewForAdmin(review, self.chat_id)
			for review in self.reviews
		]
