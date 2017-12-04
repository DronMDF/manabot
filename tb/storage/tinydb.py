from tinydb import TinyDB, where


class TinySelect:
	def __init__(self, databases):
		self.databases = databases

	def set(self, name, value, database):
		self.databases[database].set(name, value)

	def insert(self, json, database):
		self.databases[database].insert(json)

	def delete(self, id, database):
		self.databases[database].delete(id)


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

	def delete(self, id):
		TinyDB(self.filename).remove(where('id') == id)
