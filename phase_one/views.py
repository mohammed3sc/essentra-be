from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated, AllowAny  # NOQA
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from .paginations import CustomPagination
from rest_framework import generics
# views.py
from rest_framework.views import APIView
import io, csv, pandas as pd
from datetime import datetime
import re
import csv
from django.http import HttpResponse
import encodings
from io import BytesIO
from .utils import *
from.csvreader import *
from rest_framework import viewsets
from rest_framework.response import Response
from .models import OpenOrders
from .serializers import OpenOrdersSerializer
from .paginations import CustomPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from collections import defaultdict
from django.core.management import call_command
from rest_framework.decorators import action
from django.db.models import Sum, Case, When, Value, F, FloatField
import xlsxwriter
from .permissions import *
from django.views import View
from phase_one.custom_orm.custom_query import CustomQuery,PandsCustomQuery
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import time, random, json
from django.http import JsonResponse

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
import sys
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
import datetime

@method_decorator(csrf_exempt, name="dispatch")
class OpenOrdersList(View):
    table_name="E3SCORDERS"
    stock_table_name="E3SCSTOCK"
    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            open_order_data = json_data.get('open_orders', {})
            week_no=open_order_data.pop("week_no",[])
            req_dates=CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=["CHKLRDTE"]).get('CHKLRDTE',[])
            # print(req_dates[0],"------------------------+++")
            week_no=filter_dates_by_weeks(req_dates,week_no)
            # print(week_no,"----------------")
            stock_order_data = json_data.get('stock_data', {})
            export_table=json_data.get('export_table',{})
            open_order_keys = CustomQuery.get_column_names(table_name=self.table_name)
            # if "CCOMP" in open_order_keys:
            #     open_order_keys.remove('CCOMP') 
            # print(open_order_keys,"------------------------------*************88")
            inverted_column = {v: k for k, v in openorder_eng.items()}
            open_order_converted = {inverted_column.get(k, k): v for k, v in open_order_data.items()}
            if week_no:
                open_order_converted['CHKLRDTE']=week_no
                print(open_order_converted,"+++++++")
            #stock orders 
            stock_order_keys = CustomQuery.get_column_names(table_name=self.stock_table_name)
            inverted_stock_data = {v: k for k, v in stock_data_eng.items()}
            stock_data_converted = {inverted_stock_data.get(k, k): v for k, v in stock_order_data.items()}


            # Extract filter criteria
            filters = {
                key: value for key, value in open_order_converted.items() if key in open_order_keys and value
            }
            filters=convert_date_format(filters)
            # print(filters,"-----------0000000--------------")
            temp_data_mapping={}
            if json_data['stock_data']:
            #stock data filter 
                stock_data_filters = {
                    key: value for key, value in stock_data_converted.items() if key in stock_order_keys and value
                }
                stock_where_clause = build_where_clause(stock_data_filters)

                stock_filer_result = CustomQuery.get_all_data_without_pagination(table_name=self.stock_table_name,where_clause=stock_where_clause,column_name="LPROD")
                # print(stock_filer_result,"----------------")
                temp_table_data=CustomQuery.sum_balance_for_data(table_name=self.stock_table_name,
                                columns=["LWHS","LPROD"],sum_column="BAL",as_column_name="grand_total",
                                group_by_columns=["LWHS","LPROD"],ids_list=stock_filer_result,id_column="LPROD")
                temp_data_mapping = {f"{lw}--{lp.strip()}": float(total) for lw, lp, total in temp_table_data}
           
            if export_table and export_table=="open_orders":
                page_size=None
                offset=None
            else:# Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size,
                exclude_columns=['CCOMP']
            )

            
            # result_list = [
            #     {openorder_eng.get(key,key): transform_value(value) for key, value in zip(open_order_keys, item)}
            #     for item in data
            # ]
            dynamic_fields={
                "remaining_qty": "0.0",
                "open_orders_qty": "Filter StockData",
                "grand_total": "Filter StockData"
            }
            try:
                open_order_keys.remove('CCOMP')
            except Exception as e:
                pass
            result_list = [
                dict(
                    list({
                        openorder_eng.get(key, key): 
                        (float(transform_value(value)) * 1000 if key == 'LQORD' else 
                        float(transform_value(value)) / 1000 if key == 'LNET' and transform_value(value) != 0 
                        # if key == 'CHKLRDTE' and datetime.datetime.strptime(str(transform_value(value)), '%Y-%m-%d').date() < datetime.date.today()
                        
                        else transform_value(value))
                        for key, value in zip(open_order_keys, item)
                    }.items())[:3]+
                    # list({
                    #     "week_no": 
                    #     ("Backlog" if datetime.datetime.strptime(str(transform_value(item[open_order_keys.index('CHKLRDTE')])), '%d-%m-%Y').date() < datetime.date.today() else 
                    #     datetime.datetime.strptime(str(transform_value(item[open_order_keys.index('CHKLRDTE')])), '%d-%m-%Y').date().isocalendar().week)
                    # }.items()) +
                    list({
                        "week_no": 
                        ("Backlog" if datetime.datetime.strptime(str(transform_value(item[open_order_keys.index('CHKLRDTE')])), '%d-%m-%Y').date() < datetime.date.today() else 
                        ((datetime.datetime.strptime(str(transform_value(item[open_order_keys.index('CHKLRDTE')])), '%d-%m-%Y').date() - datetime.date(datetime.datetime.strptime(str(transform_value(item[open_order_keys.index('CHKLRDTE')])), '%d-%m-%Y').year, 1, 1)).days // 7) + 1)
                    }.items())+
                    list({
                        openorder_eng.get(key, key): 
                        (float(transform_value(value)) * 1000 if key == 'LQORD' else 
                        float(transform_value(value)) / 1000 if key == 'LNET' and transform_value(value) != 0 
                        # if key == 'LNET' and datetime.datetime.strptime(str(transform_value(value)), '%Y-%m-%d').date() < datetime.date.today()
                        
                        else transform_value(value))
                        for key, value in zip(open_order_keys, item)
                    }.items())[3:19] +
                    list({
                        "remaining_qty": round((float(item[15]) - float(item[13])),2) if json_data['stock_data'] else 0,
                        "open_orders_qty": (float(item[15]) * 1000) if json_data['stock_data'] else 0,
                        "grand_total": temp_data_mapping.get((str(item[0])+"--"+str(item[10]).strip()), 0.0) if temp_data_mapping else 0
                    }.items()) +
                    list({
                        openorder_eng.get(key, key): 
                        (float(transform_value(value)) * 1000 if key == 'LQORD' else 
                        float(transform_value(value)) / 1000 if key == 'LNET' and transform_value(value) != 0 
                        else transform_value(value))
                        for key, value in zip(open_order_keys, item)
                    }.items())[19:]
                )
                for item in data
            ]



        

            # print(result_list,"------------------------")

            if export_table and export_table=="open_orders":
                return generate_excel(result_list,table_name=export_table)
            else:
                
                # Get total count for pagination metadata
                total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
                total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
                # Build pagination URLs
                next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
                previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            
                filter_columns = {openorder_eng.get(k, k): v for k, v in CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=open_order_keys).items()}
                filter_columns.update({"week_no": ["Back Log"] + [str(i) for i in range(1, 53)]})
                # filter_columns.pop('CCOMP')
                # print(filter_columns.keys())
                # Build response data
                ret_data = {
                    "count": total_count,
                    "page": page_number,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "next": next_url,
                    "previous": previous_url,
                    "results": result_list,
                    "filter_columns":filter_columns,
                    "temp_column": ["remaining_qty","open_orders_qty","grand_total"]
                }

            # print(ret_data,"###########################")
        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        response=JsonResponse(ret_data)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Disable caching
        response['Pragma'] = 'no-cache'  # Older HTTP 1.0 cache control
        response['Expires'] = '0'  # Expire immediately
        
        return response
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"



@method_decorator(csrf_exempt, name="dispatch")
class StockDataList(View):
    table_name="E3SCSTOCK"

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            stock_data = json_data.get('stock_data', {})
            export_table=json_data.get('export_table',{})

            table_columns = CustomQuery.get_column_names(table_name=self.table_name)
            inverted_columns= {v: k for k, v in stock_eng.items()}
            columns_converted = {inverted_columns.get(k, k): v for k, v in stock_data.items()}

            # Extract filter criteria
            filters = {
                key: value for key, value in columns_converted.items() if key in table_columns and value
            }
            filters=convert_date_format(filters)

            if export_table and export_table=="open_orders":
                page_size=None
                offset=None
            else:
                # Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size
            )

            result_list = [
                dict(list({stock_eng.get(key, key): float(transform_value(value)) * 1000 if key == 'BAL' else 
                transform_value(value) for key, value in zip(table_columns, item)}.items()))
                for item in data
            ]
            if export_table and export_table=="stock_data":
                return generate_excel(result_list,table_name=export_table)
            else:
                # Get total count for pagination metadata
                total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
                total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

                # Build pagination URLs
                next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
                previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            
                filter_columns = {stock_eng.get(k, k): v for k, v in CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=table_columns).items()}
                # Build response data
                ret_data = {
                    "count": total_count,
                    "page": page_number,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "next": next_url,
                    "previous": previous_url,
                    "results": result_list,
                    "filter_columns":filter_columns,
                    "temp_column": []
                }

        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"


