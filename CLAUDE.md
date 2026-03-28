# WINEGOD — Catálogo Global de Vinhos

## Visão Geral

Sistema de descoberta e extração de vinhos de e-commerces ao redor do mundo.
Meta: 100% dos vinhos vendidos online em todos os países que consomem vinho.

## Stack

- **Backend**: Python 3.11
- **Banco**: PostgreSQL (único banco: `winegod`)
- **Scraping**: requests, curl_cffi, Playwright (quando necessário)
- **IA Fallback**: Claude API (Haiku/Sonnet) para lojas desconhecidas
- **Enrichment**: Gemini, Grok, DeepSeek (scores e dados complementares)
- **Deploy**: Render (início) → Docker (portável para qualquer cloud)
- **Código**: 100% em Docker desde o dia 1 (facilita migração futura)

## Estrutura do Projeto

```
winegod/
├── CLAUDE.md                       ← Este arquivo (bíblia do projeto)
├── Dockerfile                      ← Deploy portável
├── docker-compose.yml              ← Dev local com PostgreSQL
├── requirements.txt
├── .env                            ← Credenciais (NÃO commitar)
├── .env.example                    ← Template de credenciais
│
├── config/
│   ├── countries/
│   │   ├── brasil.json             ← Config do Brasil
│   │   ├── portugal.json           ← Futuro
│   │   └── ...
│   ├── platforms.json              ← Assinaturas de plataformas (global)
│   └── settings.py                 ← Configurações gerais
│
├── db/
│   ├── connection.py               ← Pool de conexões PostgreSQL
│   ├── models.py                   ← Schema/tabelas
│   ├── wines.py                    ← CRUD de vinhos (upsert, dedup)
│   ├── stores.py                   ← CRUD de lojas
│   ├── recipes.py                  ← CRUD de store_recipes
│   ├── scores.py                   ← CRUD de scores/enrichment
│   └── dedup.py                    ← Hash, normalização, deduplicação
│
├── scrapers/
│   ├── base.py                     ← Classe base para todos os scrapers
│   ├── shopify.py                  ← Shopify (global)
│   ├── woocommerce.py              ← WooCommerce (global)
│   ├── magento.py                  ← Magento (global)
│   ├── vtex.py                     ← VTEX (Brasil/LATAM)
│   ├── vtex_io.py                  ← VTEX IO (Brasil)
│   ├── nuvemshop.py                ← Nuvemshop/Tiendanube (BR/AR)
│   ├── loja_integrada.py           ← Loja Integrada (Brasil)
│   ├── dooca.py                    ← Dooca (Brasil)
│   ├── tray.py                     ← Tray (Brasil)
│   ├── wix.py                      ← Wix (global)
│   ├── prestashop.py               ← PrestaShop (Europa) — A CRIAR
│   ├── shopware.py                 ← Shopware (Alemanha) — A CRIAR
│   ├── mercadolivre.py             ← ML (curl_cffi + proxy)
│   ├── amazon.py                   ← Amazon BR (curl_cffi)
│   ├── vivino.py                   ← Vivino (dados base 1.7M)
│   ├── generico.py                 ← Plataformas custom/desconhecidas
│   └── single_source/              ← Scrapers de fonte única
│       ├── evino.py
│       ├── sonoma.py
│       ├── wine_com_br.py
│       └── mistral.py
│
├── agents/
│   ├── prompts/
│   │   ├── config_pais.md          ← Prompt: gerar config de país
│   │   └── discovery_lojas.md      ← Prompt: descobrir lojas
│   ├── ai_fallback.py              ← IA analisa HTML e gera recipe
│   └── recipe_generator.py         ← Gera store_recipe automaticamente
│
├── enrichment/
│   ├── gemini.py                   ← Enrichment via Gemini
│   ├── grok.py                     ← Enrichment via Grok
│   ├── deepseek.py                 ← Enrichment via DeepSeek
│   ├── cellartracker.py            ← Scores CellarTracker
│   └── collector.py                ← Orquestra enrichment multi-IA
│
├── orchestrator/
│   ├── scheduler.py                ← APScheduler: roda scraping diário
│   ├── country_runner.py           ← Roda extração de 1 país
│   ├── delta.py                    ← Lógica de delta (só mudanças)
│   └── queue.py                    ← Fila de tarefas (lojas novas, broken)
│
├── utils/
│   ├── http.py                     ← Requests com retry, rate limit
│   ├── antibot.py                  ← curl_cffi, Playwright helpers
│   ├── memory.py                   ← Monitoramento de RAM
│   ├── logging.py                  ← Logging padronizado
│   └── sitemap.py                  ← Parser de sitemaps
│
├── migrations/
│   ├── 001_initial_schema.sql      ← Schema inicial
│   └── 002_import_vivino.sql       ← Importar 1.7M do Vivino
│
├── dashboard/                      ← Dashboard web (futuro)
│   ├── app.py
│   ├── templates/
│   └── static/
│
└── cli.py                          ← CLI entry point
```

