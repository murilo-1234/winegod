"""
Validacao de precos antes de gravar no banco.
"""

FAIXA_PRECO = {
    "USD": (2, 50000), "EUR": (2, 50000), "GBP": (2, 40000),
    "BRL": (10, 100000), "ARS": (500, 5000000), "CLP": (1000, 10000000),
    "MXN": (30, 500000), "COP": (5000, 50000000), "PEN": (10, 50000),
    "UYU": (50, 500000), "AUD": (3, 50000), "NZD": (3, 50000),
    "CAD": (3, 50000), "CHF": (2, 50000), "JPY": (200, 5000000),
    "KRW": (2000, 50000000), "CNY": (10, 500000), "HKD": (10, 500000),
    "SGD": (3, 50000), "TWD": (50, 500000), "THB": (50, 500000),
    "INR": (100, 5000000), "ZAR": (20, 500000), "SEK": (20, 500000),
    "NOK": (20, 500000), "DKK": (20, 500000), "PLN": (5, 100000),
    "CZK": (20, 500000), "HUF": (200, 5000000), "RON": (5, 100000),
    "TRY": (10, 500000), "ILS": (10, 100000), "AED": (5, 200000),
    "BGN": (3, 100000), "GEL": (3, 50000), "MDL": (10, 100000),
    "PHP": (50, 500000), "RUB": (50, 5000000),
}

# Placeholders conhecidos
PLACEHOLDER_VALUES = {0, 0.01, 0.99, 1.00, 9999, 99999, 99999.99, 999999}


def is_valid_price(preco, moeda):
    """
    Retorna True se o preco e valido para a moeda.
    Rejeita: None, 0, negativos, placeholders, fora da faixa.
    """
    if preco is None or preco <= 0:
        return False
    if preco in PLACEHOLDER_VALUES:
        return False
    faixa = FAIXA_PRECO.get(moeda)
    if faixa:
        minimo, maximo = faixa
        if preco < minimo or preco > maximo:
            return False
    return True


def fix_centavos_magento(preco, moeda, plataforma):
    """
    Magento retorna precos em centavos (9081 = 90.81).
    Se plataforma = magento E preco > faixa_max, divide por 100.
    """
    if plataforma and 'magento' in plataforma.lower():
        faixa = FAIXA_PRECO.get(moeda, (1, 100000))
        if preco > faixa[1]:
            return preco / 100
    return preco


def is_valid_url(url):
    """
    Rejeita URLs que nao sao paginas de produto.
    """
    if not url:
        return False
    bad_patterns = ['/cart', '/checkout', '/login', '/account', '/search',
                    'javascript:', 'mailto:', '#']
    url_lower = url.lower()
    for pattern in bad_patterns:
        if pattern in url_lower:
            return False
    return True
