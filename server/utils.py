# utils.py

from fastapi import HTTPException
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def parse_function_code(code_str: str, func_name: str) -> Callable:
    """Parsuje kod string do wykonywalnej funkcji Python."""
    try:
        local_scope = {}
        # UWAGA: Użycie exec() jest niebezpieczne!
        exec(code_str, {}, local_scope)
        target_func_name = func_name.lower().replace(" ", "_")
        
        if target_func_name in local_scope:
            return local_scope[target_func_name]
        
        for key, value in local_scope.items():
            if callable(value):
                return value
        
        raise ValueError("Nie znaleziono funkcji w kodzie.")
    except Exception as e:
        logger.error(f"Błąd parsowania: {e}")
        raise HTTPException(status_code=400, detail=f"Błąd w kodzie funkcji: {str(e)}")