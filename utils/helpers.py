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

def get_week_dates(week_str):
    """Converte string da semana para datas de início e fim"""
    try:
        year, week = map(int, week_str.split('-W'))
        jan1 = date(year, 1, 1)
        week1_start = jan1 - timedelta(days=jan1.weekday())
        if jan1.weekday() > 3:
            week1_start += timedelta(weeks=1)
        start_date = week1_start + timedelta(weeks=week-1)
        end_date = start_date + timedelta(days=6)
        return start_date, end_date
    except:
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        return start_week, end_week

def get_current_week():
    """Retorna a semana atual no formato YYYY-WXX"""
    today = date.today()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"

def get_week_from_date(date_str):
    """Converte data para formato de semana"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        year, week, _ = date_obj.isocalendar()
        return f"{year}-W{week:02d}"
    except:
        return get_current_week()

def get_available_weeks():
    """Retorna lista de semanas disponíveis"""
    from models.entry import Entry
    from sqlalchemy import func
    
    try:
        # Buscar todas as datas únicas das entradas
        dates = Entry.query.with_entities(Entry.date).distinct().all()
        weeks = set()
        
        for date_tuple in dates:
            date_str = date_tuple[0]
            week = get_week_from_date(date_str)
            weeks.add(week)
        
        # Adicionar semana atual se não existir
        current_week = get_current_week()
        weeks.add(current_week)
        
        # Ordenar semanas
        sorted_weeks = sorted(list(weeks), reverse=True)
        return sorted_weeks
    except Exception as e:
        logging.error(f"Erro ao obter semanas disponíveis: {str(e)}")
        return [get_current_week()]