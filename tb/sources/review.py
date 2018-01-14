class ReviewHasheable:
	def __init__(self, review):
		self.review = review
		self.doc_id = self.review.doc_id

	def __getitem__(self, name):
		return self.review[name]

	def __hash__(self):
		return hash((
			self.review.get(n, None)
			for n in ('revision', 'verify', 'subject')
		))

	def __eq__(self, other):
		return hash(self) == hash(other)


class UpdateableReview:
	def __init__(self, exist, extern):
		self.exist = ReviewHasheable(exist)
		self.extern = ReviewHasheable(extern)
		self.doc_id = self.exist.doc_id

	def __getitem__(self, name):
		return self.extern[name]

	def needUpdate(self):
		return self.exist != self.extern
