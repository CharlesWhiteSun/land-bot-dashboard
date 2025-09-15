import sqlite3
import pandas as pd
from contextlib import closing

def query_city_data(year, city, building_type=None, house_status=None) -> pd.DataFrame:
    with closing(sqlite3.connect('ngui/database/real_estate.sqlite')) as conn:
        query = f"""
            SELECT * 
            FROM '{city}'
            WHERE 1=1
        """

        params = []

        if '~' not in year:
            query += " AND 交易年 = ?"
            params.append(year)
        else:
            query += " AND 交易年 < ?"
            params.append(year.replace('~', ''))

        if building_type:
            query += " AND 分類 = ?"
            params.append(building_type)

        if house_status:
            query += " AND 屋況 = ?"
            params.append(house_status)

        df = pd.read_sql_query(query, conn, params=params)
        return df
