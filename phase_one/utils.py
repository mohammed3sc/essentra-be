from django.apps import apps
from datetime import datetime
import re
from django.db.models import Q
from decimal import Decimal,ROUND_HALF_UP
import struct
current_date = datetime.now().date()

openorder_eng = {
    "LWHS": "warehouse",
    "CHKLODTE": "order_entry_date",
    "CHKLRDTE": "requested_ship_date",
    "HCOUN": "country",
    # "CCOMP": "customer_company_no",
    "HCUST": "customer_account",
    "HNAME": "customer_name",
    "HCPO": "customer_po",
    "HORD": "order_no",
    "LLINE": "line_no",
    "LPROD": "item_number",
    "CHCRDH": "credit_hold",
    "LQORD": "order_qty",
    "LQALL": "allocated_qty",
    "LQSHP": "shipped_qty",
    "LQTIN": "invoiced_qty",
    "BALANCE": "balance_qty",
    "HCURR": "currency",
    "LNET": "sales_price_per_1000",
    "TOTLINEVAL": "total_order_line_value",
    "BALLINEVAL": "balance_line_value",
    "LMNTR": "means_of_transport",
    "LTRMC": "freight_terms",
    "CMALPH": "customer_alpha_reference",
    "CTYPE": "customer_type",
    "RWRKC": "work_centre_no",
    "WDESC": "work_centre_description",
    "SEA": "sales_person_name",
    "HSAL": "sales_person_code",
    "column1": "try_value",
    "column2": "eur_total",
    "column3": "usd_total"
}

stock_eng = {
    "LPROD": "item_number",
    "LWHS": "warehouse",
    "LLOC": "location",
    "BAL": "balance",
    "IUMS": "stocking_unit_of_measure",
    "IDESC": "item_description",
    "LIALOC": "allocated_to_orders",
    "IVULP": "units_per_pallet",
    "IMCQTY": "default_qty_per_container",
    "ICLAS": "item_class",
    "ISCST": "standard_cost_per_unit",
    "IACST": "actual_cost_per_unit"
}


stock_data_eng={
    'LPROD': 'mesan_item',
    'LWHS': 'warehouse',
    'LLOC': 'location',
    'BAL': 'balance',
    'IUMS': 'IUMS',
    'IDESC': 'sku_description',
    'LIALOC': 'LIALOC',
    'IVULP': 'IVULP',
    'IMCQTY': 'IMCQTY',
    'ICLAS': 'ICLAS'
}

bom_eng = {
    "BPROD": "item_number",
    "BSEQ": "sequence_number",
    "BCHLD": "item_number_child",
    "LIDSC1": "description_1",
    "BQREQ": "bom_quantity_required",
    "BCLAS": "item_class_(parent)",
    "BCLAC": "item_class_(child)",
    "BBUBB": "bubble_number",
    "BOPNO": "operation_number",
    "ICLAS": "item_class",
    "IITYP": "item_type_(0,1,2,3,4,5,...)",
    "IMENDT": "creation_date",
    "IMENUS": "creation_user"
}


bom_order_book_eng={
    "BPROD": "item_number",
    "BSEQ": "sequence_number",
    "BCHLD": "item_number_child",
    "LIDSC1": "description_1",
    "BQREQ": "bom_quantity_required",
    "BCLAS": "item_class_(parent)",
    "BCLAC": "item_class_(child)",
    "BBUBB": "bubble_number",
    "BOPNO": "operation_number",
    "ICLAS": "item_class",
    "IITYP": "item_type_(0,1,2,3,4,5,...)",
    "IMENDT": "creation_date",
    "IMENUS": "creation_user",
    "CHKLRDTE": "requested_ship_date",
    "TOTLINEVAL": "total_order_line_value",
    "LWHS": "warehouse",
    "BAL": "balance",


}