@method_decorator(csrf_exempt, name="dispatch")
class BomList(View):
    table_name="E3SCBOM"

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            bom_data = json_data.get('bom', {})
            export_table=json_data.get('export_table',{})

            table_columns = CustomQuery.get_column_names(table_name=self.table_name)
            inverted_columns= {v: k for k, v in bom_eng.items()}
           
            columns_converted = {inverted_columns.get(k, k): v for k, v in bom_data.items()}
            # Extract filter criteria
            filters = {
                key: value for key, value in columns_converted.items() if key in table_columns and value
            }
            filters=convert_date_format(filters)

            if export_table and export_table=="bom":
                page_size=None
                offset=None
            else:
                # Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            # data = CustomQuery.all_table_data(
                # table_name=self.table_name,
                # where_clause=where_clause,
                # offset=offset,
                # limit=page_size
            # )
            
            data = PandsCustomQuery.bom_list(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size
            )

            result_list = [
                dict(list({bom_eng.get(key, key):transform_value(value) for key, value in zip(table_columns, item)}.items()))
                for item in data
            ]
            
            
            if export_table and export_table=="bom":
                return generate_excel(result_list,table_name=export_table)
            else:
                # Get total count for pagination metadata
                total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
                total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

                # Build pagination URLs
                next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
                previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            
                filter_columns = {bom_eng.get(k, k): v for k, v in CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=table_columns).items()}
                # Build response data
                ret_data = {
                    "count": total_count,
                    "page": page_number,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "next": next_url,
                    "previous": previous_url,
                    "results": result_list,
                    "filter_columns":filter_columns,
                    "temp_column": []
                }

        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"




@method_decorator(csrf_exempt, name="dispatch")
class BomOrderBookList(View):
    bom_table="E3SCBOM"
    open_order_table="E3SCORDERS"
    stock_table="E3SCSTOCK"
    columns = ["LPROD", "CHKLRDTE", "TOTLINEVAL","BALANCE"]

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)

            bom_stock_pivot = PandsCustomQuery.bom_stock_pivot(table_name=self.stock_table,bom_table_name=self.bom_table)
            bom_stock_pivot = bom_stock_pivot.rename(columns=bom_eng)
            
            # # Fetch data for open orders with filtering
            open_order_data = json_data.get('open_orders', {})
            bomorder_book = json_data.get('bomorder_book', {})
            export_table=json_data.get('export_table',{})

            open_order_keys = CustomQuery.get_column_names(table_name=self.open_order_table)
            inverted_open_order = {v: k for k, v in openorder_eng.items()}
            open_order_converted = {inverted_open_order.get(k, k): v for k, v in open_order_data.items()}

            filters = {key: value for key, value in open_order_converted.items() if key in open_order_keys and value}
            filters=convert_date_format(filters)
            
            where_clause = build_where_clause(filters)
            open_order_data = CustomQuery.all_table_data(
                table_name=self.open_order_table,
                where_clause=where_clause,
                columns=self.columns
            )

            # Process open order data
            result_dict = {}
            weeks = set()

            for item in open_order_data:
                mesan_item = item[self.columns.index('LPROD')]
                chk_lr_dte = datetime.datetime.strptime(str(transform_value(item[self.columns.index('CHKLRDTE')])), '%d-%m-%Y').date()
                week_no = ("Backlog" if chk_lr_dte < datetime.date.today() else f"Week{chk_lr_dte.isocalendar().week}")
                week_no = str(week_no)
                total_order_line_value = float(item[self.columns.index('BALANCE')])

                if mesan_item not in result_dict:
                    result_dict[mesan_item] = {week_no: 0.0}

                if week_no not in result_dict[mesan_item]:
                    result_dict[mesan_item][week_no] = 0.0

                result_dict[mesan_item][week_no] += total_order_line_value
                weeks.add(week_no)

            result_list = []
            for mesan_item, week_data in result_dict.items():
                grand_total = sum(week_data.values())
                result_list.append({
                    "item_number": mesan_item,
                    **week_data,
                    "grand_total": grand_total
                })

            # Convert result_list to DataFrame
            result_df = pd.DataFrame(result_list)
            # print(result_df.columns.tolist(),"%%%%%%%%%%%%%%%%%%%")
            result_df=result_df.rename(columns={'item_number': 'item_number_child'})
            # # Ensure 'item_number' is in string format for consistency

            combined_df = bom_stock_pivot.merge(result_df, on='item_number_child', how='left', suffixes=('', '_bom'))
            # combined_df = combined_df.merge(stock_pivot_df, on='item_number', how='left')
            combined_df = combined_df.map(lambda x: x.strip() if isinstance(x, str) else x)
            combined_df['openorder_grandtotal'] = combined_df['bom_quantity_required'] * combined_df['grand_total']*1000
            
            column_headers = combined_df.columns.tolist()
            db_list=CustomQuery.get_column_names(table_name=self.bom_table)
            static_list=[bom_eng[key] for key in db_list if key in bom_eng]

            static_list.insert(1,'grand_total')
            excluded_columns = static_list + ['openorder_grandtotal','STOCKGRANDTOTAL','Backlog']

            # Categorize columns in a single loop
            week_columns, remaining_columns = [], []
            # print(column_headers,"-----------------column_headers")
            for col in column_headers:
                if col.startswith("Week"):
                    week_columns.append(col)
                elif col not in excluded_columns:
                    remaining_columns.append(col)
            
            

            # Sort the list based on the numeric part
            week_columns = sorted(weeks, key=order_weeks)
            combined_df[week_columns] = combined_df[week_columns].mul(combined_df['bom_quantity_required'], axis=0)*1000
            # Create the final column order
            print(remaining_columns,"________________-")
            final_column_order =  static_list+week_columns + ['openorder_grandtotal']+remaining_columns+['STOCKGRANDTOTAL']
            final_column_order=list(dict.fromkeys(final_column_order))
            combined_df=combined_df[final_column_order]
            combined_df.fillna(0, inplace=True)
            filter_columns={col: list(set(combined_df[col])) for col in combined_df.columns}

            # Apply filtering for each column specified in the payload
            for column, values in bomorder_book.items():
                if column in combined_df.columns:
                    combined_df = combined_df[combined_df[column].isin(values)]

                
            

            # # Convert combined dataframe to JSON
            combined_json = combined_df.to_dict(orient='records')
            if export_table and export_table=="bomorder_book":
                return generate_excel(combined_json,table_name=export_table,columns=final_column_order)
            
            # Pagination logic
            page_number = int(request.GET.get('p', 1))
            page_size = int(request.GET.get('row_size', 10))
            offset = (page_number - 1) * page_size
            total_count=len(combined_json)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            # print(combined_json[(page_number-1) * page_size: page_number * page_size])

            ret_data = {
                "columns": final_column_order,
                "count": total_count,
                "page": 1,
                "page_size": 10,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results":combined_json[(page_number-1) * page_size: page_number * page_size],
                "filter_columns":filter_columns,
                "temp_column": []
            }
        except Exception as e:
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"

