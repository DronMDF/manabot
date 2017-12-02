from time import sleep
from .sources import *
from .storage import *


class Application:
	def __init__(self, config):
		self.source = SoSafe(
			SoJoin(
				SoTelegram(
					TelegramBot(
						config,
						TelegramOffsetFromDb(TinyDataBase(config.value('telegram.db')))
					),
					ReactionEcho()
				),
				SoNewReview(config=config)
			)
		)
		self.storage = StDispatch(
			StTelegram(config),
			StDbTelegramOffset(TinyDataBase(config.value('telegram.db')))
		)

	def run(self):
		while True:
			acts = self.source.actions()
			for a in acts:
				self.storage.save(a)
			sleep(5)
