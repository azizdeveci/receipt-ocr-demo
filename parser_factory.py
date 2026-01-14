from parsers.happy_center_parser import HappyCenterParser
from parsers.sok_parser import SokParser
from parsers.bim_parser import BimParser
from parsers.a101_parser import A101Parser

class ParserFactory:
    """Market tipine göre parser oluşturur"""
    
    PARSERS = {
        "happy_center": HappyCenterParser,
        "sok": SokParser,
        "bim": BimParser,
        "a101": A101Parser
    }
    
    @staticmethod
    def get_parser(market_type):
        """Market tipine göre parser döndürür"""
        parser_class = ParserFactory.PARSERS.get(market_type.lower())
        if parser_class:
            return parser_class()
        raise ValueError(f"Bilinmeyen market tipi: {market_type}")
    
    @staticmethod
    def get_available_markets():
        """Kullanılabilir market listesini döndürür"""
        return list(ParserFactory.PARSERS.keys())

