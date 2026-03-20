"""
RGVL ETL - Seed Database

Populates the canonical database with all family research data.
Run once or re-run to refresh data.

Usage:
    cd rgvl && python -m etl.seed              # safe (won't wipe)
    cd rgvl && python -m etl.seed --force      # wipe and reseed
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.db import engine, get_session, DB_PATH
from api.models import (
    Base, Pessoa, Relacionamento, Empresa, Imovel,
    ProcessoJudicial, Documento, Contato, Evento,
    TarefaPesquisa,
)


def seed(force=False):
    """Populate the database with all known family data."""

    Base.metadata.create_all(bind=engine)
    print(f'📦 Database: {DB_PATH}')

    db = get_session()

    try:
        existing_count = db.query(Pessoa).count()
        if existing_count > 0 and not force:
            print(f'⚠️  Database already has {existing_count} people.')
            print('   Use --force to wipe and reseed: python -m etl.seed --force')
            return

        # Wipe all tables (order matters for FK constraints)
        for model in [TarefaPesquisa, Evento, Contato, Documento,
                      ProcessoJudicial, Imovel, Empresa,
                      Relacionamento, Pessoa]:
            db.query(model).delete()
        db.commit()
        print('🗑️  Cleared all tables')

        # =====================================================================
        # PESSOAS (26)
        # =====================================================================

        # Geração 5 — Bisavós
        bisavo_edmundo = Pessoa(
            nome_completo='Edmundo Mariano da Costa Lanna',
            data_nascimento='1878',
            data_falecimento='1968',
            profissao='Dentista',
            status='falecido',
            geracao=5,
            fonte='FamilySearch (G9PX-G84)',
        )

        # Geração 4 — Avós
        avo_edmundo = Pessoa(
            nome_completo='Edmundo de Vasconcellos Lanna',
            data_nascimento='1922-04-24',
            local_nascimento='Barra Longa, MG',
            data_falecimento='1992-11-04',
            cpf='000.558.676-*',
            profissao='Dentista',
            status='falecido',
            geracao=4,
            fonte='FamilySearch',
            observacoes='Sepultado em BH.',
        )

        avo_nice = Pessoa(
            nome_completo='Nice Gorgulho de Vasconcellos Lanna',
            data_nascimento='1926',
            data_falecimento='2019',
            status='falecido',
            geracao=4,
            fonte='INTEL.md',
        )

        tia_avo_thereza = Pessoa(
            nome_completo='Thereza de Vasconcellos Lanna',
            data_nascimento='1923',
            data_falecimento='2006',
            status='falecido',
            geracao=4,
            fonte='familialana.com',
        )

        tia_avo_maria = Pessoa(
            nome_completo='Maria Auxiliadora de Vasconcellos Lanna',
            data_nascimento='1925',
            data_falecimento='2018',
            status='falecido',
            geracao=4,
            fonte='familialana.com',
        )

        db.add_all([bisavo_edmundo, avo_edmundo, avo_nice, tia_avo_thereza, tia_avo_maria])
        db.flush()

        avo_edmundo.pai_id = bisavo_edmundo.id

        # Geração 3 — Pais + Tios
        pai = Pessoa(
            nome_completo='Rodrigo Gorgulho de Vasconcellos Lanna',
            data_nascimento='1955-12-17',
            local_nascimento='Belo Horizonte, MG',
            cpf='314.516.326-49',
            rg='24.920/D',
            profissao='Engenheiro Civil',
            cargo='Diretor de Engenharia',
            empresa='Construtora Barbosa Mello S/A',
            email='rodrigo.lanna@barbosamello.com.br',
            telefone='(31) 3490-3600',
            endereco='Rua Gonçalves Dias 865, Apto 1201, Funcionários, BH/MG, CEP 30140-091',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='CREA-MG 24.920/D',
            observacoes='Casado com Rosália desde 1992. Diretor na Barbosa Mello desde 2013.',
        )

        mae = Pessoa(
            nome_completo='Rosália Fagundes Ladeira',
            rg='MG-313.077',
            cpf='359.959.806-10',
            profissao='Arquiteta',
            email='rosalia.ladeira@barbosamello.com.br',
            telefone='(31) 3490-3611',
            endereco='Rua Prof Bartira Mourão 546, Buritis, BH/MG',
            status='ativo',
            geracao=3,
            fonte='INTEL.md',
            observacoes='Sócia na F Ladeira Consultoria Ltda desde 2020.',
        )

        tio_henrique = Pessoa(
            nome_completo='Henrique Gorgulho de Vasconcellos Lanna',
            data_nascimento='1966-05-22',
            cpf='***.257.066-*',
            profissao='Engenheiro/Agrônomo',
            empresa='ERH Lanna Engenharia Ltda (CNPJ 02.835.659/0001-93)',
            endereco='Rua Prof Bartira Mourão 546, Apto 701, Buritis, BH/MG, CEP 30492-025',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='CREA MT13225/VD',
            observacoes='Empresa baixada jun/2024. 16+ processos no TJMG.',
        )

        tio_marcelo = Pessoa(
            nome_completo='Marcelo Gorgulho de Vasconcellos Lanna',
            local_nascimento='Belo Horizonte, MG',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='Facebook research 2016',
            observacoes='22-25 processos no TJMG (BMG, AF Administradora). Casado com Mônica Maria Almeida Lanna.',
        )

        tia_junia = Pessoa(
            nome_completo='Júnia Gorgulho de Vasconcellos Lanna',
            cpf='064.327.216-01',
            profissao='Presidente AVOSC',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='Escavador',
            observacoes='Vice-Presidente AVOSC (2011), Presidente AVOSC (2016). CNPJ 17.508.888/0001-70.',
        )

        db.add_all([pai, mae, tio_henrique, tio_marcelo, tia_junia])
        db.flush()

        pai.conjuge_id = mae.id
        pai.data_casamento = '1992'
        mae_conjuge_id = pai.id

        # Geração 1 — Rodrigo Melo (the user) + Primos
        voce = Pessoa(
            nome_completo='Rodrigo Melo Lanna',
            nome_anterior='Rodrigo da Silva Melo',
            local_nascimento='Itaituba, PA',
            profissao='Vice President',
            empresa='J.P. Morgan Asset Management',
            endereco='São Paulo, SP',
            pai_id=pai.id,
            status='ativo',
            geracao=1,
            fonte='LinkedIn (linkedin.com/in/melorodrigo)',
            observacoes='Nome alterado em 2025: Rodrigo da Silva Melo → Rodrigo Melo Lanna. Reconhecimento de paternidade fev/2017 (escritura pública).',
        )

        db.add(voce)
        db.flush()

        # Geração 1 — Primos
        primos_henrique = [
            ('Luiza Lanna', 'Filha de Henrique. Colégio Marista Dom Silvério.'),
            ('Fernanda Lanna', 'Filha de Henrique.'),
            ('Alessandra Lanna', 'Filha de Henrique.'),
            ('Paula Lanna', 'Filha de Henrique.'),
            ('Antônio Bahury Lanna', 'Filho de Henrique. Colégio Santa Doroteia.'),
            ('João Vítor Lanna', 'Filho de Henrique. Colégio Santa Doroteia.'),
        ]

        primos_marcelo = [
            ('Marcela Lanna', 'Filha de Marcelo. Escola Santo Tomás de Aquino.'),
            ('Andre Lanna', 'Filho de Marcelo. Escola Santo Tomás de Aquino.'),
            ('Bruno Lanna', 'Filho de Marcelo.'),
            ('Edmundo Lanna', 'Filho de Marcelo. Nome do bisavô.'),
        ]

        primos_junia = [
            ('Andrea Lanna', 'Filha de Júnia. Liceu Albert Sabin - Ribeirão Preto.'),
            ('Paula Lanna Silva', 'Filha de Júnia. Liceu Albert Sabin - Ribeirão Preto.'),
            ('Vivi Lanna', 'Filha de Júnia.'),
            ('Pichita Lanna', 'Filho de Júnia. Dono de buffet e restaurante.'),
            ('Julia Lanna', 'Filha de Júnia. Colégio Marista Dom Silvério.'),
        ]

        primos = []
        for nome, obs in primos_henrique:
            primos.append(Pessoa(
                nome_completo=nome, pai_id=tio_henrique.id,
                geracao=1, status='ativo',
                fonte='Facebook research 2016', observacoes=obs,
            ))
        for nome, obs in primos_marcelo:
            primos.append(Pessoa(
                nome_completo=nome, pai_id=tio_marcelo.id,
                geracao=1, status='ativo',
                fonte='Facebook research 2016', observacoes=obs,
            ))
        for nome, obs in primos_junia:
            primos.append(Pessoa(
                nome_completo=nome, mae_id=tia_junia.id,
                geracao=1, status='ativo',
                fonte='Facebook research 2016', observacoes=obs,
            ))

        db.add_all(primos)
        db.flush()
        print(f'✅ Pessoas: {db.query(Pessoa).count()}')

        # =====================================================================
        # RELACIONAMENTOS (30)
        # =====================================================================

        relationships = [
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=avo_edmundo.id, tipo='filho', confirmado=1, fonte='FamilySearch'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=avo_nice.id, tipo='conjuge', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=pai.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_nice.id, pessoa_para=pai.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=mae.id, tipo='conjuge', confirmado=1, fonte='casados 1992'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=voce.id, tipo='filho', confirmado=1, fonte='escritura 2017'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=tio_henrique.id, tipo='irmao', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=tio_marcelo.id, tipo='irmao', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=tia_junia.id, tipo='irma', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=tio_henrique.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=tio_marcelo.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=tia_junia.id, tipo='filha', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=tia_avo_thereza.id, tipo='filha', confirmado=1, fonte='familialana.com'),
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=tia_avo_maria.id, tipo='filha', confirmado=1, fonte='familialana.com'),
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=avo_nice.id, tipo='nora', confirmado=1, fonte='INTEL.md'),
        ]

        for primo in primos[:6]:
            relationships.append(Relacionamento(
                pessoa_de=tio_henrique.id, pessoa_para=primo.id,
                tipo='filho' if 'Lanna' in primo.nome_completo else 'filha',
                confirmado=0, fonte='Facebook 2016 (speculative)',
            ))
        for primo in primos[6:10]:
            relationships.append(Relacionamento(
                pessoa_de=tio_marcelo.id, pessoa_para=primo.id,
                tipo='filho' if 'Lanna' in primo.nome_completo else 'filha',
                confirmado=0, fonte='Facebook 2016 (speculative)',
            ))
        for primo in primos[10:]:
            relationships.append(Relacionamento(
                pessoa_de=tia_junia.id, pessoa_para=primo.id,
                tipo='filho' if any(n in primo.nome_completo for n in ['Pichita']) else 'filha',
                confirmado=0, fonte='Facebook 2016 (speculative)',
            ))

        db.add_all(relationships)
        db.flush()
        print(f'✅ Relacionamentos: {len(relationships)}')

        # =====================================================================
        # EMPRESAS (10)
        # =====================================================================

        companies = [
            Empresa(
                cnpj='22.676.938/0001-69', nome_fantasia='RVL Engenharia',
                razao_social='RVL Engenharia EPP',
                cidade='Belo Horizonte', uf='MG', status_jucemg='baixa',
                data_abertura='2015', pessoa_id=pai.id,
                socios=json.dumps([{'nome': 'Rodrigo Gorgulho de Vasconcellos Lanna', 'participacao': '100%'}]),
                fonte='INTEL.md', observacoes='Empresa de RGVL - 100% dele. BAIXA.',
            ),
            Empresa(
                cnpj='40.203.364/0001-93', nome_fantasia='F Ladeira Consultoria',
                razao_social='F Ladeira Consultoria Ltda',
                endereco='Rua Prof Bartira Mourão 546 - Buritis',
                cidade='Belo Horizonte', uf='MG', status_jucemg='ativa',
                pessoa_id=pai.id,
                socios=json.dumps([
                    {'nome': 'Rodrigo Gorgulho de Vasconcellos Lanna', 'participacao': '50%'},
                    {'nome': 'Rosália Fagundes Ladeira', 'participacao': '50%'},
                ]),
                fonte='INTEL.md', observacoes='Ativa desde 2020. Sócios: RGVL + Rosália.',
            ),
            Empresa(
                cnpj='17.185.786/0001-61', nome_fantasia='Construtora Barbosa Mello',
                razao_social='Construtora Barbosa Mello S/A',
                endereco='Rua Paraíba 1124, Savassi',
                cidade='Belo Horizonte', uf='MG', status_jucemg='ativa',
                capital=154768281.0, pessoa_id=pai.id,
                fonte='INTEL.md',
                observacoes='Diretor de Engenharia desde 2013. Capital social R$ 154.768.281.',
            ),
            Empresa(
                cnpj='07.514.378/0001-52', nome_fantasia='Consórcio Sossego',
                razao_social='Consórcio Sossego',
                cidade='Canaã dos Carajás', uf='PA', status_jucemg='ativa',
                pessoa_id=pai.id,
                fonte='INTEL.md', observacoes='Admin do consórcio desde 2019.',
            ),
            Empresa(
                cnpj='41.929.586/0001-50', nome_fantasia='Construtora Barbosa Mello SCP',
                razao_social='Construtora Barbosa Mello SCP 0125',
                cidade='Parauapebas', uf='PA', status_jucemg='ativa',
                capital=1000000.0, pessoa_id=pai.id,
                fonte='INTEL.md', observacoes='SCP ativa desde 2021.',
            ),
            Empresa(
                cnpj='02.835.659/0001-93', nome_fantasia='ERH Lanna Engenharia',
                razao_social='ERH Lanna Engenharia Ltda',
                endereco='Rua Prof Bartira Mourão 546 - Buritis',
                cidade='Belo Horizonte', uf='MG', status_jucemg='baixa',
                data_abertura='1998', data_baixa='2024-06-01',
                pessoa_id=tio_henrique.id,
                socios=json.dumps([{'nome': 'Henrique Gorgulho de Vasconcellos Lanna', 'participacao': '100%'}]),
                fonte='CREA MT13225/VD',
                observacoes='Empresa de Henrique. BAIXA jun/2024. 16+ processos no TJMG.',
            ),
            Empresa(
                cnpj='17.508.888/0001-70', nome_fantasia='AVOSC',
                razao_social='Associação das Voluntárias da Santa Casa',
                cidade='Belo Horizonte', uf='MG', status_jucemg='ativa',
                pessoa_id=tia_junia.id,
                fonte='Escavador',
                observacoes='Júnia foi Vice-Presidente (2011) e Presidente (2016).',
            ),
            Empresa(
                cnpj='00.000.000/0001-01', nome_fantasia='Consórcio Uchoa',
                razao_social='Consórcio Uchoa',
                cidade='Belo Horizonte', uf='MG', status_jucemg='baixa',
                pessoa_id=pai.id,
                fonte='INTEL.md', observacoes='Consórcio encerrado.',
            ),
            Empresa(
                cnpj='00.000.000/0001-02', nome_fantasia='Consórcio TKL',
                razao_social='Consórcio TKL',
                cidade='Belo Horizonte', uf='MG', status_jucemg='baixa',
                pessoa_id=pai.id,
                fonte='INTEL.md', observacoes='Consórcio encerrado.',
            ),
            Empresa(
                cnpj='00.000.000/0001-03', nome_fantasia='EBTE',
                razao_social='EBTE Engenharia e Montagens Ltda',
                cidade='Belo Horizonte', uf='MG', status_jucemg='ativa',
                pessoa_id=pai.id,
                fonte='INTEL.md', observacoes='Empresa ativa vinculada a RGVL.',
            ),
        ]

        db.add_all(companies)
        db.flush()
        print(f'✅ Empresas: {len(companies)}')

        # =====================================================================
        # IMÓVEIS (3)
        # =====================================================================

        properties = [
            Imovel(
                property_type='Apartamento',
                address='Rua Gonçalves Dias, 865, Apto. 1201',
                city='Belo Horizonte', state='MG',
                neighborhood='Funcionários',
                building_name='Quintas da Liberdade Fine Residence',
                floor='12',
                area_sqm=373.28, area_total=550.0,
                bedrooms=4, parking_spaces=5,
                owners=json.dumps([
                    'Rodrigo Gorgulho de Vasconcellos Lanna',
                    'Rosália Fagundes Ladeira',
                ]),
                purchase_date='2017-12-21',
                purchase_value=3930700.90,
                financing_value=1450000.00,
                itbi=119999.96,
                current_value=10450000.00,
                status='paid_off',
                registration='121.974',
                cartorio='3° Ofício - Cartório Bolívar',
                fonte='Registro público de imóveis - 3° Ofício, BH',
            ),
            Imovel(
                property_type='Apartamento',
                address='Rua Oliveira, 259, Apto. 303',
                city='Belo Horizonte', state='MG',
                neighborhood='Cruzeiro',
                building_name='El Bacha IV',
                area_sqm=245.5, area_total=341.25,
                bedrooms=3, parking_spaces=2,
                owners=json.dumps(['Rodrigo Gorgulho de Vasconcellos Lanna']),
                purchase_date='1982-03-16',
                current_value=3037125.00,
                status='paid_off',
                registration='15.902',
                cartorio='2° Ofício de Registro de Imóveis',
                fonte='Registro público de imóveis - 2° Ofício, BH',
            ),
            Imovel(
                property_type='Apartamento',
                address='Rua Nisio Batista de Oliveira, 158, Apto. 402',
                city='Belo Horizonte', state='MG',
                neighborhood='Novo São Lucas',
                building_name='Ed. Rio Verde',
                owners=json.dumps([
                    'Edmundo de Vasconcellos Lanna (falecido)',
                    'Herdeiros a verificar',
                ]),
                status='inventariar',
                fonte='venda-imoveis.caixa.gov.br',
                description='Antigo patrimônio do avô Edmundo (falecido 1992). Confirmar situação do inventário e titularidade atual.',
            ),
        ]

        db.add_all(properties)
        db.flush()
        print(f'✅ Imóveis: {len(properties)}')

        # =====================================================================
        # PROCESSOS JUDICIAIS (9)
        # =====================================================================

        processes = [
            ProcessoJudicial(
                process_number='1044263-83.2026.8.13.0024',
                court='TJMG',
                subject='Consumidor - Azul Linhas Aéreas',
                status='Em andamento',
                fonte='INTEL.md',
            ),
            ProcessoJudicial(
                process_number='0012345-78.2025.8.13.0001',
                court='TJMG',
                subject='Reconhecimento de Paternidade',
                status='Concluído',
                fonte='INTEL.md',
            ),
            ProcessoJudicial(
                process_number='0806055-21.2025.8.14.0024',
                court='TJSP',
                subject='Alteração de Nome',
                status='Trânsito em julgado',
                fonte='INTEL.md',
            ),
        ]

        # 6 trabalhistas no TRT3
        trt3_cases = [
            '0010863-18.2020.5.03.0025',
            '0010726-82.2019.5.03.0125',
            '0010956-45.2021.5.03.0025',
            '0010521-71.2020.5.03.0025',
            '0010398-42.2019.5.03.0125',
            '0010687-33.2022.5.03.0025',
        ]
        for num in trt3_cases:
            processes.append(ProcessoJudicial(
                process_number=num,
                court='TRT3',
                subject='Trabalhista',
                status='Em andamento',
                fonte='INTEL.md',
            ))

        db.add_all(processes)
        db.flush()
        print(f'✅ Processos judiciais: {len(processes)}')

        # =====================================================================
        # DOCUMENTOS (5)
        # =====================================================================

        documents = [
            Documento(
                doc_type='rg', title='RG - Rodrigo Gorgulho de Vasconcellos Lanna',
                description='Registro Geral MG-594.589 / 24.920/D (CREA)',
                fonte='CREA-MG',
            ),
            Documento(
                doc_type='cpf', title='CPF - Rodrigo Gorgulho de Vasconcellos Lanna',
                description='314.516.326-49',
                fonte='INTEL.md',
            ),
            Documento(
                doc_type='cpf', title='CPF - Rosália Fagundes Ladeira',
                description='359.959.806-10',
                fonte='INTEL.md',
            ),
            Documento(
                doc_type='cpf', title='CPF - Júnia Gorgulho de Vasconcellos Lanna',
                description='064.327.216-01',
                fonte='Escavador',
            ),
            Documento(
                doc_type='escritura',
                title='Escritura de Reconhecimento de Paternidade',
                description='Reconhecimento voluntário de paternidade - Rodrigo Gorgulho → Rodrigo Melo Lanna. Cartório, fev/2017.',
                fonte='Email 159fa891a9a5546f',
            ),
        ]

        db.add_all(documents)
        db.flush()
        print(f'✅ Documentos: {len(documents)}')

        # =====================================================================
        # CONTATOS (3)
        # =====================================================================

        contacts = [
            Contato(
                nome='Rodrigo da Cunha Pereira',
                role='Advogado',
                empresa=' escritório próprio',
                telefone='+55 31 3335-9450',
                email='rcp@rodrigodacunha.adv.br',
                is_primary=True,
                notes='Advogado principal - consulta inicial nov/2016, escritura de paternidade fev/2017',
                fonte='Emails',
            ),
            Contato(
                nome='Caio César Brasil Ferreira',
                role='Advogado',
                empresa=' escritório Rodrigo da Cunha',
                telefone='+55 31 8745-8245',
                email='caio@rodrigodacunha.adv.br',
                is_primary=False,
                notes='Advogado associado',
                fonte='Emails',
            ),
            Contato(
                nome='Cartório 2° Ofício de Registro de Imóveis',
                role='Cartório',
                empresa='Belo Horizonte, MG',
                is_primary=False,
                notes='Matrícula 15.902 - El Bacha IV',
                fonte='INTEL.md',
            ),
        ]

        db.add_all(contacts)
        db.flush()
        print(f'✅ Contatos: {len(contacts)}')

        # =====================================================================
        # EVENTOS (9)
        # =====================================================================

        events = [
            Evento(person_id=voce.id, event_type='nascimento', event_date='~1980',
                   description='Rodrigo Melo nascido em Itaituba/PA'),
            Evento(person_id=voce.id, event_type='contato_familiar', event_date='~2008',
                   description='Primeiro contato com família paterna via telefone da avó'),
            Evento(person_id=voce.id, event_type='contato_familiar', event_date='~2011',
                   description='Segundo contato - email de trabalho encontrado'),
            Evento(person_id=voce.id, event_type='juridico', event_date='2016-11',
                   description='Consulta jurídica inicial com Rodrigo da Cunha Pereira'),
            Evento(person_id=voce.id, event_type='pesquisa', event_date='2016-11',
                   description='Mapeamento completo da família via Facebook'),
            Evento(person_id=voce.id, event_type='reconhecimento_paternidade', event_date='2017-02',
                   description='Escritura pública voluntária de reconhecimento de paternidade'),
            Evento(person_id=voce.id, event_type='juridico', event_date='2018-12',
                   description='Abandono paterno afetivo - processo consultado mas não ajuizado'),
            Evento(person_id=voce.id, event_type='alteracao_nome', event_date='2025',
                   description='Rodrigo da Silva Melo → Rodrigo Melo Lanna'),
            Evento(person_id=avo_edmundo.id, event_type='falecimento', event_date='1992-11-04',
                   description='Edmundo de Vasconcellos Lanna faleceu. Sepultado em BH.'),
        ]

        db.add_all(events)
        db.flush()
        print(f'✅ Eventos: {len(events)}')

        # =====================================================================
        # TAREFAS DE PESQUISA (5)
        # =====================================================================

        tasks = [
            TarefaPesquisa(
                tarefa='Encontrar os 2 irmãos desconhecidos de RGVL (filhos de Edmundo + Nice além de Henrique, Marcelo, Júnia)',
                prioridade='ALTA',
                pessoa_alvo='Irmão(s) de Rodrigo Gorgulho de Vasconcellos Lanna',
                fontes_sugeridas='FamilySearch, JUCEMG, Receita Federal, Google, LinkedIn',
                status='pendente',
            ),
            TarefaPesquisa(
                tarefa='Confirmar se há mais filhos de RGVL além de Rodrigo Melo',
                prioridade='ALTA',
                pessoa_alvo='Filho(s) desconhecido(s) de RGVL',
                fontes_sugeridas='FamilySearch, Google',
                status='pendente',
            ),
            TarefaPesquisa(
                tarefa='Investigar processos judiciais de Marcelo (BMG, AF Administradora)',
                prioridade='MEDIA',
                pessoa_alvo='Marcelo Gorgulho de Vasconcellos Lanna',
                fontes_sugeridas='TJMG, Escavador',
                status='pendente',
            ),
            TarefaPesquisa(
                tarefa='Mapear filhos de Henrique (6 primos conhecidos)',
                prioridade='MEDIA',
                pessoa_alvo='Filhos de Henrique Gorgulho de Vasconcellos Lanna',
                fontes_sugeridas='Google, Facebook, LinkedIn',
                status='pendente',
            ),
            TarefaPesquisa(
                tarefa='Pesquisar Consórcio Sossego e SCP 0125 em detalhes',
                prioridade='BAIXA',
                pessoa_alvo='Rodrigo Gorgulho de Vasconcellos Lanna',
                fontes_sugeridas='JUCEMG, Receita Federal, Canaã dos Carajás',
                status='pendente',
            ),
        ]

        db.add_all(tasks)
        db.flush()
        print(f'✅ Tarefas: {len(tasks)}')

        # =====================================================================
        # COMMIT
        # =====================================================================

        db.commit()
        print(f'\n🎉 Database seeded successfully!')
        print(f'   Pessoas:             {db.query(Pessoa).count()}')
        print(f'   Relacionamentos:     {db.query(Relacionamento).count()}')
        print(f'   Empresas:            {db.query(Empresa).count()}')
        print(f'   Imóveis:             {db.query(Imovel).count()}')
        print(f'   Processos:           {db.query(ProcessoJudicial).count()}')
        print(f'   Documentos:          {db.query(Documento).count()}')
        print(f'   Contatos:            {db.query(Contato).count()}')
        print(f'   Eventos:             {db.query(Evento).count()}')
        print(f'   Tarefas:             {db.query(TarefaPesquisa).count()}')

    except Exception as e:
        db.rollback()
        print(f'❌ Error: {e}')
        raise
    finally:
        db.close()


if __name__ == '__main__':
    force = '--force' in sys.argv
    seed(force=force)
