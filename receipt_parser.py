import re

class ReceiptParser:
    def __init__(self):
        self.re_date = re.compile(r"\b\d{2}\s\d{2}[.\s]\d{4}\b")
        self.re_time = re.compile(r"\b\d{1,2}:\d{2}\b")
        self.re_money = re.compile(r"(\d+[.,]\d{2})")
        self.re_ean = re.compile(r"^\d{11,14}$")

    def parse(self, lines):
        result = {
            "market_bilgisi": None,
            "date": None,
            "time": None,
            "receipt_no": None,
            "product_code": None,
            "product": None,
            "total": None,
            "kasiyer_bilgisi": None,
            "kasa_bilgisi": None
        }

        # MARKET
        market = []
        for l in lines:
            if "TARIH" in l.upper():
                break
            market.append(l)
        result["market_bilgisi"] = "\n".join(market)

        # DATE / TIME / NO
        for l in lines:
            if result["date"] is None:
                m = self.re_date.search(l)
                if m:
                    result["date"] = m.group(0).replace(" ", ".")
            if result["time"] is None:
                m = self.re_time.search(l)
                if m:
                    result["time"] = m.group(0)
            if "FIŞ" in l.upper():
                m = re.search(r"\b\d{3,}\b", l)
                if m:
                    result["receipt_no"] = m.group(0)

        # PRODUCT CODE
        for l in lines:
            if self.re_ean.match(l.strip()):
                result["product_code"] = l.strip()

        # PRODUCT
        for l in lines:
            if self.re_money.search(l) and l.strip().endswith(("0","1","2","3","4","5","6","7","8","9")):
                result["product"] = l

        # TOTAL
        for l in lines:
            if "TOPLAM" in l.upper():
                m = self.re_money.search(l)
                if m:
                    result["total"] = float(m.group(1).replace(",", "."))
                    break

        # KASİYER / KASA
        for l in lines:
            if "KASIYER" in l.upper():
                result["kasiyer_bilgisi"] = re.sub(r"KASIYER", "", l, flags=re.I).strip()
            if "EKU" in l.upper() and "NO" in l.upper():
                result["kasa_bilgisi"] = l

        return result
