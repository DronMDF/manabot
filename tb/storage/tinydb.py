from tinydb import TinyDB, where


class TinySelect:
	def __init__(self, databases):
		self.databases = databases

	def set(self, name, value, database, table='_default'):
		self.databases[database].set(name, value, table=table)

	def insert(self, json, database, table='_default'):
		self.databases[database].insert(json, table=table)

	def update(self, id, json, database, table='_default'):
		self.databases[database].update(id, json, table=table)

	def delete(self, id, database, table='_default'):
		self.databases[database].delete(id, table=table)


class TinyDataBase:
	def __init__(self, filename):
		self.filename = filename

	def set(self, name, value, table='_default'):
		TinyDB(self.filename).table(table).upsert(
			{'name': name, 'value': value},
			where('name') == name
		)

	def get(self, name, default=None, table='_default'):
		item = TinyDB(self.filename).table(table).get(where('name') == name)
		if item is not None:
			return item.get('value', default)
		return default

	def all(self, table='_default'):
		return TinyDB(self.filename).table(table).all()

	def insert(self, json, table='_default'):
		TinyDB(self.filename).table(table).insert(json)

	# @todo #63 Для идентификации элементов при обновлении
	#  стоит использовать doc_id
	def update(self, id, json, table='_default'):
		TinyDB(self.filename).table(table).update(json, where('id') == id)

	def delete(self, id, table='_default'):
		TinyDB(self.filename).table(table).remove(doc_ids=[id])
