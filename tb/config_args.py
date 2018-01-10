from argparse import ArgumentParser


class ConfigFromArgs(object):
	def __init__(self, args, defaults):
		self.args = args
		self.defaults = defaults

	def value(self, name):
		parser = ArgumentParser()
		parser.add_argument('--token', '-t', nargs='?')
		parser.add_argument('--config', '-c', nargs='?')
		result = vars(parser.parse_args(self.args[1:]))
		params = {
			'config': 'config',
			'telegram.token': 'token'
		}
		if params.get(name) in result and result[params[name]] is not None:
			value = result[params[name]]
		else:
			value = self.defaults.value(name)
		return value
