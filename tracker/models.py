from django.db import models

class Product(models.Model):
	"""
	A specific cannabis product.
	"""
	name = models.TextField()
	product_weight = models.FloatField()
	# product_type = models.ForeignKey() # for now, we assume it's flower
	catalyst_id = models.UUIDField(blank=True, null=True)
	strain = models.TextField(blank=True)
	
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
	
	def __str__(self):
		return f"{self.product.name} {self.pk}"
	
class Measurement(models.Model):
	
	container = models.ForeignKey('Container', on_delete=models.CASCADE)
	timestamp = models.DateTimeField()
	weight = models.FloatField()
	
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