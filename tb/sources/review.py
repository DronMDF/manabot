class UpdateableReview:
	def __init__(self, exist, extern):
		self.exist = exist
		self.extern = extern
		self.doc_id = self.exist.doc_id

	def __getitem__(self, name):
		return self.extern[name]

	def needUpdate(self):
		return not all((
			self.exist['revision'] == self.extern['revision'],
			self.exist['verify'] == self.extern['verify']
		))
