import json
import pandas as pd
from pathlib import Path

class ReceiptExporter:
    def __init__(self, out_dir):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)

    def save_all(self, data):
        with open(self.out_dir / "receipt.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        df = pd.DataFrame([data])
        df.to_csv(self.out_dir / "receipt.csv", index=False, encoding="utf-8-sig")
        df.to_excel(self.out_dir / "receipt.xlsx", index=False)
