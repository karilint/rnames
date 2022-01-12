from rnames_app.models import BinningProgress

# Delete lock on binning on startup
try:
	BinningProgress.objects.filter(name='lock')[0].delete()
except:
	pass

keys = [
	'error',
	'status',

	'stage_berg',
	'stage_webby',
	'stage_stages',
	'stage_periods',
	'stage_combined_stages',
	'stage_combined_periods',

	'db_update'
]

class BinningStageProgressUpdater():
	current = 0

	def __init__(self, bpu, stage, max):
		self.bpu = bpu
		self.stage = stage
		self.max = max

	def update(self):
		self.current = self.current + 1
		self.bpu.update_stage(self.stage, self.current, self.max)

class DatabaseUpdateProgressBarUpdater(BinningStageProgressUpdater):
	def update(self):
		self.current = self.current + 1
		if self.current % 100 == 0:
			self.bpu.update_stage(self.stage, self.current, self.max)


class BinningProgressUpdater():
	def __init__(self):
		for key in keys:
			if len(BinningProgress.objects.filter(name=key)) == 0:
				try:
					BinningProgress(name=key).save()
				except:
					pass


	def update(self, key, text=None, value_one=None, value_two=None):
		obj = BinningProgress.objects.filter(name=key)[0]

		if text != None:
			obj.text = text
		if value_one != None:
			obj.value_one = value_one

		if value_two != None:
			obj.value_two = value_two

		obj.save()

	def start_binning(self):
		try:
			BinningProgress(name='lock').save()
			self.update(key='status', value_one=1)

			self.update(key='stage_berg', value_one=0, value_two=8)
			self.update(key='stage_webby', value_one=0, value_two=8)
			self.update(key='stage_stages', value_one=0, value_two=8)
			self.update(key='stage_periods', value_one=0, value_two=8)

			self.update(key='stage_combined_stages', value_one=0, value_two=1)
			self.update(key='stage_combined_periods', value_one=0, value_two=1)

			self.update(key='db_update', value_one=0, value_two=0)
			return True
		except:
			return False

	def finish_binning(self):
		self.update(key='status', value_one=2)
		BinningProgress.objects.filter(name='lock').delete()

	def update_stage(self, stage, current, max):
		self.update(key=stage, value_one=current, value_two=max)

	def set_error(self, text):
		self.update(key='error', text=text)
		self.update(key='status', value_one=-1)
		BinningProgress.objects.filter(name='lock').delete()

	def stages_updater(self):
		return BinningStageProgressUpdater(self, 'stage_stages', 8)

	def periods_updater(self):
		return BinningStageProgressUpdater(self, 'stage_periods', 8)

	def webby_updater(self):
		return BinningStageProgressUpdater(self, 'stage_webby', 8)

	def berg_updater(self):
		return BinningStageProgressUpdater(self, 'stage_berg', 8)

	def binned_stages_updater(self):
		return BinningStageProgressUpdater(self, 'stage_combined_stages', 1)

	def binned_periods_updater(self):
		return BinningStageProgressUpdater(self, 'stage_combined_periods', 1)

	def db_update_progress_updater(self, max):
		return DatabaseUpdateProgressBarUpdater(self, 'db_update', max)
