from django.shortcuts import render
from django.http import JsonResponse
from .models import Measurement
from datetime import timedelta

def dash(request):

	return render(request, 'dash.html', {})
	
def feed(request):
	measurements = Measurement.objects.filter(container__patient=request.user).order_by('timestamp')
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
	
def grams(request):
	measurements = Measurement.objects.filter(container__patient=request.user).order_by('timestamp')
	start = measurements.first().timestamp.date()# + timedelta(days=1)
	end = measurements.last().timestamp.date()
	dates = [start+timedelta(days=x) for x in range((end-start).days)]
	products = request.user.container_set.values('product__name', 'pk').distinct()
	prods = {}
	for container in request.user.container_set.all():
		if container.product.name in prods:
			prods[container.product.name]["y"] = [i+j for i,j in zip(prods[container.product.name]["y"], [container.grams_per_day(day) for day in dates])]

		else:
			prods[container.product.name] = {
				"x": dates,
				"y": [container.grams_per_day(day) for day in dates],
				"type": "bar",
				"name": container.product.name,
			}
	return JsonResponse({'data': list(prods.values()), 'layout': {'title': {'text':'Grams per day'}, 'barmode': 'stack'}})

def cannabinoids(request):
	measurements = Measurement.objects.filter(container__patient=request.user).order_by('timestamp')
	start = measurements.first().timestamp.date()
	end = measurements.last().timestamp.date()
	dates = [start+timedelta(days=x) for x in range((end-start).days)]
	data = []
	canna = {
		"thc": {
			"x": dates,
			"y": [0 for d in dates],
			"type": "bar",
			"name": "THC",
		},
		"cbd": {
			"x": dates,
			"y": [0 for d in dates],
			"type": "bar",
			"name": "CBD",
		},
		"cbg": {
			"x": dates,
			"y": [0 for d in dates],
			"type": "bar",
			"name": "CBG",
		},	
	}
	for container in request.user.container_set.all():
		canna['thc']['y'] =  [i+j for i,j in zip(canna["thc"]["y"], [container.thc_per_day(day) for day in dates])]
		canna['cbd']['y'] =  [i+j for i,j in zip(canna["cbd"]["y"], [container.cbd_per_day(day) for day in dates])]
		canna['cbg']['y'] =  [i+j for i,j in zip(canna["cbg"]["y"], [container.cbg_per_day(day) for day in dates])]
	return JsonResponse({'data': list(canna.values()), 'layout': {'title': {'text':'Cannabinoids'}, 'barmode': 'stack'}})

def cost(request):
	measurements = Measurement.objects.filter(container__patient=request.user).order_by('timestamp')
	start = measurements.first().timestamp.date()
	end = measurements.last().timestamp.date()
	dates = [start+timedelta(days=x) for x in range((end-start).days)]
	data = []
	for container in request.user.container_set.all():
		data.append({
			"x": dates,
			"y": [container.cost_per_day(day) for day in dates],
			"type": "bar",
			"name": container.product.name,
		})
	return JsonResponse({'data': data, 'layout': {'title': {'text':'Cost per day'}, 'barmode': 'stack'}})
