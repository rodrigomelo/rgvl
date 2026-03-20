"""
RGVL ETL - Seed Database

Populates the database from INTEL.md research data.
Run once or re-run to refresh data.

Usage:
    cd rgvl && python -m etl.seed
"""
import json
import sys
from pathlib import Path

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.db import engine, get_session, DB_PATH
from api.models import Base, Pessoa, Relacionamento, Empresa, TarefaPesquisa


def seed():
    """Populate the database with known family data."""

    # Create tables
    Base.metadata.create_all(bind=engine)
    print(f'📦 Database: {DB_PATH}')

    db = get_session()

    try:
        # Clear existing data
        db.query(TarefaPesquisa).delete()
        db.query(Empresa).delete()
        db.query(Relacionamento).delete()
        db.query(Pessoa).delete()
        db.commit()
        print('🗑️  Cleared existing data')

        # ==================== PESSOAS ====================

        # Geração 5 — Bisavós (great-grandparents)
        bisavo_edmundo = Pessoa(
            nome_completo='Edmundo Mariano da Costa Lanna',
            data_nascimento='1878',
            data_falecimento='1968',
            profissao='Dentista',
            status='falecido',
            geracao=5,
            fonte='INTEL.md, FamilySearch (G9PX-G84)',
        )

        # Geração 4 — Avós (grandparents)
        avo_edmundo = Pessoa(
            nome_completo='Edmundo de Vasconcellos Lanna',
            data_nascimento='1922-04-24',
            local_nascimento='Barra Longa, MG',
            data_falecimento='1992-11-04',
            cpf='000.558.676-*',
            profissao='Dentista',
            status='falecido',
            geracao=4,
            fonte='INTEL.md, FamilySearch',
            observacoes='Sepultado em BH. Propriedade: Apto 402 Ed. Rio Verde, Rua Nisio Batista de Oliveira 158, Novo São Lucas',
        )

        avo_nice = Pessoa(
            nome_completo='Nice Gorgulho de Vasconcellos Lanna',
            data_nascimento='1926',
            data_falecimento='2019',
            status='falecido',
            geracao=4,
            fonte='INTEL.md',
        )

        # Tia-avó (bisavó's other children)
        tia_avo_thereza = Pessoa(
            nome_completo='Thereza de Vasconcellos Lanna',
            data_nascimento='1923',
            data_falecimento='2006',
            status='falecido',
            geracao=4,
            fonte='INTEL.md, familialana.com',
        )

        tia_avo_maria = Pessoa(
            nome_completo='Maria Auxiliadora de Vasconcellos Lanna',
            data_nascimento='1925',
            data_falecimento='2018',
            status='falecido',
            geracao=4,
            fonte='INTEL.md, familialana.com',
        )

        db.add_all([bisavo_edmundo, avo_edmundo, avo_nice, tia_avo_thereza, tia_avo_maria])
        db.flush()
        print(f'✅ Geração 5 (bisavós): {bisavo_edmundo.id}')
        print(f'✅ Geração 4 (avós): {avo_edmundo.id}, {avo_nice.id}')

        # Link bisavó → avô
        avo_edmundo.pai_id = bisavo_edmundo.id

        # Geração 3 — Pais + Tios (parents, uncles, aunts)
        pai = Pessoa(
            nome_completo='Rodrigo Gorgulho de Vasconcellos Lanna',
            data_nascimento='1955-12-17',
            local_nascimento='Belo Horizonte, MG',
            cpf='***.516.326-*',
            rg='24.920/D',
            profissao='Engenheiro Civil',
            cargo='Diretor de Engenharia',
            empresa='Construtora Barbosa Mello S/A',
            email='rodrigo.lanna@barbosamello.com.br',
            telefone='(31) 3490-3600',
            endereco='Rua Gonçalves Dias 865, Apto 1201, Savassi, BH/MG, CEP 30140-091',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='INTEL.md, CREA-MG 24.920/D',
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
            fonte='INTEL.md, CREA MT13225/VD',
            observacoes='Irmão de RGVL. Empresa baixada jun/2024. 16+ processos no TJMG.',
        )

        tio_marcelo = Pessoa(
            nome_completo='Marcelo Gorgulho de Vasconcellos Lanna',
            local_nascimento='Belo Horizonte, MG',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='INTEL.md, Facebook research 2016',
            observacoes='Irmão de RGVL. 22-25 processos no TJMG (BMG, AF Administradora). Casado com Mônica Maria Almeida Lanna.',
        )

        tia_junia = Pessoa(
            nome_completo='Júnia Gorgulho de Vasconcellos Lanna',
            cpf='064.327.216-01',
            profissao='Presidente AVOSC',
            pai_id=avo_edmundo.id,
            mae_id=avo_nice.id,
            status='ativo',
            geracao=3,
            fonte='INTEL.md, Escavador',
            observacoes='Irmã de RGVL. Vice-Presidente AVOSC (2011), Presidente AVOSC (2016). Assoc. Voluntárias Santa Casa - CNPJ 17.508.888/0001-70.',
        )

        db.add_all([pai, mae, tio_henrique, tio_marcelo, tia_junia])
        db.flush()
        print(f'✅ Geração 3 (pais/tios): pai={pai.id}, henrique={tio_henrique.id}, marcelo={tio_marcelo.id}, junia={tia_junia.id}')

        # Link spouse
        pai.conjuge_id = mae.id
        pai.data_casamento = '1992'
        mae.conjuge_id = pai.id

        # Geração 2 — Rodrigo Melo (the user)
        voce = Pessoa(
            nome_completo='Rodrigo Melo Lanna',
            nome_anterior='Rodrigo da Silva Melo',
            local_nascimento='Itaituba, PA',
            profissao='Vice President',
            empresa='J.P. Morgan Asset Management',
            email='',
            endereco='São Paulo, SP',
            pai_id=pai.id,
            status='ativo',
            geracao=2,
            fonte='INTEL.md, LinkedIn (linkedin.com/in/melorodrigo)',
            observacoes='Nome alterado em 2025: Rodrigo da Silva Melo → Rodrigo Melo Lanna. Reconhecimento de paternidade fev/2017 (escritura pública).',
        )

        db.add(voce)
        db.flush()
        print(f'✅ Geração 2 (você): {voce.id}')

        # Geração 1 — Primos (cousins from siblings of RGVL)
        # Henrique's children
        primos_henrique = [
            ('Luiza Lanna', 'Filha de Henrique. Colégio Marista Dom Silvério.'),
            ('Fernanda Lanna', 'Filha de Henrique.'),
            ('Alessandra Lanna', 'Filha de Henrique.'),
            ('Paula Lanna', 'Filha de Henrique.'),
            ('Antônio Bahury Lanna', 'Filho de Henrique. Colégio Santa Doroteia.'),
            ('João Vítor Lanna', 'Filho de Henrique. Colégio Santa Doroteia.'),
        ]

        # Marcelo's children
        primos_marcelo = [
            ('Marcela Lanna', 'Filha de Marcelo. Escola Santo Tomás de Aquino.'),
            ('Andre Lanna', 'Filho de Marcelo. Escola Santo Tomás de Aquino.'),
            ('Bruno Lanna', 'Filho de Marcelo.'),
            ('Edmundo Lanna', 'Filho de Marcelo. Nome do bisavô.'),
        ]

        # Júnia's children
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
                nome_completo=nome,
                pai_id=tio_henrique.id,
                geracao=1,
                status='ativo',
                fonte='INTEL.md, Facebook research 2016',
                observacoes=obs,
            ))

        for nome, obs in primos_marcelo:
            primos.append(Pessoa(
                nome_completo=nome,
                pai_id=tio_marcelo.id,
                geracao=1,
                status='ativo',
                fonte='INTEL.md, Facebook research 2016',
                observacoes=obs,
            ))

        for nome, obs in primos_junia:
            primos.append(Pessoa(
                nome_completo=nome,
                mae_id=tia_junia.id,
                geracao=1,
                status='ativo',
                fonte='INTEL.md, Facebook research 2016',
                observacoes=obs,
            ))

        db.add_all(primos)
        db.flush()
        print(f'✅ Geração 1 (primos): {len(primos)} primos')

        # ==================== RELACIONAMENTOS ====================

        relationships = [
            # Bisavó → Avô
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=avo_edmundo.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            # Avô → Avó
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=avo_nice.id, tipo='conjuge', confirmado=1, fonte='INTEL.md'),
            # Avô → Pai
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=pai.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            # Avó → Pai
            Relacionamento(pessoa_de=avo_nice.id, pessoa_para=pai.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            # Pai ↔ Mãe
            Relacionamento(pessoa_de=pai.id, pessoa_para=mae.id, tipo='conjuge', confirmado=1, fonte='INTEL.md, casados 1992'),
            # Pai → Você
            Relacionamento(pessoa_de=pai.id, pessoa_para=voce.id, tipo='filho', confirmado=1, fonte='INTEL.md, escritura 2017'),
            # Pai → Irmãos
            Relacionamento(pessoa_de=pai.id, pessoa_para=tio_henrique.id, tipo='irmao', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=tio_marcelo.id, tipo='irmao', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=pai.id, pessoa_para=tia_junia.id, tipo='irma', confirmado=1, fonte='INTEL.md'),
            # Avô → Tios
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=tio_henrique.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=tio_marcelo.id, tipo='filho', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=avo_edmundo.id, pessoa_para=tia_junia.id, tipo='filha', confirmado=1, fonte='INTEL.md'),
            # Avô → Tias-avós
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=tia_avo_thereza.id, tipo='filha', confirmado=1, fonte='INTEL.md'),
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=tia_avo_maria.id, tipo='filha', confirmado=1, fonte='INTEL.md'),
            # Bisavó → Avó
            Relacionamento(pessoa_de=bisavo_edmundo.id, pessoa_para=avo_nice.id, tipo='nora', confirmado=1, fonte='INTEL.md'),
        ]

        # Tio → Primos
        for primo in primos[:6]:  # Henrique's
            relationships.append(Relacionamento(
                pessoa_de=tio_henrique.id, pessoa_para=primo.id,
                tipo='filho' if 'Lanna' in primo.nome_completo else 'filha',
                confirmado=0, fonte='Facebook 2016 (speculative)',
            ))

        for primo in primos[6:10]:  # Marcelo's
            relationships.append(Relacionamento(
                pessoa_de=tio_marcelo.id, pessoa_para=primo.id,
                tipo='filho' if 'Lanna' in primo.nome_completo else 'filha',
                confirmado=0, fonte='Facebook 2016 (speculative)',
            ))

        for primo in primos[10:]:  # Júnia's
            relationships.append(Relacionamento(
                pessoa_de=tia_junia.id, pessoa_para=primo.id,
                tipo='filho' if any(n in primo.nome_completo for n in ['Pichita']) else 'filha',
                confirmado=0, fonte='Facebook 2016 (speculative)',
            ))

        db.add_all(relationships)
        db.flush()
        print(f'✅ Relacionamentos: {len(relationships)}')

        # ==================== EMPRESAS ====================

        companies = [
            Empresa(
                cnpj='22.676.938/0001-69',
                nome_fantasia='RVL Engenharia',
                razao_social='RVL Engenharia EPP',
                cidade='Belo Horizonte', uf='MG',
                status_jucemg='baixa',
                pessoa_id=pai.id,
                socios=json.dumps([{'nome': 'Rodrigo Gorgulho de Vasconcellos Lanna', 'participacao': '100%'}]),
                fonte='INTEL.md',
                observacoes='Empresa de RGVL - 100% dele. BAIXA.',
            ),
            Empresa(
                cnpj='40.203.364/0001-93',
                nome_fantasia='F Ladeira Consultoria',
                razao_social='F Ladeira Consultoria Ltda',
                endereco='Rua Prof Bartira Mourão 546 - Buritis',
                cidade='Belo Horizonte', uf='MG',
                status_jucemg='ativa',
                pessoa_id=pai.id,
                socios=json.dumps([
                    {'nome': 'Rodrigo Gorgulho de Vasconcellos Lanna', 'participacao': '50%'},
                    {'nome': 'Rosália Fagundes Ladeira', 'participacao': '50%'},
                ]),
                fonte='INTEL.md',
                observacoes='Ativa desde 2020. Sócios: RGVL + Rosália.',
            ),
            Empresa(
                cnpj='17.185.786/0001-61',
                nome_fantasia='Construtora Barbosa Mello',
                razao_social='Construtora Barbosa Mello S/A',
                endereco='Rua Paraíba 1124, Savassi',
                cidade='Belo Horizonte', uf='MG',
                status_jucemg='ativa',
                capital=154768281.0,
                pessoa_id=pai.id,
                fonte='INTEL.md',
                observacoes='RGVL é Diretor de Engenharia desde 2013. Capital social R$ 154.768.281.',
            ),
            Empresa(
                cnpj='07.514.378/0001-52',
                nome_fantasia='Consórcio Sossego',
                razao_social='Consórcio Sossego',
                cidade='Canaã dos Carajás', uf='PA',
                status_jucemg='ativa',
                pessoa_id=pai.id,
                fonte='INTEL.md',
                observacoes='Admin do consórcio desde 2019.',
            ),
            Empresa(
                cnpj='41.929.586/0001-50',
                nome_fantasia='Construtora Barbosa Mello SCP',
                razao_social='Construtora Barbosa Mello SCP 0125',
                cidade='Parauapebas', uf='PA',
                status_jucemg='ativa',
                capital=1000000.0,
                pessoa_id=pai.id,
                fonte='INTEL.md',
                observacoes='SCP ativa desde 2021.',
            ),
            Empresa(
                cnpj='02.835.659/0001-93',
                nome_fantasia='ERH Lanna Engenharia',
                razao_social='ERH Lanna Engenharia Ltda',
                endereco='Rua Prof Bartira Mourão 546 - Buritis',
                cidade='Belo Horizonte', uf='MG',
                status_jucemg='baixa',
                data_abertura='1998',
                data_baixa='2024-06-01',
                pessoa_id=tio_henrique.id,
                socios=json.dumps([{'nome': 'Henrique Gorgulho de Vasconcellos Lanna', 'participacao': '100%'}]),
                fonte='INTEL.md, CREA MT13225/VD',
                observacoes='Empresa de Henrique. BAIXA jun/2024. 16+ processos no TJMG.',
            ),
            Empresa(
                cnpj='17.508.888/0001-70',
                nome_fantasia='AVOSC',
                razao_social='Associação das Voluntárias da Santa Casa',
                cidade='Belo Horizonte', uf='MG',
                status_jucemg='ativa',
                pessoa_id=tia_junia.id,
                fonte='INTEL.md, Escavador',
                observacoes='Júnia foi Vice-Presidente (2011) e Presidente (2016).',
            ),
        ]

        db.add_all(companies)
        db.flush()
        print(f'✅ Empresas: {len(companies)}')

        # ==================== TAREFAS ====================

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
        print(f'✅ Tarefas de pesquisa: {len(tasks)}')

        # ==================== COMMIT ====================
        db.commit()
        print(f'\n🎉 Database seeded successfully!')
        print(f'   📊 {db.query(Pessoa).count()} people')
        print(f'   🔗 {db.query(Relacionamento).count()} relationships')
        print(f'   🏢 {db.query(Empresa).count()} companies')
        print(f'   📋 {db.query(TarefaPesquisa).count()} research tasks')

    except Exception as e:
        db.rollback()
        print(f'❌ Error: {e}')
        raise
    finally:
        db.close()


if __name__ == '__main__':
    seed()