@method_decorator(csrf_exempt, name="dispatch")
class BomOrderBookPivot(View):
    bom_table="E3SCBOM"
    open_order_table="E3SCORDERS"
    stock_table="E3SCSTOCK"
    columns = ["LPROD", "CHKLRDTE", "TOTLINEVAL"]

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)

            bom_stock_pivot = PandsCustomQuery.bom_stock_pivot(table_name=self.stock_table,bom_table_name=self.bom_table)
            bom_stock_pivot = bom_stock_pivot.rename(columns=bom_eng)
            
            # # Fetch data for open orders with filtering
            open_order_data = json_data.get('open_orders', {})
            export_table=json_data.get('export_table',{})

            open_order_keys = CustomQuery.get_column_names(table_name=self.open_order_table)
            inverted_open_order = {v: k for k, v in openorder_eng.items()}
            open_order_converted = {inverted_open_order.get(k, k): v for k, v in open_order_data.items()}

            filters = {key: value for key, value in open_order_converted.items() if key in open_order_keys and value}
            filters=convert_date_format(filters)
           
            where_clause = build_where_clause(filters)
            open_order_data = CustomQuery.all_table_data(
                table_name=self.open_order_table,
                where_clause=where_clause,
                columns=self.columns
            )

            # Process open order data
            result_dict = {}
            weeks = set()

            for item in open_order_data:
                mesan_item = item[self.columns.index('LPROD')]
                chk_lr_dte = datetime.datetime.strptime(str(transform_value(item[self.columns.index('CHKLRDTE')])), '%d-%m-%Y').date()
                week_no = ("Backlog" if chk_lr_dte < datetime.date.today() else f"Week{chk_lr_dte.isocalendar().week}")
                week_no = str(week_no)
                total_order_line_value = float(item[self.columns.index('TOTLINEVAL')])

                if mesan_item not in result_dict:
                    result_dict[mesan_item] = {week_no: 0.0}

                if week_no not in result_dict[mesan_item]:
                    result_dict[mesan_item][week_no] = 0.0

                result_dict[mesan_item][week_no] += total_order_line_value
                weeks.add(week_no)

            result_list = []
            for mesan_item, week_data in result_dict.items():
                grand_total = sum(week_data.values())
                result_list.append({
                    "item_number": mesan_item,
                    **week_data,
                    "grand_total": grand_total
                })

            # Convert result_list to DataFrame
            result_df = pd.DataFrame(result_list)

            # # Ensure 'item_number' is in string format for consistency
            # result_df.index = result_df.index.astype(str)

            combined_df = bom_stock_pivot.merge(result_df, on='item_number', how='left', suffixes=('', '_bom'))
            # combined_df = combined_df.merge(stock_pivot_df, on='item_number', how='left')
            combined_df = combined_df.map(lambda x: x.strip() if isinstance(x, str) else x)
            combined_df['openorder_grandtotal'] = combined_df['bom_quantity_required'] * combined_df['grand_total']*1000
            
            column_headers = combined_df.columns.tolist()
            db_list=CustomQuery.get_column_names(table_name=self.bom_table)
            static_list=[bom_eng[key] for key in db_list if key in bom_eng]

            static_list.insert(1,'grand_total')
            excluded_columns = static_list + ['openorder_grandtotal','STOCKGRANDTOTAL','Backlog']

            # Categorize columns in a single loop
            week_columns, remaining_columns = [], []

            for col in column_headers:
                if col.startswith("Week"):
                    week_columns.append(col)
                elif col not in excluded_columns:
                    remaining_columns.append(col)
            week_columns = sorted(weeks, key=order_weeks)
            
            
            # Create the final column order
            combined_df[week_columns] = combined_df[week_columns].mul(combined_df['bom_quantity_required'], axis=0)*1000

            final_column_order =  static_list+week_columns + ['openorder_grandtotal']+remaining_columns+['STOCKGRANDTOTAL']
            combined_df=combined_df[final_column_order]
            combined_df.fillna(0, inplace=True)

            #--------------------------pivote start-------------------- 
            pivote_columns=week_columns+['openorder_grandtotal']+ remaining_columns+['STOCKGRANDTOTAL']      
            
            combined_df = combined_df.reset_index(drop=True)
            combined_df['item_number_child'] = combined_df['item_number_child'].astype(str).fillna('Unknown')  # Ensure it's a string column

            # Check the dtype to confirm it's correct
            # print(combined_df['item_number_child'].dtype)

            # Ensure item_number_child is not in pivote_columns if it's already in index
            pivote_columns = [col for col in week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL'] if col != 'item_number_child']

            pivot_table = pd.pivot_table(
                combined_df, 
                values=pivote_columns, 
                index='item_number_child', 
                aggfunc='sum'
            )

            pivot_table = pivot_table[pivote_columns]
            pivot_table = pivot_table.loc[:, ~pivot_table.columns.duplicated()]


            # Convert only the columns to floats, excluding 'col0'
            pivot_table_float = pivot_table.copy()
            pivot_table_float.loc[:, pivot_table.columns[1:]] = pivot_table_float.loc[:, pivot_table.columns[1:]].astype(float)

            # Calculate sums for the converted columns
            sums = pivot_table_float.sum()

            # Append the sums as a new row
            # pivot_table.loc['grandtotal'] = pd.Series([None] * len(pivot_table.columns), index=pivot_table.columns)
            pivot_table.loc['grandtotal', pivot_table.columns[0:]] = sums
            pivot_table = pivot_table.reset_index()
            #--------------------------pivote end-------------------- 

            # print(pivot_table,"0-------------------------------")
     
            # # Convert combined dataframe to JSON
            combined_json=combined_json.round(3)
            combined_json = pivot_table.to_dict(orient='records')
            if export_table and export_table=="bomorder_book_pivote":
                return generate_excel(combined_json,table_name=export_table,columns=["item_number_child"]+pivote_columns)
            
            
            # Pagination logic
            page_number = int(request.GET.get('p', 1))
            page_size = int(request.GET.get('row_size', 10))
            offset = (page_number - 1) * page_size
            total_count=len(pivot_table)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            # print(combined_json[(page_number-1) * page_size: page_number * page_size])

            ret_data = {
                "columns": ["item_number_child"]+pivote_columns,
                "count": total_count,
                "page": 1,
                "page_size": 10,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "result":combined_json[(page_number-1) * page_size: page_number * page_size],
                # "result":combined_json,
                "filter_columns":{"item_number":["10"]},
                "temp_column": []
            }
        except Exception as e:
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"




@method_decorator(csrf_exempt, name="dispatch")
class BomorderbookTabloList(View):
    bom_table="E3SCBOM"
    open_order_table="E3SCORDERS"
    stock_table="E3SCSTOCK"
    columns = ["LPROD", "CHKLRDTE", "TOTLINEVAL","BALANCE"]

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)

            bom_stock_pivot = PandsCustomQuery.bom_stock_pivot(table_name=self.stock_table,bom_table_name=self.bom_table)
            bom_stock_pivot = bom_stock_pivot.rename(columns=bom_eng)
            
            # # Fetch data for open orders with filtering
            open_order_data = json_data.get('open_orders', {})
            bomorderbook_pivottablo_list=json_data.get('bomorderbook_pivottablo_list', {})
            export_table=json_data.get('export_table',{})

            open_order_keys = CustomQuery.get_column_names(table_name=self.open_order_table)
            inverted_open_order = {v: k for k, v in openorder_eng.items()}
            open_order_converted = {inverted_open_order.get(k, k): v for k, v in open_order_data.items()}

            filters = {key: value for key, value in open_order_converted.items() if key in open_order_keys and value}
            filters=convert_date_format(filters)
            
            where_clause = build_where_clause(filters)
            open_order_data = CustomQuery.all_table_data(
                table_name=self.open_order_table,
                where_clause=where_clause,
                columns=self.columns
            )

            # Process open order data
            result_dict = {}
            weeks = set()

            for item in open_order_data:
                mesan_item = item[self.columns.index('LPROD')]
                chk_lr_dte = datetime.datetime.strptime(str(transform_value(item[self.columns.index('CHKLRDTE')])), '%d-%m-%Y').date()
                week_no = ("Backlog" if chk_lr_dte < datetime.date.today() else f"Week{chk_lr_dte.isocalendar().week}")
                week_no = str(week_no)
                total_order_line_value = float(item[self.columns.index('BALANCE')])

                if mesan_item not in result_dict:
                    result_dict[mesan_item] = {week_no: 0.0}

                if week_no not in result_dict[mesan_item]:
                    result_dict[mesan_item][week_no] = 0.0

                result_dict[mesan_item][week_no] += total_order_line_value
                weeks.add(week_no)

            result_list = []
            for mesan_item, week_data in result_dict.items():
                grand_total = sum(week_data.values())
                result_list.append({
                    "item_number": mesan_item,
                    **week_data,
                    "grand_total": grand_total
                })

            # Convert result_list to DataFrame
            result_df = pd.DataFrame(result_list)

            # # Ensure 'item_number' is in string format for consistency
            # result_df.index = result_df.index.astype(str)

            combined_df = bom_stock_pivot.merge(result_df, on='item_number', how='left', suffixes=('', '_bom'))
            # combined_df = combined_df.merge(stock_pivot_df, on='item_number', how='left')
            combined_df = combined_df.map(lambda x: x.strip() if isinstance(x, str) else x)
            combined_df['openorder_grandtotal'] = combined_df['bom_quantity_required'] * combined_df['grand_total']*1000
            
            column_headers = combined_df.columns.tolist()
            db_list=CustomQuery.get_column_names(table_name=self.bom_table)
            static_list=[bom_eng[key] for key in db_list if key in bom_eng]
            static_list.insert(1,'grand_total')
            excluded_columns = static_list + ['openorder_grandtotal','STOCKGRANDTOTAL','Backlog']
            
            # Categorize columns in a single loop
            week_columns, remaining_columns = [], []

            for col in column_headers:
                if col.startswith("Week"):
                    week_columns.append(col)
                elif col not in excluded_columns:
                    remaining_columns.append(col)
            week_columns = sorted(weeks, key=order_weeks)
            
            
            # Create the final column order
            combined_df[week_columns] = combined_df[week_columns].mul(combined_df['bom_quantity_required'], axis=0)*1000

            # if 'Backlog' in combined_df.columns:
            #     final_column_order = static_list + ["Backlog"] + week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL']
            # else:
            final_column_order = static_list + week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL'] 
            combined_df=combined_df[final_column_order]
            combined_df.fillna(0, inplace=True)
            
            pivote_columns=week_columns+['openorder_grandtotal']+ remaining_columns+['STOCKGRANDTOTAL']      
            #pivote
            combined_df = combined_df.reset_index(drop=True)
            combined_df['item_number_child'] = combined_df['item_number_child'].astype(str).fillna('Unknown')  # Ensure it's a string column

            # Check the dtype to confirm it's correct
            # print(combined_df['item_number_child'].dtype)

            # Ensure item_number_child is not in pivote_columns if it's already in index
            pivote_columns = [col for col in week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL'] if col != 'item_number_child']

            pivot_table = pd.pivot_table(
                combined_df, 
                values=pivote_columns, 
                index='item_number_child', 
                aggfunc='sum'
            )

            pivot_table = pivot_table[pivote_columns]
            pivot_table = pivot_table.loc[:, ~pivot_table.columns.duplicated()]


            # Convert only the columns to floats, excluding 'col0'
            pivot_table_float = pivot_table.copy()
            pivot_table_float.loc[:, pivot_table.columns[1:]] = pivot_table_float.loc[:, pivot_table.columns[1:]].astype(float)

            # Calculate sums for the converted columns
            # sums = pivot_table_float.sum()

            # Append the sums as a new row
            # pivot_table.loc['grandtotal'] = pd.Series([None] * len(pivot_table.columns), index=pivot_table.columns)
            # pivot_table.loc['grandtotal', pivot_table.columns[0:]] = sums
            pivot_table = pivot_table.reset_index()
            #--------------------------pivote end-------------------- 
            
            # pivot_table = pd.pivot_table(combined_df, values=pivote_columns, index=['item_number_child'], aggfunc='sum')
            # pivot_table=pivot_table[pivote_columns]
            # # Reset index to convert index to column
            # pivot_table = pivot_table.reset_index()


            for i in range(len(week_columns)):
                # Calculate cumulative sum up to the current week column
                cumulative_sum = pivot_table[week_columns[:i+1]].sum(axis=1)
                pivote_columns.append(week_columns[i] + "_stock")
                # Create a new column for each week indicating if the cumulative sum is <= STOCKGRANDTOTAL
                pivot_table[week_columns[i] + "_stock"] = cumulative_sum <= pivot_table["STOCKGRANDTOTAL"]
                
                # Convert the boolean result to 'Sufficient' or 'Insufficient'
                pivot_table[week_columns[i] + "_stock"] = pivot_table[week_columns[i] + "_stock"].apply(
                    lambda x: 'Sufficient' if x else 'Insufficient'
                )
            pivot_table=pivot_table.round(3)
            filter_columns={col: list(set(pivot_table[col])) for col in pivot_table.columns}

            # Apply filtering for each column specified in the payload
            for column, values in bomorderbook_pivottablo_list.items():
                if column in pivot_table.columns:
                    pivot_table = pivot_table[pivot_table[column].isin(values)]

            

            # # Convert combined dataframe to JSON
            combined_json = pivot_table.to_dict(orient='records')

            if export_table and export_table=="bomorderbook_pivottablo_list":
                return generate_excel(combined_json,table_name=export_table,columns=["item_number_child"]+pivote_columns)


            
            
            # Pagination logic
            page_number = int(request.GET.get('p', 1))
            page_size = int(request.GET.get('row_size', 10))
            offset = (page_number - 1) * page_size
            total_count=len(pivot_table)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            # print(combined_json[(page_number-1) * page_size: page_number * page_size])
            ret_data = {
                "columns": ["item_number_child"]+pivote_columns,
                "count": total_count,
                "page": 1,
                "page_size": 10,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results":combined_json[(page_number-1) * page_size: page_number * page_size],
                # "result":combined_json,
                "filter_columns":filter_columns,
                "temp_column": []
            }
        except Exception as e:
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"



@method_decorator(csrf_exempt, name="dispatch")
class FinalList(View):
    bom_table="E3SCBOM"
    open_order_table="E3SCORDERS"
    stock_table="E3SCSTOCK"
    columns = ["LPROD", "CHKLRDTE", "TOTLINEVAL","BALANCE","LQALL"]

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)

            bom_stock_pivot = PandsCustomQuery.bom_stock_pivot(table_name=self.stock_table,bom_table_name=self.bom_table)
            bom_stock_pivot = bom_stock_pivot.rename(columns=bom_eng)

            # bom_stock_pivot_child = PandsCustomQuery.bom_stock_pivot_child(table_name=self.stock_table,bom_table_name=self.bom_table)
            # bom_stock_pivot_child = bom_stock_pivot_child.rename(columns=bom_eng)


            
            # # Fetch data for open orders with filtering
            open_order_data = json_data.get('open_orders', {})
            final=json_data.get('final', {})

            export_table=json_data.get('export_table',"")
            open_order_keys = CustomQuery.get_column_names(table_name=self.open_order_table)
            inverted_open_order = {v: k for k, v in openorder_eng.items()}
            open_order_converted = {inverted_open_order.get(k, k): v for k, v in open_order_data.items()}

            filters = {key: value for key, value in open_order_converted.items() if key in open_order_keys and value}
            filters=convert_date_format(filters)
            
            where_clause = build_where_clause(filters)
            open_order_data = CustomQuery.all_table_data(
                table_name=self.open_order_table,
                where_clause=where_clause,
                columns=self.columns
            )

            # Process open order data
            result_dict = {}
            weeks = set()

            for item in open_order_data:
                mesan_item = item[self.columns.index('LPROD')]
                chk_lr_dte = datetime.datetime.strptime(str(transform_value(item[self.columns.index('CHKLRDTE')])), '%d-%m-%Y').date()
                week_no = ("Backlog" if chk_lr_dte < datetime.date.today() else f"Week{chk_lr_dte.isocalendar().week}")
                week_no = str(week_no)
                total_order_line_value = float(item[self.columns.index('BALANCE')])

                if mesan_item not in result_dict:
                    result_dict[mesan_item] = {week_no: 0.0}

                if week_no not in result_dict[mesan_item]:
                    result_dict[mesan_item][week_no] = 0.0

                result_dict[mesan_item][week_no] += total_order_line_value
                weeks.add(week_no)

            result_list = []
            for mesan_item, week_data in result_dict.items():
                grand_total = sum(week_data.values())
                result_list.append({
                    "item_number": mesan_item,
                    **week_data,
                    "grand_total": grand_total
                })

            # Convert result_list to DataFrame
            result_df = pd.DataFrame(result_list)
            
            # Adding fix for subtracting LQALL from grand_total before computation - 29-Dec-2025 - Mohammed Magar
            open_order_data_df = pd.DataFrame.from_records(open_order_data, columns=['mesan_item', 'date', 'TOTLINEVAL', 'BALANCE', 'LQALL'])
            
            # fix here to sum LQALL if there are multiple entries of orders
            open_order_data_df = open_order_data_df.groupby(['mesan_item'], as_index=False).agg({'LQALL': 'sum'})
            result_df = result_df.merge(open_order_data_df.set_index('mesan_item'), left_on='item_number', right_index=True, how='left')
            
            #subtracting LQALL from grand_total
            result_df['grand_total'] = result_df['grand_total'] - result_df['LQALL'].astype(float)

            
            # End of fix

            # # Ensure 'item_number' is in string format for consistency`
            # result_df.index = result_df.index.astype(str)

            stock_pvt = PandsCustomQuery.stock_pivot(table_name=self.stock_table)[["LPROD", "GTOTAL"]]
            stock_pvt = stock_pvt[stock_pvt["LPROD"] != "Grand Total"].rename(columns={"LPROD": "item_number_child", "GTOTAL": "CHILDSTOCKGRANDTOTAL"})

            print(stock_pvt, "+++++++++++++++++++++++++++")

            combined_df = bom_stock_pivot.merge(
                stock_pvt, on='item_number_child', how='left', suffixes=('', '_c')
            ).merge(
                result_df, on='item_number', how='left', suffixes=('', '_bom')
            )
            # Identify columns to drop dynamically
            columns_to_drop = [col for col in combined_df.columns if col.endswith('_c') and col != 'CHILDSTOCKGRANDTOTAL']

            # Drop unwanted columns
            combined_df = combined_df.drop(columns=columns_to_drop, errors='ignore')
            # print(combined_df.columns,"?????????????????????")

            # combined_df = bom_stock_pivot.merge(result_df, on='item_number', how='left', suffixes=('', '_bom'))
            # combined_df = combined_df.merge(stock_pivot_df, on='item_number', how='left')
            combined_df = combined_df.map(lambda x: x.strip() if isinstance(x, str) else x)
            combined_df['openorder_grandtotal'] = combined_df['bom_quantity_required'] * combined_df['grand_total']*1000
            
            column_headers = combined_df.columns.tolist()
            db_list=CustomQuery.get_column_names(table_name=self.bom_table)
            static_list=[bom_eng[key] for key in db_list if key in bom_eng]

            # static_list=list(bom_eng.values())
            static_list.insert(1,'grand_total')
            excluded_columns = static_list + ['openorder_grandtotal','STOCKGRANDTOTAL','CHILDSTOCKGRANDTOTAL','Backlog']

            # Categorize columns in a single loop
            week_columns, remaining_columns = [], []

            for col in column_headers:
                if col.startswith("Week"):
                    week_columns.append(col)
                elif col not in excluded_columns:
                    remaining_columns.append(col)
            week_columns = sorted(weeks, key=order_weeks)
            
            # fix subtract LQALL from week columns
            combined_df[week_columns] = combined_df[week_columns].sub(combined_df['LQALL'].astype(float), axis=0)
            
            # Create the final column order
            combined_df[week_columns] = combined_df[week_columns].mul(combined_df['bom_quantity_required'], axis=0)*1000

            # final_column_order =  static_list+["Backlog"]+week_columns + ['openorder_grandtotal']+remaining_columns+['STOCKGRANDTOTAL']
            # if 'Backlog' in combined_df.columns:
            #     final_column_order = static_list + ["Backlog"] + week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL']
            # else:
            final_column_order = static_list +week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL','CHILDSTOCKGRANDTOTAL']
            final_column_order=list(dict.fromkeys(final_column_order))
            combined_df=combined_df[final_column_order]
            combined_df.fillna(0, inplace=True)

            #---------------pivote start ----------------
            pivote_columns=week_columns+['openorder_grandtotal']+ remaining_columns+['STOCKGRANDTOTAL','CHILDSTOCKGRANDTOTAL']      
            combined_df = combined_df.reset_index(drop=True)
            combined_df['item_number_child'] = combined_df['item_number_child'].astype(str).fillna('Unknown')  # Ensure it's a string column

            # Check the dtype to confirm it's correct
            # print(combined_df['item_number_child'].dtype)
            
            # fix here 29-Dec-2025
            # combined_df['net_required']=(combined_df['openorder_grandtotal'] - combined_df['STOCKGRANDTOTAL'])*2
            combined_df['net_required']=combined_df['openorder_grandtotal'] - combined_df['CHILDSTOCKGRANDTOTAL']
            
            # fix here 29-Dec-2025
            #combined_df['net_required_after_deduction']=combined_df['net_required']-combined_df['CHILDSTOCKGRANDTOTAL']
            combined_df['net_required_after_deduction']=combined_df['net_required']-(combined_df['STOCKGRANDTOTAL'] * combined_df['bom_quantity_required'])

            # Ensure item_number_child is not in pivote_columns if it's already in index
            pivote_columns = [col for col in week_columns + ['openorder_grandtotal'] + remaining_columns + ['STOCKGRANDTOTAL','CHILDSTOCKGRANDTOTAL','net_required','net_required_after_deduction'] if col != 'item_number_child']

            pivot_table = pd.pivot_table(
                combined_df, 
                values=pivote_columns, 
                index='item_number_child', 
                aggfunc='sum'
            )

            pivot_table = pivot_table[pivote_columns]
            pivot_table = pivot_table.loc[:, ~pivot_table.columns.duplicated()]


            # Convert only the columns to floats, excluding 'col0'
            pivot_table_float = pivot_table.copy()
            pivot_table_float.loc[:, pivot_table.columns[1:]] = pivot_table_float.loc[:, pivot_table.columns[1:]].astype(float)


            pivot_table = pivot_table.reset_index()
          
            final_list=['item_number_child']
            for i in range(len(week_columns)):
                # Calculate cumulative sum up to the current week column
                cumulative_sum = pivot_table[week_columns[:i+1]].sum(axis=1)
                pivote_columns.append(week_columns[i] + "_stock")
                final_list.append(week_columns[i] + "_stock")
                # Create a new column for each week indicating if the cumulative sum is <= STOCKGRANDTOTAL
                pivot_table[week_columns[i] + "_stock"] = cumulative_sum <= pivot_table["net_required_after_deduction"]
                
                # Convert the boolean result to 'Sufficient' or 'Insufficient'
                pivot_table[week_columns[i] + "_stock"] = pivot_table[week_columns[i] + "_stock"].apply(
                    lambda x: 'Sufficient' if x else 'Insufficient'
                )
            # Final merge
            df2_subset = pivot_table[final_list] 
            final_df = pd.merge(combined_df, df2_subset, on='item_number_child', how='left')
            final_df=final_df.round(3)
            final_df.drop(columns='LQALL', inplace=True)
            
            # Fix for Topic3 Mohammed 29-Jan-2026
            # Show only entries where grand_total > 0
            final_df = final_df.loc[final_df.grand_total>0]
            
            filter_columns={col: list(set(final_df[col])) for col in final_df.columns}


            # Apply filtering for each column specified in the payload
            for column, values in final.items():
                if column in final_df.columns:
                    final_df = final_df[final_df[column].isin(values)]
            
            
            # Remove duplicates based on item_no and item_child
            # final_df = final_df.drop_duplicates(subset=['item_number', 'item_number_child'], keep='first')
            # # Convert combined dataframe to JSON
            combined_json = final_df.to_dict(orient='records')
            
            
            # Pagination logic
            page_number = int(request.GET.get('p', 1))
            page_size = int(request.GET.get('row_size', 10))
            offset = (page_number - 1) * page_size
            total_count=len(combined_json)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            # print(combined_json[(page_number-1) * page_size: page_number * page_size])
            if export_table and export_table=="final":
                return generate_excel(combined_json,table_name=export_table)
            ret_data = {
                "columns": final_column_order+['net_required','net_required_after_deduction']+final_list,
                "count": total_count,
                "page": 1,
                "page_size": 10,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results":combined_json[(page_number-1) * page_size: page_number * page_size],
                # "result":combined_json,
                "filter_columns":filter_columns,
                "temp_column": []
            }
        except Exception as e:
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"



