import os
import json
import datetime
from typing import Dict, Any

USAGE_FILE = os.path.join(os.path.dirname(__file__), "documents", "usage_stats.json")

def get_today_usage() -> Dict[str, Any]:
    """Retorna os dados de consumo diário da API."""
    today_str = datetime.date.today().isoformat()
    default_data = {
        "date": today_str,
        "requests_today": 0,
        "daily_limit": 1500,
        "rpm_limit": 15
    }
    
    if not os.path.exists(USAGE_FILE):
        return default_data
        
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("date") == today_str:
                return data
    except Exception:
        pass
        
    return default_data

def increment_usage() -> int:
    """Registra uma nova consulta realizada hoje e retorna o total acumulado."""
    today_str = datetime.date.today().isoformat()
    data = get_today_usage()
    
    if data.get("date") != today_str:
        data = {
            "date": today_str,
            "requests_today": 1,
            "daily_limit": 1500,
            "rpm_limit": 15
        }
    else:
        data["requests_today"] = data.get("requests_today", 0) + 1
        
    try:
        os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
        
    return data["requests_today"]
