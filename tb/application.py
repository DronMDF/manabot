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
				# @todo #40 Необходимо проверять, что ревью,
				#  который назначен на админа все еще ждет его реакции.
				#  Он может быть уже закрыт, или потерял статус верификации
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
