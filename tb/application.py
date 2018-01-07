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
						ReactionChoiced(
							ReactionRestrict(
								config.value('telegram.username'),
								ReactionChoiced(
									ReactionReview(
										AdminReview(TinyDataBase(config.value('admin.db')))
									),
									ReactionAlways("Не совсем понятно, что ты хочешь мне сказать...")
								)
							),
							ReactionAlways("Ты кто такой, давай, досвидания")
						)
					)
				),
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
				# @todo #57 Админу показываем только те ревью,
				#  которые не отмечены как игнорированные
				#  Если ревью отмечено как игнорированное,
				#  оно должно уйти с ревью и освободить место для других ревью
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
				),
				SoIgnoreReview(
					AdminIgnoreCommands(
						AdminCommands(
							TinyDataBase(config.value('admin.db'))
						)
					)
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
