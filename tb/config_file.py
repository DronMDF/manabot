from configparser import ConfigParser, NoOptionError, NoSectionError


class ConfigFile:
	''' Файл с конфигурацией '''
	def __init__(self, config):
		self.config = config

	def readall(self):
		return open(self.config.value('config'), 'r').read()


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