## Banco de Dados — Schema Principal

### Banco: `winegod` (PostgreSQL)

Um banco, uma verdade. Tudo centralizado.

#### Tabela: `wines` (~1.7M+ registros)
```sql
-- Cada vinho único no mundo (deduplicado por hash)
wines (
    id SERIAL PRIMARY KEY,
    hash_dedup VARCHAR(32) UNIQUE NOT NULL,  -- MD5(nome_norm + produtor_norm + safra)
    nome TEXT NOT NULL,
    nome_normalizado TEXT NOT NULL,
    produtor TEXT,
    produtor_normalizado TEXT,
    safra VARCHAR(4),
    tipo VARCHAR(50),                        -- tinto, branco, rose, espumante, etc.
    pais VARCHAR(2),                         -- ISO 3166-1 alpha-2
    pais_nome VARCHAR(100),
    regiao TEXT,
    sub_regiao TEXT,
    uvas JSONB,                              -- ["Cabernet Sauvignon", "Merlot"]
    teor_alcoolico DECIMAL(4,1),
    volume_ml INTEGER,
    ean_gtin VARCHAR(20),
    imagem_url TEXT,
    descricao TEXT,
    harmonizacao TEXT,
    -- Vivino (fonte primária de dados base)
    vivino_id BIGINT,
    vivino_rating DECIMAL(3,2),
    vivino_reviews INTEGER,
    vivino_url TEXT,
    -- Preços agregados (min/max de TODAS as fontes)
    preco_min DECIMAL(10,2),
    preco_max DECIMAL(10,2),
    moeda VARCHAR(3),                        -- BRL, EUR, USD, etc.
    -- Metadados
    total_fontes INTEGER DEFAULT 0,
    fontes JSONB,                            -- ["vivino", "shopify:grandcru", "vtex:wine.com.br"]
    descoberto_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
)
```

#### Tabela: `wine_sources` (~2M+ registros)
```sql
-- Cada vinho em cada loja (preço + URL)
wine_sources (
    id SERIAL PRIMARY KEY,
    wine_id INTEGER REFERENCES wines(id),
    store_id INTEGER REFERENCES stores(id),
    url TEXT NOT NULL,                        -- URL do produto na loja
    preco DECIMAL(10,2),
    preco_anterior DECIMAL(10,2),            -- Para detectar mudança de preço
    moeda VARCHAR(3),
    disponivel BOOLEAN DEFAULT TRUE,
    em_promocao BOOLEAN DEFAULT FALSE,
    descoberto_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(wine_id, store_id, url)
)
```

#### Tabela: `wine_scores` (enrichment por IA)
```sql
wine_scores (
    id SERIAL PRIMARY KEY,
    wine_id INTEGER REFERENCES wines(id),
    fonte VARCHAR(50) NOT NULL,              -- gemini, grok, deepseek, cellartracker, wine_enthusiast
    score DECIMAL(4,2),                      -- Nota (ex: 91.5)
    score_raw TEXT,                           -- Resposta bruta da IA
    confianca DECIMAL(3,2),                  -- 0.0 a 1.0
    dados_extra JSONB,                       -- Campos extras retornados
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(wine_id, fonte)
)
```

