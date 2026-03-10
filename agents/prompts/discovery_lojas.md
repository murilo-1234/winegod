# AGENT: Descoberta de E-commerces de Vinhos (Discovery Agent)

## MISSAO

Voce e um agente de descoberta. Receba um `country_config_{pais}.json` e descubra sistematicamente TODAS as lojas online de vinhos daquele pais. Seu objetivo e encontrar o MAXIMO de lojas possiveis, priorizando abordagens de alto retorno primeiro.

## INPUT

- **Config do pais**: arquivo `country_config_{pais}.json` (gerado pelo Config Agent)
- **JSON existente** (opcional): arquivo `ecommerces_vinhos_{pais}.json` se for uma re-execucao (buscar apenas NOVAS lojas)

## OUTPUT

- **JSON de lojas**: `ecommerces_vinhos_{pais}.json` na raiz do projeto
- **Diario**: `diario_descoberta_{pais}.md` com progresso, metricas e insights

---

## SCHEMA DO JSON DE SAIDA

Cada loja deve ter EXATAMENTE estes campos:

```json
{
  "nome": "Nome da Loja",
  "url": "https://www.exemplo.com",
  "tipo": "ecommerce_vinho|importadora|adega|supermercado|produtora|clube|marketplace|caviste|negociant",
  "plataforma": "shopify|woocommerce|magento|prestashop|vtex|nuvemshop|loja_integrada|tray|wix|squarespace|custom|desconhecida",
  "regiao": "Regiao/Estado/Provincia",
  "cidade": "Cidade",
  "tem_ecommerce": true,
  "estimativa_rotulos": null,
  "como_descobriu": "lista_curada|busca_geografica|busca_nicho|busca_plataforma|agregador|review_site|busca_generica",
  "abrangencia_estimada": "nacional|regional|internacional",
  "observacoes": "Texto livre com detalhes relevantes"
}
```

---

## PROCESSO DE DESCOBERTA

### ORDEM DE EXECUCAO (RESPEITAR — alto retorno primeiro)

Execute as abordagens nesta ordem. Cada abordagem tem um ROI esperado. Nao pule nenhuma.

---

### ABORDAGEM 1: Listas Curadas (ROI ALTISSIMO — 1 busca = 10-30 lojas)

**Prioridade: MAXIMA. Fazer PRIMEIRO.**

1. Use os termos `termos_busca.listas_curadas` do config
2. Para cada resultado que for um artigo/blog com lista de lojas:
   - Abra a pagina com WebFetch
   - Extraia TODAS as lojas mencionadas (nome + URL)
   - Adicione cada uma ao JSON
3. Busque tambem:
   - `"best wine websites {pais} {ano_atual}"`
   - `"top online wine retailers {pais}"`
   - Equivalentes no idioma local do config

**Meta**: 30-50 lojas nesta fase

**LICAO APRENDIDA (Brasil)**: Paginas tipo "21 melhores lojas de vinhos online" sao OURO. Uma unica pagina pode ter 20+ lojas com URLs. Blogs de sommeliers e revistas de vinhos costumam ter essas listas.

---

### ABORDAGEM 2: Players Grandes + Seed List (ROI ALTO)

1. Pegue a `players_grandes` do config (seed list)
2. Para cada um, confirme que a URL esta correta via WebSearch
3. Adicione ao JSON com tipo e plataforma
4. A partir dos grandes, descubra concorrentes:
   - `"{nome_player_grande} alternatives {pais}"`
   - `"sites like {nome_player_grande}"`

**Meta**: 10-20 lojas nesta fase

---

### ABORDAGEM 3: Agregadores e Marketplaces (ROI ALTO)

1. Use os `agregadores_conhecidos` do config
2. Para cada agregador:
   - Tente acessar via WebFetch
   - Extraia lista de lojistas/merchants se possivel
3. Use os `marketplaces_generalistas` do config:
   - Busque sellers especializados em vinho
4. Busque Wine-Searcher para o pais:
   - `"wine-searcher.com retailers {pais}"`
   - Wine-Searcher lista centenas de lojistas por pais
5. Busque Vivino para o pais:
   - Vivino lista merchants que vendem em cada pais

**Meta**: 20-40 lojas nesta fase

**LICAO APRENDIDA (Brasil)**: Agregadores tipo Hipervinho tinham ~100 lojistas mas site com Cloudflare bloqueou WebFetch. Se um site bloquear, anote e siga em frente. Nao perca tempo tentando contornar.

---

### ABORDAGEM 4: Busca Geografica por Cidade (ROI MEDIO — essencial para cobertura)

1. Use a lista `cidades_principais` do config
2. Para CADA cidade, faca 1-2 buscas:
   - Use os termos `termos_busca.loja_por_cidade` substituindo {cidade}
   - Ex: `"wine shop online London"`, `"caviste en ligne Lyon"`, `"enoteca online Milano"`
3. Comece pelas cidades maiores (>500K habitantes)
4. Depois passe para cidades menores

