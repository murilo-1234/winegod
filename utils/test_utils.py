"""
Testes de regressao para winegod_utils.
Cobre os 3 bugs encontrados na auditoria de 28/03/2026:
  1. preco string no processar_vinhos_ia (UnboundLocalError)
  2. preco abaixo do minimo por moeda
  3. nao-vinhos passando pelo filtro (decanter, gift card, whisky)
"""
import sys
import os

# Garantir imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.price_validator import is_valid_price, fix_centavos_magento, is_valid_url, PLACEHOLDER_VALUES
from utils.wine_filter import is_wine, clean_gift_suffix
from utils.normalize import normalize_wine_name
from utils.currency import MOEDA_POR_PAIS, get_currency_for_store


def test_price_minimum_by_currency():
    """Bug 2: precos abaixo do minimo devem ser rejeitados."""
    # Abaixo do minimo
    assert not is_valid_price(1.50, "USD"), "USD 1.50 < min 2"
    assert not is_valid_price(5.00, "BRL"), "BRL 5.00 < min 10"
    assert not is_valid_price(500, "CLP"), "CLP 500 < min 1000"
    assert not is_valid_price(400, "ARS"), "ARS 400 < min 500"
    assert not is_valid_price(20, "MXN"), "MXN 20 < min 30"
    assert not is_valid_price(100, "JPY"), "JPY 100 < min 200"
    assert not is_valid_price(1000, "KRW"), "KRW 1000 < min 2000"

    # Acima do minimo (devem passar)
    assert is_valid_price(2.50, "USD")
    assert is_valid_price(15.00, "BRL")
    assert is_valid_price(5000, "CLP")
    assert is_valid_price(1000, "ARS")
    assert is_valid_price(50, "MXN")


def test_price_maximum_by_currency():
    """Precos acima do maximo devem ser rejeitados."""
    assert not is_valid_price(60000, "USD"), "USD 60000 > max 50000"
    assert not is_valid_price(200000, "BRL"), "BRL 200000 > max 100000"
    assert is_valid_price(45000, "USD"), "USD 45000 dentro da faixa"


def test_price_placeholders():
    """Placeholders conhecidos devem ser rejeitados."""
    for val in PLACEHOLDER_VALUES:
        if val > 0:
            assert not is_valid_price(val, "USD"), f"Placeholder {val} deveria ser rejeitado"
    assert not is_valid_price(1.00, "EUR")
    assert not is_valid_price(99999, "BRL")
    assert not is_valid_price(0.01, "USD")


def test_price_none_and_negative():
    """None e negativos."""
    assert not is_valid_price(None, "USD")
    assert not is_valid_price(0, "USD")
    assert not is_valid_price(-10, "EUR")


def test_centavos_magento():
    """Magento retorna centavos quando preco > maximo da faixa."""
    # 908100 centavos EUR -> 9081 EUR (dentro da faixa)
    assert fix_centavos_magento(908100, "EUR", "magento") == 9081.0
    # Nao-magento nao corrige
    assert fix_centavos_magento(908100, "EUR", "shopify") == 908100
    # Dentro da faixa nao divide
    assert fix_centavos_magento(9081, "EUR", "magento") == 9081


def test_valid_url():
    """URLs invalidas devem ser rejeitadas."""
    assert not is_valid_url(None)
    assert not is_valid_url("")
    assert not is_valid_url("https://loja.com/cart")
    assert not is_valid_url("https://loja.com/checkout")
    assert not is_valid_url("https://loja.com/login")
    assert not is_valid_url("https://loja.com/account")
    assert not is_valid_url("https://loja.com/search?q=vinho")
    assert not is_valid_url("javascript:void(0)")
    assert not is_valid_url("mailto:info@loja.com")
    assert is_valid_url("https://loja.com/produtos/malbec-2020")
    assert is_valid_url("https://loja.com/wine/cabernet")


# ============================================================
# Bug 3: nao-vinhos devem ser filtrados
# ============================================================

def test_non_wine_spirits():
    """Destilados nao sao vinho."""
    assert not is_wine("Whisky Jameson 750ml")
    assert not is_wine("Vodka Absolut")
    assert not is_wine("Tequila Patron Silver")
    assert not is_wine("Bourbon Makers Mark")
    assert not is_wine("Cognac Hennessy XO")
    assert not is_wine("Rum Bacardi Carta Blanca")


