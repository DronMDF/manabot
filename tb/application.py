from time import sleep
from .sources import *
from .storage import *


class Application:
	def __init__(self, config):
		self.source = SoSafe(
			SoJoin(
				SoNoTelegramTimeout(
					SoTelegram(
						TelegramBot(
							config,
							TelegramOffsetFromDb(TinyDataBase(config.value('telegram.db')))
						),
						ReactionEcho()
					)
				),
				SoNewReview(
					ReviewUnderControl(TinyDataBase(config.value('gerrit.db'))),
					ReviewOnServer(config)
				),
				SoOutReview(
					ReviewUnderControl(TinyDataBase(config.value('gerrit.db'))),
					ReviewOnServer(config)
				)
			)
		)
		self.storage = StDispatch(
			StTelegram(config),
			StDatabase(
				TinySelect({
					'telegram': TinyDataBase(config.value('telegram.db')),
					'gerrit': TinyDataBase(config.value('gerrit.db'))
				})
			)
		)

	def run(self):
		while True:
			acts = self.source.actions()
			for a in acts:
				self.storage.save(a)
			sleep(5)
