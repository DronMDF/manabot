import unittest
from tb.sources.review_list import ReviewIsNeed


class ReviewListFake:
	def __init__(self, items):
		self.items = items

	def __iter__(self):
		return iter(self.items)


class ReviewIsNeedTest(unittest.TestCase):
	def testEmptyAdmins(self):
		rs = ReviewIsNeed(ReviewListFake([]), ReviewListFake(['A']))
		self.assertEqual(next(iter(rs)), 'A')
