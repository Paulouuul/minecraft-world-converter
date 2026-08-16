# world_info.py
# Informações sobre mundos Minecraft

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from utils import get_folder_size

class WorldInfo:
    """Classe para armazenar informações de um mundo"""
    
    def __init__(self, world_path: Path):
        self.path = world_path
        self.name = world_path.name
        self.size_mb = 0
        self.world_type = "Desconhecido"
        self.has_level_dat = False
        self.has_db = False
        self.has_region = False
        self.last_modified = None
        self.is_valid = False
        
        self._analyze()
        
    def _analyze(self):
        """Analisa a pasta do mundo"""
        self.last_modified = datetime.fromtimestamp(self.path.stat().st_mtime)
        self.size_mb = get_folder_size(self.path)
        
        # Verificar arquivos
        self.has_level_dat = (self.path / "level.dat").exists()
        self.has_db = (self.path / "db").exists() and (self.path / "db").is_dir()
        self.has_region = (self.path / "region").exists() and (self.path / "region").is_dir()
        
        # Determinar tipo
        if self.has_db:
            self.world_type = "Bedrock (LevelDB)"
        elif self.has_region:
            self.world_type = "Java (Anvil)"
        elif any(self.path.glob("region/*.mcr")):
            self.world_type = "Java (Alpha)"
        elif self.has_level_dat:
            self.world_type = "Minecraft (genérico)"
            
        # Validar
        self.is_valid = self.has_level_dat or self.has_db
            
    def to_dict(self) -> Dict:
        """Retorna informações em formato de dicionário"""
        return {
            'name': self.name,
            'path': self.path,
            'size_mb': self.size_mb,
            'type': self.world_type,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M'),
            'is_valid': self.is_valid,
            'has_level_dat': self.has_level_dat,
            'has_db': self.has_db,
            'has_region': self.has_region
        }
        
    def __str__(self) -> str:
        return f"{self.name} ({self.world_type}) - {self.size_mb:.1f} MB"