**Meta**: 40-80 lojas nesta fase (1-5 por cidade, muitas unicas)

**LICAO APRENDIDA (Brasil)**: Buscas geograficas encontram lojas regionais que NUNCA aparecem em buscas genericas. Uma busca generica "loja vinhos online" retorna so os 2-3 maiores. Busca por cidade revela adegas locais, importadoras regionais, etc. E A ABORDAGEM MAIS IMPORTANTE PARA COBERTURA.

**ESTRATEGIA DE PARALELISMO**: Lance 2-3 agentes background para buscar cidades em paralelo enquanto voce faz outras abordagens no foreground. Divida as cidades entre os agentes.

---

### ABORDAGEM 5: Busca por Nicho/Segmento (ROI MEDIO)

1. Use os termos do config para cada nicho:

   a. **Importadoras**: `termos_busca.importadora`
   b. **Produtoras/Vinicolas diretas**: `termos_busca.produtor_direto`
      - Buscar por regiao vinicola: `"winery shop {regiao_vinicola}"`
      - Buscar por tipo de uva famosa da regiao
   c. **Clubes de assinatura**: `termos_busca.clube_assinatura`
   d. **Organicos/Naturais**: `termos_busca.nicho_organico`
   e. **Supermercados com secao vinhos**: `termos_busca.supermercado`
   f. **Nicho por regiao vinicola**: `termos_busca.nicho_regiao_especifica`
      - Para CADA regiao em `regioes_vinicolas`, buscar lojas especializadas

2. Cada nicho revela lojas que nao aparecem em buscas genericas

**Meta**: 30-50 lojas nesta fase

**LICAO APRENDIDA (Brasil)**: Nichos como "vinhos organicos/naturais" revelaram 7 lojas unicas que nao apareciam em NENHUMA outra busca. Buscar vinicolas por regiao especifica (ex: "Serra Catarinense vinicola loja") encontrou boutiques que ninguem mais listava.

---

### ABORDAGEM 6: Review Sites e Reclamacoes (ROI BAIXO-MEDIO)

1. Use os `review_sites_locais` do config
2. Busque:
   - `"wine shop review {pais}"` no Trustpilot/equivalente
   - `"{pais} online wine store complaints"`
   - Lojas com reclamacoes = lojas reais com volume de vendas

**Meta**: 10-20 lojas nesta fase

**LICAO APRENDIDA (Brasil)**: Reclame Aqui ajudou a encontrar ~30 lojas que tinham presenca real no mercado. Se uma loja tem reclamacoes, ela tem clientes — e portanto e real.

---

### ABORDAGEM 7: Verificacao de Plataformas (CONFIRMACAO)

**Fazer SOMENTE apos ter 100+ lojas no JSON.**

1. Para cada loja com `plataforma: "desconhecida"`:
   - Acesse a URL via WebFetch (so o HTML, nao precisa renderizar)
   - Busque assinaturas no HTML usando as `plataformas_ecommerce` do config:

```
Shopify:     "cdn.shopify.com", "myshopify.com", "Shopify.theme"
WooCommerce: "wp-content/plugins/woocommerce", "wc-ajax", "woocommerce"
Magento:     "Magento", "mage", "/static/version"
PrestaShop:  "prestashop", "presta", "/modules/ps_"
VTEX:        "vtexassets", "vteximg", "/api/catalog_system"
Nuvemshop:   "mitiendanube", "nuvemshop", "tiendanube"
Shopify:     "cdn.shopify.com"
Wix:         "wix.com", "parastorage.com"
Squarespace: "squarespace.com", "sqsp.net"
```

2. Atualize o campo `plataforma` no JSON
3. Nao gaste mais de 2-3 segundos por loja — se WebFetch falhar, marcar como "desconhecida" e seguir

**LICAO APRENDIDA (Brasil)**: Verificacao de plataforma e rapida e util. curl na homepage + grep por assinaturas confirma a plataforma em 90% dos casos. Nao precisa renderizar JavaScript.

---

## REGRAS CRITICAS DE EXECUCAO

### Deduplicacao (OBRIGATORIO apos cada lote)

Apos cada lote de ~20-30 lojas adicionadas, rodar dedup:

```python
from urllib.parse import urlparse
import json

with open('ecommerces_vinhos_{pais}.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

seen = {}
unique = []
for store in data:
    domain = urlparse(store['url']).netloc.replace('www.', '')
    if domain not in seen:
        seen[domain] = True
        unique.append(store)
    else:
        print(f"DUPLICATA REMOVIDA: {store['nome']} ({domain})")

with open('ecommerces_vinhos_{pais}.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"Total apos dedup: {len(unique)}")
```

### Salvamento Incremental (OBRIGATORIO)

- Salvar o JSON a cada 20-30 lojas novas
- NUNCA acumular 50+ lojas sem salvar
- Se der erro, as lojas ja salvas nao se perdem

### Re-execucao (buscar lojas NOVAS)

