# mcworld_converter.py
# Converte pastas de mundo para .mcworld

import os
import zipfile
from pathlib import Path
from typing import Optional
from logger import Logger
from world_info import WorldInfo
from utils import get_folder_size, format_size

class MCWorldConverter:
    """Converte pastas de mundo para arquivos .mcworld"""
    
    def __init__(self, output_path: Path, logger: Optional[Logger] = None):
        self.output_path = output_path
        self.output_path.mkdir(exist_ok=True)
        self.logger = logger or Logger()
        self.logger.set_name("MCWorld")
        
    def convert(self, world_info: WorldInfo, overwrite: bool = False) -> bool:
        """Converte um mundo para .mcworld"""
        world_name = world_info.name
        output_file = self.output_path / f"{world_name}.mcworld"
        
        self.logger.log(f"\n{'─'*50}")
        self.logger.log(f"- Convertendo: {world_name}")
        self.logger.log(f"  - Tamanho: {world_info.size_mb:.1f} MB")
        self.logger.log(f"  - Tipo: {world_info.world_type}")
        
        # Verificar se arquivo já existe
        if output_file.exists():
            if not overwrite:
                self.logger.log_warning(f"Arquivo já existe: {output_file.name}")
                return False
            output_file.unlink()
            
        try:
            # Compactar
            self.logger.log(f"  - Compactando...")
            
            arquivos_total = 0
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for raiz, dirs, arquivos in os.walk(world_info.path):
                    for arquivo in arquivos:
                        caminho_completo = os.path.join(raiz, arquivo)
                        caminho_relativo = os.path.relpath(caminho_completo, world_info.path)
                        zipf.write(caminho_completo, caminho_relativo)
                        arquivos_total += 1
                        
                        # Progresso
                        if arquivos_total % 100 == 0:
                            self.logger.log(f"    - {arquivos_total} arquivos...")
            
            # Verificar resultado
            if output_file.exists():
                tamanho_mb = output_file.stat().st_size / (1024 * 1024)
                self.logger.log_success(f"Conversão concluída!")
                self.logger.log(f"  - Arquivo: {output_file.name}")
                self.logger.log(f"  - Tamanho: {tamanho_mb:.2f} MB")
                self.logger.log(f"  - Arquivos: {arquivos_total}")
                
                # Salvar informações
                info_file = self.output_path / f"{world_name}_info.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"Mundo: {world_name}\n")
                    f.write(f"Data: {world_info.last_modified}\n")
                    f.write(f"Tamanho original: {world_info.size_mb:.1f} MB\n")
                    f.write(f"Tamanho .mcworld: {tamanho_mb:.2f} MB\n")
                    f.write(f"Total arquivos: {arquivos_total}\n")
                    f.write(f"Tipo: {world_info.world_type}\n")
                
                return True
            else:
                self.logger.log_error("Arquivo de saída não foi criado!")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Erro na compactação: {e}")
            return False