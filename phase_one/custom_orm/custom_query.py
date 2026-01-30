import pyodbc
from django.conf import settings
from phase_one.utils import transform_value
from datetime import datetime, timedelta

def get_connection():
    conn_str = 'DSN=S65D663D;UID=ODBC3CS;PWD=esl7ninp29'
    return pyodbc.connect(conn_str)

class CustomQuery:
    @staticmethod
    def execute_query(query, params=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            results = cursor.fetchall()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        return results

    @staticmethod
    def get_all_schema_names():
        query="SELECT SCHEMA_NAME FROM QSYS2.SYSSCHEMAS"
        return [schema[0] for schema in CustomQuery.execute_query(query)]
    
    @staticmethod
    def get_schema_details(schema_name):
        query = f"SELECT * FROM QSYS2.SYSSCHEMAS WHERE SCHEMA_NAME = '{schema_name}'"
        return CustomQuery.execute_query(query)
    
    @staticmethod
    def get_all_tables(schema_name):
        query = "SELECT TABLE_NAME FROM QSYS2.SYSTABLES WHERE TABLE_SCHEMA = ?"
        return CustomQuery.execute_query(query, (schema_name,))
    
    # @staticmethod
    # def all_table_data(schema_name="MOSSQRYDEV",table_name=None):
    #     query = f"SELECT * FROM {schema_name}.{table_name}"
    #     return CustomQuery.execute_query(query)

    # @staticmethod
    # def all_table_data(schema_name="MOSSQRYDEV", table_name=None, where_clause=""):
    #     query = f"SELECT * FROM {schema_name}.{table_name} {where_clause}"
    #     print(query,"************************")
    #     return CustomQuery.execute_query(query)

    @staticmethod
    def get_column_names(schema_name=settings.SCHEMA_NAME, table_name=None):
        # Query using QSYS2.SYSCOLUMNS
        query = f"""
        SELECT COLUMN_NAME
        FROM QSYS2.SYSCOLUMNS
        WHERE TABLE_SCHEMA = '{schema_name}'
        AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        # print(query, "************************")
        result = CustomQuery.execute_query(query)
        return [row[0] for row in result] if result else []



    @staticmethod
    def get_distinct_column_values(schema_name=settings.SCHEMA_NAME,table_name=None, filter_columns=[]):
        # Dictionary to store distinct values for each column
        distinct_values = {}

        for column in filter_columns:
            query = f"SELECT DISTINCT {column} FROM {schema_name}.{table_name}"
            result = CustomQuery.execute_query(query)
            if filter_columns and filter_columns[0]=="CHKLRDTE":
                distinct_values[column] = [row[0] for row in result] if result else []
            else:
                distinct_values[column] = [transform_value(row[0]) for row in result] if result else []
        # print(distinct_values,"--------------------")  # Debug: Print the query
        
        return distinct_values


    @staticmethod
    def all_table_data(schema_name=settings.SCHEMA_NAME, table_name=None,where_clause="", offset=None, limit=None,columns=None,exclude_columns=None):
        if columns is None:
            columns = CustomQuery.get_column_names(schema_name=schema_name, table_name=table_name)      
        
        if exclude_columns:
            columns = [col for col in columns if col not in exclude_columns]
        # Join columns into a string for the query
        columns_str = ", ".join(columns)
        
        # Construct the SQL query with OFFSET and LIMIT for pagination
        if offset is not None and limit is not None:
            pagination_clause = f"""
            SELECT {columns_str} FROM (
                SELECT {columns_str}, ROW_NUMBER() OVER(ORDER BY {columns[0]}) AS row_num
                FROM {schema_name}.{table_name}
                {where_clause}
            ) AS subquery
            WHERE row_num > {offset} AND row_num <= {offset + limit}
            """
        else:
            pagination_clause = f"""
            SELECT {columns_str} FROM (
                SELECT {columns_str}, ROW_NUMBER() OVER(ORDER BY {columns[0]}) AS row_num
                FROM {schema_name}.{table_name}
                {where_clause}
            ) AS subquery
            """

        return CustomQuery.execute_query(pagination_clause)
    
    def count_filtered_data(schema_name="MOSSQRYDEV", table_name=None, where_clause=""):
        # Construct the SQL query to count the number of rows that match the filter criteria
        count_query = f"""
        SELECT COUNT(*) FROM {schema_name}.{table_name}
        {where_clause}
        """
        # print(count_query, "************************")
        result = CustomQuery.execute_query(count_query)
        return result[0][0] if result else 0
    

    def get_all_data_without_pagination(schema_name=settings.SCHEMA_NAME, table_name=None,where_clause="",column_name=None):
        columns = CustomQuery.get_column_names(schema_name=schema_name, table_name=table_name)

        query = f"""
        SELECT DISTINCT {column_name}
        FROM {schema_name}.{table_name}
        {where_clause}
        """
        # print(query,"**************************")

        # Execute the query and return the result
        results = CustomQuery.execute_query(query)


        # Extract unique values from the results
        unique_values = list(set(item[0].strip() for item in results))
        return unique_values

    @staticmethod
    def sum_balance_for_data(schema_name=settings.SCHEMA_NAME, table_name=None, columns=[], sum_column=None,
                            as_column_name=None, group_by_columns=None, ids_list=[],id_column=None):
        if not ids_list:
            return 0
        
        # Join the columns and group_by_columns into comma-separated strings
        columns_str = ", ".join(columns) if columns else ""
        group_by_str = ", ".join(group_by_columns) if group_by_columns else ""
        ids_str = ", ".join(f"'{str(item).strip()}'" for item in ids_list)
        
        # Construct the SQL query  33005043
        query = f"""
        SELECT {columns_str}, SUM({sum_column}) AS {as_column_name}
        FROM {schema_name}.{table_name}
        WHERE {id_column} IN ({ids_str})
        GROUP BY {group_by_str}
        """        
        return CustomQuery.execute_query(query)

    @staticmethod
    def join_table(schema_name=settings.SCHEMA_NAME, table_one=None,where_clause="", offset=None, limit=None, columns=None):
    
        second_columns = CustomQuery.get_column_names(schema_name=schema_name, table_name=table_two)
            



        print(query)

        return CustomQuery.execute_query(query)



    @staticmethod
    def get_all():
        query = "SELECT TABLE_NAME FROM QSYS2.SYSTABLES WHERE TABLE_TYPE = 'T'"  # Adjust as needed
        return CustomQuery.execute_query(query)

    @staticmethod
    def get_by_id(record_id):
        query = "SELECT * FROM myapp_mymodel WHERE id = ?"
        return CustomQuery.execute_query(query, [record_id])

    @staticmethod
    def create(record_data):
        query = "INSERT INTO myapp_mymodel (field1, field2) VALUES (?, ?)"
        CustomQuery.execute_query(query, [record_data['field1'], record_data['field2']])


    @staticmethod
    def get_data_type(schema=settings.SCHEMA_NAME, table_name=None):
        if not table_name:
            raise ValueError("Table name must be provided.")
        query = f"SELECT COLUMN_NAME, DATA_TYPE, LENGTH, NUMERIC_SCALE FROM QSYS2.SYSCOLUMNS WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'"
        dtypes = CustomQuery.execute_query(query)
        dtypedf = pd.DataFrame.from_records(dtypes, columns=['column', 'dtype', 'precision', 'scale'])
        return dtypedf

# ====================using pandas ==================

import pandas as pd 
conn = pyodbc.connect('DSN=S65D663D;UID=ODBC3CS;PWD=esl7ninp29')

class PandsCustomQuery:
    @staticmethod
    def distinct(schema_name=settings.SCHEMA_NAME,table_name=None,column_list=[]):
        columns_str = ", ".join(column_list)
        query=f"""SELECT DISTINCT {columns_str} FROM {schema_name}.{table_name}"""
        return pd.read_sql(query,conn)
    
    @staticmethod
    def stock_pivot(schema_name=settings.SCHEMA_NAME,table_name=None,where_clause=None,warehouses=None):
        # Fetch unique warehouse names
        if warehouses is None:
            warehouses_df = PandsCustomQuery.distinct(table_name=table_name, column_list=["LWHS"])
            warehouses = warehouses_df['LWHS'].tolist()

        # Construct the CASE statements for pivoting
        case_statements = ', '.join(
            f"SUM(CASE WHEN LWHS = '{warehouse}' THEN (BAL* 1000) ELSE 0 END) AS \"{warehouse}\""
            for warehouse in warehouses
        )
                    # Construct the SQL query
        query_pivot = f"""
            SELECT 
                LPROD,
                {case_statements},
                SUM(BAL * 1000) AS GTotal
            FROM 
                {schema_name}.{table_name}
                 {"WHERE " + where_clause if where_clause else ""}
            GROUP BY 
                LPROD

            UNION ALL

            SELECT 
                'Grand Total' AS LPROD,
                {', '.join(f"SUM(CASE WHEN LWHS = '{warehouse}' THEN (BAL*1000) ELSE 0 END)" for warehouse in warehouses)},
                SUM(BAL* 1000) AS GTotal
            FROM 
                {schema_name}.{table_name}
                 {"WHERE " + where_clause if where_clause else ""}
        """
        print(query_pivot,"=-----------------------")
    
        # Execute the pivot query
        return pd.read_sql(query_pivot, conn)

    # @staticmethod
    # def openorder_pivot(schema_name=settings.SCHEMA_NAME, table_name='E3SCORDERS'):
    #     # Fetch unique warehouse names (now replaced with `CHKLRDTE`)
    #     requested_ship_date_df = PandsCustomQuery.distinct(table_name=table_name, column_list=["CHKLRDTE"])
    #     requested_ship_dates = requested_ship_date_df['CHKLRDTE'].tolist()

    #     # Construct the CASE statements for pivoting

    #     case_statements = ', '.join(
    #     f"SUM(CASE WHEN CHKLRDTE = '{transform_value(ship_date)}' THEN TOTLINEVAL ELSE 0 END)"
    #     for ship_date in requested_ship_dates
    #     )

        
    #     # Construct the SQL query
    #     query_pivot = f"""
    #         SELECT 
    #             LPROD,
    #             {case_statements},
    #             SUM(TOTLINEVAL) AS GrandTotal
    #         FROM 
    #             {schema_name}.{table_name}
    #         GROUP BY 
    #             LPROD

    #         UNION ALL

    #         SELECT 
    #             'Grand Total' AS LPROD,
    #             {', '.join(f"SUM(CASE WHEN CHKLRDTE = '{transform_value(ship_date)}' THEN TOTLINEVAL ELSE 0 END)" for ship_date in requested_ship_dates)},
    #             SUM(TOTLINEVAL) AS GrandTotal
    #         FROM 
    #             {schema_name}.{table_name}
    #     """


    #     # Execute the pivot query
    #     return pd.read_sql(query_pivot, conn)






    @staticmethod
    def openorder_pivot(schema_name=settings.SCHEMA_NAME, table_name='E3SCORDERS'):
        # Fetch unique ship dates
        requested_ship_date_df = PandsCustomQuery.distinct(table_name=table_name, column_list=["CHKLRDTE"])
        requested_ship_dates = requested_ship_date_df['CHKLRDTE'].tolist()

        # Function to calculate week_no or return 'Backlog'
        def calculate_week_no(ship_date):
            ship_date = datetime.strptime(transform_value(ship_date), "%d.%m.%Y").date()
            if ship_date > datetime.today().date():
                return f"Week{ship_date.isocalendar()[1]}"
            else:
                return "Backlog"

        # Pre-calculate week_no for each ship date
        week_nos = {transform_value(ship_date): calculate_week_no(ship_date) for ship_date in requested_ship_dates}

        # Create pivot columns based on week_no values
        pivot_columns = ', '.join(
            f"SUM(CASE WHEN CHKLRDTE = '{transform_value(date)}' THEN TOTLINEVAL ELSE 0 END) AS \"{week_nos[transform_value(date)]}\""
            for date in requested_ship_dates
        )

        # Construct the SQL query
        query_pivot = f"""
            SELECT 
                LPROD,
                {pivot_columns},
                SUM(TOTLINEVAL) AS GrandTotal
            FROM 
                {schema_name}.{table_name}
            GROUP BY 
                LPROD

            UNION ALL

            SELECT 
                'Grand Total' AS LPROD,
                {', '.join(f"SUM(CASE WHEN CHKLRDTE = '{transform_value(date)}' THEN TOTLINEVAL ELSE 0 END)" for date in requested_ship_dates)},
                SUM(TOTLINEVAL) AS GrandTotal
            FROM 
                {schema_name}.{table_name}
        """

        print(query_pivot)  # For debugging

        # Execute the pivot query
        return pd.read_sql(query_pivot, conn)


    @staticmethod
    def bom_list(schema_name=settings.SCHEMA_NAME, table_name=None,where_clause="", offset=None, limit=None):
        """
        This is a custom made function to get the BOMList
        where it has to remove the duplicate entries of BPROD-BCHLD
        """
        columns = CustomQuery.get_column_names(schema_name=schema_name, table_name=table_name)
        
        # Join columns into a string for the query
        columns_str = ", ".join(columns)
        
        # Step1: CTE for aggregation, to remove duplicates from BOM based on BPROD, BCHLD, LIDSC1 & take the MAX(BQREQ) - fix Mohammed 30-Jan-2026
        cte_clause = f"""
            WITH bom_agg AS (
                SELECT
                    BPROD,
                    BCHLD,
                    LIDSC1,
                    MAX(BQREQ) AS BQREQ
                FROM {schema_name}.{table_name}
                {where_clause}
                GROUP BY
                    BPROD, BCHLD, LIDSC1
            )
        """
        
        # Construct the SQL query with OFFSET and LIMIT for pagination
        if offset is not None and limit is not None:
            pagination_clause = f"""
            {cte_clause}
            SELECT {columns_str} FROM (
                SELECT {columns_str}, ROW_NUMBER() OVER(ORDER BY BPROD, BCHLD, LIDSC1) AS row_num
                FROM bom_agg
            ) AS subquery
            WHERE row_num > {offset} AND row_num <= {offset + limit}
            """
        else:
            pagination_clause = f"""
            {cte_clause}
            SELECT {columns_str} FROM (
                SELECT {columns_str}, ROW_NUMBER() OVER(ORDER BY BPROD, BCHLD, LIDSC1) AS row_num
                FROM bom_agg
            ) AS subquery
            """

        return CustomQuery.execute_query(pagination_clause)

    @staticmethod
    def bom_stock_pivot(schema_name=settings.SCHEMA_NAME, table_name=None, bom_table_name='BOM_TABLE'):
        # Fetch unique warehouse names
        warehouses_df = PandsCustomQuery.distinct(table_name=table_name, column_list=["LWHS"])
        warehouses = warehouses_df['LWHS'].tolist()

        # Construct the CASE statements for pivoting and multiplying BAL by 1000
        case_statements = ', '.join(
            f"SUM(CASE WHEN t.LWHS = '{warehouse}' THEN t.BAL * 1000 ELSE 0 END) AS \"{warehouse}\""
            for warehouse in warehouses
        )

        # Get BOM table columns
        bom_columns_df = CustomQuery.get_column_names(table_name=bom_table_name)
        bom_columns_str = ', '.join(f"b.{col}" for col in bom_columns_df)

        # Fix Mohammed 28-Jan-2026, to consolidate duplicate rows with same item# & item_child#
        # And Fix for Topic3 where the summation to be done basedon BCHLD and not BPROD
        # And fix instead of doing SUM(BQREQ) we are taking only single row i.e eliminating duplicates
        
        # Construct the SQL query with a JOIN to the BOM table
        query_pivot = f"""
            WITH bom_agg AS (
                SELECT
                    BPROD,
                    BCHLD,
                    LIDSC1,
                    MAX(BQREQ) AS BQREQ
                FROM
                    {schema_name}.{bom_table_name}
                GROUP BY
                    BPROD, BCHLD, LIDSC1
            )
            
            SELECT 
                {bom_columns_str},
                {case_statements},
                SUM(t.BAL * 1000) AS StockGrandTotal
            FROM 
                {schema_name}.{table_name} t
            LEFT JOIN 
                bom_agg b 
            ON 
                t.LPROD = b.BCHLD
            GROUP BY 
                {bom_columns_str}

            UNION ALL

            SELECT 
                {', '.join([f'CAST(NULL AS VARCHAR(255)) AS {col}' for col in bom_columns_df])},  -- Placeholder for BOM columns
                {', '.join(f"SUM(CASE WHEN t.LWHS = '{warehouse}' THEN t.BAL * 1000 ELSE 0 END)" for warehouse in warehouses)},
                SUM(t.BAL * 1000) AS StockGrandTotal
            FROM 
                {schema_name}.{table_name} t
        """

        # Execute the pivot query
        return pd.read_sql(query_pivot, conn)
    
    @staticmethod
    def bom_stock_pivot_child(schema_name=settings.SCHEMA_NAME, table_name=None, bom_table_name='BOM_TABLE'):
        # Fetch unique warehouse names
        warehouses_df = PandsCustomQuery.distinct(table_name=table_name, column_list=["LWHS"])
        warehouses = warehouses_df['LWHS'].tolist()

        # Construct the CASE statements for pivoting and multiplying BAL by 1000
        case_statements = ', '.join(
            f"SUM(CASE WHEN t.LWHS = '{warehouse}' THEN t.BAL * 1000 ELSE 0 END) AS \"{warehouse}\""
            for warehouse in warehouses
        )

        # Get BOM table columns
        bom_columns_df = CustomQuery.get_column_names(table_name=bom_table_name)
        bom_columns_str = ', '.join(f"b.{col}" for col in bom_columns_df)

        # Construct the SQL query with a JOIN to the BOM table
        query_pivot = f"""
            SELECT 
                {bom_columns_str},
                {case_statements},
                SUM(t.BAL * 1000) AS ChildStockGrandTotal
            FROM 
                {schema_name}.{table_name} t
            LEFT JOIN 
                {schema_name}.{bom_table_name} b 
            ON 
                t.LPROD = b.BCHLD
            GROUP BY 
                {bom_columns_str}

            UNION ALL

            SELECT 
                {', '.join([f'CAST(NULL AS VARCHAR(255)) AS {col}' for col in bom_columns_df])},  -- Placeholder for BOM columns
                {', '.join(f"SUM(CASE WHEN t.LWHS = '{warehouse}' THEN t.BAL * 1000 ELSE 0 END)" for warehouse in warehouses)},
                SUM(t.BAL * 1000) AS ChildStockGrandTotal
            FROM 
                {schema_name}.{table_name} t
        """

        # Execute the pivot query
        return pd.read_sql(query_pivot, conn)


    @staticmethod
    def count_records(schema_name=settings.SCHEMA_NAME, table_name=None):
        if not table_name:
            raise ValueError("Table name must be provided.")
        count_query = f"""SELECT COUNT(*) FROM {schema_name}.{table_name}"""
        # print(count_query,"---------------------")
        result = CustomQuery.execute_query(count_query)
        return result[0][0] if result else 0




