import re
from receipt_parser_base import BaseReceiptParser

class HappyCenterParser(BaseReceiptParser):
    """Happy Center market fişleri için parser"""
    
    def __init__(self):
        super().__init__()
        self.re_date = re.compile(r"\b\d{2}\s\d{2}[.\s]\d{4}\b")
    
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

        # MARKET BİLGİSİ
        market = []
        for l in lines:
            if "TARIH" in l.upper():
                break
            market.append(l)
        result["market_bilgisi"] = "\n".join(market) if market else None

        # TARİH
        for l in lines:
            if result["date"] is None:
                m = self.re_date.search(l)
                if m:
                    result["date"] = m.group(0).replace(" ", ".")
                    break

        # SAAT
        result["time"] = self.extract_time(lines)

        # FİŞ NUMARASI
        for l in lines:
            if "FIŞ" in l.upper():
                m = re.search(r"\b\d{3,}\b", l)
                if m:
                    result["receipt_no"] = m.group(0)
                    break

        # ÜRÜN KODU
        result["product_code"] = self.extract_ean(lines)

        # ÜRÜN
        for l in lines:
            if self.re_money.search(l) and l.strip().endswith(("0","1","2","3","4","5","6","7","8","9")):
                result["product"] = l
                break

        # TOPLAM
        for l in lines:
            if "TOPLAM" in l.upper():
                m = self.re_money.search(l)
                if m:
                    result["total"] = self.normalize_money(m.group(1))
                    break

        # KASİYER
        for l in lines:
            if "KASIYER" in l.upper():
                result["kasiyer_bilgisi"] = re.sub(r"KASIYER", "", l, flags=re.I).strip()
                break

        # KASA
        for l in lines:
            if "EKU" in l.upper() and "NO" in l.upper():
                result["kasa_bilgisi"] = l
                break

        return result

