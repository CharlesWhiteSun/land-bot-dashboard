import sqlite3
import pandas as pd
from contextlib import closing
from typing import Optional, List

from utils.logger import *

import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wptftadkiqfvtxbjmusr.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_Yt1W1aogrXlc7nlRosyacw_pZvdaUl2")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def query_distribution_data(
    year, 
    city, 
    building_type=None, 
    house_status=None, 
    remove_outliers=False,
    remove_zero=False,
    limit_under_100m=False
) -> pd.DataFrame:
    
    # 開始 build 查詢
    query = supabase.table(city).select("*")
    
    # 年份條件
    if "~" not in year:
        query = query.eq("交易年", year)
    else:
        # 假設你要找 "< year"
        yr = year.replace("~", "")
        query = query.lt("交易年", yr)

    if building_type:
        query = query.eq("分類", building_type)

    if house_status:
        query = query.eq("屋況", house_status)

    try:
        # 執行查詢
        resp = query.execute()
        data = resp.data if resp and hasattr(resp, 'data') else []

        df = pd.DataFrame(data)
        if df.empty:
            return df

        # 處理 price 欄位
        if "建物總價萬元" in df.columns:
            df["price"] = pd.to_numeric(df["建物總價萬元"], errors="coerce")
        else:
            # fallback 若欄位不同
            df["price"] = pd.to_numeric(df.get("建物總價萬元", None), errors="coerce")

        # 過濾掉沒有 price
        df = df.dropna(subset=["price"])

        if remove_zero:
            df = df[df["price"] > 0]

        if limit_under_100m:
            df = df[df["price"] < 10000]

        if remove_outliers and not df.empty:
            quantile_val = 1 - remove_outliers / 100  # 例如 1% -> 0.99
            upper_bound = df["price"].quantile(quantile_val)
            df = df[df["price"] <= upper_bound]
            
        return df
    
    except Exception as e:
        log_warning(f"[Supabase] 查詢分佈圖 Error: {e}")
        return pd.DataFrame()
    

def query_multi_city_3d_data(
    cities: list[str], 
    year: str, 
    type_value=None, 
    status_value=None, 
    remove_outliers=False,
    remove_zero=False,
    limit_under_100m=False
) -> pd.DataFrame:

    all_data = []
    
    for city in cities:
        try:
            # 設定要撈的欄位
            query = (
                supabase
                .table(city)
                .select("建物坪數, 房齡, 鄉鎮市區, 建物型態, 主要用途, 屋況, 建物總價萬元")
                .eq("交易年", year)
            )

            if type_value:
                query = query.eq("分類", type_value)

            if status_value:
                query = query.eq("屋況", status_value)

            resp = query.execute()
            data = resp.data if resp and hasattr(resp, "data") else []
            if not data:
                continue

            df = pd.DataFrame(data)
            df.rename(columns={"建物總價萬元": "price"}, inplace=True)

            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df = df.dropna(subset=["price"])

            if remove_zero:
                df = df[df["price"] > 0]

            if limit_under_100m:
                df = df[df["price"] < 10000]

            if remove_outliers and not df.empty:
                quantile_val = 1 - remove_outliers / 100  # 例如 1% -> 0.99
                upper_bound = df["price"].quantile(quantile_val)
                df = df[df["price"] <= upper_bound]

            df["縣市"] = city  # 加上縣市欄位

            all_data.append(df)

        except Exception as e:
            log_warning(f"[Supabase] 查詢 3D 數據失敗（{city}）: {e}")

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def query_avg_price(
    city: str, 
    trade_object: str | None, 
    year: str, 
    house_type: str | None
) -> pd.DataFrame:
    
    try:
        query = (
            supabase.table(city)
            .select("交易年月日, 建物總價萬元")
            .eq("交易年", year)
        )

        if trade_object:
            query = query.eq("交易標的", trade_object)

        if house_type:
            query = query.eq("屋況", house_type)

        resp = query.execute()
        data = resp.data if resp and hasattr(resp, "data") else []

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        if df.empty or "交易年月日" not in df.columns or "建物總價萬元" not in df.columns:
            return pd.DataFrame()

        # 年月解析（假設格式為 'YYYYMMDD'）
        def extract_ym(trade_date_str: str) -> Optional[str]:
            try:
                if not trade_date_str or len(trade_date_str) < 6:
                    return None
                return f"{trade_date_str[:4]}-{trade_date_str[4:6]}"
            except Exception:
                return None

        df["ym"] = df["交易年月日"].apply(extract_ym)
        df = df.dropna(subset=["ym"])

        df["建物總價萬元"] = pd.to_numeric(df["建物總價萬元"], errors="coerce")
        df = df.dropna(subset=["建物總價萬元"])

        # 計算平均，四捨五入
        df_grouped = (
            df.groupby("ym")["建物總價萬元"]
            .mean()
            .round(0)
            .reset_index()
            .rename(columns={"建物總價萬元": "avg_price_million"})
            .sort_values("ym")
        )

        return df_grouped

    except Exception as e:
        log_warning(f"[Supabase] 查詢不動產年度趨勢圖 Error: {e}")
        return pd.DataFrame()


