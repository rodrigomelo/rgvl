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
        (6, 'personal_data', '2015-07-28', 'Personal data confirmed in judicial email', 'gmail', 90),
        (6, 'personal_data', '2018-12-16', 'Father data sent by Rodrigo (email "Dados do meu pai")', 'gmail', 95),
        (11, 'legal_case', '2016-11-19', 'Start of paternity investigation case (lawyer: Rodrigo da Cunha Pereira)', 'gmail', 95),
        (11, 'deed', '2017-02-01', 'Paternity Recognition Deed prepared at notary office (lawyer: Caio Cesar Brasil Ferreira)', 'gmail', 95),
        (11, 'deed', '2017-02-08', 'Personal data sent for paternity deed. Chosen name: Rodrigo Melo Lanna', 'gmail', 95),
        (11, 'legal_case', '2018-12-05', 'Emotional abandonment case discussed with lawyer Rodrigo da Cunha Pereira', 'gmail', 90),
        (11, 'legal_case', '2025-11-10', 'Full copy of paternity recognition process requested', 'gmail', 85),
        (11, 'property', '2021-11-14', 'Bradesco real estate financing contract #9078107', 'gmail', 95),
        (11, 'property', '2024-07-12', 'Removal of Lissandra Mity Norichika Onoe from financing #9078107 (domestic partnership dissolution)', 'gmail', 95),
        (11, 'property', '2019-03-14', 'Purchase of Mobi Frei Caneca apartment - Unit 1511, FGTS upfront', 'gmail', 95),
        (11, 'property', '2019-05-31', 'Mobi Frei Caneca 1511 contract registered and available for pickup', 'gmail', 90),
        (11, 'property', '2024-09-18', 'Registered fiduciary assignment and domestic partnership dissolution at 10 RISP notary - Bradesco Contract 9078107', 'gmail', 90),
        (11, 'property', '2024-10-07', 'Fiduciary assignment registration and domestic partnership dissolution at 10 RISP', 'gmail', 90),
        (11, 'name_change', '2025-08-25', 'Administrative surname change request (removal of "da Silva")', 'gmail_drive', 95),
        (11, 'legal_case', '2012-06-26', 'First contact with Dr. Claudia about paternity investigation in MG', 'gmail', 85),
    ]
    evt_count = 0
    for e in events:
        c.execute('SELECT id FROM timeline_events WHERE person_id=? AND event_date=? AND description=?', (e[0], e[2], e[3]))
        if not c.fetchone():
            c.execute('INSERT INTO timeline_events (person_id, event_type, event_date, description, source, confidence) VALUES (?,?,?,?,?,?)', e)
            evt_count += 1
    print(f"[5] Events: {evt_count} added")

    conn.commit()
    conn.close()
    print("\nMigration complete!")

if __name__ == '__main__':
    migrate()
