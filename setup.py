#!/usr/bin/env python3

import glob
import sys
import os
# pylint: disable=no-name-in-module,import-error
from distutils.core import setup, Command
from unittest import TestLoader, TextTestRunner

import pycodestyle
from pylint.lint import Run
from radon.cli import Config
from radon.cli.harvest import CCHarvester, MIHarvester
from radon.complexity import SCORE


class PylintReporter:
	def __init__(self):
		self.path_strip_prefix = os.getcwd() + os.sep
		self.errors = 0

	def on_set_current_module(self, modulename, filepath):
		pass

	def handle_message(self, msg):
		self.errors += 1
		print("%s:%u: %s (%s)" % (msg.path, msg.line, msg.msg, msg.symbol))

	def display_messages(self, section):
		pass

	def on_close(self, stat, previous_stat):
		pass


class Style(Command):
	user_options = []
	reporter = PylintReporter()

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def files(self):
		return glob.iglob('**/*.py', recursive=True)

	def pep8(self, filename):
		return pycodestyle.Checker(filename, ignore=['W191']).check_all() == 0

	def pylint(self, filename):
		# @todo #102 Постоянно выскакивает сообщение
		#  'No config file found, using default configuration'
		#  от него можно избавиться в теории, я пока не нашел подходов
		# @todo #105 в pylint ширина строки по умолчанию равна 100.
		#  Если вдруг он умеет нормально мерять табы,
		#  то можно поджать этот параметр для наших исходников.
		#  Это настраивается в опциях, параметр max-line-length,
		#  и вопрос в том, как это заинжектить.
		Run([
			'--enable=all',
			'--disable=bad-continuation',
			'--disable=broad-except',
			'--disable=invalid-name',
			'--disable=locally-disabled',
			'--disable=missing-docstring',
			'--disable=mixed-indentation',
			'--disable=no-self-use',
			'--disable=pointless-string-statement',
			'--disable=redefined-builtin',
			'--disable=suppressed-message',
			'--disable=too-few-public-methods',
			'--disable=useless-suppression',
			'--score=n',
			filename
		], reporter=self.reporter, exit=False)
		return self.reporter.errors == 0

	def radon_cc(self, filename, config):
		result = True
		for ccr in CCHarvester([filename], config).results:
			for result in ccr[1]:
				''' Не допускается Cyclomatic Complexity больше 5 '''
				if result.complexity > 5:
					print('%s: High cyclomatic complexity - %s' % (ccr[0], result))
					result = False
		return result

	def radon_mi(self, filename, config):
		result = True
		for mir in MIHarvester([filename], config).results:
			''' Не допускается Maintainability Index ниже 50% '''
			if mir[1]['mi'] < 50:
				print('%s: Low maintainability index - %u%%' % (mir[0], mir[1]['mi']))
				result = False
		return result

	def radon(self, filename):
		config = Config(
			exclude=None,
			ignore=None,
			no_assert=False,
			show_closures=False,
			order=SCORE,
			multi=True
		)
		return all((
			self.radon_cc(filename, config),
			self.radon_mi(filename, config)
		))

	def check(self, filename):
		return all((
			self.pep8(filename),
			self.pylint(filename),
			self.radon(filename)
		))

	def run(self):
		try:
			# @todo #102 Список файлов стоит передавать на контроль полностью
			#  это позволит более оптимально организовать проверку в разных чекерах.
			results = [self.check(f) for f in self.files()]
			if not all(results):
				print("Style check failed")
				sys.exit(-1)
		except Exception as exc:
			print(exc)
			sys.exit(-1)


class Test(Command):
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		try:
			suite = TestLoader().discover('test', '*.py')
			runner = TextTestRunner()
			results = runner.run(suite)
			if not results.wasSuccessful():
				print("Test failed")
				sys.exit(-1)
		except Exception as exc:
			print(exc)
			sys.exit(-1)


if __name__ == '__main__':
	setup(
		name='Manabot',
		version='1.0',
		description='Intracorporate management servers',
		author='Andrey Valyaev',
		author_email='dron.valyaev@gmail.com',
		url='https://github.com/DronMDF/manabot',
		packages=['tb', 'tb.sources', 'tb.storage'],
		data_files=[
			# @todo #2 В файле manabot.conf должен содержаться пример конфигурации.
			#  А этот файл видимо должен называться manabot.init и переименовываться при
			#  инсталляции
			('/etc/init', ['manabot.conf']),
			('/lib/systemd/system', ['manabot.service']),
			('/usr/bin', ['manabot'])
		],
		cmdclass={'style': Style, 'test': Test}
	)
