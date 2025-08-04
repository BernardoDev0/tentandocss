import json
import logging
from datetime import datetime, date, timedelta
import calendar
import pytz

# Definir timezone padrão
timezone = pytz.timezone('America/Sao_Paulo')

def safe_json_dumps(data):
    """Serializa dados para JSON de forma segura"""
    def json_serializer(obj):
        if obj is None:
            return None
        if hasattr(obj, '__class__') and 'Undefined' in str(type(obj)):
            return None
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if hasattr(obj, '__class__') and 'Decimal' in str(type(obj)):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, '__table__'):
            return str(obj)
        if hasattr(obj, '_mapping'):
            return dict(obj._mapping)
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj) if obj is not None else None
    
    try:
        if data is None:
            return json.dumps([])
        return json.dumps(data, default=json_serializer, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Erro na serialização JSON: {str(e)}")
        return json.dumps([])