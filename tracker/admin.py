from django.contrib import admin
from .models import Product, Batch, Container, Dose, Measurement, DeliveryMode

class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'product_weight')

class MeasurementAdmin(admin.ModelAdmin):
	list_display = ('timestamp', 'container', 'weight', 'net_weight')

admin.site.register(Product, ProductAdmin)
admin.site.register(Batch)
admin.site.register(Container)
admin.site.register(Dose)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(DeliveryMode)

