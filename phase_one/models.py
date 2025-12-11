from django.db import models
import datetime
from colorfield.fields import ColorField
# Create your models here.
class MesanMaster(models.Model):
    mesan_item_name=models.CharField(unique=True,max_length=300, verbose_name='LPROD')
    
    class Meta:
        managed = False
        db_table = 'mesan_master'
    
    

class OpenOrders(models.Model):
    warehouse = models.CharField(max_length=200, null=True, blank=True, verbose_name='LWHS')
    order_entry_date = models.DateField(null=True, blank=True, verbose_name='CHKLODTE')
    requested_ship_date = models.DateField(null=True, blank=True, verbose_name='CHKLRDTE')
    weekno=models.CharField(max_length=200,null=True,blank=True)
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name='HCOUN')
    customer_company_no = models.CharField(max_length=200,null=True, blank=True, verbose_name='CCOMP')
    customer_account = models.IntegerField(null=True, blank=True, verbose_name='HCUST')
    customer_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='HNAME')
    customer_po = models.CharField(max_length=50, null=True, blank=True, verbose_name='HCPO')
    order_no = models.IntegerField(null=True, blank=True, verbose_name='HORD')
    line_no = models.IntegerField(null=True, blank=True, verbose_name='LLINE')
    mesan_item = models.CharField(max_length=300, null=True, blank=True, verbose_name='LPROD')
    mesan_item_ref = models.ForeignKey(MesanMaster,on_delete=models.CASCADE, null=True, blank=True,related_name="ob_mesan_ref")
    credit_hold = models.CharField(max_length=500, null=True, blank=True, verbose_name='CHCRDH')
    order_qty = models.IntegerField(null=True, blank=True, verbose_name='LQORD')
    allocated_qty = models.FloatField(null=True, blank=True, verbose_name='LQALL')
    shipped_qty = models.FloatField(null=True, blank=True, verbose_name='LQSHP')
    invoiced_qty = models.FloatField(null=True, blank=True, verbose_name='LQTIN')
    balance_qty = models.FloatField(null=True, blank=True, verbose_name='BALANCE')
    currency = models.CharField(max_length=100,null=True, blank=True, verbose_name='HCURR')
    sales_price_per_1000 = models.FloatField(null=True, blank=True, verbose_name='LNET')
    total_order_line_value = models.FloatField(null=True, blank=True, verbose_name='TOTLINEVAL')
    balance_line_value = models.CharField(max_length=100, null=True, blank=True, verbose_name='BALLINEVAL')
    means_of_transport = models.CharField(max_length=100, null=True, blank=True, verbose_name='LMNTR')
    freight_terms = models.CharField(max_length=100, null=True, blank=True, verbose_name='LTRMC')
    customer_alpha_reference = models.CharField(max_length=100, null=True, blank=True, verbose_name='CMALPH')
    customer_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='CTYPE')
    work_centre_no = models.CharField(max_length=100, null=True, blank=True, verbose_name='RWRKC')
    work_centre_description = models.CharField(max_length=100, null=True, blank=True, verbose_name='WDESC')
    sales_person_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='SEA')
    sales_person_code = models.CharField(max_length=500, null=True, blank=True, verbose_name='HSAL')
    try_value = models.CharField(max_length=100,null=True, blank=True, verbose_name='column1')
    eur_total = models.CharField(max_length=500, null=True, blank=True, verbose_name='column2')
    usd_total = models.CharField(max_length=200, null=True, blank=True, verbose_name='column3')

            
    def save(self, *args, **kwargs):
        if datetime.datetime.strptime(str(self.requested_ship_date), '%Y-%m-%d').date() < datetime.date.today():
            self.weekno="BackLog"
        else:
            self.weekno=datetime.datetime.strptime(str(self.requested_ship_date), '%Y-%m-%d').date().isocalendar()[1]
        super(OpenOrders, self).save(*args, **kwargs)
    class Meta:
        managed = False
        db_table = 'open_orders'
        
         


class StockData(models.Model):
    mesan_item = models.CharField(max_length=500,null=True, blank=True,verbose_name='LPROD')
    mesan_item_ref = models.ForeignKey(MesanMaster,on_delete=models.CASCADE, null=True, blank=True,related_name="so_mesan_ref")
    warehouse = models.CharField(max_length=500, null=True, blank=True,verbose_name='LWHS')
    location = models.CharField(max_length=500, null=True, blank=True,verbose_name='LLOC')
    balance = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,verbose_name='BAL')
    IUMS = models.CharField(max_length=20, null=True, blank=True,verbose_name='IUMS')
    sku_description = models.CharField(max_length=100, null=True, blank=True,verbose_name='IDESC')
    LIALOC = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,verbose_name='LIALOC')
    IVULP = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,verbose_name='IVULP')
    IMCQTY = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True,verbose_name='IMCQTY')
    ICLAS = models.CharField(max_length=20, null=True, blank=True,verbose_name='ICLAS')
    
    class Meta:
        managed = False
        db_table = 'stock_data'


