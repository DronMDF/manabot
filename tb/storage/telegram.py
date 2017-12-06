import telegram

# @todo #38 Необходимо игнорировать все таймауты,
#  возникающие в процессе обращения к серверу телеграмм.
#  такое бывает и нужно умето в случае ошибок
#  нормально реагировать и не ломать логику.
#  Там возникает исключение telegram.error.TimedOut


class StTelegram:
	def __init__(self, config):
		self.config = config

	def save(self, action):
		bot = telegram.Bot(self.config.value('telegram.token'))
		action.send(bot)
