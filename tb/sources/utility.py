from itertools import chain
from unittest import TestCase
from traceback import print_exc


class SoJoin:
	def __init__(self, *sources):
		self.sources = sources

	def actions(self):
		return list(chain.from_iterable((s.actions() for s in self.sources)))


class SoFake:
	def __init__(self, result):
		self.result = result

	def actions(self):
		return self.result


class SoJoinTest(TestCase):
	def testJoin(self):
		so = SoJoin(
			SoFake([1, 2, 3]),
			SoFake([4, 5, 6])
		)
		self.assertListEqual(so.actions(), [1, 2, 3, 4, 5, 6])


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
