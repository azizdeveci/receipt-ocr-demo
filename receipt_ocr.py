import cv2
import pytesseract
import re

class ReceiptOCR:
    def __init__(self, tesseract_path, ocr_config):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.ocr_config = ocr_config

    def preprocess(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, 18, 7, 21)
        return gray

    def extract_lines(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise RuntimeError("Görsel okunamadı")

        gray = self.preprocess(img)

        data = pytesseract.image_to_data(
            gray,
            lang="tur+eng",
            config=self.ocr_config,
            output_type=pytesseract.Output.DATAFRAME
        )

        data = data.dropna(subset=["text"])
        data = data[data.conf.astype(int) > 35]

        lines = []
        for _, g in data.groupby(["block_num", "par_num", "line_num"]):
            line = " ".join(g.sort_values("left").text.tolist())
            line = re.sub(r"\s+", " ", line).strip()
            if line:
                lines.append(line)

        return list(dict.fromkeys(lines))
