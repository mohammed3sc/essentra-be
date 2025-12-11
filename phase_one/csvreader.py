# import csv
# from io import BytesIO
# import pandas as pd
# from datetime import datetime
# import re

# class CsvToObj:
#     def uploader(self,headers,row,class_name,foreign_table=None,parent_column=None,child_column=None):
#         result={}
#         date_patterns = [
#                 r'\b\d{2}\.\d{2}\.\d{4}\b',
#                 r'\b\d{4}-\d{2}-\d{2}\b',
#                 r'\b\d{2}/\d{2}/\d{4}\b',
#                 r'\b\d{2}-\d{2}-\d{4}\b'  # Add the new date pattern for "05-11-2023"
#             ]
#         for column, val in zip(headers, row):
#             val=val.strip()
#             dates = []
#             if isinstance(val, str):
#                 for pattern in date_patterns:
#                     dates += re.findall(pattern, val)

#                 if dates:
#                     try:
#                         parsed_date = None
#                         for date_str in dates:
#                             try:
#                                 parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
#                                 break
#                             except ValueError:
#                                 pass
#                             try:
#                                 parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
#                                 break
#                             except ValueError:
#                                 pass
#                             try:
#                                 parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
#                                 break
#                             except ValueError:
#                                 pass
#                             try:
#                                 parsed_date = datetime.strptime(date_str, '%d-%m-%Y')  # Adjusted format
#                                 break
#                             except ValueError:
#                                 pass

#                         if parsed_date:
#                             result[column] = parsed_date.strftime('%Y-%m-%d')
#                     except Exception as e:
#                         print(f"Error parsing date: {e}")

#                 # elif val=='-' or '-' in val or '.' in val or '' in val:
#                 elif val=='':
#                     print(column,">>>>>>>>")
#                     result[column] = None
                    
                
#                 else:
                    
#                     if foreign_table and parent_column and child_column==column:
#                         print("inside foreign key ")
#                         try:
#                             parent_obj=foreign_table.objects.get(**{parent_column:val})
#                             result[column]=parent_obj
#                             print(parent_obj,"-========")
#                         except Exception as e:
#                             print(e,"------------")
#                             result[column]=None
                            
#                     else:
#                         result[column] = val
#         try:
#             # print(result)
#             class_name.objects.create(**result)
#         except Exception as e:
#             print(f"Validation Error: {e}")
        
#     def csv_to_obj_without_pd(self,file_name,table_name,foreign_table=None,parent_column=None,child_column=None):
#         file_content = file_name.read()
#         file_like_object = BytesIO(file_content)
#         csv_reader = csv.reader((line.decode('utf-8', errors='replace') for line in file_like_object), delimiter=',')  
#         headers=next(csv_reader)
#         for row in csv_reader:
#             # for i, header in enumerate(headers):
#             print(row,"===========")
#             self.uploader(headers,row,table_name,foreign_table,parent_column,child_column)
                
   
#     def csv_to_obj_with_pd(self,file_name,table_name):
#         try:
#             reader = pd.read_csv(file_name,encoding='utf-8')
#             headers = reader.columns.tolist()       
            
#             for _, row in reader.iterrows():
#                 self.uploader(headers,row,table_name)


#         except:
#             pass

import pandas as pd
from io import BytesIO
import csv
import re
from datetime import datetime
from .utils import *
class CsvToObj:
    def uploader(self, headers, row, class_name, foreign_table=None, parent_column=None, child_column=None):
        result = {}
        date_patterns = [
            r'\b\d{2}\.\d{2}\.\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{2}/\d{2}/\d{4}\b',
            r'\b\d{2}-\d{2}-\d{4}\b'  # Add the new date pattern for "05-11-2023"
        ]
        for column, val in zip(headers, row):
            dates = []
            # if isinstance(val, str):
            val = str(val).strip()
            if is_float(val):
                print("inside float",val)
                val=float(val)
                result[column] = val
            if is_integer(val):
                print("inside int")
                val=int(val)
                result[column] = val
            print(column,val,type(val),"-------------------******************",result)
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

                elif val == '':
                    print(column, ">>>>>>>")
                    result[column] = None

                else:
                    print(foreign_table,parent_column,child_column,column,"----------Test",child_column == column)
                    if foreign_table and parent_column and child_column == column:
                        print("inside foreign key ")
                        try:
                            parent_obj = foreign_table.objects.get(**{id: val})
                            result[column] = parent_obj
                            print(parent_obj, "-========")
                        except Exception as e:
                            print(e, "------------")
                            result[column] = None

                    else:
                        result[column] = val
        try:
            # print(result)
            print(result,"--------------Try create ")
            class_name.objects.create(**result)
        except Exception as e:
            print(f"Validation Error: {e}")

    def xlsx_to_obj_with_pd(self, file_name, table_name, foreign_table=None, parent_column=None, child_column=None):
        print( file_name, table_name, foreign_table, parent_column, child_column)
        try:
            reader = pd.read_excel(file_name)
            headers = reader.columns.tolist()
            print(headers,"--------------------")
            for _, row in reader.iterrows():
                self.uploader(headers, row, table_name, foreign_table, parent_column, child_column)

        except Exception as e:
            print(f"Error converting XLSX to object: {e}")

# Usage example:
# csv_to_obj = CsvToObj()
# csv_to_obj.xlsx_to_obj_with_pd("your_excel_file.xlsx", YourModelName)


            
        
        