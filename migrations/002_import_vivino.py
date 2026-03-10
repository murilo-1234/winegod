"""Importar 1.7M vinhos do vivino_db local para winegod no Render."""
import psycopg2
import psycopg2.extras
import hashlib
import re
import unicodedata
import time
import sys

# Conexoes
VIVINO_URL = "postgresql://postgres:postgres123@localhost:5432/vivino_db"
WINEGOD_URL = "postgresql://winegod_user:iNIIVWEOOCVWTCtgSNWtGlgn6RqFYT96@dpg-d6o56scr85hc73843pvg-a.oregon-postgres.render.com/winegod"

BATCH_SIZE = 5000


def normalizar_texto(texto):
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def gerar_hash(nome, produtor, safra):
    nome_norm = normalizar_texto(nome)
    produtor_norm = normalizar_texto(produtor) if produtor else ""
    safra_str = str(safra).strip() if safra else ""
    chave = f"{nome_norm}|{produtor_norm}|{safra_str}"
    return hashlib.md5(chave.encode('utf-8')).hexdigest()


def detectar_tipo(tipo_nome):
    if not tipo_nome:
        return None
    t = tipo_nome.lower()
    mapa = {
        'red': 'tinto', 'tinto': 'tinto',
        'white': 'branco', 'branco': 'branco',
        'sparkling': 'espumante', 'espumante': 'espumante',
        'rosé': 'rose', 'rose': 'rose',
        'dessert': 'doce', 'doce': 'doce',
        'fortified': 'fortificado', 'fortificado': 'fortificado',
    }
    for key, val in mapa.items():
        if key in t:
            return val
    return tipo_nome


