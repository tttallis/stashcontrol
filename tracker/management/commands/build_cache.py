from django.core.management.base import BaseCommand, CommandError
from tracker.models import Patient, Measurement, PatientDay
from datetime import timedelta

class Command(BaseCommand):
	help = "Closes the specified poll for voting"

	def handle(self, *args, **options):
		for patient in Patient.objects.all():
			print(patient.user.container_set.all())
			measurements = Measurement.objects.filter(container__patient=patient.user).order_by('timestamp')
			start = measurements.first().timestamp.date()
			end = measurements.last().timestamp.date()
			dates = [start+timedelta(days=x) for x in range((end-start).days)]
			for d in dates:
				active_containers = patient.user.container_set.all() # TO DO filter by date
				pd, _ = PatientDay.objects.get_or_create(
					patient=patient,
					date=d,
				)
				for container in active_containers:
					pd.grams += container.grams_per_day(d)
					pd.thc += container.thc_per_day(d)
					pd.cbd += container.cbd_per_day(d)
					print(container.cost_per_day(d))
					
				pd.save()
				