@method_decorator(csrf_exempt, name="dispatch")
class RouteList(View):
    table_name="E3SCROUTE"
    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            route_data = json_data.get('route', {})
            export_table=json_data.get('export_table',{})

            table_columns = CustomQuery.get_column_names(table_name=self.table_name)
            inverted_columns= {v: k for k, v in route_eng.items()}
            columns_converted = {inverted_columns.get(k, k): v for k, v in route_data.items()}

            # Extract filter criteria
            filters = {
                key: value for key, value in columns_converted.items() if key in table_columns and value
            }
            filters=convert_date_format(filters)
            
            if export_table and export_table=="route":
                page_size=None
                offset=None
            else:# Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size
            
            # Pagination parameters
            # page_number = int(request.GET.get('p', 1))
            # page_size = int(request.GET.get('row_size', 10))
            # offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size
            )

            result_list = [
                dict(list({route_eng.get(key, key): transform_value(value) for key, value in zip(table_columns, item)}.items()))
                for item in data
            ]
            if export_table and export_table=="route":
                return generate_excel(result_list,table_name=export_table)

            # Get total count for pagination metadata
            total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            
            filter_columns = {route_eng.get(k, k): v for k, v in CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=table_columns).items()}

            # Build response data
            ret_data = {
                "count": total_count,
                "page": page_number,
                "page_size": page_size,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results": result_list,
                "filter_columns": filter_columns
            }

        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"


