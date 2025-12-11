# myapp/management/commands/update_data.py

from django.core.management.base import BaseCommand
from phase_one.models import *
from datetime import datetime,date


class Command(BaseCommand):
    help = 'Updates week no daily'

    def handle(self, *args, **options):
        # Your logic to update data
        oo_object=OpenOrders.objects.all()
        for i in oo_object:
            if datetime.strptime(str(i.requested_ship_date), '%Y-%m-%d').date() < date.today():
                i.weekno="BackLog"
            else:
                i.weekno=datetime.strptime(str(i.requested_ship_date), '%Y-%m-%d').date().isocalendar()[1]
            i.save()
        self.stdout.write(self.style.SUCCESS('Week No Data updated successfully'))
