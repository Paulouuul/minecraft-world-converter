# config.py
# Configurações do projeto - usando .env

import os
from pathlib import Path
from typing import List, Dict, Optional

# CARREGAR .ENV

def load_env_file(env_path: Path = None) -> dict:
    """Carrega variáveis do arquivo .env"""
    env_vars = {}
    
    if env_path is None:
        env_path = Path.cwd() / ".env"
    
    if not env_path.exists():
        # Tentar .env.example
        env_path = Path.cwd() / ".env.example"
        if not env_path.exists():
            return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Ignorar linhas vazias e comentários
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


class Config:
    """Configurações globais do projeto (carregadas do .env)"""
    

    # CARREGAR VARIÁVEIS

    _env = load_env_file()
    

    # CAMINHO BASE

    BASE_PATH = Path.cwd()
    

    # PASTAS DO PROJETO

    OUTPUT_MCWORLD_PATH = BASE_PATH / _env.get('OUTPUT_MCWORLD_PATH', 'MUNDOS_MCWORLD')
    OUTPUT_JAVA_PATH = BASE_PATH / _env.get('OUTPUT_JAVA_PATH', 'MUNDOS_JAVA')
    BACKUP_PATH = BASE_PATH / _env.get('BACKUP_PATH', 'BACKUP_MUNDOS')
    TEMP_PATH = BASE_PATH / _env.get('TEMP_PATH', 'temp_conversao')
    
    # Pasta origem dos mundos (com.mojang inteiro)
    SOURCE_MCWORLD_PATH = BASE_PATH / _env.get('SOURCE_MCWORLD_PATH', 'MINECRAFTDATA/com.mojang')
    

    # CAMINHOS DO MINECRAFT BEDROCK

    MINECRAFT_BEDROCK_PATH = Path(
        _env.get('MINECRAFT_BEDROCK_PATH', '')
    ).expanduser() or Path(os.environ.get('APPDATA', '')) / "Minecraft Bedrock"
    
    # ID do usuário
    MINECRAFT_USER_ID = _env.get('MINECRAFT_USER_ID', '16283763834770312692')
    
    # Caminhos completos
    MINECRAFT_USERS_PATH = MINECRAFT_BEDROCK_PATH / "Users"
    MINECRAFT_SHARED_PATH = MINECRAFT_USERS_PATH / "Shared" / "games" / "com.mojang"
    MINECRAFT_USER_PATH = MINECRAFT_USERS_PATH / MINECRAFT_USER_ID / "games" / "com.mojang"
    MINECRAFT_COM_MOJANG = MINECRAFT_USER_PATH
    MINECRAFT_WORLDS_PATH = MINECRAFT_USER_PATH / "minecraftWorlds"
    

    # ARQUIVOS DE LOG

    LOG_FILE_MCWORLD = BASE_PATH / _env.get('LOG_FILE_MCWORLD', 'mcworld_converter_log.txt')
    LOG_FILE_JAVA = BASE_PATH / _env.get('LOG_FILE_JAVA', 'java_converter_log.txt')
    LOG_FILE_GENERAL = BASE_PATH / _env.get('LOG_FILE_GENERAL', 'converter_log.txt')
    LOG_FILE_SYNC = BASE_PATH / _env.get('LOG_FILE_SYNC', 'minecraft_sync_log.txt')
    LOG_FILE_PARALLEL = BASE_PATH / _env.get('LOG_FILE_PARALLEL', 'parallel_converter_log.txt')
    

    # CONFIGURAÇÕES DE CONVERSÃO

    TIMEOUT_SECONDS = int(_env.get('TIMEOUT_SECONDS', 7200))
    COMPRESSION_LEVEL = int(_env.get('COMPRESSION_LEVEL', 6))
    MAX_WORKERS = int(_env.get('MAX_WORKERS', 8))
    

    # CONFIGURAÇÕES DE SINCRONIZAÇÃO

    SYNC_WORKERS = int(_env.get('SYNC_WORKERS', 8))
    SYNC_FORCE = _env.get('SYNC_FORCE', 'false').lower() in ('true', '1', 'yes')
    

    # MAPEAMENTO DE PASTAS

    @classmethod
    def _parse_list(cls, key: str, default: List[str]) -> List[str]:
        """Converte string do .env para lista"""
        value = cls._env.get(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]
    
    PASTAS_SHARED = _parse_list.__func__(
        None, 
        'PASTAS_SHARED',
        ['behavior_packs', 'development_behavior_packs', 'development_resource_packs', 
         'development_skin_packs', 'resource_packs', 'skin_packs', 'world_templates']
    )
    
    PASTAS_USER = _parse_list.__func__(
        None,
        'PASTAS_USER',
        ['minecraftWorlds', 'custom_skins', 'minecraftpe', 'Screenshots']
    )
    

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
    def get_sync_paths(cls) -> dict:
        """Retorna os caminhos para sincronização"""
        return {
            'origem': cls.SOURCE_MCWORLD_PATH,
            'destino_shared': cls.MINECRAFT_SHARED_PATH,
            'destino_user': cls.MINECRAFT_USER_PATH,
            'shared_path': cls.MINECRAFT_SHARED_PATH,
            'user_path': cls.MINECRAFT_USER_PATH
        }
    
    @classmethod
    def get_minecraft_paths(cls, user_id: str = None) -> dict:
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
        print("📋 CONFIGURAÇÕES DO PROJETO (do .env)")
        print("="*60)
        print(f"BASE_PATH: {cls.BASE_PATH}")
        print(f"\n📂 Pastas:")
        print(f"  SOURCE_MCWORLD_PATH: {cls.SOURCE_MCWORLD_PATH}")
        print(f"  OUTPUT_MCWORLD_PATH: {cls.OUTPUT_MCWORLD_PATH}")
        print(f"  OUTPUT_JAVA_PATH: {cls.OUTPUT_JAVA_PATH}")
        print(f"  BACKUP_PATH: {cls.BACKUP_PATH}")
        print(f"\n🎮 Minecraft:")
        print(f"  MINECRAFT_BEDROCK_PATH: {cls.MINECRAFT_BEDROCK_PATH}")
        print(f"  MINECRAFT_USER_ID: {cls.MINECRAFT_USER_ID}")
        print(f"  MINECRAFT_SHARED_PATH: {cls.MINECRAFT_SHARED_PATH}")
        print(f"  MINECRAFT_USER_PATH: {cls.MINECRAFT_USER_PATH}")
        print(f"\n📝 Logs:")
        print(f"  LOG_FILE_SYNC: {cls.LOG_FILE_SYNC}")
        print(f"  LOG_FILE_MCWORLD: {cls.LOG_FILE_MCWORLD}")
        print(f"\n⚙️ Configurações:")
        print(f"  SYNC_WORKERS: {cls.SYNC_WORKERS}")
        print(f"  SYNC_FORCE: {cls.SYNC_FORCE}")
        print(f"  MAX_WORKERS: {cls.MAX_WORKERS}")
        print(f"\n📂 Mapeamento de pastas:")
        print(f"  Shared: {cls.PASTAS_SHARED}")
        print(f"  User: {cls.PASTAS_USER}")
        print("="*60 + "\n")


# FUNÇÃO PARA INICIALIZAÇÃO
def init_project():
    """Inicializa o projeto criando todas as pastas necessárias"""
    Config.create_directories()
    print("✅ Pastas do projeto criadas com sucesso!")
    Config.print_config()
    return Config


if __name__ == "__main__":
    # Teste de configurações
    init_project()