"""
RGVL ETL - Sync Database to INTEL.md

Reads new/updated records from DB (by timestamp) and appends them
as a "Recent Discoveries" section to INTEL.md.

This closes the loop: collectors write to DB → sync updates INTEL.

Supported tables: pessoas, empresas_familia, relacionamentos, tarefas_pesquisa

NOT covered by this sync (silent skip — add formatter if needed later):
  - imoveis         (Imovel)
  - processos_judiciais (ProcessoJudicial)
  - documentos  (Documento)
  - contatos    (Contato)
  - diarios_oficiais (DiarioOficial)
  - perfis     (Perfil)
  - events     (Evento)

Usage:
    cd rgvl && python -m etl.sync_to_intel

Collectors should run this after writing to DB:
    from etl.sync_to_intel import sync
    sync()
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.db import get_session
from api.models import Pessoa, Empresa, Relacionamento, TarefaPesquisa

INTEL_PATH = PROJECT_ROOT / 'docs' / 'INTEL.md'
SYNC_MARKER_FILE = PROJECT_ROOT / 'database' / 'last_sync.txt'

# Naive UTC datetime — ensures consistent ISO-8601 formatting
# "YYYY-MM-DD HH:MM:SS.ffffff" without timezone suffix.
# SQLite stores all datetimes this way; keeping everything naive avoids
# comparison mismatches between naive (DB) and aware (Python) values.
_UTC = timezone.utc


def _utc_now() -> datetime:
    """Return current UTC time as a naive datetime (HH:MM:SS.ffffff)."""
    return datetime.now(_UTC).replace(tzinfo=None)


def _read_last_sync() -> datetime | None:
    """Read last sync timestamp from marker file. Returns naive UTC datetime."""
    if not SYNC_MARKER_FILE.exists():
        return None
    try:
        text = SYNC_MARKER_FILE.read_text().strip()
        # Strip any timezone suffix added by older isoformat() versions
        text = text.replace('+00:00', '')
        return datetime.fromisoformat(text)
    except (ValueError, OSError):
        return None


def _write_last_sync(ts: datetime) -> None:
    """Write naive UTC datetime to marker file in ISO-8601 format."""
    SYNC_MARKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Store as naive ISO string so it parses consistently
    SYNC_MARKER_FILE.write_text(ts.isoformat())


def _person_summary(p: Pessoa) -> str:
    """Format a single pessoa record as markdown."""
    lines = [f"### {p.nome_completo}"]

    fields = [
        ('CPF', p.cpf),
        ('Nascimento', p.data_nascimento),
        ('Local', p.local_nascimento),
        ('Profissão', p.profissao),
        ('Cargo', p.cargo),
        ('Empresa', p.empresa),
        ('Status', p.status),
        ('Fonte', p.fonte),
        ('Observações', p.observacoes),
    ]

    table_rows = []
    for label, value in fields:
        if value:
            table_rows.append(f"| **{label}** | {value} |")

    if table_rows:
        lines.append('')
        lines.append('| Campo | Valor |')
        lines.append('|-------|-------|')
        lines.extend(table_rows)

    return '\n'.join(lines)


def _company_summary(e: Empresa) -> str:
    """Format a single empresa record as markdown."""
    lines = [f"### {e.nome_fantasia or e.razao_social}"]

    fields = [
        ('CNPJ', e.cnpj),
        ('Razão Social', e.razao_social),
        ('Status', e.status_jucemg),
        ('Cidade/UF', f"{e.cidade}, {e.uf}" if e.cidade else e.uf),
        ('Data Abertura', e.data_abertura),
        ('Fonte', e.fonte),
        ('Observações', e.observacoes),
    ]

    table_rows = []
    for label, value in fields:
        if value:
            table_rows.append(f"| **{label}** | {value} |")

    if table_rows:
        lines.append('')
        lines.append('| Campo | Valor |')
        lines.append('|-------|-------|')
        lines.extend(table_rows)

    if e.socios:
        try:
            socios = json.loads(e.socios)
            lines.append('')
            lines.append('**Sócios:**')
            for s in socios:
                lines.append(f"- {s.get('nome', 'N/A')} ({s.get('participacao', 'N/A')})")
        except (json.JSONDecodeError, TypeError):
            pass

    return '\n'.join(lines)


def _relationship_summary(r: Relacionamento, session) -> str:
    """Format a single relationship record as markdown."""
    try:
        de = session.get(Pessoa, r.pessoa_de)
        para = session.get(Pessoa, r.pessoa_para)
        de_nome = de.nome_completo if de else f"[ID {r.pessoa_de}]"
        para_nome = para.nome_completo if para else f"[ID {r.pessoa_para}]"
    except Exception:
        de_nome = f"[ID {r.pessoa_de}]"
        para_nome = f"[ID {r.pessoa_para}]"

    status = '✅ Confirmado' if r.confirmado else '⚠️ Especulativo'

    lines = [
        f"**{de_nome}** → *{r.tipo}* → **{para_nome}**",
        f"- Tipo: {r.tipo} | {status}",
    ]

    if r.fonte:
        lines.append(f"- Fonte: {r.fonte}")
    if r.observacao:
        lines.append(f"- Obs: {r.observacao}")

    return '\n'.join(lines)


def _task_summary(t: TarefaPesquisa) -> str:
    """Format a single task record as markdown."""
    status_emoji = {
        'pendente': '⏳',
        'em_andamento': '🔄',
        'concluido': '✅',
        'bloqueado': '🚫',
    }.get(t.status, '❓')

    priority_color = {
        'ALTA': '🔴',
        'MEDIA': '🟡',
        'BAIXA': '🟢',
    }.get(t.prioridade, '')

    lines = [
        f"### {t.tarefa} {status_emoji} {priority_color}",
        '',
        f"**Alvo:** {t.pessoa_alvo or 'N/A'}",
        f"**Status:** {t.status or 'pendente'}",
        f"**Prioridade:** {t.prioridade or 'N/A'}",
    ]

    if t.fontes_sugeridas:
        lines.append(f"**Fontes sugeridas:** {t.fontes_sugeridas}")
    if t.resultado:
        lines.append(f"**Resultado:** {t.resultado}")

    return '\n'.join(lines)


def _build_discoveries_section(new_ts: datetime, discoveries: dict, session) -> str:
    """Build a 'Recent Discoveries' markdown section."""
    lines = [
        '',
        '---',
        '',
        f"## 🆕 Descobertas Recentes ({new_ts.strftime('%Y-%m-%d %H:%M')})",
        '',
    ]

    if not any(discoveries.values()):
        lines.append('*Nenhum registro novo desde a última sincronização.*')
        return '\n'.join(lines)

    if discoveries.get('pessoas'):
        lines.append(f"### 👥 Pessoas ({len(discoveries['pessoas'])})")
        lines.append('')
        for p in discoveries['pessoas']:
            lines.append(_person_summary(p))
            lines.append('')

    if discoveries.get('empresas'):
        lines.append(f"### 🏢 Empresas ({len(discoveries['empresas'])})")
        lines.append('')
        for e in discoveries['empresas']:
            lines.append(_company_summary(e))
            lines.append('')

    if discoveries.get('relacionamentos'):
        lines.append(f"### 🔗 Relacionamentos ({len(discoveries['relacionamentos'])})")
        lines.append('')
        for r in discoveries['relacionamentos']:
            lines.append(_relationship_summary(r, session))
            lines.append('')

    if discoveries.get('tarefas'):
        lines.append(f"### 📋 Tarefas de Pesquisa ({len(discoveries['tarefas'])})")
        lines.append('')
        for t in discoveries['tarefas']:
            lines.append(_task_summary(t))
            lines.append('')

    return '\n'.join(lines)


def sync() -> dict:
    """
    Main sync function. Call this from collectors after writing to DB.

    Returns a dict with counts of synced items.
    """
    db = get_session()

    try:
        last_sync = _read_last_sync()
        now = _utc_now()

        # Use datetime object directly — never a string.
        # SQLite serializes naive datetime as "YYYY-MM-DD HH:MM:SS.ffffff"
        # which compares correctly against the stored column values.
        since = last_sync if last_sync else datetime(1970, 1, 1)

        new_pessoas = db.query(Pessoa).filter(
            Pessoa.created_at > since
        ).all()

        new_empresas = db.query(Empresa).filter(
            Empresa.created_at > since
        ).all()

        new_relacionamentos = db.query(Relacionamento).filter(
            Relacionamento.created_at > since
        ).all()

        new_tarefas = db.query(TarefaPesquisa).filter(
            TarefaPesquisa.created_at > since
        ).all()

        discoveries = {
            'pessoas': new_pessoas,
            'empresas': new_empresas,
            'relacionamentos': new_relacionamentos,
            'tarefas': new_tarefas,
        }

        total = sum(len(v) for v in discoveries.values())

        if total == 0:
            print('📭 No new records since last sync.')
            return {'synced': 0}

        # Build section
        section = _build_discoveries_section(now, discoveries, db)

        # Append to INTEL
        INTEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(INTEL_PATH, 'a', encoding='utf-8') as f:
            f.write(section)

        # Update sync marker
        _write_last_sync(now)

        print(f'✅ Synced to INTEL.md:')
        print(f'   👥 {len(new_pessoas)} pessoas')
        print(f'   🏢 {len(new_empresas)} empresas')
        print(f'   🔗 {len(new_relacionamentos)} relacionamentos')
        print(f'   📋 {len(new_tarefas)} tarefas')
        print(f'   📄 Section appended to INTEL.md')

        return {
            'synced': total,
            'pessoas': len(new_pessoas),
            'empresas': len(new_empresas),
            'relacionamentos': len(new_relacionamentos),
            'tarefas': len(new_tarefas),
        }

    finally:
        db.close()


if __name__ == '__main__':
    result = sync()
    sys.exit(0)
