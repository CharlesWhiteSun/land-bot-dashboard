import sqlite3
import pandas as pd
from contextlib import closing

DB_PATH = 'ngui/database/real_estate.sqlite'

def query_distribution_data(year, city, building_type=None, house_status=None) -> pd.DataFrame:
    with closing(sqlite3.connect(DB_PATH)) as conn:
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
    
def query_avg_price(city: str, trade_object: str, year: str, house_type: str) -> pd.DataFrame:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        sql = f'''
            SELECT 
                SUBSTR(`交易年月日`, 1, 4) || '-' || SUBSTR(`交易年月日`, 5, 2) as ym,
                ROUND(AVG(`總價元`) / 10000.0, 1) as avg_price_million
            FROM `{city}`
            WHERE 1=1
                AND `交易標的` = ?
                AND `交易年` = ?
                AND `屋況` = ?
            GROUP BY ym
            ORDER BY ym
        '''
        params = (trade_object, year, house_type)
        df = pd.read_sql_query(sql, conn, params=params)
        return df
