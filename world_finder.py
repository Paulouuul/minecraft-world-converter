# world_finder.py
# Encontra mundos Minecraft

from pathlib import Path
from typing import List, Optional
from world_info import WorldInfo

class WorldFinder:
    """Encontra e lista mundos Minecraft"""
    
    def __init__(self, search_path: Optional[Path] = None):
        self.search_path = search_path
        self.worlds = []
        
    def find_worlds(self) -> List[WorldInfo]:
        """Encontra todos os mundos no caminho especificado"""
        self.worlds = []
        
        if not self.search_path or not self.search_path.exists():
            return self.worlds
            
        # Verificar se é uma pasta de mundo diretamente
        if (self.search_path / "level.dat").exists() or (self.search_path / "db").exists():
            info = WorldInfo(self.search_path)
            if info.is_valid:
                self.worlds.append(info)
            return self.worlds
            
        # Procurar em subpastas
        for item in self.search_path.iterdir():
            if item.is_dir():
                info = WorldInfo(item)
                if info.is_valid:
                    self.worlds.append(info)
                    
        return self.worlds
    
    def find_world_by_name(self, name: str) -> Optional[WorldInfo]:
        """Encontra um mundo específico pelo nome"""
        for world in self.worlds:
            if world.name == name:
                return world
        return None
    
    def filter_worlds(self, names: List[str]) -> List[WorldInfo]:
        """Filtra mundos por lista de nomes"""
        if not names:
            return self.worlds
        return [w for w in self.worlds if w.name in names]
    
    def get_summary(self) -> str:
        """Retorna resumo dos mundos encontrados"""
        if not self.worlds:
            return "Nenhum mundo encontrado"
            
        lines = [f"📋 Mundos encontrados: {len(self.worlds)}"]
        for i, world in enumerate(self.worlds, 1):
            lines.append(f"  {i}. {world}")
        return '\n'.join(lines)