import json
import pandas as pd
from pathlib import Path

class ReceiptExporter:

    @staticmethod
    def export(data, out_dir="outputs"):
        Path(out_dir).mkdir(exist_ok=True)

        with open(f"{out_dir}/receipt.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        rows = []
        for p in data["products"]:
            rows.append({
                "date": data["date"],
                "receipt_no": data["receipt_no"],
                "product": p["name"],
                "price": p["price"],
                "total": data["total"]
            })

        df = pd.DataFrame(rows)
        df.to_csv(f"{out_dir}/receipt.csv", index=False, encoding="utf-8-sig")
        df.to_excel(f"{out_dir}/receipt.xlsx", index=False)
