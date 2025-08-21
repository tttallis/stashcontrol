from django.shortcuts import render
from django.http import JsonResponse
from .models import Measurement

def dash(request):
	measurements = Measurement.objects.order_by('timestamp')
	timestamps = [m.timestamp.isoformat() for m in measurements]
	weights = [m.weight for m in measurements]
	data = {}
	for container in request.user.container_set.all():
		# data[container.pk]
		print(container)

	return render(request, 'dash.html', {
		'timestamps': timestamps,
		'weights': weights,
	})
	
def feed(request):
	measurements = Measurement.objects.order_by('timestamp')
	timestamps = [m.timestamp.isoformat() for m in measurements]
	weights = [m.weight for m in measurements]
	data = []
	
	for container in request.user.container_set.all():
		container_measures = measurements.filter(container=container)
		data.append({
			"x": [m.timestamp.isoformat() for m in container_measures],
			"y": [m.weight for m in container_measures],
			"type": "scatter",
			"name": container.product.name,
		})
	
	return JsonResponse({'data': data, 'layout': {'title': {'text':'WEEEEEEED'}}})