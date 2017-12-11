class AdminReview:
	def __init__(self, db):
		self.db = db

	def active(self):
		return self.db.get('active_review', False)


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


class SoReviewForAdmin:
	def __init__(self, reviews, chat_id):
		self.reviews = reviews
		self.chat_id = chat_id

	def actions(self):
		return [
			AcReviewForAdmin(review, self.chat_id)
			for review in self.reviews
		]
