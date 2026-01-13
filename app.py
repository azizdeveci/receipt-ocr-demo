from flask import Flask, render_template, request
import os, cv2

from core.receipt_ocr import ReceiptOCR
from parsers.generic_market import GenericMarketParser
from parsers.happy_center import HappyCenterParser

app = Flask(__name__)
UPLOADS = "uploads"
os.makedirs(UPLOADS, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    parsed = None

    if request.method == "POST":
        market = request.form["market"]
        file = request.files["file"]

        path = os.path.join(UPLOADS, file.filename)
        file.save(path)

        img = cv2.imread(path)
        img_bin = ReceiptOCR.preprocess(img)
        lines = ReceiptOCR.extract_lines(img_bin)

        if market == "happy":
            parsed = HappyCenterParser.parse(lines)
        else:
            parsed = GenericMarketParser.parse(lines)

    return render_template("index.html", parsed=parsed)

if __name__ == "__main__":
    app.run(debug=True)
