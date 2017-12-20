import hashlib
import re


class AcTelegramUpdate:
	def __init__(self, update):
		self.update = update

	def save(self, db):
		db.set('update_id', self.update.update_id, 'telegram')

	def send(self, transport):
		transport.sendMessage(
			chat_id=self.update.message.chat.id,
			text=self.update.message.text
		)


class ReactionEcho:
	def check(self, update):
		return True

	def react(self, update):
		return AcTelegramUpdate(update)


class ReactionRestrict:
	def __init__(self, name, reaction):
		self.name = name
		self.reaction = reaction

	def check(self, update):
		if update.effective_user.username != self.name:
			return False
		return self.reaction.check(update)

	def react(self, update):
		assert update.effective_user.username == self.name
		return self.reaction.react(update)


class ReactionChoiced:
	def __init__(self, *reactions):
		self.reactions = reactions

	def check(self, update):
		return any((r.check(update) for r in self.reactions))

	def react(self, update):
		for r in self.reactions:
			if r.check(update):
				return r.react(update)


class AcTelegramText:
	def __init__(self, update, text):
		self.update = update
		self.text = text

	def save(self, db):
		db.set('update_id', self.update.update_id, 'telegram')

	def send(self, transport):
		transport.sendMessage(
			chat_id=self.update.effective_chat.id,
			text=self.text
		)


class ReactionAlways:
	def __init__(self, text):
		self.text = text

	def check(self, update):
		return True

	def react(self, update):
		return AcTelegramText(update, self.text)


class ReactionReview:
	def __init__(self, review):
		self.review = review

	def action(self, update):
		hash = hashlib.md5(self.review.active().encode('ascii')).hexdigest()
		rx = re.match('(approve|reject|ignore) %s' % hash, update.callback_query.data)
		if rx:
			return rx.group(1)
		return None

	def check(self, update):
		return self.action(update)

	def react(self, update):
		# @todo #49 Эта информация нам не интересна, сейчас она возвращается для теста.
		#  Необходимо предпринять меры, которые пожелал сделать админ.
		#  Режектим или сабмитим геррит, это раз.
		#  Если админ сказал Игнорировать - то надо прикопать в БД, что этот ревью нам не интересен
		return AcTelegramText(update, self.action(update))
