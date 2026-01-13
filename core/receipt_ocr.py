import cv2
import pytesseract
import pandas as pd
import re

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
CFG_OCR = r"--oem 3 --psm 6 -c preserve_interword_spaces=1"

class ReceiptOCR:

    @staticmethod
    def preprocess(img):
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, 18, 7, 21)
        return cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 9
        )

    @staticmethod
    def extract_lines(img_bin):
        data = pytesseract.image_to_data(
            img_bin,
            lang="tur+eng",
            config=CFG_OCR,
            output_type=pytesseract.Output.DATAFRAME
        )

        data = data.dropna(subset=["text"])
        data["conf"] = pd.to_numeric(data["conf"], errors="coerce").fillna(-1)
        data = data[data["conf"] > 35]

        lines = []
        for (_, _, _), g in data.groupby(["block_num", "par_num", "line_num"]):
            g = g.sort_values("left")
            line = " ".join(g.text.tolist())
            line = re.sub(r"\s+", " ", line).strip()
            if line:
                lines.append(line)

        # tekrarları temizle
        uniq, seen = [], set()
        for l in lines:
            key = re.sub(r"[^A-Z0-9]", "", l.upper())
            if key not in seen:
                seen.add(key)
                uniq.append(l)

        return uniq
