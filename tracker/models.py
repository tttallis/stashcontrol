from django.db import models

class Product(models.Model):
	"""
	A specific cannabis product.
	"""
	name = models.TextField()
	product_weight = models.FloatField()
	# product_type = models.ForeignKey() # for now, we assume it's flower
	catalyst_id = models.UUIDField(blank=True, null=True)
	# strain?
	
class Batch(models.Model):
	"""
	A specific batch
	"""
	identifier = models.TextField()
	# strain?
	
class Container(models.Model):
	"""
	A specific container of cannabis.
	"""
	product = models.ForeignKey('Product', on_delete=models.CASCADE)
	batch = models.ForeignKey('Batch', blank=True, null=True, on_delete=models.SET_NULL)
	dispensed = models.DateTimeField(blank=True, null=True)
	patient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	opened = models.DateTimeField(blank=True, null=True)
	finished = models.DateTimeField(blank=True, null=True)
	include_container_weight = models.BooleanField(default=True, help_text="Is the container weight included in measurements?")
	include_lid_weight = models.BooleanField(default=False, help_text="Is the lid weight included in measurements?")
	include_humidity_pack_weight = models.BooleanField(default=True, help_text="Is a humidity pack weight included in measurements?")
	
class Measurement(models.Model):
	
	container = models.ForeignKey('Container', on_delete=models.CASCADE)
	timestamp = models.DateTimeField()
	weight = models.FloatField()
	
class DeliveryMode(models.Model):
	name = models.CharField(max_length=100, blank=True)
	user_defined = models.BooleanField()
	user = models.ForeignKey('auth.User', blank=True, null=True, on_delete=models.CASCADE)
	
class Dose(models.Model):
	container = models.ForeignKey('Container', on_delete=models.CASCADE)
	timestamp = models.DateTimeField()
	mode = models.ForeignKey('DeliveryMode', on_delete=models.CASCADE)
	size = models.PositiveIntegerField(default=1)