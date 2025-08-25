from django.http import JsonResponse
from .models import Measurement
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

@login_required
def dash(request):
	today = timezone.now()
	start = datetime.combine(today.replace(day=1), datetime.min.time())
	end = datetime.combine(today, datetime.max.time()) + relativedelta(day=31)
	dispensed_this_month = request.user.container_set.filter(dispensed__range=(start, end))#.annotate(total_grams=Sum("product__product_weight"))
	total_weight = 0
	total_cost = 0
	for d in dispensed_this_month:
		total_weight += d.product.product_weight
		total_cost += d.cost		
	return render(request, 'dash.html', {"dispensed": dispensed_this_month, "total_weight": total_weight, "total_cost": total_cost})
	
@login_required
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
			"line": {"shape": 'spline'},
		})
		
	# data.append({
	# 	"x": [m.timestamp.isoformat() for m in container_measures],
	# 	"y": [m.net_weight for m in measurements],
	# 	"type": "scatter",
	# 	"name": "All flower",
	# })
	
	return JsonResponse({'data': data, 'layout': {'title': {'text':'Stash net weight'}}})
	
@login_required
def grams(request):
	measurements = Measurement.objects.filter(container__patient=request.user).order_by('timestamp')
	start = measurements.first().timestamp.date()# + timedelta(days=1)
	end = measurements.last().timestamp.date()
	dates = [start+timedelta(days=x) for x in range((end-start).days)]
	products = request.user.container_set.values('product__name', 'pk').distinct()
	prods = {}
	this_week = 0
	last_week = 0
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
		this_week += container.consumption_over_time(timezone.now(), timezone.now() - timedelta(days=7))
		last_week += container.consumption_over_time(timezone.now() - timedelta(days=7), timezone.now() - timedelta(days=14))
		
	return JsonResponse({'data': list(prods.values()), 'layout': {'title': {'text':'Grams per day'}, 'barmode': 'stack'}, 'this_week': this_week, 'last_week': last_week})

@login_required
def cannabinoids(request):
	measurements = Measurement.objects.filter(container__patient=request.user).order_by('timestamp')
	start = measurements.first().timestamp.date()
	end = measurements.last().timestamp.date()
	dates = [start+timedelta(days=x) for x in range((end-start).days)]
	# TO DO: I'm sure there's a more elegant and performant solution using comprehensions
	# but for now I'm using this dumb approach
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

@login_required
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
	
@login_required
def dashboard(request):
	today = timezone.now()
	start = datetime.combine(today.replace(day=1), datetime.min.time())
	end = datetime.combine(today, datetime.max.time()) + relativedelta(day=31)
	usage = {}
	for container in request.user.container_set.all(): # filter by time
		if container.product.name in usage:
			usage[container.product.name] = usage[container.product.name] + container.grams_per_month(today)
		else:
			usage[container.product.name] = container.grams_per_month(today)
		
	usage['all'] = sum(usage.values())
	usage['now'] = today

	return JsonResponse({'data': usage, 'layout': {}})

def login_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
	
		user = authenticate(request, username=username, password=password)
	
		if user is not None:
			login(request, user)
			return redirect('dashboard')  # ✅ redirect to dashboard now
		else:
			messages.error(request, 'Invalid username or password.')
	
	return render(request, 'login.html')
