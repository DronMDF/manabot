from .review import *


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


class ReviewIgnored:
	def __init__(self, reviews):
		self.reviews = reviews

	def __iter__(self):
		return (r for r in self.reviews if r.get('status', 'none') == 'ignored')


class ReviewOne:
	def __init__(self, reviews):
		self.reviews = reviews

	def __iter__(self):
		return iter([next(iter(self.reviews))])


class ReviewIsNeed:
	def __init__(self, current, reviews):
		self.current = current
		self.reviews = reviews

	def __iter__(self):
		# Если в current что-то есть - новые не нужны
		return iter([] if list(self.current) else self.reviews)


class ReviewDifference:
	def __init__(self, reviews, others):
		self.reviews = reviews
		self.others = others

	def __iter__(self):
		others_id = {r['id'] for r in self.others}
		return (r for r in self.reviews if r['id'] not in others_id)


class ReviewForUpdate:
	def __init__(self, extern, exists):
		self.extern = extern
		self.exists = exists

	def updateable(self):
		exists_id = {r['id']: r for r in self.exists}
		return (
			UpdateableReview(exists_id[r['id']], r)
			for r in self.extern
			if r['id'] in exists_id
		)

	def __iter__(self):
		return (r for r in self.updateable() if r.needUpdate())