def main():
    print("=== Importacao Vivino -> WineGod ===\n")

    # Conectar
    src = psycopg2.connect(VIVINO_URL)
    dst = psycopg2.connect(WINEGOD_URL)
    src_cur = src.cursor(name='vivino_reader', cursor_factory=psycopg2.extras.DictCursor)
    dst_cur = dst.cursor()

    # Contar total
    count_cur = src.cursor()
    count_cur.execute("SELECT COUNT(*) FROM vivino_vinhos")
    total = count_cur.fetchone()[0]
    count_cur.close()
    print(f"Total vinhos no Vivino: {total:,}\n")

    # Query de leitura
    src_cur.execute("""
        SELECT
            v.id, v.nome, v.vinicola_nome, v.tipo_nome,
            v.pais_codigo, v.pais_nome, v.regiao_nome, v.sub_regiao,
            v.rating_medio, v.total_ratings, v.preco, v.moeda,
            v.safra, v.uvas, v.url_imagem, v.url_vivino,
            v.acidez, v.efervescencia, v.intensidade, v.docura, v.tanino,
            v.sabores, v.harmonizacao, v.estilo_descricao,
            v.is_natural, v.slug, v.descoberto_em, v.atualizado_em,
            v.nota_estimada, v.dados_extras
        FROM vivino_vinhos v
        ORDER BY v.id
    """)

    # SQL de insert
    insert_sql = """
        INSERT INTO wines (
            hash_dedup, nome, nome_normalizado, produtor, produtor_normalizado,
            safra, tipo, pais, pais_nome, regiao, sub_regiao, uvas,
            vivino_id, vivino_rating, vivino_reviews, vivino_url,
            imagem_url, descricao, harmonizacao,
            preco_min, preco_max, moeda,
            total_fontes, fontes,
            descoberto_em, atualizado_em
        ) VALUES (
            %(hash_dedup)s, %(nome)s, %(nome_normalizado)s, %(produtor)s, %(produtor_normalizado)s,
            %(safra)s, %(tipo)s, %(pais)s, %(pais_nome)s, %(regiao)s, %(sub_regiao)s, %(uvas)s,
            %(vivino_id)s, %(vivino_rating)s, %(vivino_reviews)s, %(vivino_url)s,
            %(imagem_url)s, %(descricao)s, %(harmonizacao)s,
            %(preco_min)s, %(preco_max)s, %(moeda)s,
            1, '["vivino"]'::jsonb,
            %(descoberto_em)s, %(atualizado_em)s
        )
        ON CONFLICT (hash_dedup) DO UPDATE SET
            vivino_id = COALESCE(wines.vivino_id, EXCLUDED.vivino_id),
            vivino_rating = COALESCE(EXCLUDED.vivino_rating, wines.vivino_rating),
            vivino_reviews = COALESCE(EXCLUDED.vivino_reviews, wines.vivino_reviews),
            vivino_url = COALESCE(EXCLUDED.vivino_url, wines.vivino_url),
            imagem_url = COALESCE(wines.imagem_url, EXCLUDED.imagem_url),
            preco_min = LEAST(wines.preco_min, EXCLUDED.preco_min),
            preco_max = GREATEST(wines.preco_max, EXCLUDED.preco_max),
            atualizado_em = NOW()
    """

    inserted = 0
    duplicates = 0
    errors = 0
    batch = []
    start = time.time()

    while True:
        rows = src_cur.fetchmany(BATCH_SIZE)
        if not rows:
            break

        for row in rows:
            try:
                nome = row['nome']
                produtor = row['vinicola_nome']
                safra = str(row['safra']) if row['safra'] else None

                if not nome:
                    errors += 1
                    continue

                hash_dedup = gerar_hash(nome, produtor, safra)

                # Montar uvas como JSON
                uvas_raw = row['uvas']
                if uvas_raw:
                    import json
                    try:
                        uvas_json = json.dumps(uvas_raw.split(', ') if isinstance(uvas_raw, str) else uvas_raw)
                    except:
                        uvas_json = None
                else:
                    uvas_json = None

                record = {
                    'hash_dedup': hash_dedup,
                    'nome': nome,
                    'nome_normalizado': normalizar_texto(nome),
                    'produtor': produtor,
                    'produtor_normalizado': normalizar_texto(produtor),
                    'safra': safra[:4] if safra and len(safra) >= 4 else safra,
                    'tipo': detectar_tipo(row['tipo_nome']),
                    'pais': row['pais_codigo'],
                    'pais_nome': row['pais_nome'],
                    'regiao': row['regiao_nome'],
                    'sub_regiao': row['sub_regiao'],
                    'uvas': uvas_json,
                    'vivino_id': row['id'],
                    'vivino_rating': row['rating_medio'],
                    'vivino_reviews': row['total_ratings'],
                    'vivino_url': row['url_vivino'],
                    'imagem_url': row['url_imagem'],
                    'descricao': row['estilo_descricao'],
                    'harmonizacao': row['harmonizacao'],
                    'preco_min': row['preco'],
                    'preco_max': row['preco'],
                    'moeda': row['moeda'] or 'EUR',
                    'descoberto_em': row['descoberto_em'],
                    'atualizado_em': row['atualizado_em'],
                }

                batch.append(record)

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  ERRO: {e} | nome={row.get('nome', '?')}")

        # Executar batch
        if batch:
            try:
                psycopg2.extras.execute_batch(dst_cur, insert_sql, batch, page_size=1000)
                dst.commit()
                inserted += len(batch)
            except Exception as e:
                dst.rollback()
                # Tentar um por um para nao perder o batch inteiro
                for record in batch:
                    try:
                        dst_cur.execute(insert_sql, record)
                        dst.commit()
                        inserted += 1
                    except Exception as e2:
                        dst.rollback()
                        duplicates += 1
            batch = []

        elapsed = time.time() - start
        rate = inserted / elapsed if elapsed > 0 else 0
        pct = (inserted + duplicates + errors) / total * 100
        eta_min = (total - inserted - duplicates - errors) / rate / 60 if rate > 0 else 0
        print(f"  {inserted:>10,} importados | {duplicates:,} dupes | {errors:,} erros | {pct:.1f}% | {rate:.0f}/s | ETA: {eta_min:.1f}min", flush=True)

    # Final
    elapsed = time.time() - start
    print(f"\n=== CONCLUIDO ===")
    print(f"Importados:  {inserted:,}")
    print(f"Duplicatas:  {duplicates:,}")
    print(f"Erros:       {errors:,}")
    print(f"Tempo:       {elapsed/60:.1f} min")

    # Verificar total no destino
    dst_cur.execute("SELECT COUNT(*) FROM wines")
    print(f"Total wines: {dst_cur.fetchone()[0]:,}")

    src_cur.close()
    src.close()
    dst_cur.close()
    dst.close()


if __name__ == "__main__":
    main()
