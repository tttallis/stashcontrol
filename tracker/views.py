from django.shortcuts import render
from django.http import JsonResponse
from .models import Measurement

def dash(request):

	return render(request, 'dash.html', {})
	
def feed(request):
	measurements = Measurement.objects.order_by('timestamp')
	timestamps = [m.timestamp.isoformat() for m in measurements]
	weights = [m.weight for m in measurements]
	data = []
	
	for container in request.user.container_set.all():
		container_measures = measurements.filter(container=container)
		data.append({
			"x": [m.timestamp.isoformat() for m in container_measures],
			"y": [m.net_weight for m in container_measures],
			"type": "scatter",
			"name": container.product.name,
		})
		
	# data.append({
	# 	"x": [m.timestamp.isoformat() for m in container_measures],
	# 	"y": [m.net_weight for m in measurements],
	# 	"type": "scatter",
	# 	"name": "All flower",
	# })
	
	return JsonResponse({'data': data, 'layout': {'title': {'text':'Stash net weight'}}})
	
def thc(request):
	pass