master_eng = {
    "IID": "record_id_im/iz",
    "IPFDV": "group_code",
    "IMSSPC": "stability_planning_specificati",
    "ICLAS": "item_class",
    "IPROD": "item_number",
    "IDESC": "item_description",
    "IDSCE": "extra_description",
    "IVULP": "units_per_pallet",
    "IMCQTY": "default_qty_per_container",
    "IMCMOQ": "customer_minimum_order_qty",
    "IMCSOQ": "customer_standard_order_qty",
    "IMCIOQ": "customer_incremental_order_qty",
    "IMUNRD": "un/na_id_for_road",
    "ICFAC": "facility_code",
    "ICMIN": "minimum_balance",
    "ICLOTS": "lot_size",
    "ICMXIN": "maximum_inventory",
    "ICCMOQ": "customer_minimum_order_qty",
    "ICCSOQ": "customer_standard_order_qty",
    "ICCIOQ": "customer_incremental_order_qty",
    "ICIOQ": "incremental_order_quantity",
    "IREF01": "group_sales_analysis_field",
    "IREF02": "group_sales_analysis_field",
    "IREF03": "group_sales_analysis_field",
    "IUMR": "selling_unit_of_measure",
    "IADJ": "month_to_date_adjustments",
    "IRCT": "month_to_date_receipts",
    "IISS": "month_to_date_issues",
    "IOPB": "opening_balance",
    "IYISS": "year_to_date_issues",
    "IYTDU": "year_to_date_sales_units",
    "IYSLS": "year_to_date_sales_amount",
    "IMSLS": "month_to_date_sales_amount",
    "IUMS": "stocking_unit_of_measure",
    "IUMP": "purch_unit_of_measure",
    "IUMCN": "u/m_purchase_to_stock_conv",
    "IITYP": "item_type_(0,1,2,3,4,...)",
    "ILEAD": "days_lead_time",
    "IVEND": "primary_vendor",
    "IVEN2": "alternate_vendor_number",
    "ICUSA": "allocated_to_customer_orders",
    "IPRDA": "allocated_to_prod_orders",
    "IMIN": "minimum_balance",
    "ILDTE": "last_transaction_date",
    "ILIST": "price_field",
    "ISCST": "standard_cost_per_unit",
    "IACST": "actual_cost_per_unit",
    "IFCST": "frozen_standard_cost",
    "ILEVL": "low_level_code_for_mrp_costs",
    "IONOD": "on_order_quantity",
    "IDISC": "item_discount_code",
    "INSEQ": "last_bill_of_materials_seq",
    "ITSEQ": "last_sequence_number",
    "ICYC": "cycle_counts_per_year",
    "IDRAW": "drawing_number",
    "IMTDU": "month_to_date_sales_units",
    "IMRP": "mrp_cde_m=mstr_sch_p=prod_pl",
    "IACT": "mrp_activity_code_y=active",
    "IORDP": "order_policy_code_(blank_a_f_g)",
    "IYRCT": "year_to_date_receipts",
    "IAVEU": "average_monthly_usage",
    "IABC": "abc_inventory_code",
    "ILABL": "last_planning_bom_seq",
    "IPACK": "packaging_size_code",
    "IABBT": "list_catalog_number",
    "IWGHT": "weight_per_unit_of_measure",
    "IORDC": "order_setup_cost",
    "ILOTS": "lot_size_reorder_point",
    "IYADJ": "year_to_date_adjustments",
    "IMCOS": "month_to_date_cost_of_sales",
    "IYCOS": "year_to_date_cost_of_sales",
    "IMUST": "y=must_issue_this_item_for_mul",
    "IBUYC": "planner_code",
    "ISACT": "simulation_mrp_act_flag",
    "IWHS": "default_warehouse",
    "ITGQY": "target_annual_quantity",
    "IMPSD": "mps_demand_code_-_i_d_s_g",
    "IPURC": "purchasing_buyer_code",
    "IMHZRD": "hazard_code",
    "ICPLNC": "planner_code",
    "ICLEAD": "lead_time",
    "ICPURC": "purchasing_buyer_code",
    "ICMPSD": "mps_demand_code_-_i_d_s_g",
    "ICPFDV": "group_code",
    "ICSLDY": "shelf_life_days",
    "ICABC": "abc_code"
}