#### Tabela: `stores` (lojas descobertas)
```sql
stores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    dominio VARCHAR(200) NOT NULL UNIQUE,    -- ex: "grandcru.com.br"
    pais VARCHAR(2) NOT NULL,                -- ISO
    tipo VARCHAR(50),                        -- ecommerce_vinho, importadora, supermercado, etc.
    plataforma VARCHAR(50),                  -- shopify, woocommerce, vtex, etc.
    regiao VARCHAR(100),
    cidade VARCHAR(100),
    abrangencia VARCHAR(20),                 -- nacional, regional, internacional
    total_vinhos INTEGER DEFAULT 0,
    ativa BOOLEAN DEFAULT TRUE,
    como_descobriu VARCHAR(50),
    observacoes TEXT,
    descoberta_em TIMESTAMPTZ DEFAULT NOW(),
    atualizada_em TIMESTAMPTZ DEFAULT NOW()
)
```

#### Tabela: `store_recipes` (como extrair de cada loja)
```sql
store_recipes (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores(id) UNIQUE,
    plataforma VARCHAR(50) NOT NULL,
    metodo_listagem VARCHAR(20) NOT NULL,    -- sitemap, api, crawl, search
    url_sitemap TEXT,
    url_api TEXT,
    filtro_urls TEXT,                         -- Regex para filtrar URLs de produtos
    metodo_extracao VARCHAR(20),             -- json_ld, microdata, og_tags, api_json, html_parse
    campos_mapeados JSONB,                   -- Mapeamento campo→seletor/path
    anti_bot VARCHAR(20) DEFAULT 'none',     -- none, cloudflare, akamai, custom
    usa_curl_cffi BOOLEAN DEFAULT FALSE,
    usa_playwright BOOLEAN DEFAULT FALSE,
    headers_custom JSONB,
    sitemap_hash VARCHAR(32),                -- Hash do último sitemap (para delta)
    total_produtos INTEGER,
    tempo_medio_seg INTEGER,                 -- Tempo médio de extração em segundos
    ultima_extracao TIMESTAMPTZ,
    ultima_falha TIMESTAMPTZ,
    falhas_consecutivas INTEGER DEFAULT 0,
    sucesso BOOLEAN DEFAULT TRUE,
    criado_por VARCHAR(20) DEFAULT 'auto',   -- auto, ai_fallback, manual
    notas TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
)
```

#### Tabela: `executions` (log de cada rodada)
```sql
executions (
    id SERIAL PRIMARY KEY,
    pais VARCHAR(2),
    fonte VARCHAR(100),                      -- "shopify", "vtex", "vivino", etc.
    store_id INTEGER REFERENCES stores(id),  -- NULL se for fonte global
    tipo VARCHAR(20),                        -- full, delta, retry
    status VARCHAR(20),                      -- running, completed, failed, stopped
    vinhos_encontrados INTEGER DEFAULT 0,
    vinhos_novos INTEGER DEFAULT 0,
    vinhos_atualizados INTEGER DEFAULT 0,
    precos_alterados INTEGER DEFAULT 0,
    erros INTEGER DEFAULT 0,
    memoria_max_mb INTEGER,
    tempo_seg INTEGER,
    checkpoint JSONB,                        -- Para retomar de onde parou
    iniciado_em TIMESTAMPTZ DEFAULT NOW(),
    finalizado_em TIMESTAMPTZ
)
```

## Sistema de Store Recipes (CORE do projeto)

### Como funciona o delta diário (RÁPIDO):

1. **Sitemap-based delta:**
   - Fetch sitemap → calcular hash MD5
   - Comparar com `store_recipes.sitemap_hash`
   - Se IGUAL → SKIP (0 requests na loja)
   - Se DIFERENTE → comparar URLs, extrair só novas/alteradas

2. **API-based delta (Shopify/WooCommerce):**
   - Shopify: `GET /products.json?updated_at_min={ultima_extracao}`
   - WooCommerce: `GET /wp-json/wc/store/products?modified_after={ultima_extracao}`
   - Só retorna produtos novos ou com preço alterado