def query_multi_year_price(
    city: str, 
    trade_object: str | None, 
    years: list[str], 
    house_type: str | None
) -> pd.DataFrame:
    
    try:
        # 查詢必要欄位
        query = supabase.table(city).select("交易年月日, 建物總價萬元, 交易年")

        if years:
            query = query.in_("交易年", years)
        if trade_object:
            query = query.eq("交易標的", trade_object)
        if house_type:
            query = query.eq("屋況", house_type)

        resp = query.execute()
        data = resp.data if resp and hasattr(resp, "data") else []

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # 欄位檢查
        if "交易年月日" not in df.columns or "建物總價萬元" not in df.columns:
            return pd.DataFrame()

        # 時間解析
        def extract_year_month(date_str):
            if not date_str or len(date_str) < 6:
                return None, None
            return date_str[:4], date_str[4:6]

        df["year"], df["month"] = zip(*df["交易年月日"].map(extract_year_month))
        df = df.dropna(subset=["year", "month"])

        df["建物總價萬元"] = pd.to_numeric(df["建物總價萬元"], errors="coerce")
        df = df.dropna(subset=["建物總價萬元"])

        df["month"] = df["month"].astype(int)

        # 平均並排序
        grouped = (
            df.groupby(["year", "month"])["建物總價萬元"]
            .mean()
            .round(0)
            .reset_index()
            .rename(columns={"建物總價萬元": "avg_price_million"})
            .sort_values(["year", "month"], ascending=[False, True])
        )

        return grouped

    except Exception as e:
        log_warning(f"[Supabase] 查詢多年度趨勢圖 Error: {e}")
        return pd.DataFrame()


def query_multi_city_price_with_age(
    cities: list[str], year: str,
    trade_object: str | None,
    house_type: str | None,
    remove_outliers=0,
    use_median=False,
    remove_zero=False,
    limit_under_100m=False
) -> pd.DataFrame:
    
    dfs = []

    for city in cities:
        try:
            # 基礎查詢欄位
            query = supabase.table(city).select("交易年月日, 房齡, 建物總價萬元, 交易標的, 屋況")
            query = query.eq("交易年", year)

            # 交易標的與屋況條件
            if trade_object:
                query = query.eq("交易標的", trade_object)
            if house_type:
                query = query.eq("屋況", house_type)

            resp = query.execute()
            data = resp.data if hasattr(resp, "data") else []

            if not data:
                continue

            df = pd.DataFrame(data)
            if df.empty:
                continue

            # 清洗與欄位處理
            df["房齡"] = pd.to_numeric(df["房齡"], errors="coerce")
            df["price"] = pd.to_numeric(df["建物總價萬元"], errors="coerce")

            # 排除空值或不合法房齡
            df = df.dropna(subset=["房齡", "price"])
            df = df[df["房齡"].apply(lambda x: isinstance(x, (int, float)) and x >= 0)]

            # 解析月份
            def extract_month(date_str):
                if not date_str or len(date_str) < 6:
                    return None
                return int(date_str[4:6])

            df["month"] = df["交易年月日"].apply(extract_month)
            df = df.dropna(subset=["month"])

            # 條件過濾
            if remove_zero:
                df = df[df["price"] > 0]

            if limit_under_100m:
                df = df[df["price"] < 10000]

            if remove_outliers > 0 and not df.empty:
                quantile_val = 1 - remove_outliers / 100  # 例如 1% -> 0.99
                upper_bound = df["price"].quantile(quantile_val)
                df = df[df["price"] <= upper_bound]

            if df.empty:
                continue

            # 聚合
            agg_func = "median" if use_median else "mean"
            df_grouped = (
                df.groupby(["month", "房齡"])["price"]
                .agg(agg_func)
                .reset_index()
                .rename(columns={"price": "avg_price_million", "房齡": "house_age"})
            )
            df_grouped["city"] = city
            dfs.append(df_grouped)

        except Exception as e:
            log_warning(f"[Supabase] 查詢房齡價格錯誤({city}): {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()

