from unittest import TestCase
from tb.config_default import ConfigDefault
from tb.config_file import ConfigFromFile


class ConfigString:
	''' Строка с файловой конфигурацией '''
	def __init__(self, content):
		self.content = content

	def readall(self):
		return self.content


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
