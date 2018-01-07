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


class ReviewDifference:
	def __init__(self, reviews, others):
		self.reviews = reviews
		self.others = others

	def __iter__(self):
		others_id = {r['id'] for r in self.others}
		return (r for r in self.reviews if r['id'] not in others_id)


class UpdateableReview:
	def __init__(self, exist, extern):
		self.exist = exist
		self.extern = extern
		self.doc_id = self.exist.doc_id

	def __getitem__(self, name):
		return self.extern[name]

	def needUpdate(self):
		return not all((
			self.exist['revision'] == self.extern['revision'],
			self.exist['verify'] == self.extern['verify']
		))


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


class ReviewById:
	def __init__(self, reviews, gerrit_id):
		self.reviews = reviews
		self.gerrit_id = gerrit_id

	def value(self):
		return next((r for r in self.reviews if r['id'] == self.gerrit_id))