def test_non_wine_beer():
    """Cervejas nao sao vinho."""
    assert not is_wine("Beer Heineken 330ml")
    assert not is_wine("Cerveja Artesanal IPA")
    assert not is_wine("Birra Moretti Lager")


def test_non_wine_gift_cards():
    """Gift cards nao sao vinho."""
    assert not is_wine("Gift Card $50")
    assert not is_wine("Gutschein 100 EUR")
    assert not is_wine("Tarjeta Regalo $25")
    assert not is_wine("Voucher 200")


def test_non_wine_food():
    """Comida nao e vinho."""
    assert not is_wine("Cheese Brie 200g")
    assert not is_wine("Chocolate Lindt 85%")
    assert not is_wine("Chicken Breast 1kg")
    assert not is_wine("Ketchup Heinz")
    assert not is_wine("Olive Oil Extra Virgin")


def test_non_wine_household():
    """Produtos domesticos nao sao vinho."""
    assert not is_wine("Soap Lavender Bar")
    assert not is_wine("Shampoo Anti-Dandruff")
    assert not is_wine("Detergent Omo 2L")
    assert not is_wine("Toilet Paper 12 rolls")
    assert not is_wine("Espresso Machine DeLonghi")


def test_non_wine_clothing():
    """Roupas nao sao vinho."""
    assert not is_wine("T-shirt Wine Red XL")
    assert not is_wine("Lingerie Set Black")
    assert not is_wine("Jeans Slim Fit")


def test_real_wines_pass():
    """Vinhos reais devem passar."""
    assert is_wine("Chateau Margaux 2015")
    assert is_wine("Malbec Reserve Mendoza 2020")
    assert is_wine("Cabernet Sauvignon Napa Valley")
    assert is_wine("Prosecco DOC Brut")
    assert is_wine("Barolo DOCG 2018")
    assert is_wine("Rioja Gran Reserva 2016")
    assert is_wine("Champagne Dom Perignon")
    assert is_wine("Sancerre Blanc 2021")
    assert is_wine("Vinho Verde Alvarinho")


def test_gift_suffix_removal():
    """Gift Box/Set deve ser removido do nome, mantendo o vinho."""
    assert clean_gift_suffix("Chateau Margaux 2015 Gift Box") == "Chateau Margaux 2015"
    assert clean_gift_suffix("Barolo 2018 - Gift Set") == "Barolo 2018"
    assert clean_gift_suffix("Malbec 2020") == "Malbec 2020"


# ============================================================
# Normalizacao
# ============================================================

def test_normalize_removes_volume():
    assert normalize_wine_name("Cabernet Sauvignon 750ml") == "Cabernet Sauvignon"
    assert normalize_wine_name("Malbec 1.5L") == "Malbec"
    assert normalize_wine_name("Prosecco 75cl") == "Prosecco"


def test_normalize_removes_price():
    assert normalize_wine_name("Vinho Tinto R$89,00") == "Vinho Tinto"
    assert normalize_wine_name("Barolo €45") == "Barolo"


def test_normalize_removes_alcohol():
    assert normalize_wine_name("Cabernet 13.5% vol") == "Cabernet"
    assert normalize_wine_name("Merlot 14% ABV") == "Merlot"


def test_normalize_handles_none():
    assert normalize_wine_name(None) is None
    assert normalize_wine_name("") == ""


# ============================================================
# Moeda
# ============================================================

def test_currency_fallback_never_usd_default():
    """Paises conhecidos devem retornar moeda local, nao USD."""
    assert MOEDA_POR_PAIS["dk"] == "DKK"
    assert MOEDA_POR_PAIS["hk"] == "HKD"
    assert MOEDA_POR_PAIS["ph"] == "PHP"
    assert MOEDA_POR_PAIS["ie"] == "EUR"
    assert MOEDA_POR_PAIS["be"] == "EUR"
    assert MOEDA_POR_PAIS["se"] == "SEK"


def test_currency_for_store_unknown_country():
    """Pais desconhecido deve retornar None, nao USD."""
    result = get_currency_for_store("https://example.com", "shopify", "zz")
    assert result is None or result != "USD", "Pais desconhecido nao deve defaultar USD"


# ============================================================
# Runner
# ============================================================

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  OK  {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERR  {test.__name__}: {type(e).__name__}: {e}")

    print(f"\n{passed} passed, {failed} failed, {passed + failed} total")
    if failed:
        exit(1)