purchase_eng = {
    "PID": "record_id_po/pz/rq/rz",
    "PPROD": "item_number",
    "LIDSC1": "description_1",
    "IDESC": "item_description",
    "PEDTE": "po_entry_date",
    "PORD": "purchase_order_number",
    "PQORD": "quantity_ordered",
    "PQREC": "quantity_received",
    "BALANCE": "pqord-pqrec",
    "PDDTE": "due_date",
    "PVEND": "po_vendor_number",
    "VNDNAM": "vendor_name",
    "PECST": "expected_cost_per_unit_transaction",
    "PBECST": "base_curr_expected_cost_per_unit",
    "VCURR": "currency_code",
    "PUM": "purchase_u/m",
    "PLINE": "line_number",
    "VNDAD1": "address_line_1",
    "VNDAD2": "address_line_2",
    "VSTATE": "vendor_state",
    "VCOUN": "country_code",
    "VNDAD3": "address_line_3",
    "VCON": "vendor_contact_name",
    "IMDSFW": "warehouse",
    "VTERMS": "terms_code",
    "TALEPEKNO": "poprf_uniq_offer_for_mrp_result_for_excel",
    "POCUR": "transaction_currency_code"
}



route_eng = {
    "IPROD": "item_number",
    "IDESC": "item_description",
    "LIDSC1": "description_1",
    "ICLAS": "item_class",
    "IITYP": "item_type_(0_1_2_3_4_5_...user)",
    "ROPNO": "operation_number",
    "RSTAT": "operation_status",
    "RWRKC": "work_center_number",
    "ROPDS": "operation_description",
    "RLAB": "labor_hours_run",
    "RSET": "labor_hours_setup",
    "RMAC": "machine_hours",
    "RTOFLG": "inside_outside_operation_flag",
    "RTOUTC": "outside_cost_basis_code",
    "RTWHS": "facility_code",
    "RTFWIP": "backflush_from_location",
    "RTTWHS": "backflush_to_warehouse",
    "RTTWIP": "backflush_to_location",
    "LILANG": "language",
    "RID": "record_id_rt/rz",
    "RTDEPT": "operation_department"
}



work_order_eng = {
    "SORD": "shop_order_number",
    "SPROD": "item_number",
    "IDESC": "item_description",
    "SRDTE": "release_date",
    "SDDTE": "due_date",
    "SQREQ": "quantity_required",
    "SQFIN": "quantity_finished",
    "SCORD": "customer_order_number",
    "SCUST": "customer_number",
    "CNME": "customer_name",
    "SCOM": "comment",
    "SOENDT": "date_created",
    "SOMNDT": "date_last_changed",
    "SWHS": "shop_ord_warehouse",
    "SOENUS": "created_by",
    "SLOC": "shop_order_location",
    "SUTIM1": "user_defined_time_1",
    "SCLIN": "customer_order_line_number",
    "SOCRDT": "original_customer_request_date",
    "SSTAT": "shop_order_status",
    "SUDAT1": "user_defined_date_1",
    "SQREMM": "quantity_remaining",
    "SODRAW": "drawing_number",
    "SODWGS": "drawing_page_number",
    "SUTMZ2": "user_defined_time_zone_2",
    "SUTIM2": "user_defined_time_2",
    "SUDAT2": "user_defined_date_2",
    "SUTMZ1": "user_defined_time_zone_1",
    "BALANCE": "sqreq_sqfin"
}


# openorder_eng = {
#     "LWHS": "warehouse",
    # "CHKLODTE": "substr_diglodte_7_2_substr_diglodte_5",
    # "CHKLRDTE": "substr_diglrdte_7_2_substr_diglrdte_5",
