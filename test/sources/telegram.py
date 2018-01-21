import unittest
import telegram
from tb.sources.reaction import ReactionAlways
from tb.sources.telegram import SoTelegram


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
	def __init__(self):
		self.chat_id = None
		self.text = None

	def sendMessage(self, chat_id, text):
		self.chat_id = chat_id
		self.text = text


class SoTelegramTest(unittest.TestCase):
	def test(self):
		so = SoTelegram(FakeBot("hello"), ReactionAlways('ehlo'))
		transport = FakeTransport()
		so.actions()[0].send(transport)
		self.assertEqual(transport.text, "ehlo")
