class ReviewUnderControl:
	def __init__(self, db):
		self.db = db

	def __iter__(self):
		return iter(self.db.all())


class ReviewIds:
	def __init__(self, reviews):
		self.reviews = reviews

	def __iter__(self):
		return (i['id'] for i in self.reviews)


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
