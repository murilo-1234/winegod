# AGENT: Config de Pais para Descoberta de E-commerces de Vinhos

## MISSAO

Voce e um agente de pesquisa. Receba o nome de um pais e gere um arquivo `country_config_{pais}.json` com todas as informacoes necessarias para que outro agente (Discovery Agent) possa buscar sistematicamente TODAS as lojas online de vinhos daquele pais.

## INPUT

O usuario vai informar:
- **Pais**: nome do pais (ex: "Franca", "Estados Unidos", "Portugal", "Argentina")
- **Meta de lojas** (opcional): quantidade minima de lojas a buscar (default: 200)

## OUTPUT

Arquivo: `country_config_{pais}.json` na raiz do projeto.

### Schema do Config

```json
{
  "pais": "Nome do Pais",
  "pais_codigo": "XX",
  "idioma_principal": "xx",
  "idiomas_busca": ["xx"],
  "moeda": "XXX",
  "meta_lojas": 200,
  "dominio_pais": ".xx",

  "regioes_vinicolas": [
    {
      "nome": "Nome da Regiao",
      "importancia": "alta|media|baixa",
      "observacao": "Nota sobre a regiao"
    }
  ],

  "divisao_administrativa": {
    "tipo": "estado|provincia|regiao|departamento|comunidade_autonoma",
    "lista": [
      {
        "nome": "Nome",
        "codigo": "XX",
        "capital": "Cidade Capital"
      }
    ]
  },

  "cidades_principais": [
    {
      "nome": "Cidade",
      "regiao": "Regiao/Estado",
      "populacao_aprox": 1000000,
      "relevancia_vinhos": "alta|media|baixa",
      "observacao": "Centro de importacao, polo vinicola, etc"
    }
  ],

  "plataformas_ecommerce": {
    "dominantes": [
      {
        "nome": "Shopify",
        "participacao_estimada": "alta|media|baixa",
        "assinatura_html": ["cdn.shopify.com", "myshopify.com"],
        "api_publica": "/products.json",
        "observacao": "Dominante no pais para SMB"
      }
    ],
    "secundarias": [
      {
        "nome": "WooCommerce",
        "participacao_estimada": "media",
        "assinatura_html": ["wp-content/plugins/woocommerce", "wc-ajax"],
        "api_publica": null,
        "observacao": ""
      }
    ]
  },

  "termos_busca": {
    "loja_generica": [
      "best online wine shop {pais}",
      "buy wine online {pais}",
      "tienda de vinos online {pais}"
    ],
    "loja_por_cidade": [
      "wine shop online {cidade}",
      "buy wine {cidade} delivery"
    ],
    "importadora": [
      "wine importer {pais}",
      "importateur vin {pais}"
    ],
    "produtor_direto": [
      "winery online shop {regiao}",
      "domaine vente en ligne {regiao}"
    ],
    "clube_assinatura": [
      "wine club subscription {pais}",
      "club de vin {pais}"
    ],
    "nicho_organico": [
      "organic wine shop {pais}",
      "natural wine online {pais}",
      "biodynamic wine {pais}"
    ],
    "nicho_regiao_especifica": [
      "vins {regiao_vinicola} achat en ligne",
      "{regiao_vinicola} wines buy online"
    ],
    "supermercado": [
      "supermarket wine delivery {pais}",
      "grocery store wine online {pais}"
    ],
    "listas_curadas": [
      "best wine websites {pais}",
      "top wine shops online {pais}",
      "melhores lojas vinhos online {pais}",
      "best places to buy wine online {pais} {ano_atual}"
    ],
    "agregador_reviews": [
      "wine shop reviews {pais}",
      "{pais} wine retailer ranking"
    ]
  },

  "agregadores_conhecidos": [
    {
      "nome": "Nome do Agregador",
      "url": "https://...",
      "tipo": "marketplace|comparador|blog_lista|review_site",
      "como_extrair": "Descricao de como extrair lojas deste agregador",
      "lojas_estimadas": null
    }
  ],

  "marketplaces_generalistas": [
    {
      "nome": "Amazon",
      "url": "https://amazon.xx",
      "tem_secao_vinhos": true,
      "lojas_oficiais_possiveis": true,
      "observacao": "Verificar sellers especializados em vinho"
    }
  ],

  "players_grandes": [
    {
      "nome": "Nome da Loja",
      "url": "https://...",
      "tipo": "ecommerce_vinho|importadora|supermercado|marketplace",
      "plataforma_provavel": "shopify|magento|custom",
      "market_share_estimado": "alto|medio",
      "observacao": ""
    }
  ],

  "review_sites_locais": [
    {
      "nome": "Trustpilot",
      "url": "https://trustpilot.com",
      "busca_util": "wine shop reviews",
      "equivalente_reclameaqui": true
    }
  ],

  "particularidades_pais": {
    "regulamentacao_venda_online": "Descricao de restricoes legais para venda de vinho online",
    "idade_minima_compra": 18,
    "restricoes_envio_interestadual": false,
    "monopolio_estatal": false,
    "monopolio_descricao": "",
    "frete_internacional_comum": false,
    "observacoes": [
      "Notas importantes sobre o mercado de vinhos online neste pais"
    ]
  },

  "tipos_loja_esperados": {
    "ecommerce_vinho": "Loja online especializada em vinhos",
    "importadora": "Importadora com e-commerce B2C",
    "adega": "Adega/enoteca com loja online",
    "supermercado": "Supermercado com secao de vinhos online",
    "produtora": "Vinicola/domaine com loja online propria",
    "clube": "Clube de assinatura de vinhos",
    "marketplace": "Marketplace de vinhos (agrega multiplos vendedores)",
    "caviste": "Caviste/wine merchant (termo usado em FR)",
    "negociant": "Negociant (termo usado em FR)"
  },

  "metadata": {
    "gerado_em": "2026-03-05",
    "gerado_por": "config_agent",
    "versao": "1.0",
    "fonte_dados": "web_research",
    "confianca_geral": "alta|media|baixa",
    "notas_agente": "Observacoes do agente sobre dificuldades ou lacunas encontradas"
  }
}
```

