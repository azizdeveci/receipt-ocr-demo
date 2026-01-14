from flask import Flask, render_template, request
from receipt_ocr import ReceiptOCR
from parser_factory import ParserFactory
from receipt_exporter import ReceiptExporter
import os
from pathlib import Path

app = Flask(__name__)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

Path(UPLOAD_DIR).mkdir(exist_ok=True)
Path(OUTPUT_DIR).mkdir(exist_ok=True)

ocr = ReceiptOCR("/usr/bin/tesseract", "--oem 3 --psm 6")
exporter = ReceiptExporter(OUTPUT_DIR)

# 🔥 GÜN İÇİNDE OKUNAN TÜM FİŞLER
receipt_log = []   # [{receipt_no, total, market_type}]

@app.route("/", methods=["GET", "POST"])
def index():
    global receipt_log

    parsed = None
    day_total = sum(r["total"] for r in receipt_log)
    available_markets = ParserFactory.get_available_markets()
    market_names = {
        "happy_center": "Happy Center",
        "sok": "ŞOK",
        "bim": "BIM",
        "a101": "A101"
    }

    if request.method == "POST":
        market_type = request.form.get("market_type")
        file = request.files.get("receipt")
        
        if not market_type:
            return render_template(
                "index.html",
                parsed=None,
                receipts=receipt_log,
                day_total=day_total,
                available_markets=available_markets,
                market_names=market_names,
                error="Lütfen market tipini seçin!"
            )
        
        if file:
            try:
                # Parser'ı seç
                parser = ParserFactory.get_parser(market_type)
                
                # Görüntüyü kaydet
                img_path = os.path.join(UPLOAD_DIR, file.filename)
                file.save(img_path)

                # OCR ile metin çıkar
                lines = ocr.extract_lines(img_path)
                
                # Market'e özel parse işlemi
                parsed = parser.parse(lines)
                parsed["market_type"] = market_type

                # Gün sonu hesabı
                if parsed["receipt_no"] and parsed["total"] is not None:
                    receipt_log.append({
                        "receipt_no": parsed["receipt_no"],
                        "total": parsed["total"],
                        "market_type": market_type
                    })

                day_total = sum(r["total"] for r in receipt_log)
                
            except Exception as e:
                return render_template(
                    "index.html",
                    parsed=None,
                    receipts=receipt_log,
                    day_total=day_total,
                    available_markets=available_markets,
                    market_names=market_names,
                    error=f"Hata: {str(e)}"
                )

    return render_template(
        "index.html",
        parsed=parsed,
        receipts=receipt_log,
        day_total=day_total,
        available_markets=available_markets,
        market_names=market_names
    )

@app.route("/reset-day")
def reset_day():
    global receipt_log
    receipt_log = []
    return index()

if __name__ == "__main__":
    app.run(debug=True)
