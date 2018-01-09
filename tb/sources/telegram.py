import telegram
import unittest
from .reaction import ReactionAlways


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


# @todo #38 Нужно сделать класс,
#  который будет игнорировать таймауты в этом классе.
#  Там возникает исключение telegram.error.TimedOut

class SoTelegram:
	def __init__(self, bot, reaction):
		self.bot = bot
		self.reaction = reaction

	def actions(self):
		update = self.bot.getUpdates()
		return [self.reaction.react(u) for u in update if self.reaction.check(u)]


class FakeMessage(telegram.Message):
	def __init__(self, text):
		super().__init__(
			chat=telegram.Chat(id=1, type='private'),
			message_id=1,
			from_user=telegram.User(
				id=1,
				first_name='Test',
				is_bot=False
			),
			date=1,
			text=text,
		)


class FakeBot:
	def __init__(self, text):
		self.text = text

	def getUpdates(self):
		return [telegram.Update(7, FakeMessage(self.text))]


class FakeTransport:
	def sendMessage(self, chat_id, text):
		self.chat_id = chat_id
		self.text = text


class SoTelegramTest(unittest.TestCase):
	def test(self):
		so = SoTelegram(FakeBot("hello"), ReactionAlways('ehlo'))
		transport = FakeTransport()
		so.actions()[0].send(transport)
		self.assertEqual(transport.text, "ehlo")
