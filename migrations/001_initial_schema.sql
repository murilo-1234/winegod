-- WineGod — Schema Inicial
-- Executar: psql $DATABASE_URL -f migrations/001_initial_schema.sql

-- Tabela principal: vinhos únicos
CREATE TABLE IF NOT EXISTS wines (
    id SERIAL PRIMARY KEY,
    hash_dedup VARCHAR(32) UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    nome_normalizado TEXT NOT NULL,
    produtor TEXT,
    produtor_normalizado TEXT,
    safra VARCHAR(4),
    tipo VARCHAR(50),
    pais VARCHAR(2),
    pais_nome VARCHAR(100),
    regiao TEXT,
    sub_regiao TEXT,
    uvas JSONB,
    teor_alcoolico DECIMAL(4,1),
    volume_ml INTEGER,
    ean_gtin VARCHAR(20),
    imagem_url TEXT,
    descricao TEXT,
    harmonizacao TEXT,
    vivino_id BIGINT,
    vivino_rating DECIMAL(3,2),
    vivino_reviews INTEGER,
    vivino_url TEXT,
    preco_min DECIMAL(10,2),
    preco_max DECIMAL(10,2),
    moeda VARCHAR(3),
    total_fontes INTEGER DEFAULT 0,
    fontes JSONB DEFAULT '[]'::jsonb,
    descoberto_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para wines
CREATE INDEX IF NOT EXISTS idx_wines_pais ON wines(pais);
CREATE INDEX IF NOT EXISTS idx_wines_tipo ON wines(tipo);
CREATE INDEX IF NOT EXISTS idx_wines_vivino_id ON wines(vivino_id);
CREATE INDEX IF NOT EXISTS idx_wines_nome_norm ON wines(nome_normalizado);
CREATE INDEX IF NOT EXISTS idx_wines_produtor_norm ON wines(produtor_normalizado);
CREATE INDEX IF NOT EXISTS idx_wines_atualizado ON wines(atualizado_em);

-- Tabela: cada vinho em cada loja (preço + URL)
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    url TEXT NOT NULL,
    dominio VARCHAR(200) NOT NULL UNIQUE,
    pais VARCHAR(2) NOT NULL,
    tipo VARCHAR(50),
    plataforma VARCHAR(50),
    regiao VARCHAR(100),
    cidade VARCHAR(100),
    abrangencia VARCHAR(20),
    total_vinhos INTEGER DEFAULT 0,
    ativa BOOLEAN DEFAULT TRUE,
    como_descobriu VARCHAR(50),
    observacoes TEXT,
    descoberta_em TIMESTAMPTZ DEFAULT NOW(),
    atualizada_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stores_pais ON stores(pais);
CREATE INDEX IF NOT EXISTS idx_stores_plataforma ON stores(plataforma);
CREATE INDEX IF NOT EXISTS idx_stores_ativa ON stores(ativa);

-- Tabela: vinhos por fonte (loja + preço + URL)
CREATE TABLE IF NOT EXISTS wine_sources (
    id SERIAL PRIMARY KEY,
    wine_id INTEGER REFERENCES wines(id) ON DELETE CASCADE,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    preco DECIMAL(10,2),
    preco_anterior DECIMAL(10,2),
    moeda VARCHAR(3),
    disponivel BOOLEAN DEFAULT TRUE,
    em_promocao BOOLEAN DEFAULT FALSE,
    descoberto_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(wine_id, store_id, url)
);

CREATE INDEX IF NOT EXISTS idx_sources_wine ON wine_sources(wine_id);
CREATE INDEX IF NOT EXISTS idx_sources_store ON wine_sources(store_id);
CREATE INDEX IF NOT EXISTS idx_sources_disponivel ON wine_sources(disponivel);

-- Tabela: scores de IA / enrichment
CREATE TABLE IF NOT EXISTS wine_scores (
    id SERIAL PRIMARY KEY,
    wine_id INTEGER REFERENCES wines(id) ON DELETE CASCADE,
    fonte VARCHAR(50) NOT NULL,
    score DECIMAL(4,2),
    score_raw TEXT,
    confianca DECIMAL(3,2),
    dados_extra JSONB,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(wine_id, fonte)
);

CREATE INDEX IF NOT EXISTS idx_scores_wine ON wine_scores(wine_id);
CREATE INDEX IF NOT EXISTS idx_scores_fonte ON wine_scores(fonte);

-- Tabela: recipes de extração por loja
CREATE TABLE IF NOT EXISTS store_recipes (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE UNIQUE,
    plataforma VARCHAR(50) NOT NULL,
    metodo_listagem VARCHAR(20) NOT NULL,
    url_sitemap TEXT,
    url_api TEXT,
    filtro_urls TEXT,
    metodo_extracao VARCHAR(20),
    campos_mapeados JSONB,
    anti_bot VARCHAR(20) DEFAULT 'none',
    usa_curl_cffi BOOLEAN DEFAULT FALSE,
    usa_playwright BOOLEAN DEFAULT FALSE,
    headers_custom JSONB,
    sitemap_hash VARCHAR(32),
    total_produtos INTEGER,
    tempo_medio_seg INTEGER,
    ultima_extracao TIMESTAMPTZ,
    ultima_falha TIMESTAMPTZ,
    falhas_consecutivas INTEGER DEFAULT 0,
    sucesso BOOLEAN DEFAULT TRUE,
    criado_por VARCHAR(20) DEFAULT 'auto',
    notas TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela: log de execuções
CREATE TABLE IF NOT EXISTS executions (
    id SERIAL PRIMARY KEY,
    pais VARCHAR(2),
    fonte VARCHAR(100),
    store_id INTEGER REFERENCES stores(id),
    tipo VARCHAR(20),
    status VARCHAR(20) DEFAULT 'running',
    vinhos_encontrados INTEGER DEFAULT 0,
    vinhos_novos INTEGER DEFAULT 0,
    vinhos_atualizados INTEGER DEFAULT 0,
    precos_alterados INTEGER DEFAULT 0,
    erros INTEGER DEFAULT 0,
    memoria_max_mb INTEGER,
    tempo_seg INTEGER,
    checkpoint JSONB,
    iniciado_em TIMESTAMPTZ DEFAULT NOW(),
    finalizado_em TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exec_pais ON executions(pais);
CREATE INDEX IF NOT EXISTS idx_exec_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_exec_iniciado ON executions(iniciado_em);

-- View: resumo por país
CREATE OR REPLACE VIEW country_summary AS
SELECT
    s.pais,
    COUNT(DISTINCT s.id) AS total_lojas,
    COUNT(DISTINCT s.id) FILTER (WHERE s.ativa) AS lojas_ativas,
    COUNT(DISTINCT ws.wine_id) AS vinhos_com_fonte,
    SUM(s.total_vinhos) AS total_vinhos_lojas
FROM stores s
LEFT JOIN wine_sources ws ON ws.store_id = s.id
GROUP BY s.pais
ORDER BY total_lojas DESC;

-- View: resumo por plataforma
CREATE OR REPLACE VIEW platform_summary AS
SELECT
    s.plataforma,
    s.pais,
    COUNT(*) AS total_lojas,
    SUM(s.total_vinhos) AS total_vinhos
FROM stores s
WHERE s.ativa = TRUE
GROUP BY s.plataforma, s.pais
ORDER BY total_lojas DESC;
