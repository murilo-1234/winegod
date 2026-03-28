"""
Normalizacao de nomes de vinho.
Pipeline: unescape HTML -> remover volume -> remover preco -> limpar.
"""
import html
import re
import unicodedata

# Volume patterns
VOLUME_PATTERN = re.compile(
    r'\s*[-–—]?\s*\(?\s*\d+(?:[.,]\d+)?\s*'
    r'(?:ml|cl|l|lt|ltr|litre|liter|litro|oz|fl\.?\s*oz)\s*\)?\s*',
    re.IGNORECASE
)

# Price patterns em qualquer moeda
PRICE_PATTERN = re.compile(
    r'(?:R\$|€|\$|£|¥|₩|kr|zł|Kč|Ft|lei|₺|₽|₪|AED|BRL|EUR|USD|GBP)\s*'
    r'\d+[.,]?\d*(?:\s*(?:por|per|each|unidade|unit))?',
    re.IGNORECASE
)

# Alcohol percentage
ALCOHOL_PATTERN = re.compile(
    r'\s*[-–—]?\s*\d+[.,]?\d*\s*%\s*(?:vol|alc|abv)?\s*\.?\s*',
    re.IGNORECASE
)


def normalize_wine_name(nome):
    """
    Pipeline completo de normalizacao:
    1. HTML unescape
    2. Remove volume (750ml, 75cl, 1.5L)
    3. Remove preco (R$89,00)
    4. Remove teor alcoolico (13.5% vol)
    5. Limpa espacos e pontuacao trailing
    """
    if not nome:
        return nome

    # 1. HTML entities
    nome = html.unescape(nome)

    # 2. Volume
    nome = VOLUME_PATTERN.sub(' ', nome)

    # 3. Preco
    nome = PRICE_PATTERN.sub(' ', nome)

    # 4. Alcool
    nome = ALCOHOL_PATTERN.sub(' ', nome)

    # 5. Limpar
    nome = re.sub(r'\s+', ' ', nome).strip()
    nome = nome.strip('-–— .,;:')

    return nome


def normalize_for_search(nome):
    """
    Normalizacao para busca/dedup.
    MANTEM caracteres nao-latinos (japones, russo, coreano, etc).
    Remove apenas acentos combinantes (diacriticos).
    """
    if not nome:
        return nome

    nome = nome.lower().strip()

    # Remove acentos combinantes (e -> e) mas MANTEM kanji, cirillico, etc
    nome = unicodedata.normalize('NFKD', nome)
    nome = ''.join(c for c in nome if not unicodedata.combining(c))

    # Remove pontuacao mas MANTEM letras de qualquer script + numeros + espacos
    nome = re.sub(r'[^\w\s]', '', nome, flags=re.UNICODE)

    # Normaliza espacos
    nome = re.sub(r'\s+', ' ', nome).strip()

    return nome