#     "CHKLODTE": "order_entry_date",
#     "CHKLRDTE": "requested_ship_date",
#     "HCOUN": "order_country_code",
#     "CCOMP": "company_number",
#     "HCUST": "customer_number",
#     "HNAME": "ship_to_name",
#     "CHCRDH": "credit_hold_reason_code",
#     "HORD": "order_number",
#     "LLINE": "order_line_number",
#     "LPROD": "item_number",
#     "LITEM": "item_number",
#     "LQORD": "quantity_ordered",
#     "LQALL": "quantity_allocated",
#     "LQSHP": "quantity_shipped",
#     "LQTIN": "quantity_invoiced",
#     "BALANCE": "balance",
#     "HCURR": "currency_code",
#     "LNET": "net_price_trans_stocking",
#     "TOTLINEVAL": "lqord_lnet",
#     "BALLINEVAL": "balance_lnet",
#     "LMNTR": "means_of_transportation",
#     "LTRMC": "freight_terms_code",
#     "CMALPH": "alpha_search_key",
#     "CTYPE": "cust_type",
#     "HCPO": "customer_po",
#     "RWRKC": "work_center_number",
#     "WDESC": "description",
#     "LSAL": "salesperson_number",
#     "CHSAL2": "secondary_order_salesperson",
#     "HSAL": "primary_order_salesperson",
#     "HSAL2": "split_salesperson",
#     "CDEA1": "group_code_1",
#     "CDEA2": "group_code_2",
#     "UNITCOST": "t05_total01"
# }


def get_week_number(date_str):
    """Convert a date string to the ISO week number."""
    date = datetime.strptime(date_str, '%d-%m-%Y')  # Adjust format as needed
    return date.isocalendar()[1]



def filter_dates_by_weeks(date_list, week_list):

    filtered_dates = []
    week_set = set(week_list)  # Convert list to set for faster lookups
    
    for date_str in date_list:
        date_str=transform_value(date_str)
        # print(date_str,"date")
        week_no = get_week_number(date_str)
        if str(week_no) in week_set:
            filtered_dates.append(date_str)
    
    return filtered_dates






def order_weeks(week_name):
    match = re.search(r'(\d+)', week_name)
    return int(match.group()) if match else 0





def build_where_clause(filters):
    if not filters:
        return ""
    conditions = []
    for key, value in filters.items():
        if isinstance(value, list):
            # Convert list to a comma-separated string for SQL IN clause
            formatted_values = "', '".join(map(str, value))
            conditions.append(f"{key} IN ('{formatted_values}')")
        else:
            conditions.append(f"{key} = '{value}'")
    return "WHERE " + " AND ".join(conditions)


def transform_value(value):
    if isinstance(value, bytes):
        try: 
            return value.decode('cp037').replace('.','-')  # Adjust encoding as needed
        except UnicodeDecodeError:
            return value.decode('latin-1').replace('.','-')  # Fallback if initial decode fails
    elif isinstance(value, str):
        return value.rstrip()
    elif isinstance(value, Decimal):
        value = value.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        # integer_part, decimal_part = str(value).split('.')
        # formatted_integer = "{:,}".format(int(integer_part)).replace(",", ".")
        # return f"{formatted_integer},{decimal_part}"
        return str(value)
        
    return value



open_order_columns=["HEDTE","HCUST",
                    "CHARCU","CHINCU",
                    "CHSHCU","HORD",
                    "CLOCLS","CLUTYP",
                    "HCPO","LICFAC",
                    "CLTFAC","LWHS",
                    "LTOWH","LLINE",
                    "LPROD","LUM",
                    "LQORD","LQALL",
                    "LQPCK","LQSHP",
                    "LQTIN","LRDTE",
                    "HCURR","LNET",
                    "LBNET","CLSORD",
                    "CLSTS1","CLSTS2",
                    "CLSTS3","CLSTS4",
                    "CLSTS5","CLENUS",
                    "LSHIP","LMNTR",
                    "HNAME","HAD1",
                    "HAD2","HAD3",
                    "HPOST"]

open_order_filter = ['warehouse',
                     'order_entry_date',
                     'requested_ship_date',
                     'customer_account',
                     'mesan_item',
                     'allocated_qty',
                     'shipped_qty',
                     'balance_qty',
                     'customer_name',
                     'order_qty','order_no','weekno']
stock_data=['location','warehouse','balance']


# Generated columns
temp_column=['remaining_qty','open_orders_qty','grand_total']

def get_verbose_names(model_name,data):
    try:
        x={field.name: field.verbose_name for field in model_name._meta.get_fields()}
        if x:
            verbose_fields={}
            for field_name, verbose_name in x.items():
                verbose_fields[field_name]=verbose_name
            for dictionary in data:
                keys_to_replace = list(dictionary.keys())  
                for key in keys_to_replace:
                    if key in verbose_fields:
                        new_key =key+","+verbose_fields[key]
                        dictionary[new_key] = dictionary.pop(key)
                    else:
                        dictionary[key] = dictionary.pop(key)
            return data
        else:
            return None
    except LookupError:
        return None
    



