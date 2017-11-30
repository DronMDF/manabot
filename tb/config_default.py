class ConfigDefault:
	def __init__(self, values):
		self.values = values

	def value(self, name):
		if name not in self.values:
			raise RuntimeError("No param '%s' in configuration" % name)
		return self.values[name]
