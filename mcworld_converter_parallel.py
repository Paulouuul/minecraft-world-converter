# mcworld_converter_parallel.py
# Converte pastas de mundo para .mcworld em PARALELO

import os
import zipfile
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
from logger import Logger
from world_info import WorldInfo
from utils import get_folder_size, format_size

class MCWorldConverterParallel:
    """Converte pastas de mundo para arquivos .mcworld em paralelo"""
    
    def __init__(self, output_path: Path, logger: Optional[Logger] = None, max_workers: int = 4):
        self.output_path = output_path
        self.output_path.mkdir(exist_ok=True)
        self.logger = logger or Logger()
        self.logger.set_name("MCWorld-Parallel")
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'current': 0
        }
        
    def _convert_single(self, world_info: WorldInfo, overwrite: bool = False) -> tuple:
        """Converte um único mundo (executado em paralelo)"""
        world_name = world_info.name
        output_file = self.output_path / f"{world_name}.mcworld"
        
        # Atualizar contador (thread-safe)
        with self.lock:
            self.stats['current'] += 1
            current = self.stats['current']
            total = self.stats['total']
        
        self.logger.log(f"[{current}/{total}] - Iniciando: {world_name}")
        
        try:
            # Verificar se arquivo já existe
            if output_file.exists() and not overwrite:
                self.logger.log_warning(f"[{current}/{total}] ⏭️ Pulado: {world_name} (já existe)")
                return (world_name, False, "Arquivo já existe")
            
            # Compactar
            arquivos_total = 0
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for raiz, dirs, arquivos in os.walk(world_info.path):
                    for arquivo in arquivos:
                        caminho_completo = os.path.join(raiz, arquivo)
                        caminho_relativo = os.path.relpath(caminho_completo, world_info.path)
                        zipf.write(caminho_completo, caminho_relativo)
                        arquivos_total += 1
            
            # Verificar resultado
            if output_file.exists():
                tamanho_mb = output_file.stat().st_size / (1024 * 1024)
                self.logger.log_success(f"[{current}/{total}] - {world_name} ({tamanho_mb:.1f} MB, {arquivos_total} arquivos)")
                
                # Salvar informações
                info_file = self.output_path / f"{world_name}_info.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"Mundo: {world_name}\n")
                    f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Tamanho original: {world_info.size_mb:.1f} MB\n")
                    f.write(f"Tamanho .mcworld: {tamanho_mb:.2f} MB\n")
                    f.write(f"Total arquivos: {arquivos_total}\n")
                
                return (world_name, True, f"{tamanho_mb:.1f} MB")
            else:
                return (world_name, False, "Arquivo não criado")
                
        except Exception as e:
            self.logger.log_error(f"[{current}/{total}] ❌ {world_name}: {e}")
            return (world_name, False, str(e))
    
    def convert(self, worlds: List[WorldInfo], overwrite: bool = False) -> dict:
        """Converte múltiplos mundos em paralelo"""
        if not worlds:
            self.logger.log_warning("Nenhum mundo para converter")
            return {'success': 0, 'failed': 0}
        
        self.stats['total'] = len(worlds)
        self.stats['success'] = 0
        self.stats['failed'] = 0
        self.stats['current'] = 0
        
        self.logger.log(f"\n{'='*60}")
        self.logger.log(f"INICIANDO CONVERSÃO PARALELA")
        self.logger.log(f"{'='*60}")
        self.logger.log(f"- Total de mundos: {len(worlds)}")
        self.logger.log(f"- Trabalhadores: {self.max_workers}")
        self.logger.log(f"- Saída: {self.output_path}")
        self.logger.log(f"{'='*60}\n")
        
        resultados = []
        
        # Executar em paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter todas as tarefas
            futures = {
                executor.submit(self._convert_single, world, overwrite): world 
                for world in worlds
            }
            
            # Coletar resultados conforme são concluídos
            for future in as_completed(futures):
                world_name, success, message = future.result()
                if success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
                resultados.append((world_name, success, message))
        
        # Resumo final
        self.logger.log(f"\n{'='*60}")
        self.logger.log(f"RESUMO FINAL (PARALELO)")
        self.logger.log(f"{'='*60}")
        self.logger.log(f"  Total: {self.stats['total']} mundos")
        self.logger.log(f"  - Sucessos: {self.stats['success']}")
        self.logger.log(f"  - Falhas: {self.stats['failed']}")
        self.logger.log(f"  - Trabalhadores: {self.max_workers}")
        self.logger.log(f"  - Saída: {self.output_path}")
        
        return self.stats