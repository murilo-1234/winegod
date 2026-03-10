"""WineGod CLI — Entry point."""
import sys
import json
import os

def print_usage():
    print("""
WineGod — Catálogo Global de Vinhos

Uso:
    python cli.py setup                     Criar tabelas no banco
    python cli.py status                    Ver resumo geral
    python cli.py status <pais>             Ver resumo de um país (ex: BR, PT, FR)

    python cli.py scrape <pais>             Rodar extração completa de um país
    python cli.py scrape <pais> --delta     Rodar só delta (mudanças desde última vez)
    python cli.py scrape <pais> <plataforma>  Rodar só uma plataforma (ex: shopify)

    python cli.py stores <pais>             Listar lojas de um país
    python cli.py stores add <json_file>    Importar lojas de um JSON
    python cli.py stores detect <url>       Detectar plataforma de uma URL

    python cli.py enrich <pais>             Rodar enrichment para vinhos de um país
    python cli.py enrich <pais> --source=gemini  Enrichment com fonte específica

    python cli.py import vivino <file>      Importar dados do Vivino
    python cli.py import brasil             Importar dados existentes do vinhos_brasil

    python cli.py recipe generate <store_id>    Gerar recipe para uma loja
    python cli.py recipe test <store_id>        Testar recipe de uma loja
    python cli.py recipe ai <store_id>          Usar IA para gerar recipe
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "setup":
        from db.connection import get_connection, release_connection
        conn = get_connection()
        try:
            migration_path = os.path.join(os.path.dirname(__file__), 'migrations', '001_initial_schema.sql')
            with open(migration_path, 'r') as f:
                sql = f.read()
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            print("✓ Tabelas criadas com sucesso!")
        except Exception as e:
            conn.rollback()
            print(f"✗ Erro: {e}")
        finally:
            release_connection(conn)

    elif command == "status":
        pais = sys.argv[2].upper() if len(sys.argv) > 2 else None
        from db.connection import execute_query
        if pais:
            stores = execute_query(
                "SELECT plataforma, COUNT(*) as total, SUM(total_vinhos) as vinhos "
                "FROM stores WHERE pais = %s AND ativa = TRUE "
                "GROUP BY plataforma ORDER BY total DESC", (pais,)
            )
            total_wines = execute_query(
                "SELECT COUNT(*) as total FROM wines WHERE pais = %s", (pais,)
            )
            print(f"\n=== {pais} ===")
            print(f"Vinhos únicos: {total_wines[0]['total']:,}")
            print(f"\nLojas por plataforma:")
            for s in stores:
                print(f"  {s['plataforma'] or 'desconhecida':20s} {s['total']:4d} lojas  {s['vinhos'] or 0:8,} vinhos")
        else:
            summary = execute_query(
                "SELECT pais, COUNT(*) as lojas, SUM(total_vinhos) as vinhos "
                "FROM stores WHERE ativa = TRUE "
                "GROUP BY pais ORDER BY lojas DESC"
            )
            total = execute_query("SELECT COUNT(*) as total FROM wines")
            print(f"\n=== WineGod — Status Geral ===")
            print(f"Total vinhos únicos: {total[0]['total']:,}")
            print(f"\nPor país:")
            for s in summary:
                print(f"  {s['pais']}  {s['lojas']:4d} lojas  {s['vinhos'] or 0:8,} vinhos")

    else:
        print(f"Comando '{command}' ainda não implementado.")
        print_usage()


if __name__ == "__main__":
    main()
