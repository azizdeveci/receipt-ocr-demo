import re
from receipt_parser_base import BaseReceiptParser

class A101Parser(BaseReceiptParser):
    
    
    def __init__(self):
        super().__init__()
        self.re_date = re.compile(r"\b(\d{1,2})[/.\s-](\d{1,2})[/.\s-](\d{2,4})\b")
    
    def normalize_date(self, match):
        day, month, year = match.groups()
        year = "20" + year if len(year) == 2 else year
        return f"{day.zfill(2)}.{month.zfill(2)}.{year}"
    
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

        
        market = []
        for l in lines:
            if any(keyword in l.upper() for keyword in ["TARIH", "TARI", "TARİH", "DATE"]):
                break
            if l.strip():
                market.append(l)
        result["market_bilgisi"] = "\n".join(market) if market else None

        
        for l in lines:
            if result["date"] is None:
                date_match = self.re_date.search(l)
                if date_match:
                    result["date"] = self.normalize_date(date_match)
                    break

        
        result["time"] = self.extract_time(lines)

        # FİŞ NUMARASI
        for l in lines:
            if any(keyword in l.upper() for keyword in ["FIŞ", "FIS", "FİŞ", "BELGE", "FATURA"]):
                if "NO" in l.upper() or "NUMARA" in l.upper():
                    m = re.search(r"\b\d{3,}\b", l)
                    if m:
                        result["receipt_no"] = m.group(0)
                        break

        # ÜRÜN KODU
        result["product_code"] = self.extract_ean(lines)

        # ÜRÜN
        for l in lines:
            if self.re_money.search(l) and len(l.strip()) > 5:
                result["product"] = l.strip()
                break

        # TOPLAM
        for l in lines:
            if any(keyword in l.upper() for keyword in ["TOPLAM", "GENEL TOPLAM", "TOPLAM TUTAR"]):
                m = self.re_money.search(l)
                if m:
                    result["total"] = self.normalize_money(m.group(1))
                    break

        # KASİYER
        for l in lines:
            if "KASIYER" in l.upper() or "KASİYER" in l.upper():
                cleaned = re.sub(r"(?i)KASIYER[:\s]*", "", l).strip()
                if cleaned:
                    result["kasiyer_bilgisi"] = cleaned
                    break

        # KASA
        for l in lines:
            if any(keyword in l.upper() for keyword in ["KASA", "POS", "EKU", "TERMINAL"]):
                if "NO" in l.upper():
                    result["kasa_bilgisi"] = l.strip()
                    break

        return result

