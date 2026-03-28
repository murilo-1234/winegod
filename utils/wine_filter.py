"""
Filtro para separar vinhos de nao-vinhos.
Roda ANTES do insert no banco.
"""
import re

# Produtos que NUNCA sao vinho
NON_WINE_KEYWORDS = re.compile(
    r'\b(whisky|whiskey|vodka|gin(?!\s*\w*ger)|rum\b|tequila|cognac|bourbon|'
    r'beer|cerveja|birra|bier|'
    r'gift\s*card|gutschein|carte\s*cadeau|tarjeta\s*regalo|voucher|'
    r'cheese|queijo|fromage|formaggio|'
    r'chocolate|coffee|cafe\s|espresso|'
    r'ketchup|mayonnaise|mustard|vinegar|olive\s*oil|'
    r'soap|shampoo|candle|perfume|cream|lotion|'
    r't-shirt|camiseta|shirt|jeans|bra\b|panties|lingerie|'
    r'flower|flor\b|bouquet|'
    r'volleyball|basketball|soccer|dumbbell|'
    r'pet\s*food|dog\s*food|cat\s*food|'
    r'chicken|frango|beef|pork|fish\b|shrimp|'
    r'toothpaste|mouthwash|razor|detergent|'
    r'toilet\s*paper|paper\s*towel|'
    r'espresso\s*machine|coffee\s*machine|grinder)\b',
    re.IGNORECASE
)

# Sufixos que indicam embalagem (manter o vinho, remover sufixo)
GIFT_SUFFIX = re.compile(
    r'\s*[-–—]?\s*(gift\s*(box|boxed|set|tin|bag|pack|wrapped|packaging))\s*$',
    re.IGNORECASE
)


def is_wine(nome):
    """Retorna True se o produto provavelmente e vinho."""
    if not nome or len(nome.strip()) < 3:
        return False
    return not NON_WINE_KEYWORDS.search(nome)


def clean_gift_suffix(nome):
    """Remove 'Gift Box', 'Gift Set' etc do nome, mantendo o vinho."""
    return GIFT_SUFFIX.sub('', nome).strip()