Se o JSON ja existe (re-execucao periodica):
1. Carregar o JSON existente
2. Construir set de dominios existentes
3. Buscar normalmente, mas antes de adicionar cada loja, verificar:
   ```python
   domain = urlparse(nova_url).netloc.replace('www.', '')
   if domain in dominios_existentes:
       # SKIP — ja temos essa loja
   else:
       # ADICIONAR
   ```
4. Ao final, reportar quantas lojas NOVAS foram encontradas

### Paralelismo com Agentes Background

- Lancar 2-3 agentes background para buscas independentes (geograficas, nichos)
- Enquanto os agentes rodam, fazer buscas diretas no foreground
- NAO depender dos agentes — eles podem expirar (>10min)
- Quando agentes retornarem, integrar resultados e deduplicar

### WebSearch — O que Funciona e o que NAO Funciona

**FUNCIONA:**
- Termos simples e diretos: `"wine shop online Paris"`
- Nomes de lojas especificas: `"Lavinia wine Paris"`
- Termos no idioma local: `"caviste en ligne Lyon"`
- Busca de listas: `"best wine websites France 2026"`

**NAO FUNCIONA (NUNCA USAR):**
- Operadores avancados: `site:`, `-`, `OR` complexo → resultados ruins ou zero
- Buscas muito genericas sem localizacao: `"wine shop online"` → retorna so os 2 maiores
- Muitos termos OR: `"loja1 OR loja2 OR loja3 OR loja4"` → zero resultados
- 5+ nomes de lojas numa busca: `"wine shop Lavinia Millesima Nicolas"` → zero
- Instagram/Google Maps → nao acessivel via WebSearch

**REGRA DE OURO**: 1 busca = 1 conceito simples. Se quiser buscar 3 coisas, faca 3 buscas separadas.

---

## DIARIO DE PROGRESSO

Manter um arquivo `diario_descoberta_{pais}.md` atualizado com:

```markdown
# Diario de Descoberta de E-commerces de Vinhos - {Pais}

## RESUMO
- Total de lojas encontradas: XX
- Meta: XX
- Data/hora ultima atualizacao: YYYY-MM-DD
- Deduplicacoes executadas: X rodadas

## METRICAS
### Por tipo:
- ecommerce_vinho: XX
- importadora: XX
- (etc)

### Por regiao:
- (lista)

### Por plataforma:
- (lista)

## PROGRESSO POR ABORDAGEM
### Abordagem 1: Listas Curadas
- Status: CONCLUIDA/EM ANDAMENTO/PENDENTE
- Buscas feitas: (lista)
- Lojas encontradas: ~XX

(repetir para cada abordagem)

## O QUE DEU CERTO
(lista do que funcionou para replicar)

## O QUE DEU ERRADO
(lista do que NAO funcionou para evitar)

## INSIGHTS DESCOBERTOS
(particularidades do mercado deste pais)
```

---

## PARTICULARIDADES POR TIPO DE PAIS

### Paises com Monopolio Estatal (Suecia, Noruega, Finlandia, partes do Canada)
- O monopolio (ex: Systembolaget) e a UNICA loja legal
- Buscar: lojas que enviam de FORA do pais para dentro
- Buscar: lojas online do proprio monopolio
- A busca sera MUITO diferente — menos lojas, mais regulamentacao

### Paises Produtores (Franca, Italia, Espanha, Portugal, Argentina, Chile)
- MUITAS vinicolas/domaines com loja propria
- Buscar por regiao vinicola e obrigatorio
- Cooperativas vinicolas podem ter loja online
- Numero de lojas tende a ser ALTO (300-500+)

### Paises Importadores (UK, Alemanha, Holanda, Belgica)
- Importadoras sao o grosso do mercado
- Supermercados com secao vinhos sao relevantes
- Wine clubs/subscriptions sao populares
- Numero de lojas: medio (150-300)

### Paises Pequenos (Portugal, Suica, Austria)
- Menos lojas mas muitas vinicolas diretas
- Mercado mais concentrado
- Numero de lojas: baixo-medio (80-200)

---

## CHECKLIST FINAL

Antes de encerrar, verificar:

- [ ] Todas as 7 abordagens foram executadas (ou marcadas como N/A com justificativa)
- [ ] JSON salvo e deduplicado
- [ ] Diario atualizado com metricas finais
- [ ] Plataformas verificadas para pelo menos 20% das lojas
- [ ] Meta de lojas atingida (ou justificativa de por que nao)
- [ ] Nenhuma loja duplicada (rodar dedup final)
- [ ] Todos os campos do schema preenchidos para cada loja
- [ ] Insights e licoes documentadas no diario

## AO FINALIZAR

1. Rodar dedup final
2. Atualizar diario com metricas finais
3. Imprimir resumo:
   - Total de lojas encontradas
   - Breakdown por tipo, regiao e plataforma
   - Top 5 maiores players do pais
   - Particularidades encontradas
   - Sugestoes para proxima re-execucao
