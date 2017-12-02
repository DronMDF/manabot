from configparser import ConfigParser, NoOptionError, NoSectionError
from unittest import TestCase
from .config_default import ConfigDefault


class ConfigFile:
	''' Файл с конфигурацией '''
	def __init__(self, config):
		self.config = config

	def readall(self):
		return open(self.config.value('config'), 'r').read()


class ConfigString:
	''' Строка с файловой конфигурацией '''
	def __init__(self, content):
		self.content = content

	def readall(self):
		return self.content


class ConfigFromFile:
	def __init__(self, configfile, defaults):
		self.configfile = configfile
		self.defaults = defaults

	def value(self, name):
		config = ConfigParser()
		config.read_string(self.configfile.readall())
		try:
			result = config.get(*name.split('.'))
		except (NoSectionError, NoOptionError):
			result = self.defaults.value(name)
		return result


class ConfigFromFileTest(TestCase):
	def testTelegramTokenInFile(self):
		config = ConfigFromFile(
			ConfigString('[telegram]\ntoken=token'),
			ConfigDefault({})
		)
		self.assertEqual(config.value('telegram.token'), 'token')

	def testConfigFileDefaults(self):
		config = ConfigFromFile(
			ConfigString(''),
			ConfigDefault({'section.key': 'value'})
		)
		self.assertEqual(config.value('section.key'), 'value')

	def testConfigFileDefaultsIfSectionPresent(self):
		config = ConfigFromFile(
			ConfigString('[section]'),
			ConfigDefault({'section.key': 'value'})
		)
		self.assertEqual(config.value('section.key'), 'value')

	def testFileWithTwoGroups(self):
		config = ConfigFromFile(
			ConfigString(
				'\n'.join((
					'[telegram]',
					'token = token',
					'[gerrit]',
					'url = http://gerrit.com',
					'db = gerrit.json'
				))
			),
			ConfigDefault({})
		)
		self.assertEqual(config.value('gerrit.db'), 'gerrit.json')
