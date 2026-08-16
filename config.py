# config.py
# Configurações do projeto - COMPLETO

import os
from pathlib import Path

class Config:
    """Configurações globais do projeto"""
    
    # CAMINHO BASE
    BASE_PATH = Path.cwd()
    
    # PASTAS DO PROJETO
    # Pastas de conversão
    DEFAULT_WORLDS_PATH = BASE_PATH / "MINECRAFTDATA" / "com.mojang" / "minecraftWorlds"
    OUTPUT_MCWORLD_PATH = BASE_PATH / "MUNDOS_MCWORLD"
    OUTPUT_JAVA_PATH = BASE_PATH / "MUNDOS_JAVA"
    BACKUP_PATH = BASE_PATH / "BACKUP_MUNDOS"
    TEMP_PATH = BASE_PATH / "temp_conversao"
    
    # Pasta origem dos mundos (com.mojang inteiro)
    SOURCE_MCWORLD_PATH = BASE_PATH / "MINECRAFTDATA" / "com.mojang"
    
    # CAMINHOS DO MINECRAFT BEDROCK
    # A pasta do Minecraft fica em:
    # %APPDATA%/Roaming/Minecraft Bedrock/
    MINECRAFT_BEDROCK_PATH = Path(os.environ.get('APPDATA', '')) / "Minecraft Bedrock"
    
    # ID do usuário (padrão)
    MINECRAFT_USER_ID = "16283763834770312692"
    
    # Caminhos completos
    MINECRAFT_USERS_PATH = MINECRAFT_BEDROCK_PATH / "Users"
    MINECRAFT_SHARED_PATH = MINECRAFT_USERS_PATH / "Shared" / "games" / "com.mojang"
    MINECRAFT_USER_PATH = MINECRAFT_USERS_PATH / MINECRAFT_USER_ID / "games" / "com.mojang"
    MINECRAFT_COM_MOJANG = MINECRAFT_USER_PATH
    MINECRAFT_WORLDS_PATH = MINECRAFT_USER_PATH / "minecraftWorlds"
    
    # ARQUIVOS DE LOG
    LOG_FILE_MCWORLD = BASE_PATH / "mcworld_converter_log.txt"
    LOG_FILE_JAVA = BASE_PATH / "java_converter_log.txt"
    LOG_FILE_GENERAL = BASE_PATH / "converter_log.txt"
    LOG_FILE_SYNC = BASE_PATH / "minecraft_sync_log.txt"
    LOG_FILE_PARALLEL = BASE_PATH / "parallel_converter_log.txt"
    
    # CONFIGURAÇÕES DE CONVERSÃO
    TIMEOUT_SECONDS = 7200          # 2 horas
    COMPRESSION_LEVEL = 6           # 0-9, 6 é o padrão do ZIP
    MAX_WORKERS = 8                 # Workers padrão para conversão paralela
    
    # CONFIGURAÇÕES DE SINCRONIZAÇÃO
    SYNC_WORKERS = 8                # Número de cópias paralelas
    SYNC_FORCE = False              # Forçar cópia sem confirmação
    
    # Mapeamento de pastas para destinos (Shared vs User)
    PASTAS_SHARED = [
        'behavior_packs',
        'development_behavior_packs',
        'development_resource_packs',
        'development_skin_packs',
        'resource_packs',
        'skin_packs',
        'world_templates'
    ]
    
    PASTAS_USER = [
        'minecraftWorlds',
        'custom_skins',
        'minecraftpe',
        'Screenshots'
    ]
    
    # MÉTODOS
    @classmethod
    def create_directories(cls):
        """Cria todos os diretórios necessários"""
        cls.OUTPUT_MCWORLD_PATH.mkdir(exist_ok=True)
        cls.OUTPUT_JAVA_PATH.mkdir(exist_ok=True)
        cls.BACKUP_PATH.mkdir(exist_ok=True)
        cls.TEMP_PATH.mkdir(exist_ok=True)
        cls.MINECRAFT_SHARED_PATH.mkdir(parents=True, exist_ok=True)
        cls.MINECRAFT_WORLDS_PATH.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_sync_paths(cls):
        """Retorna os caminhos para sincronização"""
        return {
            'origem': cls.SOURCE_MCWORLD_PATH,
            'destino_shared': cls.MINECRAFT_SHARED_PATH,
            'destino_user': cls.MINECRAFT_USER_PATH,
            'shared_path': cls.MINECRAFT_SHARED_PATH,
            'user_path': cls.MINECRAFT_USER_PATH
        }
    
    @classmethod
    def get_minecraft_paths(cls, user_id: str = None):
        """Retorna caminhos do Minecraft para um usuário específico"""
        user_id = user_id or cls.MINECRAFT_USER_ID
        return {
            'base': cls.MINECRAFT_BEDROCK_PATH,
            'users': cls.MINECRAFT_USERS_PATH,
            'shared': cls.MINECRAFT_SHARED_PATH,
            'user': cls.MINECRAFT_USERS_PATH / user_id / "games" / "com.mojang",
            'worlds': cls.MINECRAFT_USERS_PATH / user_id / "games" / "com.mojang" / "minecraftWorlds"
        }
    
    @classmethod
    def get_destino_pasta(cls, nome_pasta: str) -> Path:
        """Retorna o destino correto para uma pasta (Shared ou User)"""
        if nome_pasta in cls.PASTAS_SHARED:
            return cls.MINECRAFT_SHARED_PATH / nome_pasta
        elif nome_pasta in cls.PASTAS_USER:
            return cls.MINECRAFT_USER_PATH / nome_pasta
        else:
            # Pastas desconhecidas vão para User
            return cls.MINECRAFT_USER_PATH / nome_pasta
    
    @classmethod
    def get_tipo_pasta(cls, nome_pasta: str) -> str:
        """Retorna o tipo de destino ('Shared' ou 'User')"""
        if nome_pasta in cls.PASTAS_SHARED:
            return "Shared"
        elif nome_pasta in cls.PASTAS_USER:
            return "User"
        else:
            return "User (desconhecido)"
    
    @classmethod
    def print_config(cls):
        """Imprime todas as configurações para debug"""
        print("\n" + "="*60)
        print("CONFIGURAÇÕES DO PROJETO")
        print("="*60)
        print(f"BASE_PATH: {cls.BASE_PATH}")
        print(f"\n- Pastas:")
        print(f"  SOURCE_MCWORLD_PATH: {cls.SOURCE_MCWORLD_PATH}")
        print(f"  OUTPUT_MCWORLD_PATH: {cls.OUTPUT_MCWORLD_PATH}")
        print(f"  OUTPUT_JAVA_PATH: {cls.OUTPUT_JAVA_PATH}")
        print(f"  BACKUP_PATH: {cls.BACKUP_PATH}")
        print(f"\n- Minecraft:")
        print(f"  MINECRAFT_BEDROCK_PATH: {cls.MINECRAFT_BEDROCK_PATH}")
        print(f"  MINECRAFT_USER_ID: {cls.MINECRAFT_USER_ID}")
        print(f"  MINECRAFT_SHARED_PATH: {cls.MINECRAFT_SHARED_PATH}")
        print(f"  MINECRAFT_USER_PATH: {cls.MINECRAFT_USER_PATH}")
        print(f"\n- Logs:")
        print(f"  LOG_FILE_SYNC: {cls.LOG_FILE_SYNC}")
        print(f"  LOG_FILE_MCWORLD: {cls.LOG_FILE_MCWORLD}")
        print(f"\n- Configurações:")
        print(f"  SYNC_WORKERS: {cls.SYNC_WORKERS}")
        print(f"  SYNC_FORCE: {cls.SYNC_FORCE}")
        print(f"  MAX_WORKERS: {cls.MAX_WORKERS}")
        print(f"\n- Mapeamento de pastas:")
        print(f"  Shared: {cls.PASTAS_SHARED}")
        print(f"  User: {cls.PASTAS_USER}")
        print("="*60 + "\n")

# FUNÇÃO PARA INICIALIZAÇÃO RÁPID
def init_project():
    """Inicializa o projeto criando todas as pastas necessárias"""
    Config.create_directories()
    print("✅ Pastas do projeto criadas com sucesso!")
    Config.print_config()
    return Config


if __name__ == "__main__":
    # Teste de configurações
    init_project()