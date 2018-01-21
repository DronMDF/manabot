from time import sleep
from .sources import (
	AdminCommands,
	AdminFilteredCommands,
	ReactionAlways,
	ReactionChoiced,
	ReactionRestrict,
	ReactionReview,
	ReviewDifference,
	ReviewForUpdate,
	ReviewIgnored,
	ReviewIsNeed,
	ReviewListAdmin,
	ReviewListByCommands,
	ReviewOne,
	ReviewOnServer,
	ReviewUnderControl,
	ReviewVerified,
	SoAdminReviewIsOut,
	SoIgnoreReview,
	SoJoin,
	SoNewReview,
	SoNoTelegramTimeout,
	SoOutReview,
	SoReviewForAdmin,
	SoSafe,
	SoSubmitReview,
	SoTelegram,
	SoUpdateReview,
	TelegramBot,
	TelegramOffsetFromDb
)
from .storage import (
	StDatabase,
	StDispatch,
	StTelegram,
	TinyDataBase,
	TinySelect
)


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
				SoOutReview(
					ReviewDifference(
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db'))),
						ReviewOnServer(config)
					)
				),
				SoNewReview(
					ReviewDifference(
						ReviewOnServer(config),
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
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
						AdminFilteredCommands(
							AdminCommands(
								TinyDataBase(config.value('admin.db'))
							),
							'ignore'
						),
						ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
					)
				),
				SoSubmitReview(
					ReviewListByCommands(
						AdminFilteredCommands(
							AdminCommands(
								TinyDataBase(config.value('admin.db'))
							),
							'submit'
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
							# @todo #86 Этот кусок кода повторяется два раза.
							#  Возможно его стоит вынести в отдельный класс ReviewListForAdmin
							ReviewDifference(
								ReviewVerified(
									ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
								),
								ReviewIgnored(
									ReviewUnderControl(TinyDataBase(config.value('gerrit.db')))
								)
							)
						)
					),
					config.value('telegram.chat_id')
				)
				# @todo #55 Источник событий по режекту ревью
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
