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


class AcAdminAction:
	def __init__(self, update_id, action, review_id):
		self.update_id = update_id
		self.action = action
		self.review_id = review_id

	def save(self, db):
		db.insert(
			{
				'action': self.action,
				'review_id': self.review_id
			},
			database='admin',
			table='commands'
		)
		db.set('update_id', self.update_id, 'telegram')

	def send(self, transport):
		pass
