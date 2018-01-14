import unittest
from tb.sources.review import ReviewHasheable


class ReviewFake:
	def __init__(self, **kwargs):
		self.doc_id = None
		self.values = kwargs

	def __getitem__(self, name):
		return self.kwargs[name]


class TestReviewHasheable(unittest.TestCase):
	def testEqual(self):
		r1 = ReviewHasheable(ReviewFake(revision=10, verify=False, subject='yyy'))
		r2 = ReviewHasheable(ReviewFake(revision=10, verify=False, subject='yyy'))
		self.assertEqual(hash(r1), hash(r2))

	def testDiffer(self):
		r1 = ReviewHasheable(ReviewFake(revision=10, verify=False, subject='yyx'))
		r2 = ReviewHasheable(ReviewFake(revision=10, verify=False, subject='yyy'))
		self.assertEqual(hash(r1), hash(r2))
