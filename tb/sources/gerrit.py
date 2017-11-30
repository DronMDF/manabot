from pygerrit2.rest import GerritRestAPI
from requests.auth import HTTPBasicAuth
from unittest import TestCase

# @todo #1 Формат Action для создания новых ревью в БД
#  Новый ревью должен создаваться неинициализированным,
#  чтобы попасть под очередной анализ


class ReviewUnderControl:
	def __init__(self, db):
		self.db = db

	def __next__(self):
		return (i['id'] for i in db.all())


class ReviewOnServer:
	def __init__(self, config):
		self.config = config

	def __next__(self):
		return (
			i['id'] for i in GerritRestAPI(
				url=self.config.value('gerrit.url'),
				auth=HTTPDigestAuth(
					self.config.value('gerrit.user'),
					self.config.value('gerrit.password')
				)
			).get('/changes/')
		)


class SoNewReview:
	def __init__(self, config):
		self.controlled_ids = ReviewUnderControl(
			TinyDataBase(config.value('gerrit.db'))
		)
		self.remote_ids = ReviewOnServer(config)

	def actions(self):
		# @todo #13 Найти на сервере (self.remote_ids) что-то такое,
		#  чего нет в списке контролируемых. (self.controlled_ids)
		#  И на эти ревью создать Action
		return []


class SoNewReviewTest(TestCase):
	def testNewFromClean(self):
		# @todo #13 Написать тест на создание элементов, если база пуста.
		#  Класс пока не очень тестируемый.
		pass

	def testNewWithExists(self):
		# @todo #13 Написать тест на создание элементов, если в базе что-то есть
		pass
