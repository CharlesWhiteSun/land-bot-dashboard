import sqlite3
import pandas as pd
from contextlib import closing

DB_PATH = 'ngui/database/real_estate.sqlite'

def query_distribution_data(year, city, building_type=None, house_status=None, remove_outliers=False) -> pd.DataFrame:
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

        try:
            df = pd.read_sql_query(query, conn, params=params)

            if remove_outliers and not df.empty:
                quantile_val = 1 - remove_outliers / 100  # 例如 1% -> 0.99
                upper_bound = df["建物總價萬元"].quantile(quantile_val)
                df = df[df["建物總價萬元"] <= upper_bound]
                
            return df
        except Exception as e:
            print(f"[SQL] 查詢不動產分佈圖 Error: {e}")
            return df
    

def query_multi_city_3d_data(cities: list[str], year: str, type_value=None, status_value=None, remove_outliers=False) -> pd.DataFrame:
    from contextlib import closing
    import sqlite3
    import pandas as pd

    all_data = []
    with closing(sqlite3.connect(DB_PATH)) as conn:
        for city in cities:
            query = f"""
                SELECT 
                    '{city}' as 縣市,
                    建物坪數, 建物總價萬元, 房齡,
                    鄉鎮市區, 建物型態, 主要用途, 屋況
                FROM "{city}"
                WHERE 交易年 = ?
            """
            params = [year]

            if type_value:
                query += " AND 分類 = ?"
                params.append(type_value)

            if status_value:
                query += " AND 屋況 = ?"
                params.append(status_value)

            df = pd.read_sql_query(query, conn, params=params)

            if remove_outliers and not df.empty:
                upper_bound = df["建物總價萬元"].quantile(0.99)
                df = df[df["建物總價萬元"] <= upper_bound]

            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def query_avg_price(city: str, trade_object: str | None, year: str, house_type: str | None) -> pd.DataFrame:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        sql = f'''
            SELECT 
                SUBSTR(`交易年月日`, 1, 4) || '-' || SUBSTR(`交易年月日`, 5, 2) as ym,
                AVG(`建物總價萬元`) as avg_price_million
            FROM `{city}`
            WHERE 1=1
                AND `交易年` = ?
        '''
        params = [year]

        if trade_object:
            sql += " AND `交易標的` = ?"
            params.append(trade_object)

        if house_type:
            sql += " AND `屋況` = ?"
            params.append(house_type)

        sql += '''
            GROUP BY ym
            ORDER BY ym
        '''

        df = pd.read_sql_query(sql, conn, params=params)
        try:
            df = pd.read_sql_query(sql, conn, params=params)
            return df
        except Exception as e:
            print(f"[SQL] 查詢不動產年度趨勢圖 Error: {e}")
            return df


def query_multi_year_price(city: str, trade_object: str | None, years: list[str], house_type: str | None) -> pd.DataFrame:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        placeholders = ','.join(['?'] * len(years))
        sql = f'''
            SELECT 
                SUBSTR(`交易年月日`, 1, 4) as year,
                CAST(SUBSTR(`交易年月日`, 5, 2) AS INTEGER) as month,
                AVG(`建物總價萬元`) as avg_price_million
            FROM `{city}`
            WHERE 1=1
                AND `交易年` IN ({placeholders})
        '''
        params = years

        if trade_object:  # 有選擇交易標的時才加條件
            sql += " AND `交易標的` = ?"
            params.append(trade_object)

        if house_type:  # 有選擇屋況時才加條件
            sql += " AND `屋況` = ?"
            params.append(house_type)

        sql += '''
            GROUP BY year, month
            ORDER BY year DESC, month
        '''
        try:
            df = pd.read_sql_query(sql, conn, params=params)
            return df
        except Exception as e:
            print(f"[SQL] 查詢複合年度比較趨勢圖 Error: {e}")
            return df


def query_multi_city_price_with_age(cities: list[str], year: str, trade_object: str | None, house_type: str | None, remove_outliers=False) -> pd.DataFrame:
    dfs = []
    with closing(sqlite3.connect(DB_PATH)) as conn:
        for city in cities:
            sql = f'''
                SELECT 
                    '{city}' AS city,
                    CAST(SUBSTR(`交易年月日`, 5, 2) AS INTEGER) AS month,
                    CAST(`房齡` AS INTEGER) AS house_age,
                    AVG(`建物總價萬元`) as avg_price_million
                FROM `{city}`
                WHERE `交易年` = ?
                  AND `房齡` NOT NULL AND `房齡` != '' AND `房齡` != '見其他登記事項'
            '''
            params = [year]

            if trade_object:
                sql += " AND `交易標的` = ?"
                params.append(trade_object)

            if house_type:
                sql += " AND `屋況` = ?"
                params.append(house_type)

            sql += '''
                GROUP BY month, house_age
                ORDER BY 房齡, 建物總價萬元
            '''

            try:
                df = pd.read_sql_query(sql, conn, params=params)

                if remove_outliers and not df.empty:
                    quantile_val = 1 - remove_outliers / 100  # 例如 1% -> 0.99
                    upper_bound = df["avg_price_million"].quantile(quantile_val)
                    df = df[df["avg_price_million"] <= upper_bound]

                df = df.dropna(subset=['house_age'])
                df['house_age'] = df['house_age'].astype(int)
                dfs.append(df)
            except Exception as e:
                print(f"[SQL] 查詢屋齡3D趨勢圖錯誤({city}): {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()
