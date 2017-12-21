from tinydb import TinyDB, where

# @todo #55 Необходима поддержка таблиц.
#  Иначе в admin.json у нас будут перемешиваться команды и параметры.


class TinySelect:
	def __init__(self, databases):
		self.databases = databases

	def set(self, name, value, database):
		self.databases[database].set(name, value)

	def insert(self, json, database):
		self.databases[database].insert(json)

	def update(self, id, json, database):
		self.databases[database].update(id, json)

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

	def all(self):
		return TinyDB(self.filename).all()

	def insert(self, json):
		TinyDB(self.filename).insert(json)

	def update(self, id, json):
		TinyDB(self.filename).update(json, where('id') == id)

	def delete(self, id):
		TinyDB(self.filename).remove(where('id') == id)
