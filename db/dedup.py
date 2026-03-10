"""Deduplicação de vinhos — hash e normalização."""
import hashlib
import re
import unicodedata


def normalizar_texto(texto):
    """Remove acentos, pontuação, lowercase, espaços únicos."""
    if not texto:
        return ""
    # Lowercase
    texto = texto.lower().strip()
    # Remove acentos
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    # Remove pontuação (mantém alfanumérico + espaço)
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    # Espaços únicos
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def gerar_hash_dedup(nome, produtor, safra):
    """Gera hash MD5 para deduplicação cross-source."""
    nome_norm = normalizar_texto(nome)
    produtor_norm = normalizar_texto(produtor) if produtor else ""
    safra_str = str(safra).strip() if safra else ""
    chave = f"{nome_norm}|{produtor_norm}|{safra_str}"
    return hashlib.md5(chave.encode('utf-8')).hexdigest()


def extrair_safra(texto):
    """Extrai ano de safra de um texto (ex: '2020', 'Safra 2019')."""
    if not texto:
        return None
    match = re.search(r'\b(19[5-9]\d|20[0-2]\d)\b', str(texto))
    return match.group(1) if match else None


def extrair_tipo_vinho(texto):
    """Detecta tipo de vinho a partir do nome/descrição."""
    if not texto:
        return None
    texto_lower = texto.lower()
    tipos = {
        'espumante': r'\b(espumante|sparkling|cava|prosecco|cremant|sekt)\b',
        'champagne': r'\b(champagne|champanhe)\b',
        'rose': r'\b(ros[eé]|rosado)\b',
        'branco': r'\b(branco|white|blanc|bianco|blanco|weiss)\b',
        'tinto': r'\b(tinto|red|rouge|rosso|rojo|rot)\b',
        'doce': r'\b(doce|sweet|dessert|late harvest|colheita tardia|licoroso|moscatel)\b',
        'fortificado': r'\b(porto|port|madeira|marsala|sherry|jerez|xerez)\b',
    }
    for tipo, pattern in tipos.items():
        if re.search(pattern, texto_lower):
            return tipo
    return None


def detectar_pais_vinho(texto):
    """Detecta país de origem do vinho."""
    if not texto:
        return None
    texto_lower = texto.lower()
    paises = {
        'FR': r'\b(fran[cç]a|france|bordeaux|bourgogne|burgundy|champagne|rhone|loire|alsace|languedoc)\b',
        'IT': r'\b(it[aá]lia|italy|toscana|tuscany|piemonte|piedmont|veneto|sicilia|puglia)\b',
        'ES': r'\b(espanha|spain|rioja|ribera del duero|priorat|cava|jerez)\b',
        'PT': r'\b(portugal|douro|alentejo|dao|bairrada|vinho verde|madeira)\b',
        'AR': r'\b(argentina|mendoza|malbec|patagonia)\b',
        'CL': r'\b(chile|chileno|maipo|colchagua|casablanca)\b',
        'BR': r'\b(brasil|brazil|serra ga[uú]cha|vale dos vinhedos)\b',
        'US': r'\b(estados unidos|usa|napa|sonoma|california|oregon|washington)\b',
        'AU': r'\b(austr[aá]lia|australia|barossa|mclaren vale|hunter valley)\b',
        'ZA': r'\b([aá]frica do sul|south africa|stellenbosch|franschhoek)\b',
        'NZ': r'\b(nova zel[aâ]ndia|new zealand|marlborough|hawke)\b',
        'DE': r'\b(alemanha|germany|mosel|rheingau|pfalz|riesling)\b',
        'AT': r'\b([aá]ustria|austria|wachau|burgenland|gruner veltliner)\b',
        'UY': r'\b(uruguai|uruguay|tannat)\b',
    }
    for codigo, pattern in paises.items():
        if re.search(pattern, texto_lower):
            return codigo
    return None
