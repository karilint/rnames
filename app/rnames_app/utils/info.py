class FakeUpdater():
	def update(self, msg, meta):
		pass

class BinningProgressUpdater():
	task = None

	def __init__(self, task):
		self.task = task

	def update(self, msg):
		if self.task is not None:
			self.task.update_state(state='PROGRESS', meta={'msg': msg})