@method_decorator(csrf_exempt, name="dispatch")
class WorkOrderList(View):
    table_name="E3SCWORKO"
    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            workorder_data = json_data.get('work_order', {})
            export_table=json_data.get('export_table',{})

            table_columns = CustomQuery.get_column_names(table_name=self.table_name)
            inverted_columns= {v: k for k, v in work_order_eng.items()}
            columns_converted = {inverted_columns.get(k, k): v for k, v in workorder_data.items()}

            
            # Extract filter criteria
            filters = {
                key: value for key, value in columns_converted.items() if key in table_columns and value
            }

            if export_table and export_table=="work_order":
                page_size=None
                offset=None
            else:# Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size
            
            # Pagination parameters
            # page_number = int(request.GET.get('p', 1))
            # page_size = int(request.GET.get('row_size', 10))
            # offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size
            )

            result_list = [
                dict(list({work_order_eng.get(key, key): transform_value(value) for key, value in zip(table_columns, item)}.items()))
                for item in data
            ]

            if export_table and export_table=="work_order":
                return generate_excel(result_list,table_name=export_table)

            # Get total count for pagination metadata
            total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            
            filter_columns = {work_order_eng.get(k, k): v for k, v in CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=table_columns).items()}
            
            # Build response data
            ret_data = {
                "count": total_count,
                "page": page_number,
                "page_size": page_size,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results": result_list,
                "filter_columns": filter_columns
            }

        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"


@method_decorator(csrf_exempt, name="dispatch")
class MasterList(View):
    table_name="E3SCMASTER"
    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            bom_data = json_data.get("master_data_list", {})
            export_table=json_data.get('export_table',{})

            keys = CustomQuery.get_column_names(table_name=self.table_name)

            # Extract filter criteria
            filters = {
                key: value for key, value in bom_data.items() if key in keys and value
            }

            if export_table and export_table=="master_data":
                page_size=None
                offset=None
            else:# Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size
            
            # Pagination parameters
            # page_number = int(request.GET.get('p', 1))
            # page_size = int(request.GET.get('row_size', 10))
            # offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size
            )

            result_list = [
                {key: transform_value(value) for key, value in zip(keys, item)}
                for item in data
            ]
            if export_table and export_table=="master_data":
                return generate_excel(result_list,table_name=export_table)

            # Get total count for pagination metadata
            total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None

            # Build response data
            ret_data = {
                "count": total_count,
                "page": page_number,
                "page_size": page_size,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results": result_list,
                "filter_columns": keys
            }

        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"

@method_decorator(csrf_exempt, name="dispatch")
class PurchaseList(View):
    table_name="E3SCPURCHA"
    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            purchase_data = json_data.get("purchase_sas",{})
            export_table=json_data.get('export_table',{})

            table_columns = CustomQuery.get_column_names(table_name=self.table_name)
            inverted_columns= {v: k for k, v in purchase_eng.items()}
            columns_converted = {inverted_columns.get(k, k): v for k, v in purchase_data.items()}


            # Extract filter criteria
            filters = {
                key: value for key, value in columns_converted.items() if key in table_columns and value
            }

            if export_table and export_table=="purchase_sas":
                page_size=None
                offset=None
            else:# Pagination parameters
                page_number = int(request.GET.get('p', 1))
                page_size = int(request.GET.get('row_size', 10))
                offset = (page_number - 1) * page_size
            
            # # Pagination parameters
            # page_number = int(request.GET.get('p', 1))
            # page_size = int(request.GET.get('row_size', 10))
            # offset = (page_number - 1) * page_size

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
          # Fetch data with filters and pagination directly from the database
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                offset=offset,
                limit=page_size
            )

            result_list = [
                dict(list({purchase_eng.get(key, key): transform_value(value) for key, value in zip(table_columns, item)}.items()))
                for item in data
            ]

            if export_table and export_table=="purchase_sas":
                return generate_excel(result_list,table_name=export_table)


            # Get total count for pagination metadata
            total_count = CustomQuery.count_filtered_data(table_name=self.table_name, where_clause=where_clause)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages

            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None
            filter_columns = {purchase_eng.get(k, k): v for k, v in CustomQuery.get_distinct_column_values(table_name=self.table_name,filter_columns=table_columns).items()}
            
            # Build response data
            ret_data = {
                "count": total_count,
                "page": page_number,
                "page_size": page_size,
                "total_pages": total_pages,
                "next": next_url,
                "previous": previous_url,
                "results": result_list,
                "filter_columns": filter_columns
            }

        
        except Exception as e:
            # err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            print(e,"------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
        
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"




