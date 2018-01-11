from unittest import TestCase
from tb.sources.utility import SoJoin


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