3. **Full rescan (mensal):**
   - 1x por mês, ignorar delta e refazer tudo
   - Detectar produtos removidos (disponivel=FALSE)

### Quando recipe falha → IA Fallback:

```
Loja sem recipe ou recipe quebrado
  → Fetch homepage HTML (50KB)
  → Enviar para Claude Haiku com prompt especializado
  → IA retorna recipe JSON
  → Testar recipe (extrair 3 produtos amostra)
  → Se OK → salvar recipe (criado_por = 'ai_fallback')
  → Se falhou → marcar como needs_human_review
```

## Regras para o Claude

### REGRA 0 — Comunicação
- Respostas curtas e diretas
- Sem jargão desnecessário
- Bullet points > parágrafos

### REGRA 1 — Commit e Push
- SEMPRE perguntar antes de commit/push
- Só commitar arquivos que VOCÊ alterou nesta sessão
- Nunca `git add .` ou `git add -A`

### REGRA 2 — Scrapers
- Platform-centric: 1 scraper por plataforma, NÃO por loja
- Adicionar loja = adicionar dict na config, ZERO código novo
- Sitemap-first: sempre preferir sitemap sobre crawl
- JSON-LD > microdata > OG tags > HTML parse

### REGRA 3 — Deduplicação
- Hash: MD5(normalizar(nome) + "|" + normalizar(produtor) + "|" + safra)
- Normalização: lowercase, sem acentos, sem pontuação, espaços únicos
- ON CONFLICT: merge fontes, LEAST(preco_min), GREATEST(preco_max), COALESCE campos

### REGRA 4 — Memória (se usar Playwright)
- Limite: 350MB (ou configurável)
- Monitorar RAM a cada N itens
- Reiniciar browser a cada 25 itens
- Bloquear images/media via page.route()
- gc.collect() a cada 5 itens

### REGRA 5 — Anti-Bot
- Nível 0 (maioria): requests simples com User-Agent
- Nível 1 (Cloudflare leve): curl_cffi com impersonate='chrome131'
- Nível 2 (WAF agressivo): Playwright headless + stealth
- Nível 3 (ML/Amazon): curl_cffi + proxy residencial
- NUNCA escalar nível sem necessidade — começar pelo 0

### REGRA 6 — Extração de Preços (winegod_utils)
1. NUNCA usar USD como moeda default. Usar `utils.currency.get_currency_for_store()` ou fallback `MOEDA_POR_PAIS[pais]`.
2. SEMPRE validar preço com `utils.price_validator.is_valid_price()` antes de gravar.
3. SEMPRE filtrar não-vinhos com `utils.wine_filter.is_wine()` antes de gravar.
4. SEMPRE normalizar nome com `utils.normalize.normalize_wine_name()` antes de gravar.
5. Para Magento: aplicar `fix_centavos_magento()` no preço.
6. Rejeitar URLs inválidas com `is_valid_url()`.
7. Biblioteca compartilhada em `C:\winegod\utils\` — usada por Codex, Admin e Claude.

## Dados Iniciais

- **Vivino**: 1.7M vinhos (fonte primária — ratings, reviews, metadata)
- **Brasil**: 144K vinhos de 182 lojas (19 plataformas)
- **CellarTracker**: Scores via Vivino cross-reference
- **Enrichment IA**: Scores Gemini, Grok, DeepSeek para subset

## Países Prioritários (Fase 1)

1. **Brasil** (PRONTO — 182 lojas, 144K vinhos)
2. **Portugal** (mercado pequeno, muitas quintas com loja online)
3. **EUA** (maior mercado, muitas restrições por estado)
4. **França** (maior produtor, milhares de domaines)
5. **Itália** (segundo produtor, muitas enoteche online)
6. **Espanha** (terceiro produtor, bodegas com loja)
7. **UK** (maior importador europeu, mercado concentrado)
8. **Argentina** (produtor LATAM, Tiendanube)
9. **Chile** (produtor LATAM)
10. **Alemanha** (maior consumidor europeu, Shopware)
