import unittest
from tb.sources.admin import ReviewListAdmin


class DatabaseFake:
	def __init__(self, value):
		self.value = value

	def get(self, name, default):
		assert name
		assert default
		return self.value


class ReviewListAdminTest(unittest.TestCase):
	def testEmptyDatabase(self):
		rs = ReviewListAdmin(DatabaseFake(False))
		self.assertEqual(len(list(rs)), 0)

	def testIdPresent(self):
		rs = ReviewListAdmin(DatabaseFake('ID'))
		self.assertEqual(next(iter(rs))['id'], 'ID')