class BOM(models.Model):
    BPROD = models.CharField(max_length=500, null=True, blank=True)
    BSEQ = models.IntegerField(null=True, blank=True)
    BCHLD = models.CharField(max_length=500,null=True, blank=True)
    LIDSC1 = models.CharField(max_length=100, null=True, blank=True)
    BQREQ = models.IntegerField(null=True, blank=True)
    BCLAS = models.CharField(max_length=100, null=True, blank=True)
    BCLAC = models.CharField(max_length=100, null=True, blank=True)
    BBUBB = models.IntegerField(null=True, blank=True)
    BOPNO = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'bom'

class Route(models.Model):
    IPROD = models.CharField(max_length=200)
    IDESC = models.CharField(max_length=100, blank=True, null=True)
    LIDSC1 = models.CharField(max_length=100, blank=True, null=True)
    ICLAS = models.CharField(max_length=100, blank=True, null=True)
    IITYP = models.CharField(max_length=100, blank=True, null=True)
    ROPNO = models.IntegerField(blank=True, null=True)
    RSTAT = models.IntegerField(blank=True, null=True)
    RWRKC = models.IntegerField(blank=True, null=True)
    ROPDS = models.CharField(max_length=100, blank=True, null=True)
    RLAB = models.FloatField(blank=True, null=True)
    RSET = models.FloatField(blank=True, null=True)
    RMAC = models.FloatField(blank=True, null=True)
    RTOFLG = models.IntegerField(blank=True, null=True)
    RTOUTC = models.IntegerField(blank=True, null=True)
    RTWHS = models.IntegerField(blank=True, null=True)
    RTFWIP = models.CharField(max_length=100, blank=True, null=True)
    RTTWHS = models.CharField(max_length=100, blank=True, null=True)
    RTTWIP = models.CharField(max_length=100, blank=True, null=True)
    LILANG = models.CharField(max_length=100, blank=True, null=True)
    RID = models.CharField(max_length=200, blank=True, null=True)
    RTDEPT = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'route'


class PurchaseSas(models.Model):
    PID = models.CharField(max_length=200, null=True, blank=True)
    PPROD = models.CharField(max_length=200, null=True, blank=True)
    LIDSC1 = models.CharField(max_length=100, null=True, blank=True)
    IDESC = models.CharField(max_length=100, null=True, blank=True)
    PEDTE = models.DateField(null=True, blank=True)
    PORD = models.IntegerField(null=True, blank=True)
    PQORD = models.FloatField(null=True, blank=True)
    PQREC = models.FloatField(null=True, blank=True)
    BALANCE = models.FloatField(null=True, blank=True)
    PDDTE = models.DateField(null=True, blank=True)
    PVEND = models.IntegerField(null=True, blank=True)
    VNDNAM = models.CharField(max_length=100, null=True, blank=True)
    PECST = models.FloatField(null=True, blank=True)
    PBECST = models.FloatField(null=True, blank=True)
    VCURR = models.CharField(max_length=100, null=True, blank=True)
    PUM = models.CharField(max_length=100, null=True, blank=True)
    PLINE = models.CharField(max_length=100, null=True, blank=True)
    VNDAD1 = models.CharField(max_length=100, null=True, blank=True)
    VNDAD2 = models.CharField(max_length=100, null=True, blank=True)
    VSTATE = models.CharField(max_length=500, null=True, blank=True)
    VCOUN = models.CharField(max_length=500, null=True, blank=True)
    VNDAD3 = models.CharField(max_length=100, null=True, blank=True)
    VCON = models.CharField(max_length=500, null=True, blank=True)
    IMDSFW = models.CharField(max_length=500, null=True, blank=True)
    VTERMS = models.CharField(max_length=500, null=True, blank=True)
    TALEPEKNO = models.CharField(max_length=500, null=True, blank=True)
    POCUR = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'purchase_sas'

