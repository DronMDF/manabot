from unittest import TestCase
from tb.config_args import ConfigFromArgs
from tb.config_default import ConfigDefault


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

	def testValueNotConfiguredFromCommandLine(self):
		config = ConfigFromArgs(['p'], ConfigDefault({'gerrit.db': 'gerrit.json'}))
		self.assertEqual(config.value('gerrit.db'), 'gerrit.json')
