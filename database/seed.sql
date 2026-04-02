-- ================================================
-- RGVL - SEED DATA - Known Data
-- ================================================

-- ================================================
-- PEOPLE IDENTIFIED
-- ================================================

-- RGVL (Owner - reference)
INSERT INTO people (id, full_name, birth_date, birth_place, cpf, profession, position, company, status, generation, source, notes)
VALUES (1, 'Rodrigo Gorgulho de Vasconcellos Lanna', '1955-12-17', 'Belo Horizonte, MG', '***.516.326-*', 'Civil Engineer', 'Engineering Director', 'Construtora Barbosa Mello S/A', 'active', 4, 'INTEL.md', 'Father of Rodrigo Melo - found');

-- Henrique (Sibling - ONLY one found)
INSERT INTO people (id, full_name, cpf, profession, company, status, generation, source, notes)
VALUES (2, 'Henrique Gorgulho de Vasconcellos Lanna', NULL, 'Engineer/Agronomist', 'ERH Lanna Engenharia Ltda (CNPJ 02.835.659/0001-93)', 'active', 3, 'INTEL.md', 'Sibling of RGVL - ONLY one found. CREA MT13225. Company closed Jun/2024. Address: Rua Prof Bartira Mourao 546 - Buritis BH');

-- Rosalia (RGVL Spouse)
INSERT INTO people (id, full_name, company, status, generation, source, notes)
VALUES (3, 'Rosalia Fagundes Ladeira', 'F Ladeira Consultoria Ltda (CNPJ 40.203.364/0001-93)', 'active', 4, 'INTEL.md', 'RGVL spouse (married 1992). Partner at F Ladeira Consultoria since 2020');

-- Rodrigo Melo Lanna (Son)
INSERT INTO people (id, full_name, profession, status, generation, source, notes)
VALUES (4, 'Rodrigo Melo Lanna', 'Vice President - J.P. Morgan Asset Management', 'active', 5, 'INTEL.md', 'Son of RGVL. LinkedIn: linkedin.com/in/melorodrigo');

-- ================================================
-- RELATIONSHIPS
-- ================================================

-- RGVL is sibling of Henrique
INSERT INTO relationships (person1_id, person2_id, relationship_type, confirmed, source)
VALUES (1, 2, 'sibling', 1, 'INTEL.md - Henrique confirmed as RGVL sibling');

-- RGVL is married to Rosalia
INSERT INTO relationships (person1_id, person2_id, relationship_type, confirmed, source)
VALUES (1, 3, 'spouse', 1, 'INTEL.md - Married since 1992');

-- Rodrigo Melo is son of RGVL
INSERT INTO relationships (person1_id, person2_id, relationship_type, confirmed, source)
VALUES (1, 4, 'child', 1, 'INTEL.md');

-- ================================================
-- COMPANIES
-- ================================================

INSERT INTO companies (cnpj, trade_name, partners, address, city, state, registration_status, opening_date, closing_date, person_id, source, notes)
VALUES
('22.676.938/0001-69', 'RVL Engenharia', '[{"name": "Rodrigo Gorgulho de Vasconcellos Lanna", "participation": "100%"}]', NULL, 'Belo Horizonte', 'MG', 'closed', NULL, NULL, 1, 'INTEL.md', 'RGVL company - 100% his - CLOSED'),

('40.203.364/0001-93', 'F Ladeira Consultoria Ltda', '[{"name": "Rodrigo Gorgulho de Vasconcellos Lanna", "participation": "50%"},{"name": "Rosalia Fagundes Ladeira", "participation": "50%"}]', 'Rua Prof Bartira Mourao 546 - Buritis', 'Belo Horizonte', 'MG', 'active', NULL, NULL, 1, 'INTEL.md', 'Active - partners: RGVL + Rosalia'),

('17.185.786/0001-61', 'Construtora Barbosa Mello S/A', NULL, NULL, NULL, 'MG', 'active', NULL, NULL, 1, 'INTEL.md', 'RGVL is Engineering Director since 1992'),

('02.835.659/0001-93', 'ERH Lanna Engenharia Ltda', '[{"name": "Henrique Gorgulho de Vasconcellos Lanna", "participation": "100%"}]', 'Rua Prof Bartira Mourao 546 - Buritis', 'Belo Horizonte', 'MG', 'closed', '1998', '2024-06-01', 2, 'INTEL.md', 'Henrique company - CLOSED in Jun/2024. 16 legal cases at TJMG');

-- ================================================
-- RESEARCH TASKS - HIGH PRIORITY
-- ================================================

INSERT INTO research_tasks (task, priority, target_person, suggested_sources, status)
VALUES
('Find the 2 unknown siblings of RGVL', 'HIGH', 'Sibling(s) of Rodrigo Gorgulho de Vasconcellos Lanna', 'FamilySearch, JUCEMG, Receita Federal, Google, LinkedIn', 'pending'),

('Confirm if there are more children of RGVL besides Rodrigo Melo', 'HIGH', 'Unknown child(ren) of RGVL', 'FamilySearch, Google', 'pending'),

('Find parents of RGVL (Rodrigo Gorgulho father)', 'HIGH', 'Father of Rodrigo Gorgulho de Vasconcellos Lanna', 'FamilySearch, Receita Federal', 'pending');
