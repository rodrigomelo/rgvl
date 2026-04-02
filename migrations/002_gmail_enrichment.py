#!/usr/bin/env python3
"""
Migration: Gmail/Drive investigation data enrichment
Date: 2026-03-29
Source: Email extraction from melorodrigo@gmail.com

Changes:
- Added ex-partner Lissandra Mity Norichika Onoe (id=31)
- 12 document records (IDs, certs, contracts)
- 6 timeline events (property, legal, name change)
- Updated father (id=6): email, profession, address
- Updated mother (id=27): CPF, RG
"""

import sqlite3, os, sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'rgvl.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Add Lissandra
    c.execute("INSERT OR IGNORE INTO people (full_name, cpf, status, source, notes) VALUES (?, ?, ?, ?, ?)",
              ('Lissandra Mity Norichika Onoe', '348.391.958-97', 'ex-partner', 'gmail_bradesco',
               'Domestic partnership dissolved 2024, no asset division, no children'))
    print(f"[1] Lissandra: {'added' if c.rowcount else 'exists'}")

    # 2. Update father (id=6)
    c.execute("UPDATE people SET email='rlanna@cbmsa.com.br', profession='Engineer', address='Rua Ceara, 1305, Apto 1202, Bairro Funcionarios, Belo Horizonte, MG' WHERE id=6")
    print(f"[2] Father updated: {c.rowcount} rows")

    # 3. Update mother (id=27)
    c.execute("UPDATE people SET cpf='294.043.982-68', rg='22.999.211-0', birth_place='Itaituba, PA' WHERE id=27")
    print(f"[3] Mother updated: {c.rowcount} rows")

    # 4. Documents
    docs = [
        ('identificacao', 'Titulo de Eleitor - Rodrigo Melo Lanna', '325194820132, Zona 006, Secao 313, emitido 2003-01-16', None, '2003-01-16', None, 'gmail'),
        ('identificacao', 'Certificado de Alistamento Militar - Rodrigo Melo Lanna', '040403113695, 2aRM-4aCM JSM Vila Mariana, 2003-01-16 a 2003-12-31', None, '2003-01-16', '2003-12-31', 'gmail'),
        ('identificacao', 'Cartao do Cidadao/PIS - Rodrigo Melo Lanna', '13378939892-02, emitido 2010-01-28', None, '2010-01-28', None, 'gmail'),
        ('identificacao', 'RG - Rodrigo Melo Lanna', '38.204.405-8, SSP/SP, emitido 2015-03-26', None, '2015-03-26', None, 'gmail'),
        ('cpf', 'CPF - Rodrigo Melo Lanna', '317.462.238-71', None, None, None, 'gmail'),
        ('cpf', 'CPF - Joana Ivanete Silva Melo', '294.043.982-68', None, None, None, 'gmail'),
        ('cpf', 'CPF - Lissandra Mity Norichika Onoe', '348.391.958-97', None, None, None, 'gmail_bradesco'),
        ('certidao', 'Certidao de Nascimento - Rodrigo Melo Lanna', '038205, Cartorio 2 Oficio de Itaituba, Livro A064, Folha 0038', None, None, None, 'gmail'),
        ('certidao', 'Certidao de Nascimento - Joana Ivanete Silva Melo', '7434, Cartorio 2 Oficio de Itaituba, Livro A027, Folha 289', None, None, None, 'gmail'),
        ('contrato', 'Contrato Financiamento Imobiliario Bradesco #9078107', 'Financiamento apartamento, 2021-11-14', None, '2021-11-14', None, 'gmail_bradesco'),
        ('contrato', 'Exclusao de Mutuario - Bradesco #9078107', 'Exclusao de Lissandra, 2024-09-18', None, '2024-09-18', None, 'gmail_bradesco'),
        ('escritura', 'Requerimento Alteracao de Sobrenome - Rodrigo Melo Lanna', 'Exclusao de "da Silva", 2025-08-25', None, '2025-08-25', None, 'gmail_drive'),
    ]
    doc_count = 0
    for d in docs:
        c.execute('SELECT id FROM documents WHERE title=?', (d[1],))
        if not c.fetchone():
            c.execute('INSERT INTO documents (doc_type, title, description, file_path, issue_date, expiry_date, source) VALUES (?,?,?,?,?,?,?)', d)
            doc_count += 1
    print(f"[4] Documents: {doc_count} added")

    # 5. Timeline events
    events = [
        (6, 'DADOS_PESSOAIS', '2015-07-28', 'Dados pessoais confirmados em email judicial', 'gmail', 90),
        (6, 'DADOS_PESSOAIS', '2018-12-16', 'Dados do pai enviados por Rodrigo (email "Dados do meu pai")', 'gmail', 95),
        (11, 'PROCESSO_JUDICIAL', '2016-11-19', 'Inicio do caso de investigacao de paternidade (advogado: Rodrigo da Cunha Pereira)', 'gmail', 95),
        (11, 'ESCRITURA', '2017-02-01', 'Escritura de Reconhecimento de Paternidade preparada pelo cartorio (advogado: Caio Cesar Brasil Ferreira)', 'gmail', 95),
        (11, 'ESCRITURA', '2017-02-08', 'Dados pessoais enviados para escritura de paternidade. Nome escolhido: Rodrigo Melo Lanna', 'gmail', 95),
        (11, 'PROCESSO_JUDICIAL', '2018-12-05', 'Caso de abandono paterno afetivo discutido com advogado Rodrigo da Cunha Pereira', 'gmail', 90),
        (11, 'PROCESSO_JUDICIAL', '2025-11-10', 'Solicitada copia integral do processo de reconhecimento de paternidade', 'gmail', 85),
        (11, 'IMOVEL', '2021-11-14', 'Contrato de financiamento imobiliario Bradesco #9078107', 'gmail', 95),
        (11, 'IMOVEL', '2024-07-12', 'Exclusao de mutuaria Lissandra Mity Norichika Onoe do financiamento #9078107 (dissolucao uniao estavel)', 'gmail', 95),
        (11, 'IMOVEL', '2019-03-14', 'Compra apartamento Mobi Frei Caneca - Unidade 1511, FGTS a vista', 'gmail', 95),
        (11, 'IMOVEL', '2019-05-31', 'Contrato Mobi Frei Caneca 1511 registrado e disponivel para retirada', 'gmail', 90),
        (11, 'IMOVEL', '2024-09-18', 'Exclusao de mutuaria registrada no 10 RISP - Contrato Bradesco 9078107', 'gmail', 90),
        (11, 'IMOVEL', '2024-10-07', 'Registro cessao fiduciante e dissolucao uniao estavel no cartorio 10 RISP', 'gmail', 90),
        (11, 'NOME', '2025-08-25', 'Requerimento administrativo de alteracao de sobrenome (exclusao de da Silva)', 'gmail_drive', 95),
        (11, 'PROCESSO_JUDICIAL', '2012-06-26', 'Primeiro contato com Dra. Claudia sobre investigacao de paternidade em MG', 'gmail', 85),
    ]
    evt_count = 0
    for e in events:
        c.execute('SELECT id FROM events WHERE person_id=? AND event_date=? AND description=?', (e[0], e[2], e[3]))
        if not c.fetchone():
            c.execute('INSERT INTO events (person_id, event_type, event_date, description, source, confidence) VALUES (?,?,?,?,?,?)', e)
            evt_count += 1
    print(f"[5] Events: {evt_count} added")

    conn.commit()
    conn.close()
    print("\nMigration complete!")

if __name__ == '__main__':
    migrate()
