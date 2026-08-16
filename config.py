# config.py
# Configurações do projeto

import os
from pathlib import Path

class Config:
    """Configurações globais do projeto"""
    
    # Caminho base (onde o script está)
    BASE_PATH = Path.cwd()
    
    # Pastas padrão (caminhos relativos)
    DEFAULT_WORLDS_PATH = BASE_PATH / "MINECRAFTDATA" / "com.mojang" / "minecraftWorlds"
    OUTPUT_MCWORLD_PATH = BASE_PATH / "MUNDOS_MCWORLD"
    OUTPUT_JAVA_PATH = BASE_PATH / "MUNDOS_JAVA"
    BACKUP_PATH = BASE_PATH / "BACKUP_MUNDOS"
    TEMP_PATH = BASE_PATH / "temp_conversao"
    
    # ============================================================
    # CAMINHOS DO MINECRAFT BEDROCK (RELATIVOS)
    # ============================================================
    # A pasta do Minecraft fica em:
    # %APPDATA%/Roaming/Minecraft Bedrock/Users/<USER_ID>/games/com.mojang
    MINECRAFT_BEDROCK_PATH = Path(os.environ.get('APPDATA', '')) / "Minecraft Bedrock"
    MINECRAFT_USER_ID = "16283763834770312692"  # Seu ID de usuário
    MINECRAFT_COM_MOJANG = MINECRAFT_BEDROCK_PATH / "Users" / MINECRAFT_USER_ID / "games" / "com.mojang"
    MINECRAFT_WORLDS_PATH = MINECRAFT_COM_MOJANG / "minecraftWorlds"
    
    # Pasta origem dos mundos (onde estão os .mcworld)
    SOURCE_MCWORLD_PATH = BASE_PATH / "MINECRAFTDATA" / "com.mojang"
    
    # Arquivos de log
    LOG_FILE_MCWORLD = BASE_PATH / "conversao_mcworld_log.txt"
    LOG_FILE_JAVA = BASE_PATH / "conversao_java_log.txt"
    LOG_FILE_GENERAL = BASE_PATH / "conversao_log.txt"
    LOG_FILE_SYNC = BASE_PATH / "sincronizacao_log.txt"
    
    # Configurações de conversão
    TIMEOUT_SECONDS = 7200  # 2 horas
    COMPRESSION_LEVEL = 6   # 0-9, 6 é o padrão do ZIP
    
    # Configurações de sincronização
    SYNC_WORKERS = 8        # Número de cópias paralelas
    SYNC_FORCE = False      # Forçar cópia sem confirmação
    
    @classmethod
    def create_directories(cls):
        """Cria todos os diretórios necessários"""
        cls.OUTPUT_MCWORLD_PATH.mkdir(exist_ok=True)
        cls.OUTPUT_JAVA_PATH.mkdir(exist_ok=True)
        cls.BACKUP_PATH.mkdir(exist_ok=True)
        cls.TEMP_PATH.mkdir(exist_ok=True)
        cls.MINECRAFT_WORLDS_PATH.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_sync_paths(cls):
        """Retorna os caminhos para sincronização"""
        return {
            'origem': cls.SOURCE_MCWORLD_PATH,
            'destino': cls.MINECRAFT_COM_MOJANG
        }