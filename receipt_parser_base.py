import re
from abc import ABC, abstractmethod

class BaseReceiptParser(ABC):
    """Tüm market parser'ları için base sınıf"""
    
    def __init__(self):
        self.re_time = re.compile(r"\b(\d{1,2}):(\d{2})\b")
        self.re_money = re.compile(r"(\d{1,3}(?:[.,]\d{3})*[.,]\d{2}|\d+[.,]\d{2})")
        self.re_ean = re.compile(r"^\d{11,14}$")
    
    @abstractmethod
    def parse(self, lines):
    
        pass
    
    def extract_time(self, lines):
        
        for l in lines:
            time_match = self.re_time.search(l)
            if time_match:
                return time_match.group(0)
        return None
    
    def extract_ean(self, lines):
        
        for l in lines:
            if self.re_ean.match(l.strip()):
                return l.strip()
        return None
    
    def normalize_money(self, money_str):
        
        if not money_str:
            return None
        try:
            # Binlik ayırıcıları kaldır, virgülü noktaya çevir
            normalized = money_str.replace(".", "").replace(",", ".")
            return float(normalized)
        except ValueError:
            return None

