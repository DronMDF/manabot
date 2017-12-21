import hashlib
import re


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


class AcAdminAction:
	def __init__(self, update_id, action, review_id):
		self.update_id = update_id
		self.action = action
		self.review_id = review_id

	def save(self, db):
		db.insert({
			'action': self.action,
			'review_id': self.review_id
		}, 'admin')
		db.set('update_id', self.update_id, 'telegram')

	def send(self, transport):
		pass


class ReactionReview:
	def __init__(self, review):
		self.review = review

	def action(self, update):
		hash = hashlib.md5(self.review.active().encode('ascii')).hexdigest()
		rx = re.match(
			'(approve|reject|ignore) %s' % hash,
			update.callback_query.data
		)
		if rx:
			return rx.group(1)
		return None

	def check(self, update):
		return self.action(update)

	def react(self, update):
		return AcAdminAction(
			update.update_id,
			self.action(update),
			self.review.active()
		)