class MasterData(models.Model):
    IID = models.CharField(max_length=500, null=True, blank=True)
    IMSSPC = models.CharField(max_length=500, null=True, blank=True)
    IPROD = models.CharField(max_length=100, null=True, blank=True)
    IDESC = models.CharField(max_length=100, null=True, blank=True)
    IDSCE = models.IntegerField(null=True, blank=True)
    IVULP = models.IntegerField(null=True, blank=True)
    IMCQTY = models.CharField(max_length=100, null=True, blank=True)
    ICLAS = models.CharField(max_length=50, null=True, blank=True)
    INSEQ = models.CharField(max_length=50, null=True, blank=True)
    IPFDV = models.CharField(max_length=50, null=True, blank=True)
    IITYP = models.CharField(max_length=50, null=True, blank=True)
    IREF01 = models.CharField(max_length=100, null=True, blank=True)
    IREF02 = models.CharField(max_length=100, null=True, blank=True)
    IREF03 = models.CharField(max_length=100, null=True, blank=True)
    IWGHT = models.IntegerField(null=True, blank=True)
    IMCOMC = models.IntegerField(null=True, blank=True)
    IYSLS = models.IntegerField(null=True, blank=True)
    IYTDU = models.IntegerField(null=True, blank=True)
    IUMR = models.CharField(max_length=50, null=True, blank=True)
    ICOND = models.CharField(max_length=50, null=True, blank=True)
    IMUNRD = models.IntegerField(null=True, blank=True)
    IMUNRL = models.IntegerField(null=True, blank=True)
    IMUNAI = models.IntegerField(null=True, blank=True)
    ISITM = models.CharField(max_length=100, null=True, blank=True)
    IMENDT = models.IntegerField(null=True, blank=True)
    URUN = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'master_data'

class WorkOrder(models.Model):
    SORD = models.CharField(max_length=100, null=True, blank=True)
    SPROD = models.CharField(max_length=500, null=True, blank=True)
    IDESC = models.CharField(max_length=100, null=True, blank=True)
    SRDTE = models.DateField(null=True, blank=True)
    SDDTE = models.DateField(null=True, blank=True)
    SQREQ = models.IntegerField(null=True, blank=True)
    SQFIN = models.IntegerField(null=True, blank=True)
    SCORD = models.IntegerField(null=True, blank=True)
    SCUST = models.IntegerField(null=True, blank=True)
    CNME = models.CharField(max_length=500, null=True, blank=True)
    SCOM = models.CharField(max_length=500, null=True, blank=True)
    SOENDT = models.DateField(null=True, blank=True)
    SOMNDT = models.DateField(null=True, blank=True)
    SWHS = models.CharField(max_length=100, null=True, blank=True)
    SOENUS = models.CharField(max_length=100, null=True, blank=True)
    SLOC = models.CharField(max_length=100, null=True, blank=True)
    SUTIM1 = models.TimeField(null=True, blank=True)
    SCLIN = models.IntegerField(null=True, blank=True)
    SOCRDT = models.DateField(null=True, blank=True)
    SSTAT = models.IntegerField(null=True, blank=True)
    SUDAT1 = models.DateField(null=True, blank=True)
    SQREMM = models.IntegerField(null=True, blank=True)
    SODRAW = models.IntegerField(null=True, blank=True)
    SODWGS = models.IntegerField(null=True, blank=True)
    SUTMZ2 = models.CharField(max_length=100, null=True, blank=True)
    SUTIM2 = models.TimeField(null=True, blank=True)
    SUDAT2 = models.DateField(null=True, blank=True)
    SUTMZ1 = models.CharField(max_length=100, null=True, blank=True)
    BALANCE = models.IntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'work_order'
        
        
class CustomerMaster(models.Model):
    customer_id = models.CharField(max_length=200, blank=True, null=True)
    musteri_tipi = models.CharField(max_length=200, blank=True, null=True)
    top_style = models.CharField(max_length=200, blank=True, null=True)
    sales_manager = models.CharField(max_length=200, blank=True, null=True)
    field_sales = models.CharField(max_length=200, blank=True, null=True)
    crm_respon = models.CharField(max_length=200, blank=True, null=True)
    planner = models.CharField(max_length=200, blank=True, null=True)
    coutry_code = models.CharField(max_length=200, blank=True, null=True)  
    country = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        # managed = False
        db_table = 'customer_master'
        
    

class LeadTimeMaster(models.Model):
    IPROD = models.CharField(max_length=200, blank=True, null=True)
    IDESC = models.CharField(max_length=200, blank=True, null=True)
    ICLEAD = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'lead_time'



class EventType(models.Model):
    type_name = models.CharField(max_length=200, blank=True, null=True)
    color = ColorField(default='#FF0000')
    
    class Meta:
        managed = False
        db_table = 'event_type'
    
    

class Event(models.Model):
    type_name=models.ForeignKey(EventType,on_delete=models.CASCADE,related_name='event_type')
    title = models.CharField(max_length=200, blank=True, null=True)
    start = models.DateField(blank=True,null=True)
    end = models.DateField(blank=True,null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    description= models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'event'



class SupplyType(models.Model):
    type_name=models.CharField(max_length=50,blank=True,null=True)
    code=models.CharField( max_length=50,blank=True,null=True)
    class Meta:
        # managed = False
        db_table = 'supplay_type'
        
    def __str__(self):
        if self.code:
            return self.code

class MasterSupplyCode(models.Model):
    item=models.CharField(max_length=50,blank=True,null=True)
    type=models.ForeignKey(SupplyType, on_delete=models.CASCADE,blank=True,null=True)
    is_deleted=models.BooleanField(default=False)
    
    class Meta:
        # managed = False
        db_table = 'master_supplay_code'
