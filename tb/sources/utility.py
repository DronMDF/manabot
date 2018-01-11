from itertools import chain
from traceback import print_exc


class SoJoin:
	def __init__(self, *sources):
		self.sources = sources

	def actions(self):
		return list(chain.from_iterable((s.actions() for s in self.sources)))


class SoSafe:
	def __init__(self, source):
		self.source = source

	def actions(self):
		try:
			return self.source.actions()
		except Exception:
			print_exc()
			# @todo #58 Из текста исключения необходимо
			#  сформировать сообщение для администратора
			return []
