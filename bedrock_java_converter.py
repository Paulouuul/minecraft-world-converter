# bedrock_java_converter.py
# Converte mundos Bedrock -> Java

from pathlib import Path
from typing import Optional
from logger import Logger
from world_info import WorldInfo

class BedrockJavaConverter:
    """Converte mundos Bedrock para Java usando MCC Toolchest"""
    
    def __init__(self, output_path: Path, logger: Optional[Logger] = None):
        self.output_path = output_path
        self.output_path.mkdir(exist_ok=True)
        self.logger = logger or Logger()
        self.logger.set_name("Bedrock->Java")
        self.mcc_available = self._check_mcc()
        
    def _check_mcc(self) -> bool:
        """Verifica se MCC Toolchest está disponível"""
        try:
            from mcc_toolchest import convert_bedrock_to_java
            self.convert_func = convert_bedrock_to_java
            return True
        except ImportError:
            return False
            
    def convert(self, world_info: WorldInfo, overwrite: bool = False) -> bool:
        """Converte um mundo Bedrock para Java"""
        if not self.mcc_available:
            self.logger.log_error("MCC Toolchest não disponível!")
            self.logger.log_info("Instale: pip install mcc-toolchest")
            return False
            
        world_name = world_info.name
        output_path = self.output_path / f"{world_name}_java"
        
        self.logger.log(f"\n{'─'*50}")
        self.logger.log(f"📁 Convertendo: {world_name}")
        self.logger.log(f"  📊 Tamanho: {world_info.size_mb:.1f} MB")
        self.logger.log(f"  📂 Tipo: {world_info.world_type}")
        
        # Verificar se já existe
        if output_path.exists():
            if not overwrite:
                self.logger.log_warning(f"Pasta de saída já existe: {output_path.name}")
                return False
            import shutil
            shutil.rmtree(output_path)
            
        try:
            self.logger.log(f"  🔄 Convertendo com MCC Toolchest...")
            
            # Usar função importada
            self.convert_func(str(world_info.path), str(output_path))
            
            # Verificar resultado
            if output_path.exists() and any(output_path.iterdir()):
                self.logger.log_success("Conversão concluída!")
                return True
            else:
                self.logger.log_error("Pasta de saída vazia!")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Erro: {e}")
            return False