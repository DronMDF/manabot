from tinydb import TinyDB, where


class TinyDataBase:
	def __init__(self, filename):
		self.filename = filename

	def set(self, name, value):
		TinyDB(self.filename).upsert(
			{'name': name, 'value': value},
			where('name') == name
		)

	def get(self, name, default=None):
		db = TinyDB(self.filename)
		item = db.get(where('name') == name)
		if item is not None:
			return item.get('value', default)
		return default

	def insert(self, json):
		TinyDB(self.filename).insert(json)

	def all(self):
		return TinyDB(self.filename).all()
