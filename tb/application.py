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
						ReactionRestrict(
							config.value('telegram.username'),
							ReactionChoiced(
								ReactionReview(
									ReviewListAdmin(TinyDataBase(config.value('admin.db')))
								),
								ReactionAlways("Не совсем понятно, что ты хочешь мне сказать...")
							)
						)
					)
				),
				# Gerrit sources
				SoNewReview(
					ReviewDifference(
						ReviewOnServer(config),
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
					)
				),
				SoOutReview(
					ReviewDifference(
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db'))),
						ReviewOnServer(config)
					)
				),
				SoUpdateReview(
					ReviewForUpdate(
						ReviewOnServer(config),
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db'))),
					)
				),
				# Admin sources
				SoIgnoreReview(
					ReviewListByCommands(
						AdminIgnoreCommands(
							AdminCommands(
								TinyDataBase(config.value('admin.db'))
							)
						),
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
					)
				),
				SoAdminReviewIsOut(
					ReviewDifference(
						ReviewListAdmin(TinyDataBase(config.value('admin.db'))),
						ReviewDifference(
							ReviewVerified(
								ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
							),
							ReviewIgnored(
								ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
							)
						)
					),
					config.value('telegram.chat_id')
				),
				SoReviewForAdmin(
					ReviewOne(
						ReviewIsNeed(
							ReviewListAdmin(TinyDataBase(config.value('admin.db'))),
							ReviewVerified(
								ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
							)
						)
					),
					config.value('telegram.chat_id')
				)
				# @todo #55 Источник событий по режекту ревью
				#  Команды админа хранятся в БД админа, в отдельной таблице задач.
				# @todo #55 Источник событий по аппруву ревью
				#  Команды админа хранятся в БД админа, в отдельной таблице задач.
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
