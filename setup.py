#!/usr/bin/env python3

import glob
import sys
from distutils.core import setup, Command
from itertools import chain
from unittest import TestLoader, TextTestRunner

import pycodestyle
from radon.cli import Config
from radon.cli.harvest import CCHarvester, MIHarvester
from radon.complexity import SCORE


class Style(Command):
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def files(self):
		return glob.iglob('**/*.py', recursive=True)

	def pep8(self, f):
		return pycodestyle.Checker(f, ignore=['W191']).check_all() == 0

	def radon_cc(self, f, config):
		result = True
		for ccr in CCHarvester([f], config).results:
			for r in ccr[1]:
				''' Не допускается Cyclomatic Complexity больше 5 '''
				if r.complexity > 5:
					print('%s: High cyclomatic complexity - %s' % (ccr[0], r))
					result = False
		return result

	def radon_mi(self, f, config):
		result = True
		for mir in MIHarvester([f], config).results:
			''' Не допускается Maintainability Index ниже 50% '''
			if mir[1]['mi'] < 50:
				print('%s: Low maintainability index - %u%%' % (mir[0], mir[1]['mi']))
				result = False
		return result

	def radon(self, f):
		config = Config(
			exclude=None,
			ignore=None,
			no_assert=False,
			show_closures=False,
			order=SCORE,
			multi=True
		)
		return all((
			self.radon_cc(f, config),
			self.radon_mi(f, config)
		))

	def check(self, f):
		return all((
			self.pep8(f),
			self.radon(f)
		))

	def run(self):
		try:
			if not all((self.check(f) for f in self.files())):
				print("Style check failed")
				sys.exit(-1)
		except Exception as e:
			print(e)
			sys.exit(-1)


class Test(Command):
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		try:
			# @todo #71 Тесты считаются странно,
			#  удалил два теста, и их стало меньше на 8...
			#  Возможно это из за звездочных импортов
			suite = TestLoader().discover('.', '*.py')
			runner = TextTestRunner()
			results = runner.run(suite)
			if not results.wasSuccessful():
				print("Test failed")
				sys.exit(-1)
		except Exception as e:
			print(e)
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
