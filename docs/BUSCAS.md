-- ================================================
-- RGVL - QUERIES DE BUSCA - Dados Faltantes
-- Created: 2026-03-19
-- Agent: Poseidon
-- ================================================

-- ================================================
-- CONSULTA 1: Buscar CNPJs no JUCEMG por "Lanna" + BH
-- ================================================
/*
Objetivo: Encontrar empresas dos irmãos desconhecidos
Fonte: JUCEMG (www.jucemg.mg.gov.br)
Query: Buscar todos os CNPJs com "Lanna" em Belo Horizonte, MG
Alternativa: API aberta: https://minhareceita.org/
*/

-- Query para buscar na Receita Federal (via site):
-- https://minhareceita.org/
-- Termo: "Lanna" + "Belo Horizonte" + natureza: "Engenharia"

-- ================================================
-- CONSULTA 2: FamilySearch - 3 Irmãos
-- ================================================
/*
Estratégia:
1. Buscar "Gorgulho de Vasconcellos Lanna" + BH + 1950-1965
2. Filtrar por registros civis (nascimentos)
3. IDs prováveis: Henrique já encontrado, buscar mais 2

URL: https://www.familysearch.org/pt/
Filtros:
- Local: Belo Horizonte, Minas Gerais, Brasil
- Período: 1950-1965
- Nome: Gorgulho de Vasconcellos Lanna
- Tipo: Nascimento
*/

-- ================================================
-- CONSULTA 3: Receita Federal - CPF por Nome
-- ================================================
/*
API não-oficial disponível: https://minhareceita.org/
Permite busca por nome + data de nascimento

Queries:
1. "Henrique Gorgulho de Vasconcellos Lanna"
   → Validar CPF já existente

2. "Rodrigo Gorgulho de Vasconcellos Lanna"
   → Confirmar CPF (temos parcial: ***.516.326-*)

3. Buscar pais:
   - "[Nome do pai] Gorgulho de Vasconcellos Lanna"
   - "[Nome da mãe]" (Ladeira? Ou sobrenome completo?)

4. Buscar irmãos:
   - Padrão: "[Nome] Gorgulho de Vasconcellos Lanna"
   - Usar nome "Gorgulho" como filtro principal
*/

-- ================================================
-- CONSULTA 4: LinkedIn - Buscar "Lanna" + BH
-- ================================================
/*
URL: https://www.linkedin.com/search/results/people/
Query: "Gorgulho de Vasconcellos Lanna"
Local: Belo Horizonte, Minas Gerais, Brasil

Alternativa via Google:
site:linkedin.com/in "Gorgulho" "Lanna" "Belo Horizonte"
*/

-- ================================================
-- CONSULTA 5: TJMG - Processos da Família
-- ================================================
/*
URL: https://www.tjmg.jus.br/
Buscar por nome: "Gorgulho de Vasconcellos Lanna"
Buscar por empresa: "ERH Lanna" (já sabemos de 16 processos de Henrique)
Buscar por empresa: "RVL Engenharia" (RGVL)

Podem revelar familiares em ações judiciais
*/

-- ================================================
-- CONSULTA 6: Google - Busca Geral
-- ================================================
/*
Queries para executar:
1. "Gorgulho de Vasconcellos Lanna" Belo Horizonte
2. "Gorgulho de Vasconcellos Lanna" engenharia
3. "Henrique Lanna" Belo Horizonte
4. "ERH Lanna" engenharia Belo Horizonte
5. "Rodrigo Gorgulho" Lanna Barbosa Mello
6. "Nice Gorgulho de Vasconcellos Lanna" (possível tia - já citada na INTEL)
7. "Edmundo Gorgulho de Vasconcellos Lanna" (possível tio - já citado na INTEL)
*/

-- ================================================
-- SCRIPT: Gerar combinações de nomes para busca
-- ================================================
/*
Nomes comuns para completar padrões:
- Paulo Gorgulho de Vasconcellos Lanna
- Carlos Gorgulho de Vasconcellos Lanna  
- Antonio Gorgulho de Vasconcellos Lanna
- Fernando Gorgulho de Vasconcellos Lanna
- Eduardo Gorgulho de Vasconcellos Lanna
- Maria Gorgulho de Vasconcellos Lanna
- Ana Gorgulho de Vasconcellos Lanna

Estratégia:
1. Buscar todos com "Gorgulho" + "Vasconcellos" + "Lanna" no FamilySearch
2. Cruzar com empresas no JUCEMG
3. Validar nascimentos em BH 1950-1965
*/
