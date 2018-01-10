import telegram


class TelegramOffsetFromDb:
	def __init__(self, db):
		self.db = db

	def value(self):
		return self.db.get('update_id', 0) + 1


class TelegramBot:
	def __init__(self, config, offset):
		self.config = config
		self.offset = offset

	def getUpdates(self):
		bot = telegram.Bot(self.config.value("telegram.token"))
		return bot.getUpdates(offset=self.offset.value())


class SoNoTelegramTimeout:
	def __init__(self, source):
		self.source = source

	def actions(self):
		try:
			actions = self.source.actions()
		except telegram.error.TimedOut:
			actions = []
		return actions


class SoTelegram:
	def __init__(self, bot, reaction):
		self.bot = bot
		self.reaction = reaction

	def actions(self):
		update = self.bot.getUpdates()
		return [self.reaction.react(u) for u in update if self.reaction.check(u)]
