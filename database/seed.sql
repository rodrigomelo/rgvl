-- ================================================
-- RGVL - SEED DATA - Dados Conhecidos
-- ================================================

-- ================================================
-- PESSOAS JÁ IDENTIFICADAS
-- ================================================

-- RGVL (Próprio - referência)
INSERT INTO pessoas (id, nome_completo, data_nascimento, local_nascimento, cpf, profissao, cargo, empresa, Status, geracao, fonte, observacoes)
VALUES (1, 'Rodrigo Gorgulho de Vasconcellos Lanna', '1955-12-17', 'Belo Horizonte, MG', '***.516.326-*', 'Engenheiro Civil', 'Diretor de Engenharia', 'Construtora Barbosa Mello S/A', 'ativo', 4, 'INTEL.md', 'Pai do Rodrigo Melo - encontrado');

-- Henrique (Irmão - UNICO encontrado)
INSERT INTO pessoas (id, nome_completo, cpf, profissao, empresa, Status, geracao, fonte, observacoes)
VALUES (2, 'Henrique Gorgulho de Vasconcellos Lanna', NULL, 'Engenheiro/Agrônomo', 'ERH Lanna Engenharia Ltda (CNPJ 02.835.659/0001-93)', 'ativo', 3, 'INTEL.md', 'Irmão de RGVL - UNICO encontrado. CREA MT13225. Empresa baixa jun/2024. End: Rua Prof Bartira Mourao 546 - Buritis BH');

-- Rosália (Esposa de RGVL)
INSERT INTO pessoas (id, nome_completo, empresa, Status, geracao, fonte, observacoes)
VALUES (3, 'Rosália Fagundes Ladeira', 'F Ladeira Consultoria Ltda (CNPJ 40.203.364/0001-93)', 'ativo', 4, 'INTEL.md', 'Esposa de RGVL (casados 1992). Sócia na F Ladeira Consultoria desde 2020');

-- Rodrigo Melo Lanna (Filho)
INSERT INTO pessoas (id, nome_completo, profissao, Status, geracao, fonte, observacoes)
VALUES (4, 'Rodrigo Melo Lanna', 'Vice President - J.P. Morgan Asset Management', 'ativo', 5, 'INTEL.md', 'Filho de RGVL. LinkedIn: linkedin.com/in/melorodrigo');

-- ================================================
-- RELACIONAMENTOS
-- ================================================

-- RGVL é irmão de Henrique
INSERT INTO relacionamentos (pessoa_de, pessoa_para, tipo, confirmado, fonte)
VALUES (1, 2, 'irmao', 1, 'INTEL.md - Henrique é irmão confirmado de RGVL');

-- RGVL é casado com Rosália
INSERT INTO relacionamentos (pessoa_de, pessoa_para, tipo, confirmado, fonte)
VALUES (1, 3, 'conjuge', 1, 'INTEL.md - Casados desde 1992');

-- Rodrigo Melo é filho de RGVL
INSERT INTO relacionamentos (pessoa_de, pessoa_para, tipo, confirmado, fonte)
VALUES (1, 4, 'filho', 1, 'INTEL.md');

-- ================================================
-- EMPRESAS
-- ================================================

INSERT INTO empresas_familia (cnpj, nome_fantasia, socios, endereco, cidade, uf, status_jucemg, data_abertura, data_baixa, pessoa_id, fonte, observacoes)
VALUES 
('22.676.938/0001-69', 'RVL Engenharia', '[{"nome": "Rodrigo Gorgulho de Vasconcellos Lanna", "participacao": "100%"}]', NULL, 'Belo Horizonte', 'MG', 'baixa', NULL, NULL, 1, 'INTEL.md', 'Empresa de RGVL - 100% dele - BAIXA'),

('40.203.364/0001-93', 'F Ladeira Consultoria Ltda', '[{"nome": "Rodrigo Gorgulho de Vasconcellos Lanna", "participacao": "50%"},{"nome": "Rosália Fagundes Ladeira", "participacao": "50%"}]', 'Rua Prof Bartira Mourao 546 - Buritis', 'Belo Horizonte', 'MG', 'ativa', NULL, NULL, 1, 'INTEL.md', 'Ativa - sócios: RGVL + Rosália'),

('17.185.786/0001-61', 'Construtora Barbosa Mello S/A', NULL, NULL, NULL, 'MG', 'ativa', NULL, NULL, 1, 'INTEL.md', 'RGVL é Diretor de Engenharia desde 1992'),

('02.835.659/0001-93', 'ERH Lanna Engenharia Ltda', '[{"nome": "Henrique Gorgulho de Vasconcellos Lanna", "participacao": "100%"}]', 'Rua Prof Bartira Mourao 546 - Buritis', 'Belo Horizonte', 'MG', 'baixa', '1998', '2024-06-01', 2, 'INTEL.md', 'Empresa de Henrique - BAIXA em jun/2024. 16 processos no TJMG');

-- ================================================
-- TAREFAS DE PESQUISA - PRIORIDADE ALTA
-- ================================================

INSERT INTO tarefas_pesquisa (tarefa, prioridade, pessoa_alvo, fontes_sugeridas, status)
VALUES 
('Encontrar os 2 irmãos desconhecidos de RGVL', 'ALTA', 'Irmão(s) de Rodrigo Gorgulho de Vasconcellos Lanna', 'FamilySearch, JUCEMG, Receita Federal, Google, LinkedIn', 'pendente'),

('Confirmar se há mais filhos de RGVL além de Rodrigo Melo', 'ALTA', 'Filho(s) desconhecido(s) de RGVL', 'FamilySearch, Google', 'pendente'),

('Encontrar pais de RGVL (pai de Rodrigo Gorgulho)', 'ALTA', 'Pai de Rodrigo Gorgulho de Vasconcellos Lanna', 'FamilySearch, Receita Federal', 'pendente');
