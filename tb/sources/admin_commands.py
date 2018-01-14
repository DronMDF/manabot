from time import time


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


class ReviewByCommand:
	def __init__(self, review, command):
		self.review = review
		self.command = command
		self.doc_id = review.doc_id

	def __getitem__(self, name):
		if name == 'command_id':
			return self.command.doc_id
		return self.review[name]


class ReviewListByCommands:
	def __init__(self, commands, reviews):
		self.commands = commands
		self.reviews = reviews

	def __iter__(self):
		cs = {c['review_id']: c for c in self.commands}
		return (
			ReviewByCommand(r, cs[r['id']])
			for r in self.reviews
			if r['id'] in cs
		)


class AcIgnoreReview:
	def __init__(self, review):
		self.review = review

	def send(self, transport):
		pass

	def save(self, db):
		db.update(self.review.doc_id, {
			'status': 'ignore',
			'time': int(time())
		}, 'gerrit')
		db.delete(self.review['command_id'], 'admin', 'commands')


class SoIgnoreReview:
	def __init__(self, reviews):
		self.reviews = reviews

	def actions(self):
		return [AcIgnoreReview(c) for c in self.reviews]