@method_decorator(csrf_exempt, name="dispatch")
class OrderBookPivot(View):
    table_name = "E3SCORDERS"
    columns = ["LPROD", "CHKLRDTE", "TOTLINEVAL","BALANCE"]

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            open_order_data = json_data.get('open_orders', {})
            export_table=json_data.get('export_table',{})

            open_order_keys = CustomQuery.get_column_names(table_name=self.table_name)

            inverted_open_order = {v: k for k, v in openorder_eng.items()}
            open_order_converted = {inverted_open_order.get(k, k): v for k, v in open_order_data.items()}

            # Extract filter criteria
            filters = {
                key: value for key, value in open_order_converted.items() if key in open_order_keys and value
            }

            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)
            
            # Fetch data with filters
            data = CustomQuery.all_table_data(
                table_name=self.table_name,
                where_clause=where_clause,
                columns=self.columns
            )
            
            # Process data
            result_dict = {}
            weeks = set()
            
            for item in data:
                mesan_item = item[self.columns.index('LPROD')]  
                chk_lr_dte = datetime.datetime.strptime(str(transform_value(item[self.columns.index('CHKLRDTE')])), '%d-%m-%Y').date()
                week_no = ("Backlog" if chk_lr_dte < datetime.date.today() else chk_lr_dte.isocalendar().week)
                week_no = str(week_no)
                total_order_line_value = float(item[self.columns.index('BALANCE')])
                
                if mesan_item not in result_dict:
                    result_dict[mesan_item] = {week_no: 0.0}
                
                if week_no not in result_dict[mesan_item]:
                    result_dict[mesan_item][week_no] = 0.0
                
                result_dict[mesan_item][week_no] += total_order_line_value
                weeks.add(week_no)
            # Convert to required format
            result_list = []
            for mesan_item, week_data in result_dict.items():
                grand_total = sum(week_data.values())
                week_data = {key: round(value, 3) if isinstance(value, float) else value for key, value in week_data.items()}

                result_list.append({
                    "item_number": mesan_item,
                    **week_data,
                    "grand_total":round(grand_total, 3) 
                })
            columns=['item_number']+sorted(weeks, key=lambda x: (x != 'Backlog', x))+['grand_total']
            
            if export_table and export_table=="open_orders_pivote":
                return generate_excel(result_list,table_name=export_table,columns=columns)



            
            ret_data = {
                "columns": columns,
                "result": result_list
            }
        
        except Exception as e:
            print(e, "------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)


@method_decorator(csrf_exempt, name="dispatch")
class StockPivot(View):
    table_name = "E3SCSTOCK"
    columns = ["LPROD", "LWHS", "BAL"]

    def post(self, request):
        try:
            # Getting JSON object
            body = request.body.decode()
            json_data = json.loads(body)
            stock_data = json_data.get('stock_data', {})
            export_table=json_data.get('export_table',{})

            stock_data_keys = CustomQuery.get_column_names(table_name=self.table_name)
            
            inverted_column = {v: k for k, v in stock_eng.items()}
            converted_column = {inverted_column.get(k, k): v for k, v in stock_data.items()}

            # Extract filter criteria
            filters = {
                key: value for key, value in converted_column.items() if key in stock_data_keys and value
            }
            # Construct the WHERE clause for filtering
            where_clause = build_where_clause(filters)


            stock_pvt=PandsCustomQuery.stock_pivot(table_name=self.table_name,where_clause=where_clause,warehouses=filters.get("LWHS",None))
            # dentify the "Grand Total" row
            grand_total_row = stock_pvt[stock_pvt['LPROD'] == 'Grand Total']

            # Drop the "Grand Total" row from the original DataFrame
            df_without_grand_total = stock_pvt[stock_pvt['LPROD'] != 'Grand Total']

            # Append the "Grand Total" row to the end using pd.concat
            stock_pvt = pd.concat([df_without_grand_total, grand_total_row], ignore_index=True)
            
             # # Convert combined dataframe to JSON
            combined_json = stock_pvt.to_dict(orient='records')

            page_number = int(request.GET.get('p', 1))
            page_size = int(request.GET.get('row_size', 10))
            offset = (page_number - 1) * page_size
            total_count=len(stock_pvt)
            total_pages = (total_count + page_size - 1) // page_size  # Calculate total pages
            
            # Build pagination URLs
            next_url = self.build_pagination_url(request.GET.copy(), page_number + 1) if page_number < total_pages else None
            previous_url =self.build_pagination_url(request.GET.copy(), page_number - 1) if page_number > 1 else None



            if filters.get('LWHS',[]):
                columns=["LPROD"]+filters.get('LWHS',[])+['GTOTAL']
            else:
                columns=["LPROD","IK","IF","IM",'GTOTAL']
                
            if export_table and export_table=="stock_data_pivote":
                return generate_excel(combined_json,table_name=export_table,columns=columns)




            ret_data = {
                "columns": columns,
                "count":total_count,
                "result": combined_json[(page_number-1) * page_size: page_number * page_size],
                "next":next_url,
                "previous":previous_url,
                "last_index":combined_json[-1]
            }
        
        except Exception as e:
            print(e, "------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)
    def build_pagination_url(self, query_params, page_number):
        query_params['p'] = page_number
        return f"{self.request.build_absolute_uri(self.request.path)}?{urlencode(query_params)}"



def generate_excel(results, table_name,columns=None):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    if columns:
        # Write the header row based on the predefined columns
        for col_num, header in enumerate(columns):
            worksheet.write(0, col_num, header)

        # Write data rows
        for row_num, row_data in enumerate(results, start=1):
            for col_num, key in enumerate(columns):
                # Use .get() to handle missing columns and write data accordingly
                worksheet.write(row_num, col_num, row_data.get(key, None))  # Replace None with a default value if needed

    else:
        # Write the header
        headers = list(results[0].keys())
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Write data rows
        for row_num, row_data in enumerate(results, start=1):
            for col_num, key in enumerate(headers):
                worksheet.write(row_num, col_num, row_data[key])

    # Close the workbook
    workbook.close()

    # Rewind the buffer
    output.seek(0)

    # Create the HttpResponse object with the appropriate Excel header.
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{table_name}.xlsx"'

    return response



class EditLeadTime(generics.RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    queryset = LeadTimeMaster.objects.all()
    serializer_class = LeadTimeSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SidebarCount(View):
    def post(self, request):
        try:
            # Getting JSON object
            pq=PandsCustomQuery()
            body = request.body.decode()
            json_data = json.loads(body)
            ret_data={
                "open_order_count":pq.count_records(table_name="E3SCORDERS"),
                "stock_order_count":pq.count_records(table_name="E3SCSTOCK"),
                "bom_count":pq.count_records(table_name="E3SCBOM"),
                "purchase_count":pq.count_records(table_name="E3SCPURCHA"),
                "route_count":pq.count_records(table_name="E3SCROUTE"),
                "workcenter_count":pq.count_records(table_name="E3SCWORKO"),
                "customer_count":CustomerMaster.objects.count(),
                "leadtime_count":LeadTimeMaster.objects.count(),
                "supply_count":MasterSupplyCode.objects.count(),
            }
        except Exception as e:
            print(e, "------------------------")
            ret_data = {'status': 'failed', 'err_msg': str(e), 'data': ''}
            logging.error(e)
        
        return JsonResponse(ret_data)




#------------------------------Old code start --------------------------------------------------------

class OpenOrdersViewSet(viewsets.ModelViewSet):
    # two_years_ago = datetime.now() - timedelta(days=365 * 2)
    authentication_classes = [JWTAuthentication]
    queryset = OpenOrders.objects.all().order_by('-id')
    serializer_class = OpenOrdersSerializer
    pagination_class = CustomPagination
    permissions=["Can view open orders"]
    permission_classes = [CustomDynamicPermission(allowed_permissions=permissions)]

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        current_date = datetime.now().date()
        
        # queryset = OpenOrders.objects.filter(filter_query(convert_list(request.data.copy()))).filter(balance_qty__gte=1)
        queryset = OpenOrders.objects.filter(filter_query(convert_list(request.data['open_orders'].copy())))
        if request.data['stock_data']:
            mesan = MesanMaster.objects.exclude(ob_mesan_ref__weekno=None).filter(filter_query(convert_list(request.data['stock_data'].copy(),"so_mesan_ref__"))).annotate(
                warehouse=models.F('so_mesan_ref__warehouse'),
                balance=models.F('so_mesan_ref__balance'),
            ).values('so_mesan_ref__mesan_item', 'warehouse').annotate(
                balance_sum=Sum('balance')
            )

            combined_result = defaultdict(lambda: defaultdict(float))

            # Iterate through mesan and directly combine values for the same mesan_item
            for item in mesan:
                mesan_item = item["so_mesan_ref__mesan_item"]
                warehouse = item["warehouse"]
                balance_sum = item["balance_sum"]
                
                if balance_sum is not None:
                    combined_result[mesan_item][warehouse] += float(balance_sum)

            # Calculate grand_total for each mesan_item
            for values in combined_result.values():
                values["grand_total"] = sum(values.values())

            # Convert combined_result to a list of dictionaries with the desired format
            combined_result_list = [{"mesan_item": mesan_item, **values} for mesan_item, values in combined_result.items()]   
        
       
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result = result.data
            temp=[]
            for core_obj in result['results']:
                core_obj.pop('mesan_item_ref') 
                if request.data['stock_data']:
                    gt = get_value_by_key_with_value("mesan_item", core_obj.get('mesan_item'), "grand_total", combined_result_list)
                    # core_obj['open_orders_qty'] = float(gt) - float(core_obj['open_orders_qty']) if gt else None if core_obj.pop('mesan_item') not in temp
                    if gt and core_obj.get('mesan_item') not in temp:
                        temp.append(core_obj.get('mesan_item'))
                        core_obj['open_orders_qty'] = float(gt) - float(core_obj['open_orders_qty']) 
                    # else:
                         
                    # else:
                    #     core_obj['open_orders_qty']=None
                    #     if core_obj.get('mesan_item') not in temp else core_obj['open_orders_qty']

                else:
                    core_obj['open_orders_qty']="Filter StockData"
                    gt = "Filter StockData"
                    
                core_obj_list = list(core_obj.items())
                core_obj_list.insert(19, ('remaining_qty', core_obj['remaining_qty']))
                core_obj_list.insert(20, ('open_orders_qty', core_obj['open_orders_qty']))
                core_obj_list.insert(21, ('grand_total', gt))
                core_obj.clear()
                core_obj.update(core_obj_list)

            result['filter_columns'] = {column: list(set(values)) for column, values in zip(open_order_filter, zip(*OpenOrders.objects.values_list(*open_order_filter).distinct()))}
            result['temp_column']=temp_column
            return Response(result)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data['filter_columns'] = [] 
        data['temp_column']=[]
        
        return Response(data)


class OpenOrdersDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    queryset = OpenOrders.objects.all()
    OpenOrders._meta.verbose_name
    serializer_class = OpenOrdersEditSerializer

class StockDataViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = (AllowAny,)
    
    queryset = StockData.objects.all().order_by('-id')
    serializer_class = StockDataSerializer
    pagination_class = CustomPagination

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        queryset = StockData.objects.filter(filter_query(convert_list(request.data['stock_data'].copy())))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result = result.data
            result['filter_columns'] = {column: list(set(values)) for column, values in zip(stock_data, zip(*StockData.objects.values_list(*stock_data).distinct()))}
            
            return Response(result)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data['filter_columns'] = [] 
        return Response(data)
    
class StockDataDetail(generics.RetrieveUpdateAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = (AllowAny,)
    queryset = StockData.objects.all()
    serializer_class = StockDataSerializer

class BomViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = BOM.objects.all().order_by('-id')
    serializer_class = BomSerializer
    pagination_class = CustomPagination

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        queryset = BOM.objects.filter(filter_query(convert_list(request.data['bom'].copy())))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result = result.data
            result['filter_columns'] = open_order_filter
            return Response(result)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data['filter_columns'] = [] 
        return Response(data)

class BomDetail(generics.RetrieveUpdateAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = (AllowAny,)
    
    queryset = BOM.objects.all()
    serializer_class = BomSerializer

class BomEdit(View):
    permission_classes = (AllowAny,)
    
    def get(self, request, pk, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM bom WHERE id = %s", [pk])
            row = cursor.fetchone()
            if row is None:
                return JsonResponse({'error': 'BOM not found'}, status=404)
            
            columns = [col[0] for col in cursor.description]
            bom = dict(zip(columns, row))
            return JsonResponse(bom, encoder=DjangoJSONEncoder, safe=False)

    def put(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE bom 
                SET BPROD = %s, BSEQ = %s, BCHLD = %s, LIDSC1 = %s, BQREQ = %s,
                    BCLAS = %s, BCLAC = %s, BBUBB = %s, BOPNO = %s
                WHERE id = %s
            """, [
                data.get('BPROD'),
                data.get('BSEQ'),
                data.get('BCHLD'),
                data.get('LIDSC1'),
                data.get('BQREQ'),
                data.get('BCLAS'),
                data.get('BCLAC'),
                data.get('BBUBB'),
                data.get('BOPNO'),
                pk
            ])
            
            if cursor.rowcount == 0:
                return JsonResponse({'error': 'BOM not found'}, status=404)

            return JsonResponse({'message': 'BOM updated successfully'}, status=200)

class RouteViews(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    pagination_class = CustomPagination

class PurchaseSasViews(generics.ListCreateAPIView):
    queryset = PurchaseSas.objects.all()
    serializer_class = PurchaseSasSerializer
    pagination_class = CustomPagination

class MasterDataViews(generics.ListCreateAPIView):
    queryset = MasterData.objects.all()
    serializer_class = MasterDataSerializer
    pagination_class = CustomPagination
    



class CustomerViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = CustomerMaster.objects.all().order_by('-id')
    serializer_class = CustomerSerializer
    pagination_class = CustomPagination

    

    
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):

        queryset = CustomerMaster.objects.filter(filter_query(convert_list(request.data['customer'].copy())))
        page = self.paginate_queryset(queryset)
        
        fields = CustomerMaster._meta.get_fields()
        filter_columns = {}
        
        # Loop through each field and get unique values
        for field in fields:
            # Skip related fields (ForeignKey, ManyToMany, etc.)
            if not field.is_relation:
                field_name = field.name
                filter_columns[field_name] = list(CustomerMaster.objects.values_list(field_name, flat=True).distinct())
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result = result.data
            result['filter_columns'] = filter_columns
            return Response(result)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data['filter_columns'] = [] 
        return Response(data)
    

class LeadTimeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]
    queryset = LeadTimeMaster.objects.all().order_by('-id')
    serializer_class = LeadTimeSerializer
    pagination_class = CustomPagination

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        queryset = LeadTimeMaster.objects.filter(filter_query(convert_list(request.data['lead_time'].copy())))
        page = self.paginate_queryset(queryset)
        fields = LeadTimeMaster._meta.get_fields()
        filter_columns = {}
        
        # Loop through each field and get unique values
        for field in fields:
            # Skip related fields (ForeignKey, ManyToMany, etc.)
            if not field.is_relation:
                field_name = field.name
                filter_columns[field_name] = list(LeadTimeMaster.objects.values_list(field_name, flat=True).distinct())

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result = result.data
            result['filter_columns'] = filter_columns
            return Response(result)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        data['filter_columns'] = filter_columns
        return Response(data)

class MasterSupplyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = MasterSupplyCode.objects.all().order_by('-id')
    serializer_class = MasterSupplyCodeSerializer
    pagination_class = CustomPagination
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        queryset = MasterSupplyCode.objects.filter(filter_query(convert_list(request.data['master_supply_code'].copy())))
        page = self.paginate_queryset(queryset)

        fields = MasterSupplyCode._meta.get_fields()
        filter_columns = {}
        
        # Loop through each field and get unique values
        for field in fields:
            # Skip related fields (ForeignKey, ManyToMany, etc.)
            if not field.is_relation:
                field_name = field.name
                filter_columns[field_name] = list(queryset.values_list(field_name, flat=True).distinct())

        
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result = result.data
            result['filter_columns'] = filter_columns
            return Response(result)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        


class WorkOrderViews(generics.ListCreateAPIView):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    pagination_class = CustomPagination
    

class EventViews(generics.ListCreateAPIView):
    permission_classes = (AllowAny,)
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # pagination_class = CustomPagination
    
    

class FileUploadView(APIView):
    permission_classes = (AllowAny,)
    
    queryset = OpenOrders.objects.all()
            
    def post(self, request, *args, **kwargs):
        file_name = request.FILES.get('file')
        table_name=request.data.get('table_name')
        csv_obj=CsvToObj()
        if table_name == "open_orders":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,OpenOrders)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,OpenOrders)
                  
        if table_name == "bom":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,BOM)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,BOM)
                  
        if table_name == "purchase_sas":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,PurchaseSas)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,PurchaseSas)
        if table_name == "stock_data":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,StockData)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,StockData)
        if table_name == "route":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,Route)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,Route)
            
        if table_name == "master_data":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,MasterData)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,MasterData)
        
        if table_name == "customer":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,CustomerMaster)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,CustomerMaster)
        if table_name == "lead_time":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,LeadTimeMaster)
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,LeadTimeMaster)
        if table_name == "master_supply_code":
            try:
                csv_obj.csv_to_obj_without_pd(file_name,MasterSupplyCode,SupplyType,"code","type")
            except:
                csv_obj.xlsx_to_obj_with_pd(file_name,MasterSupplyCode,SupplyType,"code","type")
        
        
       
        return Response({'message': 'File uploaded successfully'})



class ExportCSVView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        table_name = request.GET.get('table_name')
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="your_data.xlsx"'
        
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        
        if table_name == "open_orders":
            queryset = OpenOrders._meta.get_fields()    
        elif table_name == "bom":
            queryset = BOM._meta.get_fields()    
        elif table_name == "purchase_sas":
            queryset = PurchaseSas._meta.get_fields()      
        elif table_name == "stock_data":
            queryset = StockData._meta.get_fields()      
        elif table_name == "route":
            queryset = Route._meta.get_fields()      
        elif table_name == "master_data":
            queryset = MasterData._meta.get_fields()    
        elif table_name == "work_order":
            queryset = WorkOrder._meta.get_fields()    
        elif table_name == "customer":
            queryset = CustomerMaster._meta.get_fields()  
        elif table_name == "lead_time":
            queryset = LeadTimeMaster._meta.get_fields() 
        elif table_name == "master_supply_code":
            queryset = MasterSupplyCode._meta.get_fields()   
        else:
            # Handle the case when table_name is not found
            queryset = []
        
        field_names = [field.name for field in queryset]
        
        for col_num, field_name in enumerate(field_names):
            worksheet.write(0, col_num, field_name)
        
        workbook.close()
        return response


class ExportPivotXlsx(viewsets.ModelViewSet):
    queryset = MesanMaster.objects.all()
    serializer_class = MesanMasterSerializer
    permission_classes = (AllowAny,)
    

    # @action(detail=False, methods=['post'])
    def create(self, request, *args, **kwargs):
        table_name = request.data.get('table_name')
        # queryset = self.get_queryset(request)
        

        # if not queryset:
        #     return Response("Invalid table name or empty queryset", status=400)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="your_data.xlsx"'

        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        
        if table_name =="open_orders":
            queryset=MesanMaster.objects.exclude(ob_mesan_ref__weekno=None).filter(filter_query(convert_list(request.data['open_orders'].copy(),"ob_mesan_ref__")))
            unique_weeks = queryset.values_list('ob_mesan_ref__weekno', flat=True).distinct()
            field_names =  sorted(['mesan_item']+list(unique_weeks), key=sort_week_number)+["grand_total"]

            for col_num, field_name in enumerate(field_names):
                worksheet.write(0, col_num, field_name)
            combined_result = defaultdict(lambda: defaultdict(float))

            for item in queryset.values('ob_mesan_ref__mesan_item', 'ob_mesan_ref__weekno').annotate(week_cost_sum=Sum('ob_mesan_ref__total_order_line_value')):
                mesan_item = item["ob_mesan_ref__mesan_item"]
                weekno = item["ob_mesan_ref__weekno"]
                week_cost_sum = item["week_cost_sum"]

                if week_cost_sum is not None:
                    combined_result[mesan_item][weekno] += week_cost_sum

            for values in combined_result.values():
                values["grand_total"] = sum(values.values())

            combined_result_list = [{"mesan_item": mesan_item, **values} for mesan_item, values in combined_result.items()]
            for row_num, item in enumerate(combined_result_list, start=1):
                for col_num, field_name in enumerate(item, start=0):
                    worksheet.write(row_num, field_names.index(field_name), item[field_name])
        if table_name =="stock_data":
            stock_data_qs = MesanMaster.objects.exclude(so_mesan_ref__warehouse=None).filter(filter_query(convert_list(request.data['stock_data'].copy(),"so_mesan_ref__")))
            unique_locations=stock_data_qs.values_list('so_mesan_ref__warehouse', flat=True).distinct()
            field_names =  sorted(['mesan_item']+list(unique_locations), key=sort_week_number)+["grand_total"]
            for col_num, field_name in enumerate(field_names):
                worksheet.write(0, col_num, field_name)
            
            mesan = stock_data_qs.annotate(
                warehouse=models.F('so_mesan_ref__warehouse'),
                balance=models.F('so_mesan_ref__balance'),
            ).values('so_mesan_ref__mesan_item', 'warehouse').annotate(
                balance_sum=Sum('balance')
            )

            combined_result = defaultdict(lambda: defaultdict(float))

            # Iterate through mesan and directly combine values for the same mesan_item
            for item in mesan:
                mesan_item = item["so_mesan_ref__mesan_item"]
                warehouse = item["warehouse"]
                balance_sum = item["balance_sum"]
                
                if balance_sum is not None:
                    combined_result[mesan_item][warehouse] += float(balance_sum)

            # Calculate grand_total for each mesan_item
            for values in combined_result.values():
                values["grand_total"] = sum(values.values())

            # Convert combined_result to a list of dictionaries with the desired format
            combined_result_list = [{"mesan_item": mesan_item, **values} for mesan_item, values in combined_result.items()]
            for row_num, item in enumerate(combined_result_list, start=1):
                for col_num, field_name in enumerate(item, start=0):
                    worksheet.write(row_num, field_names.index(field_name), item[field_name])
        # self.write_data_to_worksheet(worksheet, queryset,field_names)

        workbook.close()
        return response

    def get_queryset(self):
        pass
        # if table_name == "open_orders":
            # Put your queryset logic here based on table_name
        # return MesanMaster.objects.exclude(ob_mesan_ref__weekno=None).filter(filter_query(convert_list(request.data['open_orders'].copy(),"ob_mesan_ref__")))

    # def write_data_to_worksheet(self, worksheet, queryset,field_names):
    #     combined_result = self.combine_queryset_data(queryset)

    #     for row_num, item in enumerate(combined_result, start=1):
    #         for col_num, field_name in enumerate(item, start=0):
    #             worksheet.write(row_num, field_names.index(field_name), item[field_name])

    # def combine_queryset_data(self, queryset):
    #     combined_result = defaultdict(lambda: defaultdict(float))

    #     for item in queryset.values('ob_mesan_ref__mesan_item', 'ob_mesan_ref__weekno').annotate(week_cost_sum=Sum('ob_mesan_ref__total_order_line_value')):
    #         mesan_item = item["ob_mesan_ref__mesan_item"]
    #         weekno = item["ob_mesan_ref__weekno"]
    #         week_cost_sum = item["week_cost_sum"]

    #         if week_cost_sum is not None:
    #             combined_result[mesan_item][weekno] += week_cost_sum

    #     for values in combined_result.values():
    #         values["grand_total"] = sum(values.values())

    #     combined_result_list = [{"mesan_item": mesan_item, **values} for mesan_item, values in combined_result.items()]

    #     return combined_result_list





class RefreshOpenOrder(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        call_command('update_week')
        return Response({"message":"Week No Data updated successfully"})



class OpenOrderPivotTable(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs): 
        
        unique_weeks = MesanMaster.objects.exclude(ob_mesan_ref__weekno=None).filter(filter_query(convert_list(request.data['open_orders'].copy(),"ob_mesan_ref__"))).values_list('ob_mesan_ref__weekno', flat=True).distinct()
        mesan = MesanMaster.objects.exclude(ob_mesan_ref__weekno=None).filter(filter_query(convert_list(request.data['open_orders'].copy(),"ob_mesan_ref__"))).annotate(
            weekno=models.F('ob_mesan_ref__weekno'),
            week_cost=models.F('ob_mesan_ref__total_order_line_value'),
        ).values('ob_mesan_ref__mesan_item', 'weekno').annotate(
            week_cost_sum=Sum('week_cost')
        )


        combined_result = defaultdict(lambda: defaultdict(float))

        # Iterate through mesan and directly combine values for the same mesan_item
        for item in mesan:
            mesan_item = item["ob_mesan_ref__mesan_item"]
            weekno = item["weekno"]
            week_cost_sum = item["week_cost_sum"]
            
            if week_cost_sum is not None:
                combined_result[mesan_item][weekno] += week_cost_sum

        # Calculate grand_total for each mesan_item
        for values in combined_result.values():
            values["grand_total"] = sum(values.values())

        # Convert combined_result to a list of dictionaries with the desired format
        combined_result_list = [{"mesan_item": mesan_item, **values} for mesan_item, values in combined_result.items()]            
        return Response({"weeks":sorted(unique_weeks, key=sort_week_number),"result":combined_result_list})


class StockDataPivotTable(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs): 
        
        unique_locations = MesanMaster.objects.exclude(so_mesan_ref__warehouse=None).filter(filter_query(convert_list(request.data['stock_data'].copy(),"so_mesan_ref__"))).values_list('so_mesan_ref__warehouse', flat=True).distinct()
        mesan = MesanMaster.objects.exclude(ob_mesan_ref__weekno=None).filter(filter_query(convert_list(request.data['stock_data'].copy(),"ob_mesan_ref__"))).annotate(
            warehouse=models.F('so_mesan_ref__warehouse'),
            balance=models.F('so_mesan_ref__balance'),
        ).values('so_mesan_ref__mesan_item', 'warehouse').annotate(
            balance_sum=Sum('balance')
        )

        combined_result = defaultdict(lambda: defaultdict(float))

        # Iterate through mesan and directly combine values for the same mesan_item
        for item in mesan:
            mesan_item = item["so_mesan_ref__mesan_item"]
            warehouse = item["warehouse"]
            balance_sum = item["balance_sum"]
            
            if balance_sum is not None:
                combined_result[mesan_item][warehouse] += float(balance_sum)

        # Calculate grand_total for each mesan_item
        for values in combined_result.values():
            values["grand_total"] = sum(values.values())

        # Convert combined_result to a list of dictionaries with the desired format
        combined_result_list = [{"mesan_item": mesan_item, **values} for mesan_item, values in combined_result.items()]            
        return Response({"weeks":unique_locations,"result":combined_result_list})





