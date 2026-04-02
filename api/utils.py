"""
RGVL API - Shared utilities
"""
from datetime import datetime


STATUS_ALIASES = {
    'pending': {'pending', 'pendente'},
    'success': {'success', 'sucesso'},
    'failed': {'failed', 'falha'},
    'partial': {'partial', 'parcial'},
    'active': {'active', 'ativo', 'ativa'},
    'inactive': {'inactive', 'inativo', 'inativa'},
    'closed': {'closed', 'baixa', 'encerrado', 'encerrada'},
    'in_progress': {'in_progress', 'andamento'},
    'completed': {'completed', 'concluido', 'concluida'},
    'high': {'high', 'alta'},
    'medium': {'medium', 'media', 'média'},
    'low': {'low', 'baixa'},
}

EVENT_TYPE_ALIASES = {
    'nascimento': 'birth',
    'falecimento': 'death',
    'casamento': 'marriage',
    'dados_pessoais': 'personal_data',
    'empresarial': 'company',
    'escritura': 'deed',
    'imovel': 'property',
    'processo_judicial': 'legal',
    'juridico': 'legal',
    'pesquisa': 'research',
    'contato_familiar': 'family_contact',
    'reconhecimento_paternidade': 'paternity',
    'alteracao_nome': 'name_change',
    'nome': 'name_change',
}

RELATIONSHIP_TYPE_ALIASES = {
    'pai': 'father',
    'mae': 'mother',
    'filho': 'son',
    'filha': 'daughter',
    'irmao': 'brother',
    'irma': 'sister',
    'conjuge': 'spouse',
    'tio': 'uncle',
    'tia': 'aunt',
    'sobrinho': 'nephew',
    'sobrinha': 'niece',
    'avo_pai': 'grandfather_paternal',
    'avo_mae': 'grandmother_maternal',
    'neto': 'grandson',
    'neta': 'granddaughter',
    'primo': 'male_cousin',
    'prima': 'female_cousin',
    'genro': 'son_in_law',
    'nora': 'daughter_in_law',
    'sogro': 'father_in_law',
    'sogra': 'mother_in_law',
    'cunhado': 'brother_in_law',
    'cunhada': 'sister_in_law',
}

CONFIDENCE_ALIASES = {
    'confirmed': 'high',
    'alta': 'high',
    'high': 'high',
    'media': 'medium',
    'média': 'medium',
    'medium': 'medium',
    'baixa': 'low',
    'low': 'low',
}


def _normalize_alias(value, alias_map):
    if not isinstance(value, str):
        return value

    normalized = value.strip().lower().replace(' ', '_')
    for canonical, aliases in alias_map.items():
        if normalized in aliases:
            return canonical
    return normalized


def normalize_status(value):
    return _normalize_alias(value, STATUS_ALIASES)


def normalize_priority(value):
    return _normalize_alias(value, {
        'high': {'high', 'alta'},
        'medium': {'medium', 'media', 'média'},
        'low': {'low', 'baixa'},
    })


def normalize_event_type(value):
    if not isinstance(value, str):
        return value
    normalized = value.strip().lower().replace(' ', '_')
    return EVENT_TYPE_ALIASES.get(normalized, normalized)


def normalize_relationship_type(value):
    if not isinstance(value, str):
        return value
    normalized = value.strip().lower().replace(' ', '_')
    return RELATIONSHIP_TYPE_ALIASES.get(normalized, normalized)


def normalize_confidence(value):
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return value

    normalized = value.strip().lower()
    if normalized.isdigit():
        return int(normalized)
    return CONFIDENCE_ALIASES.get(normalized, normalized)


def status_filter_values(value):
    normalized = normalize_status(value)
    return STATUS_ALIASES.get(normalized, {normalized})


def priority_filter_values(value):
    normalized = normalize_priority(value)
    mapping = {
        'high': {'high', 'alta', 'ALTA'},
        'medium': {'medium', 'media', 'média', 'MEDIA', 'MÉDIA'},
        'low': {'low', 'baixa', 'BAIXA'},
    }
    return mapping.get(normalized, {value})


def model_to_dict(obj):
    """Convert a SQLAlchemy model instance to a dictionary."""
    if obj is None:
        return None
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        elif column.name in {'status', 'registration_status'}:
            result[column.name] = normalize_status(value)
        elif column.name == 'priority':
            result[column.name] = normalize_priority(value)
        elif column.name == 'event_type':
            result[column.name] = normalize_event_type(value)
        elif column.name == 'relationship_type':
            result[column.name] = normalize_relationship_type(value)
        elif column.name == 'confidence':
            result[column.name] = normalize_confidence(value)
        else:
            result[column.name] = value
    return result


def models_to_list(instances):
    """Convert a list of SQLAlchemy instances to list of dicts."""
    return [model_to_dict(obj) for obj in instances]
