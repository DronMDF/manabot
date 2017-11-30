from argparse import ArgumentParser
from unittest import TestCase


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
		if all((
			name in params,
			params[name] in result,
			result[params[name]] is not None
		)):
			value = result[params[name]]
		else:
			value = self.defaults.value(name)
		return value


class ConfigFromArgsTest(TestCase):
	def testTelegramTokenInCommandLine(self):
		config = ConfigFromArgs(['prog', '-t', 'token'], ConfigDefault({}))
		self.assertEqual(config.value('telegram.token'), 'token')

	def testConfigFileInCommandLine(self):
		config = ConfigFromArgs(['p', '-c', '/etc/tb.conf'], ConfigDefault({}))
		self.assertEqual(config.value('config'), '/etc/tb.conf')

	def testDefaults(self):
		config = ConfigFromArgs(['p'], ConfigDefault({'telegram.token': 'token'}))
		self.assertEqual(config.value('telegram.token'), 'token')
