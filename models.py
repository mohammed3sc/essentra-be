# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Bom(models.Model):
    id = models.BigIntegerField(primary_key=True)
    bprod = models.CharField(max_length=500, blank=True, null=True)
    bseq = models.IntegerField(blank=True, null=True)
    bchld = models.CharField(max_length=500, blank=True, null=True)
    lidsc1 = models.CharField(max_length=100, blank=True, null=True)
    bqreq = models.IntegerField(blank=True, null=True)
    bclas = models.CharField(max_length=100, blank=True, null=True)
    bclac = models.CharField(max_length=100, blank=True, null=True)
    bbubb = models.IntegerField(blank=True, null=True)
    bopno = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bom'


class CustomPermission(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.TextField()
    permission_id = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'custom_permission'


class CustomerMaster(models.Model):
    id = models.BigIntegerField(primary_key=True)
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
        managed = False
        db_table = 'customer_master'


class Event(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type_name_id = models.BigIntegerField()
    end = models.DateField(blank=True, null=True)
    start = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'event'


class EventType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type_name = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'event_type'


class LeadTime(models.Model):
    id = models.BigIntegerField(primary_key=True)
    iprod = models.CharField(max_length=200, blank=True, null=True)
    idesc = models.CharField(max_length=200, blank=True, null=True)
    iclead = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lead_time'


class MasterData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    iid = models.CharField(max_length=500, blank=True, null=True)
    imsspc = models.CharField(max_length=500, blank=True, null=True)
    iprod = models.CharField(max_length=100, blank=True, null=True)
    idesc = models.CharField(max_length=100, blank=True, null=True)
    idsce = models.IntegerField(blank=True, null=True)
    ivulp = models.IntegerField(blank=True, null=True)
    imcqty = models.CharField(max_length=100, blank=True, null=True)
    iclas = models.CharField(max_length=50, blank=True, null=True)
    inseq = models.CharField(max_length=50, blank=True, null=True)
    ipfdv = models.CharField(max_length=50, blank=True, null=True)
    iityp = models.CharField(max_length=50, blank=True, null=True)
    iref01 = models.CharField(max_length=100, blank=True, null=True)
    iref02 = models.CharField(max_length=100, blank=True, null=True)
    iref03 = models.CharField(max_length=100, blank=True, null=True)
    iwght = models.IntegerField(blank=True, null=True)
    imcomc = models.IntegerField(blank=True, null=True)
    iysls = models.IntegerField(blank=True, null=True)
    iytdu = models.IntegerField(blank=True, null=True)
    iumr = models.CharField(max_length=50, blank=True, null=True)
    icond = models.CharField(max_length=50, blank=True, null=True)
    imunrd = models.IntegerField(blank=True, null=True)
    imunrl = models.IntegerField(blank=True, null=True)
    imunai = models.IntegerField(blank=True, null=True)
    isitm = models.CharField(max_length=100, blank=True, null=True)
    imendt = models.IntegerField(blank=True, null=True)
    urun = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_data'


class MasterSupplayCode(models.Model):
    id = models.BigIntegerField(primary_key=True)
    item = models.CharField(max_length=50, blank=True, null=True)
    type = models.ForeignKey('SupplayType', models.DO_NOTHING, blank=True, null=True)
    is_deleted = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'master_supplay_code'


class OpenOrders(models.Model):
    id = models.BigIntegerField(primary_key=True)
    warehouse = models.CharField(max_length=200, blank=True, null=True)
    order_entry_date = models.DateField(blank=True, null=True)
    requested_ship_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    customer_account = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=500, blank=True, null=True)
    customer_po = models.CharField(max_length=50, blank=True, null=True)
    order_no = models.IntegerField(blank=True, null=True)
    line_no = models.IntegerField(blank=True, null=True)
    mesan_item_ref = models.CharField(max_length=300, blank=True, null=True)
    credit_hold = models.CharField(max_length=500, blank=True, null=True)
    order_qty = models.IntegerField(blank=True, null=True)
    allocated_qty = models.FloatField(blank=True, null=True)
    shipped_qty = models.FloatField(blank=True, null=True)
    invoiced_qty = models.FloatField(blank=True, null=True)
    balance_qty = models.FloatField(blank=True, null=True)
    sales_price_per_1000 = models.FloatField(blank=True, null=True)
    total_order_line_value = models.FloatField(blank=True, null=True)
    balance_line_value = models.CharField(max_length=100, blank=True, null=True)
    means_of_transport = models.CharField(max_length=100, blank=True, null=True)
    freight_terms = models.CharField(max_length=100, blank=True, null=True)
    customer_alpha_reference = models.CharField(max_length=100, blank=True, null=True)
    customer_type = models.CharField(max_length=100, blank=True, null=True)
    work_centre_no = models.CharField(max_length=100, blank=True, null=True)
    work_centre_description = models.CharField(max_length=100, blank=True, null=True)
    sales_person_name = models.IntegerField(blank=True, null=True)
    sales_person_code = models.CharField(max_length=500, blank=True, null=True)
    eur_total = models.CharField(max_length=500, blank=True, null=True)
    usd_total = models.CharField(max_length=200, blank=True, null=True)
    currency = models.CharField(max_length=100, blank=True, null=True)
    try_value = models.CharField(max_length=100, blank=True, null=True)
    weekno = models.CharField(max_length=200, blank=True, null=True)
    customer_company_no = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_orders'


class PurchaseSas(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pid = models.CharField(max_length=200, blank=True, null=True)
    pprod = models.CharField(max_length=200, blank=True, null=True)
    lidsc1 = models.CharField(max_length=100, blank=True, null=True)
    idesc = models.CharField(max_length=100, blank=True, null=True)
    pedte = models.DateField(blank=True, null=True)
    pord = models.IntegerField(blank=True, null=True)
    pqord = models.FloatField(blank=True, null=True)
    pqrec = models.FloatField(blank=True, null=True)
    balance = models.FloatField(blank=True, null=True)
    pddte = models.DateField(blank=True, null=True)
    pvend = models.IntegerField(blank=True, null=True)
    vndnam = models.CharField(max_length=100, blank=True, null=True)
    pecst = models.FloatField(blank=True, null=True)
    pbecst = models.FloatField(blank=True, null=True)
    vcurr = models.CharField(max_length=100, blank=True, null=True)
    pum = models.CharField(max_length=100, blank=True, null=True)
    pline = models.CharField(max_length=100, blank=True, null=True)
    vndad1 = models.CharField(max_length=100, blank=True, null=True)
    vndad2 = models.CharField(max_length=100, blank=True, null=True)
    vstate = models.CharField(max_length=500, blank=True, null=True)
    vcoun = models.CharField(max_length=500, blank=True, null=True)
    vndad3 = models.CharField(max_length=100, blank=True, null=True)
    vcon = models.CharField(max_length=500, blank=True, null=True)
    imdsfw = models.CharField(max_length=500, blank=True, null=True)
    vterms = models.CharField(max_length=500, blank=True, null=True)
    talepekno = models.CharField(max_length=500, blank=True, null=True)
    pocur = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchase_sas'


class Roles(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'roles'


class RolesPermissions(models.Model):
    id = models.BigIntegerField(primary_key=True)
    role = models.ForeignKey(Roles, models.DO_NOTHING)
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'roles_permissions'
        unique_together = (('permission_id', 'role'),)


class Route(models.Model):
    id = models.BigIntegerField(primary_key=True)
    iprod = models.CharField(max_length=200)
    idesc = models.CharField(max_length=100, blank=True, null=True)
    lidsc1 = models.CharField(max_length=100, blank=True, null=True)
    iclas = models.CharField(max_length=100, blank=True, null=True)
    iityp = models.CharField(max_length=100, blank=True, null=True)
    ropno = models.IntegerField(blank=True, null=True)
    rstat = models.IntegerField(blank=True, null=True)
    rwrkc = models.IntegerField(blank=True, null=True)
    ropds = models.CharField(max_length=100, blank=True, null=True)
    rlab = models.FloatField(blank=True, null=True)
    rset = models.FloatField(blank=True, null=True)
    rmac = models.FloatField(blank=True, null=True)
    rtoflg = models.IntegerField(blank=True, null=True)
    rtoutc = models.IntegerField(blank=True, null=True)
    rtwhs = models.IntegerField(blank=True, null=True)
    rtfwip = models.CharField(max_length=100, blank=True, null=True)
    rttwhs = models.CharField(max_length=100, blank=True, null=True)
    rttwip = models.CharField(max_length=100, blank=True, null=True)
    lilang = models.CharField(max_length=100, blank=True, null=True)
    rid = models.CharField(max_length=200, blank=True, null=True)
    rtdept = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route'


class StockData(models.Model):
    id = models.BigIntegerField(primary_key=True)
    iums = models.CharField(max_length=20, blank=True, null=True)
    iclas = models.CharField(max_length=20, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    mesan_item = models.CharField(max_length=500, blank=True, null=True)
    sku_description = models.CharField(max_length=100, blank=True, null=True)
    warehouse = models.CharField(max_length=500, blank=True, null=True)
    imcqty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ivulp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lialoc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stock_data'


class SupplayType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type_name = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'supplay_type'


class TokenBlacklistBlacklistedtoken(models.Model):
    blacklisted_at = models.DateTimeField()
    token = models.OneToOneField('TokenBlacklistOutstandingtoken', models.DO_NOTHING)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'token_blacklist_blacklistedtoken'


class TokenBlacklistOutstandingtoken(models.Model):
    token = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()
    user_id = models.BigIntegerField(blank=True, null=True)
    jti = models.CharField(unique=True, max_length=255)
    id = models.BigIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'token_blacklist_outstandingtoken'


class WorkOrder(models.Model):
    id = models.BigIntegerField(primary_key=True)
    sord = models.CharField(max_length=100, blank=True, null=True)
    sprod = models.CharField(max_length=500, blank=True, null=True)
    idesc = models.CharField(max_length=100, blank=True, null=True)
    srdte = models.DateField(blank=True, null=True)
    sddte = models.DateField(blank=True, null=True)
    sqreq = models.IntegerField(blank=True, null=True)
    sqfin = models.IntegerField(blank=True, null=True)
    scord = models.IntegerField(blank=True, null=True)
    scust = models.IntegerField(blank=True, null=True)
    cnme = models.CharField(max_length=500, blank=True, null=True)
    scom = models.CharField(max_length=500, blank=True, null=True)
    soendt = models.DateField(blank=True, null=True)
    somndt = models.DateField(blank=True, null=True)
    swhs = models.CharField(max_length=100, blank=True, null=True)
    soenus = models.CharField(max_length=100, blank=True, null=True)
    sloc = models.CharField(max_length=100, blank=True, null=True)
    sutim1 = models.TimeField(blank=True, null=True)
    sclin = models.IntegerField(blank=True, null=True)
    socrdt = models.DateField(blank=True, null=True)
    sstat = models.IntegerField(blank=True, null=True)
    sudat1 = models.DateField(blank=True, null=True)
    sqremm = models.IntegerField(blank=True, null=True)
    sodraw = models.IntegerField(blank=True, null=True)
    sodwgs = models.IntegerField(blank=True, null=True)
    sutmz2 = models.CharField(max_length=100, blank=True, null=True)
    sutim2 = models.TimeField(blank=True, null=True)
    sudat2 = models.DateField(blank=True, null=True)
    sutmz1 = models.CharField(max_length=100, blank=True, null=True)
    balance = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'work_order'
