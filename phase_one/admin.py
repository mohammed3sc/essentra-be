from django.contrib import admin
from .models import *
# Register your models here.
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

class OpenOrdersAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(OpenOrders, OpenOrdersAdmin) 


class BomAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(BOM,BomAdmin) 


class StockDataAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(StockData,StockDataAdmin)

class CustomerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(CustomerMaster,CustomerAdmin)
admin.site.register(Event)
admin.site.register(EventType)

class SupplyTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(SupplyType,SupplyTypeAdmin)

class MasterSupplyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(MasterSupplyCode,MasterSupplyAdmin)


class MesanMasterAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(MesanMaster,MesanMasterAdmin)


class LeadAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
admin.site.register(LeadTimeMaster,LeadAdmin)


 