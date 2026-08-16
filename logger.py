# logger.py
# Sistema de logs

from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    """Sistema de logging unificado"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_lines = []
        self.log_file = log_file
        self.name = "Geral"
        
    def set_name(self, name: str):
        """Define o nome do logger"""
        self.name = name
        
    def set_log_file(self, log_file: Path):
        """Define o arquivo de log"""
        self.log_file = log_file
        
    def log(self, message: str, show: bool = True):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{self.name}] {message}"
        self.log_lines.append(log_entry)
        if show:
            print(log_entry)
            
    def log_section(self, title: str):
        """Adiciona uma seção no log"""
        self.log(f"{'='*60}")
        self.log(f"🎮 {title}")
        self.log(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"{'='*60}")
        
    def log_error(self, message: str):
        """Log de erro"""
        self.log(f"❌ {message}")
        
    def log_success(self, message: str):
        """Log de sucesso"""
        self.log(f"✅ {message}")
        
    def log_warning(self, message: str):
        """Log de aviso"""
        self.log(f"⚠️ {message}")
        
    def log_info(self, message: str):
        """Log de informação"""
        self.log(f"ℹ️ {message}")
        
    def save_log(self):
        """Salva o log em arquivo"""
        if self.log_file:
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.log_lines))
                self.log(f"📝 Log salvo em: {self.log_file}")
            except Exception as e:
                print(f"Erro ao salvar log: {e}")
                
    def get_log_lines(self) -> list:
        """Retorna todas as linhas do log"""
        return self.log_lines