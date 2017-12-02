class StDatabase:
	def __init__(self, db):
		self.db = db

	def save(self, action):
		action.save(self.db)
