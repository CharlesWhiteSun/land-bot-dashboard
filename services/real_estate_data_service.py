from pathlib import Path
import pandas as pd

class RealEstateDataService:
    def __init__(self, data_dir: str = "./data/clean"):
        self.data_dir = Path(data_dir)

    def load_city_data(self, city: str) -> pd.DataFrame:
        file_path = self.data_dir / f"{city}_clean.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"找不到資料檔案：{file_path.as_posix()}")  # ⭐ 統一為 POSIX 格式

        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(f"{city} 的資料為空")
        if "總價元" not in df.columns:
            raise ValueError("缺少必要欄位：總價元")

        return df