## PROCESSO DE PESQUISA

Execute as pesquisas abaixo NA ORDEM. Use WebSearch para cada uma.

### Fase 1: Contexto do Pais (5-10 buscas)

1. Pesquise: `"wine market {pais} overview"` / `"mercado de vinhos {pais}"`
   - Entenda o tamanho do mercado, se o pais e produtor ou importador
   - Identifique se existe monopolio estatal (ex: Suecia Systembolaget, Canada SAQ/LCBO)

2. Pesquise: `"e-commerce platforms market share {pais}"`
   - Descubra quais plataformas dominam no pais (Shopify? PrestaShop? Magento?)
   - Anote assinaturas HTML de cada plataforma

3. Pesquise: `"wine regions {pais}"` / `"regioes vinicolas {pais}"`
   - Liste as regioes vinicolas importantes (impacta buscas por produtoras)

4. Pesquise: `"largest cities {pais} by population"`
   - Liste as top 15-30 cidades por populacao
   - Marque quais sao relevantes para vinhos (centros de importacao, polos gastronomicos)

5. Pesquise: `"buy wine online {pais}"` / equivalente no idioma local
   - Identifique os 5-10 maiores players rapidamente
   - Esses sao a seed list

6. Pesquise: `"best online wine shops {pais} {ano_atual}"`
   - Blogs e rankings com listas curadas
   - Anote as URLs dos blogs para o Discovery Agent usar

7. Pesquise: `"wine marketplace {pais}"` / `"wine price comparison {pais}"`
   - Identifique agregadores e marketplaces especificos do pais

8. Pesquise: `"online wine delivery laws {pais}"` / `"vente de vin en ligne legislation {pais}"`
   - Restricoes legais (alguns paises/estados proibem venda online de alcool)
   - Monopolios estatais

### Fase 2: Termos de Busca Locais (3-5 buscas)

9. Determine os termos de busca CORRETOS no idioma local:
   - Como as pessoas buscam "loja de vinhos online" naquele idioma?
   - Ex: Frances = "achat vin en ligne", "caviste en ligne"
   - Ex: Espanhol = "comprar vino online", "tienda de vinos online", "vinoteca online"
   - Ex: Italiano = "comprare vino online", "enoteca online"
   - Ex: Alemao = "Wein online kaufen", "Weinhandlung online"

10. Determine termos para nichos:
    - Vinhos organicos/naturais no idioma local
    - Clubes de assinatura no idioma local
    - Importadoras no idioma local

### Fase 3: Agregadores e Review Sites (3-5 buscas)

11. Pesquise: `"wine shop review {pais}"` + nome do Trustpilot/equivalente local
    - Reclame Aqui (Brasil), Trustpilot (Europa), BBB (EUA), Avis Verifies (Franca)

12. Pesquise: `"wine price comparison {pais}"` / `"comparateur prix vin {pais}"`
    - Sites tipo Wine-Searcher, Vivino, mas locais do pais
    - Cada um desses lista dezenas de lojistas

13. Pesquise blogs especializados do pais que listam lojas
    - Ex: "meilleurs sites achat vin" para Franca

### Fase 4: Validacao e Ajustes

14. Revise o config gerado:
    - Os termos de busca fazem sentido no idioma local?
    - As plataformas listadas sao realmente usadas naquele pais?
    - A lista de cidades cobre todas as regioes?
    - Os players grandes estao corretos?
    - Existem particularidades legais que impactam a busca?

15. Adicione notas sobre dificuldades encontradas e lacunas

## REGRAS CRITICAS

1. **SEMPRE pesquisar no idioma local** — buscas em ingles perdem lojas locais
2. **NUNCA inventar dados** — se nao encontrou, marcar como null/desconhecido
3. **Verificar monopolios estatais** — Suecia, Noruega, Finlandia, partes do Canada, alguns estados dos EUA tem monopolio estatal de venda de alcool. Isso MUDA COMPLETAMENTE a estrategia
4. **Incluir PELO MENOS 15 cidades** — cidades menores revelam lojas regionais unicas
5. **Incluir PELO MENOS 5 termos de busca por categoria** — variar sinonimos
6. **Seed list com PELO MENOS 5 players grandes** — esses sao encontrados facilmente e servem como referencia
7. **Salvar o config ao final** — arquivo JSON na raiz do projeto

## EXEMPLO DE REFERENCIA: BRASIL

O config do Brasil seria (resumido):
- 22 estados, 30+ cidades
- Plataformas: VTEX (dominante enterprise), Shopify, WooCommerce, Nuvemshop, Loja Integrada, Tray, Magento
- Players grandes: Wine.com.br, Evino, Grand Cru, Mistral, Divvino
- Agregadores: Vivino BR, Hipervinho, Vinho Todo Dia (blog), Winer (blog)
- Particularidade: sem monopolio, venda livre, delivery nationwide
- Resultado: 385 lojas encontradas

## AO FINALIZAR

1. Salve o arquivo `country_config_{pais}.json` na raiz do projeto
2. Imprima um resumo:
   - Quantas regioes/cidades listadas
   - Quantas plataformas identificadas
   - Quantos players grandes na seed list
   - Particularidades importantes (monopolio? restricoes?)
   - Confianca geral do config (alta/media/baixa)
3. Informe se o pais tem alguma particularidade que o Discovery Agent precisa saber
