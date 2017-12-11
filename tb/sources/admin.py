
class ReviewVerified:
	def __init__(self, reviews):
		self.reviews = reviews

	def __iter__(self):
		return (r for r in self.reviews if r['verify'])


class ReviewOne:
	def __init__(self, reviews):
		self.reviews = reviews

	def __iter__(self):
		return iter([next(iter(self.reviews))])


class ReviewIsNeed:
	def __init__(self, reviews, current):
		self.reviews = reviews
		self.current = current

	def __iter__(self):
		if not self.current.active():
			return iter(self.reviews)
		else:
			return iter([])


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
