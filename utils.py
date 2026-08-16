# utils.py
# Funções utilitárias

import os
import shutil
from pathlib import Path
from datetime import datetime

def get_file_size(path: Path) -> float:
    """Retorna o tamanho do arquivo em MB"""
    try:
        return path.stat().st_size / (1024 * 1024)
    except:
        return 0.0

def get_folder_size(path: Path) -> float:
    """Retorna o tamanho da pasta em MB"""
    try:
        total_size = 0
        for file in path.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size / (1024 * 1024)
    except:
        return 0.0

def get_file_count(path: Path) -> int:
    """Retorna o número de arquivos em uma pasta"""
    try:
        return len([f for f in path.rglob('*') if f.is_file()])
    except:
        return 0

def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """Copia um arquivo com segurança"""
    try:
        if dst.exists() and not overwrite:
            return False
        if dst.exists():
            dst.unlink()
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

def safe_copytree(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """Copia uma pasta com segurança"""
    try:
        if dst.exists():
            if not overwrite:
                return False
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return True
    except Exception:
        return False

def format_size(size_bytes: int) -> str:
    """Formata tamanho em bytes para string legível"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def format_time(seconds: float) -> str:
    """Formata tempo em segundos para string legível"""
    if seconds < 60:
        return f"{seconds:.0f} segundos"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutos"
    else:
        return f"{seconds/3600:.1f} horas"

def get_timestamp() -> str:
    """Retorna timestamp atual formatado"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def confirm_action(prompt: str, default: bool = False) -> bool:
    """Solicita confirmação do usuário"""
    if default:
        response = input(f"{prompt} (s/N): ")
    else:
        response = input(f"{prompt} (s/N): ")
    return response.lower() == 's'