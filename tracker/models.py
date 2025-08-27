from django.db import models
from datetime import date, datetime
from pytz import timezone
from django.conf import settings
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

class Patient(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	monthly_limit = models.PositiveIntegerField(default=60)
	monthly_target = models.PositiveIntegerField(default=30)

class Sponsor(models.Model):
	"""
	The company that "sponsors" the product.
	"""
	name = models.TextField()
	
	def __str__(self):
		return self.name

class Product(models.Model):
	"""
	A specific cannabis product.
	"""
	name = models.TextField()
	sponsor = models.ForeignKey(Sponsor, on_delete=models.PROTECT, null=True, blank=True)
	product_weight = models.FloatField()
	# product_type = models.ForeignKey() # for now, we assume it's flower
	catalyst_id = models.UUIDField(blank=True, null=True)
	strain = models.TextField(blank=True)
	thc = models.FloatField(default=0)
	cbd = models.FloatField(default=0)
	cbg = models.FloatField(default=0)
	cbv = models.FloatField(default=0)
	cbc = models.FloatField(default=0)
	thcv = models.FloatField(default=0)
	
	def __str__(self):
		return self.name
	
class Batch(models.Model):
	"""
	A specific batch
	"""
	product = models.ForeignKey('Product', on_delete=models.CASCADE)
	identifier = models.TextField()
	strain = models.TextField(blank=True)
	
	def __str__(self):
		return self.identifier
	
class Container(models.Model):
	"""
	A specific container of cannabis.
	"""
	product = models.ForeignKey('Product', on_delete=models.CASCADE)
	batch = models.ForeignKey('Batch', blank=True, null=True, on_delete=models.SET_NULL)
	dispensed = models.DateField(blank=True, null=True)
	patient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	opened = models.DateField(blank=True, null=True)
	finished = models.DateField(blank=True, null=True)
	include_container_weight = models.BooleanField(default=True, help_text="Is the container weight included in measurements?")
	include_lid_weight = models.BooleanField(default=False, help_text="Is the lid weight included in measurements?")
	include_humidity_pack_weight = models.BooleanField(default=True, help_text="Is a humidity pack weight included in measurements?")
	initial_gross = models.FloatField()
	cost = models.DecimalField(max_digits=7, decimal_places=2)
	
	def __str__(self):
		return f"{self.product.name} {self.pk}"
		
	def weight_at_time(self, dt):
		prev = self.measurement_set.filter(timestamp__lt=dt).order_by('-timestamp').first()
		next = self.measurement_set.filter(timestamp__gt=dt).order_by('timestamp').first()
		if not next and not prev:
			return 0
		if not prev:
			return next.weight
		if not next:
			return prev.weight
		epoch = next.timestamp - prev.timestamp
		prior_gap = dt - prev.timestamp
		delta = prev.weight - next.weight
		return prev.weight - (prior_gap / epoch * delta)
		
	def consumption_over_time(self, start, end):
		return self.weight_at_time(start) - self.weight_at_time(end)
		
	def get_day_times(self, day):
		tz = timezone(settings.TIME_ZONE)
		start = datetime.combine(day, datetime.min.time(), tzinfo=tz)
		end = datetime.combine(day, datetime.max.time(), tzinfo=tz)
		return start, end
		
	def get_month_times(self, day):
		tz = timezone(settings.TIME_ZONE)
		start = datetime.combine(day.replace(day=1), datetime.min.time(), tzinfo=tz)
		end = datetime.combine(day, datetime.max.time(), tzinfo=tz) + relativedelta(day=31)
		return start, end
		
	def day_moving_average_times(self, day):
		tz = timezone(settings.TIME_ZONE)
		start = day - timdelta(days=extra)
		end = day + timdelta(days=extra)
		start_weight = datetime.combine(start, datetime.min.time(), tzinfo=tz)
		end_weight = datetime.combine(end, datetime.max.time(), tzinfo=tz)
		return start, end

	def grams_per_day(self, day):
		return self.consumption_over_time(*self.get_day_times(day))
		
	def grams_per_month(self, day):
		return self.consumption_over_time(*self.get_month_times(day))
		
	def grams_per_day_moving_average(self, day, extra):
		return self.consumption_over_time(*self.day_moving_average_times(day)) / 2 * extra + 1

	def thc_per_day(self, day):
		return (self.grams_per_day(day) / self.product.product_weight) * (self.product.product_weight * self.product.thc)
		
	def cbd_per_day(self, day):
		return (self.grams_per_day(day) / self.product.product_weight) * (self.product.product_weight * self.product.cbd)
		
	def cbg_per_day(self, day):
		return (self.grams_per_day(day) / self.product.product_weight) * (self.product.product_weight * self.product.cbg)
		
	def cost_per_day(self, day):
		return (self.grams_per_day(day) / self.product.product_weight) * float(self.cost)
		
	@property
	def initial_tare(self):
		return self.initial_gross - self.initial_tare
	
class Measurement(models.Model):
	
	container = models.ForeignKey('Container', on_delete=models.CASCADE)
	timestamp = models.DateTimeField()
	weight = models.FloatField()
	initial = models.BooleanField()
	final = models.BooleanField()
	
	@property
	def net_weight(self):
		return self.weight - (self.container.initial_gross - self.container.product.product_weight)
	
	def __str__(self):
		return f"{self.container.product.name} - {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}: {self.weight}g"
	
class DeliveryMode(models.Model):
	name = models.CharField(max_length=100, blank=True)
	user_defined = models.BooleanField()
	user = models.ForeignKey('auth.User', blank=True, null=True, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.name
	
class Dose(models.Model):
	container = models.ForeignKey('Container', on_delete=models.CASCADE)
	timestamp = models.DateTimeField()
	mode = models.ForeignKey('DeliveryMode', on_delete=models.CASCADE)
	size = models.PositiveIntegerField(default=1)
	
class PatientDay(models.Model):
	patient = models.ForeignKey('patient', on_delete=models.CASCADE)
	date = models.DateField()
	grams = models.FloatField(default=0)
	cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)
	thc = models.FloatField(default=0)
	cbd = models.FloatField(default=0)
	cbg = models.FloatField(default=0)
	cbv = models.FloatField(default=0)
	cbc = models.FloatField(default=0)
	thcv = models.FloatField(default=0)
	containers = models.JSONField(default=list)
	
	def __str__(self):
		return f"{self.patient} {str(self.date)}"
