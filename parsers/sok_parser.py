import re
from receipt_parser_base import BaseReceiptParser

class SokParser(BaseReceiptParser):
    """ŞOK market fişleri için parser"""
    
    def __init__(self):
        super().__init__()
        # ŞOK'ta tarih formatı: DD/MM/YYYY veya DD.MM.YYYY
        self.re_date = re.compile(r"\b(\d{1,2})[/.\s-](\d{1,2})[/.\s-](\d{2,4})\b")
    
    def normalize_date(self, match):
        """Tarihi normalize eder"""
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

        # MARKET BİLGİSİ - "TARI H:" veya "TARIH" ile bitiyor
        market = []
        for l in lines:
            if "TARI" in l.upper() or "TARIH" in l.upper():
                break
            if l.strip():
                market.append(l)
        result["market_bilgisi"] = "\n".join(market) if market else None

        # TARİH - "TARI H:25/03/2019" formatında
        for l in lines:
            if result["date"] is None:
                date_match = self.re_date.search(l)
                if date_match:
                    result["date"] = self.normalize_date(date_match)
                    break

        # SAAT - "SAAT:19:18" formatında
        result["time"] = self.extract_time(lines)

        # FİŞ NUMARASI - "Fig NO: 307" veya "FIŞ NO:" formatında
        for l in lines:
            if any(keyword in l.upper() for keyword in ["FIG", "FIŞ", "FIS"]):
                if "NO" in l.upper():
                    m = re.search(r"\b\d{3,}\b", l)
                    if m:
                        result["receipt_no"] = m.group(0)
                        break

        # ÜRÜN KODU
        result["product_code"] = self.extract_ean(lines)

        # ÜRÜN - İlk ürün satırı
        for l in lines:
            if self.re_money.search(l) and len(l.strip()) > 5:
                # ŞOK'ta ürün formatı: "PIYALE INCE UZUN 500 %8 *1,35"
                if "%" in l or "*" in l or self.re_money.search(l):
                    result["product"] = l.strip()
                    break

        # TOPLAM - "TOPLAM" veya en büyük para değeri
        for l in lines:
            if "TOPLAM" in l.upper():
                m = self.re_money.search(l)
                if m:
                    result["total"] = self.normalize_money(m.group(1))
                    break
        
        # Eğer toplam bulunamazsa, en büyük para değerini al
        if result["total"] is None:
            amounts = []
            for l in lines:
                for match in self.re_money.finditer(l):
                    amount = self.normalize_money(match.group(1))
                    if amount:
                        amounts.append(amount)
            if amounts:
                result["total"] = max(amounts)

        # KASİYER - "ASİ YER" veya "KASIYER" (OCR hatası olabilir)
        for l in lines:
            if any(keyword in l.upper() for keyword in ["KASIYER", "ASİ YER", "KAS YER"]):
                cleaned = re.sub(r"(?i)(KASIYER|ASİ YER|KAS YER)[:\s]*", "", l).strip()
                if cleaned:
                    result["kasiyer_bilgisi"] = cleaned
                    break

        # KASA - "RANS NO" veya "KASA NO"
        for l in lines:
            if any(keyword in l.upper() for keyword in ["RANS NO", "KASA NO", "POS NO"]):
                result["kasa_bilgisi"] = l.strip()
                break

        return result

