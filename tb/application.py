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
						# @todo #46 Когда мы нажимаем на кнопку - мы получаем событие с коллбеком
						#  сейчас оно никак не парсится.
						#  а нужно связать с герритом и отправить вердикт туда.
						ReactionEcho()
					)
				),
				SoNewReview(
					ReviewIds(ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))),
					ReviewIds(ReviewOnServer(config))
				),
				SoOutReview(
					ReviewIds(ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))),
					ReviewIds(ReviewOnServer(config))
				),
				SoUpdateReview(
					ReviewOnServer(config),
					ReviewUnderControl(TinyDataBase(config.value('gerrit.db'))),
				),
				SoAdminReviewIsOut(
					ReviewIsOut(
						AdminReview(TinyDataBase(config.value('admin.db'))),
						ReviewIds(
							ReviewVerified(
								ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
							)
						)
					),
					config.value('telegram.chat_id')
				),
				SoReviewForAdmin(
					ReviewIsNeed(
						ReviewOne(
							ReviewVerified(
								ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
							)
						),
						AdminReview(TinyDataBase(config.value('admin.db')))
					),
					config.value('telegram.chat_id')
				)
			)
		)
		self.storage = StDispatch(
			StTelegram(config),
			StDatabase(
				TinySelect({
					'telegram': TinyDataBase(config.value('telegram.db')),
					'gerrit': TinyDataBase(config.value('gerrit.db')),
					'admin': TinyDataBase(config.value('admin.db'))
				})
			)
		)

	def run(self):
		while True:
			acts = self.source.actions()
			for a in acts:
				self.storage.save(a)
			sleep(5)