def csv_to_obj(self, headers=None,reader=None, class_name=None):
        if not headers:
            headers = reader.columns.tolist()       
        date_patterns = [
            r'\b\d{2}\.\d{2}\.\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{2}/\d{2}/\d{4}\b',
            r'\b\d{2}-\d{2}-\d{4}\b'  # Add the new date pattern for "05-11-2023"
        ]

        for _, row in reader.iterrows():
            result = {}
            for column, val in zip(headers, row):
                dates = []
                if isinstance(val, str):
                    for pattern in date_patterns:
                        dates += re.findall(pattern, val)

                    if dates:
                        try:
                            parsed_date = None
                            for date_str in dates:
                                try:
                                    parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                                    break
                                except ValueError:
                                    pass
                                try:
                                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                                    break
                                except ValueError:
                                    pass
                                try:
                                    parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                                    break
                                except ValueError:
                                    pass
                                try:
                                    parsed_date = datetime.strptime(date_str, '%d-%m-%Y')  # Adjusted format
                                    break
                                except ValueError:
                                    pass

                            if parsed_date:
                                result[column] = parsed_date.strftime('%Y-%m-%d')
                        except Exception as e:
                            print(f"Error parsing date: {e}")

                    elif val=='-' or '-' in val or '.' in val:
                        result[column] = None
                        
                    
                    else:
                        result[column] = val
            try:
                class_name.objects.create(**result)
            except Exception as e:
                print(f"Validation Error: {e}")
# 


def currentWeek():
    return datetime.strptime(str(current_date), '%Y-%m-%d').date().isocalendar()[1]



# Convert date strings to datetime objects
def filter_query(payload):
    filter_params = {}
    for key, value in payload.items():
        # if "_date" in key:  # Check if the key represents a date field
        #     filter_params[key] = datetime.strptime(value[0], "%Y-%m-%d").date()
        # if key=="weekno":
        #     x=["BackLog" if isinstance(i, str) and i == "BackLog" else (str(int(i) + currentWeek())) for i in value]
                
                
        #     filter_params[str(key)+"__in"]=x
            
        # else:
        filter_params[str(key)+"__in"] = value
        
    # print(filter_params,"*****************************")
    # Construct dynamic queryset filtering
    query_filters = Q(**filter_params)
    # print(query_filters,"############")
    return query_filters

# convert non list values to list 
def convert_list(data,related_name=None):
    new_data={}
    if related_name:
        for key, value in data.items():
            if not isinstance(value, list):
                new_data[related_name+key] = [value]
            else:
                new_data[related_name+key]=value  
    else:
        print("inside_else convert_list&&&&&&&",data,new_data)
        
        for key, value in data.items():
            if not isinstance(value, list):
                new_data[key] = [value]
            else:
                new_data=data
    
    return new_data



def convert_date_format(input_dict):
    dte=["IMENDT", 
    "CHKLRDTE",
    "ILDTE",
    "PEDTE",
    "PDDTE",
    "SRDTE",
    "SDDTE",
    "SOCRDT",
    "CHKLODTE",
    "CHKLRDTE"]

    output_dict = input_dict.copy()
    for key, value in output_dict.items():
        if key in dte and isinstance(value, list):
            output_dict[key] = [
                date.replace('-', '.') for date in value if isinstance(date, str)
            ]
    return output_dict








def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False



def sort_week_number(week_str):
    if week_str.isdigit():
        return int(week_str)
    else:
        return -1  # For "BackLog", treat it as -1 to sort it first


def get_value_by_key_with_value(key_to_check, value_to_find, other_key, list_of_dicts):
    for dictionary in list_of_dicts:
        if key_to_check in dictionary and dictionary[key_to_check] == value_to_find:
            return dictionary.get(other_key)  # Return the value of the other key
    return None  


def dict_index(core_obj,index,new_key,new_value):
    dict_items = list(core_obj.items())
    dict_items.insert(index, (new_key, new_value))
    core_obj =dict(dict_items)
    return core_obj
