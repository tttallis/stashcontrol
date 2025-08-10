from django.contrib import admin
from .models import Product, Batch, Container, Dose, Measurement, DeliveryMode

# Register your models here.
admin.site.register(Product)
admin.site.register(Batch)
admin.site.register(Container)
admin.site.register(Dose)
admin.site.register(Measurement)
admin.site.register(DeliveryMode)

