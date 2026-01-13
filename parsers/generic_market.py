import re

class GenericMarketParser:

    RE_DATE = re.compile(r"\b\d{2}[./-]\d{2}[./-]\d{2,4}\b")
    RE_TIME = re.compile(r"\b\d{1,2}:\d{2}(:\d{2})?\b")
    RE_PRICE = re.compile(r"\b\d{1,4}[.,]\d{2}\b")
    RE_VAT = re.compile(r"%\s*(\d{1,2})\b")

    @classmethod
    def parse(cls, lines):
        result = {
            "date": None,
            "time": None,
            "receipt_no": None,
            "products": [],
            "total": None
        }

        for l in lines:
            if not result["date"]:
                m = cls.RE_DATE.search(l)
                if m:
                    result["date"] = m.group(0).replace("/", ".")

            if not result["time"]:
                m = cls.RE_TIME.search(l)
                if m:
                    result["time"] = m.group(0)

            if not result["receipt_no"]:
                m = re.search(r"(FIŞ|FIS|FIG)\s*NO[:\s]*([0-9]+)", l.upper())
                if m:
                    result["receipt_no"] = m.group(2)

        for l in lines:
            if "TOPLAM" in l.upper():
                m = cls.RE_PRICE.search(l)
                if m:
                    result["total"] = float(m.group(0).replace(",", "."))
                    break

        for l in lines:
            if cls.RE_PRICE.search(l) and not "TOPLAM" in l.upper():
                name = cls.RE_PRICE.sub("", l)
                vat = cls.RE_VAT.search(l)
                price = cls.RE_PRICE.search(l)

                result["products"].append({
                    "name": name.strip(),
                    "vat": int(vat.group(1)) if vat else None,
                    "price": float(price.group(0).replace(",", ".")) if price else None
                })

        if not result["total"]:
            prices = [p["price"] for p in result["products"] if p["price"]]
            result["total"] = round(sum(prices), 2)

        return result
