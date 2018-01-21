import hashlib
import re
from .action import *


class ReactionRestrict:
	def __init__(self, name, reaction):
		self.name = name
		self.reaction = reaction

	def check(self, update):
		user = update.effective_user
		if user is None or user.username != self.name:
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


class ReactionAlways:
	def __init__(self, text):
		self.text = text

	def check(self, update):
		assert update
		return True

	def react(self, update):
		return AcTelegramText(update, self.text)


class ReactionReview:
	def __init__(self, reviews):
		self.reviews = reviews

	def action(self, update):
		if update.callback_query:
			review_id = next((r['id'] for r in self.reviews), 'none')
			review_id_hash = hashlib.md5(review_id.encode('ascii')).hexdigest()
			rx = re.match(
				'(approve|reject|ignore) %s' % review_id_hash,
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
			next(iter(self.reviews))['id']
		)
