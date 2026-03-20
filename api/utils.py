"""
RGVL API - Shared utilities
"""
from datetime import datetime


def model_to_dict(obj):
    """Convert a SQLAlchemy model instance to a dictionary."""
    if obj is None:
        return None
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value
    return result


def models_to_list(instances):
    """Convert a list of SQLAlchemy instances to list of dicts."""
    return [model_to_dict(obj) for obj in instances]
