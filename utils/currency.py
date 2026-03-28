"""
Deteccao de moeda da loja via API/HTML.
Uma chamada por loja (nao por produto).
"""
import logging
import requests as _requests

logger = logging.getLogger(__name__)

# Mapeamento pais -> moeda (fallback quando API nao retorna)
MOEDA_POR_PAIS = {
    "ae": "AED", "ar": "ARS", "at": "EUR", "au": "AUD", "be": "EUR",
    "bg": "BGN", "br": "BRL", "ca": "CAD", "ch": "CHF", "cl": "CLP",
    "cn": "CNY", "co": "COP", "cz": "CZK", "de": "EUR", "dk": "DKK",
    "es": "EUR", "fi": "EUR", "fr": "EUR", "gb": "GBP", "ge": "GEL",
    "gr": "EUR", "hk": "HKD", "hr": "EUR", "hu": "HUF", "ie": "EUR",
    "il": "ILS", "in": "INR", "it": "EUR", "jp": "JPY", "kr": "KRW",
    "lu": "EUR", "md": "MDL", "mx": "MXN", "nl": "EUR", "no": "NOK",
    "nz": "NZD", "pe": "PEN", "ph": "PHP", "pl": "PLN", "pt": "EUR",
    "ro": "RON", "ru": "RUB", "se": "SEK", "sg": "SGD", "th": "THB",
    "tr": "TRY", "tw": "TWD", "us": "USD", "uy": "UYU", "za": "ZAR",
}

# Moedas validas para validacao rapida
_VALID_CURRENCIES = set(MOEDA_POR_PAIS.values())


def get_currency_shopify(base_url, session=None):
    """
    Shopify: GET /meta.json -> {"currency": "DKK"}
    Alternativa: GET /cart.json (tem "currency")
    Retorna string da moeda ou None se falhar.
    """
    sess = session or _requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0'}

    # Tentar /meta.json primeiro
    try:
        resp = sess.get(f"{base_url}/meta.json", timeout=10, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            currency = data.get("currency")
            if currency and currency.upper() in _VALID_CURRENCIES:
                return currency.upper()
    except Exception:
        pass

    # Tentar /cart.json
    try:
        resp = sess.get(f"{base_url}/cart.json", timeout=10, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            currency = data.get("currency")
            if currency and currency.upper() in _VALID_CURRENCIES:
                return currency.upper()
    except Exception:
        pass

    return None


def get_currency_woocommerce(base_url, session=None):
    """
    WooCommerce: GET /wp-json/wc/store/v1/cart -> {"totals": {"currency_code": "PLN"}}
    Alternativa: parsear moeda do primeiro produto via Store API.
    Retorna string da moeda ou None.
    """
    sess = session or _requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0'}

    # Tentar cart endpoint (nao precisa auth)
    try:
        resp = sess.get(f"{base_url}/wp-json/wc/store/v1/cart", timeout=10, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            totals = data.get("totals", {})
            currency = totals.get("currency_code")
            if currency and currency.upper() in _VALID_CURRENCIES:
                return currency.upper()
    except Exception:
        pass

    # Tentar primeiro produto
    try:
        resp = sess.get(f"{base_url}/wp-json/wc/store/v1/products?per_page=1", timeout=10, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                prices = data[0].get("prices", {})
                currency = prices.get("currency_code")
                if currency and currency.upper() in _VALID_CURRENCIES:
                    return currency.upper()
    except Exception:
        pass

    return None


def get_currency_vtex(product_json):
    """
    VTEX: o JSON do produto JA contem "currencyCode" em sellers/commertialOffer.
    So precisa ler o campo.
    """
    if not product_json:
        return None

    try:
        items = product_json.get("items", [])
        if items:
            sellers = items[0].get("sellers", [])
            if sellers:
                offer = sellers[0].get("commertialOffer", {})
                currency = offer.get("CurrencySymbolPosition")  # nem sempre tem
                # VTEX nao expoe currency_code diretamente na search API
                # Mas pode ter em ListPriceFormatted ou PriceWithoutDiscount
                formatted = offer.get("ListPriceFormatted") or offer.get("PriceWithoutDiscount") or ""
                if "R$" in str(formatted):
                    return "BRL"
                if "€" in str(formatted):
                    return "EUR"
                if "£" in str(formatted):
                    return "GBP"
                if "US$" in str(formatted) or "U$" in str(formatted):
                    return "USD"
    except Exception:
        pass

    return None


def get_currency_for_store(base_url, plataforma, pais_codigo, session=None):
    """
    Funcao principal: tenta detectar moeda via API da plataforma.
    Se falhar, usa fallback pais -> moeda.
    NUNCA retorna USD como default (a menos que pais = 'us').
    """
    detected = None
    plat = (plataforma or "").lower()

    if plat == "shopify":
        detected = get_currency_shopify(base_url, session)
    elif plat == "woocommerce":
        detected = get_currency_woocommerce(base_url, session)
    # VTEX e Tiendanube nao tem endpoint de moeda — usa fallback por pais

    if detected:
        return detected

    # Fallback: pais -> moeda
    pais = (pais_codigo or "").lower()
    moeda = MOEDA_POR_PAIS.get(pais)
    if moeda:
        return moeda

    # Pais desconhecido: retorna None, NAO USD
    logger.warning(f"Moeda desconhecida para pais={pais_codigo}, loja={base_url}")
    return None
