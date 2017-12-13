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
		# @todo #40 Нужно предоставить администратору основную информацию
		#  title, коммит, патчсет, статус верификации и ревью.
		#  И выдать список доступных действий в виде экранных кнопок.
		transport.sendMessage(
			self.chat_id,
			text='GERRIT: Update review %s, (%s, %s)' % (
				self.review['id'],
				self.review['revision'][:7],
				self.review['verify']
			)
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
