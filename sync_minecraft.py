# sync_minecraft.py
# Sincroniza pastas com.mojang - recebe caminho do Minecraft e User ID
# CORRIGIDO: Perguntas sequenciais, copia em paralelo

import shutil
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import argparse
import sys

from config import Config

class MinecraftWorldSync:
    """Sincroniza pastas com.mojang - recebe caminho do Minecraft e User ID"""
    
    def __init__(self, minecraft_path: Path, user_id: str, origem: Path = None, max_workers: int = None):
        self.minecraft_path = Path(minecraft_path)
        self.user_id = user_id
        
        # Determinar caminhos
        self.shared_path = self.minecraft_path / "Users" / "Shared" / "games" / "com.mojang"
        self.user_path = self.minecraft_path / "Users" / user_id / "games" / "com.mojang"
        
        # Pasta origem
        self.origem = origem or Config.SOURCE_MCWORLD_PATH
        
        self.max_workers = max_workers or Config.SYNC_WORKERS
        self.lock = threading.Lock()
        
        # Estatisticas
        self.itens_copiados = 0
        self.itens_pulados = 0
        self.itens_sobrescritos = 0
        self.erros = 0
        self.total_itens = 0
        
        # Modo de sobrescrita (definido no inicio)
        self.modo_sobrescrita = None  # 'all', 'none', 'ask'
        
        # Fila para processamento sequencial de perguntas
        self.fila_perguntas = []
        self.processando_pergunta = False
        
        # Log
        self.log_file = Config.LOG_FILE_SYNC
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== SINCRONIZACAO INICIADA EM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(f"- Origem: {self.origem}\n")
            f.write(f"- Minecraft: {self.minecraft_path}\n")
            f.write(f"- User ID: {self.user_id}\n")
            f.write(f"- Shared: {self.shared_path}\n")
            f.write(f"- User: {self.user_path}\n")
            f.write(f"- Workers: {self.max_workers}\n")
            f.write(f"{'='*60}\n\n")
        
        # Mapeamento de pastas para destinos
        self.pastas_shared = ['behavior_packs', 'development_behavior_packs', 'resource_packs', 'development_resource_packs', 'skin_packs', 'development_skin_packs', 'world_templates']
        self.pastas_user = ['minecraftWorlds', 'custom_skins', 'minecraftpe', 'Screenshots']
        
    def log(self, mensagem: str, salvar: bool = True, mostrar: bool = True):
        if mostrar:
            print(mensagem)
        if salvar:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%H:%M:%S')} - {mensagem}\n")
    
    def get_destino(self, nome_pasta: str) -> Path:
        """Retorna o destino correto para uma pasta"""
        if nome_pasta in self.pastas_shared:
            return self.shared_path / nome_pasta
        elif nome_pasta in self.pastas_user:
            return self.user_path / nome_pasta
        else:
            return self.user_path / nome_pasta
    
    def perguntar_sobrescrita(self, item_nome: str, caminho: str) -> str:
        """Pergunta ao usuario o que fazer com um item existente"""
        print(f"\n  Item existe: {item_nome}")
        print(f"    Caminho: {caminho}")
        print("    [S] Sobrescrever")
        print("    [N] Nao sobrescrever (manter existente)")
        
        while True:
            resposta = input("    Escolha (S/N): ").lower()
            if resposta in ['s', 'n']:
                return resposta
            print("    Opcao invalida! Digite S ou N")
    
    def processar_item_com_pergunta(self, origem_item, destino_item, idx, total) -> dict:
        """Processa um item que requer pergunta (sequencial)"""
        nome_item = origem_item.name
        caminho_relativo = str(origem_item.relative_to(self.origem))
        
        # Usar lock para garantir que apenas uma pergunta por vez
        with self.lock:
            resposta = self.perguntar_sobrescrita(nome_item, caminho_relativo)
        
        if resposta == 'n':
            with self.lock:
                self.itens_pulados += 1
            return {
                'nome': nome_item,
                'caminho': caminho_relativo,
                'status': 'pulado',
                'progresso': f"[{idx}/{total}]",
                'mensagem': 'Mantido (usuario escolheu nao)'
            }
        
        # Se 's', vai sobrescrever
        return self.copiar_item_direto(origem_item, destino_item, idx, total, True)
    
    def copiar_item_direto(self, origem_item, destino_item, idx, total, sobrescrever: bool) -> dict:
        """Copia um item diretamente (sem perguntas)"""
        nome_item = origem_item.name
        caminho_relativo = str(origem_item.relative_to(self.origem))
        
        try:
            destino_parent = destino_item.parent
            if not destino_parent.exists():
                destino_parent.mkdir(parents=True, exist_ok=True)
            
            # Se existe e vai sobrescrever - remover primeiro
            if destino_item.exists():
                if destino_item.is_dir():
                    shutil.rmtree(destino_item)
                else:
                    destino_item.unlink()
                with self.lock:
                    self.itens_sobrescritos += 1
                status_msg = "SOBRESCRITO"
            else:
                status_msg = "COPIADO"
                with self.lock:
                    self.itens_copiados += 1
            
            # Copiar
            if origem_item.is_dir():
                shutil.copytree(origem_item, destino_item)
                tipo = "Pasta"
            else:
                shutil.copy2(origem_item, destino_item)
                tipo = "Arquivo"
            
            # Calcular tamanho
            if origem_item.is_dir():
                tamanho_mb = sum(f.stat().st_size for f in origem_item.rglob('*') if f.is_file()) / (1024 * 1024)
            else:
                tamanho_mb = origem_item.stat().st_size / (1024 * 1024)
            
            destino_tipo = "Shared" if "Shared" in str(destino_item) else "User"
            return {
                'nome': nome_item,
                'caminho': caminho_relativo,
                'status': status_msg.lower(),
                'progresso': f"[{idx}/{total}]",
                'mensagem': f'{tipo} -> {destino_tipo} ({tamanho_mb:.1f} MB)'
            }
            
        except Exception as e:
            with self.lock:
                self.erros += 1
            return {
                'nome': nome_item,
                'caminho': caminho_relativo,
                'status': 'erro',
                'progresso': f"[{idx}/{total}]",
                'mensagem': str(e)
            }
    
    def copiar_item(self, args: tuple) -> dict:
        """Copia um item (pasta ou arquivo)"""
        origem_item, destino_item, idx, total = args
        nome_item = origem_item.name
        caminho_relativo = str(origem_item.relative_to(self.origem))
        
        # Verificar se item existe
        if destino_item.exists():
            # Aplicar o modo de sobrescrita definido no inicio
            if self.modo_sobrescrita == 'none':
                with self.lock:
                    self.itens_pulados += 1
                return {
                    'nome': nome_item,
                    'caminho': caminho_relativo,
                    'status': 'pulado',
                    'progresso': f"[{idx}/{total}]",
                    'mensagem': 'Ignorado (modo ignore all)'
                }
            elif self.modo_sobrescrita == 'all':
                return self.copiar_item_direto(origem_item, destino_item, idx, total, True)
            elif self.modo_sobrescrita == 'ask':
                # Processar com pergunta (sequencial)
                return self.processar_item_com_pergunta(origem_item, destino_item, idx, total)
        
        # Item nao existe - copiar direto
        return self.copiar_item_direto(origem_item, destino_item, idx, total, False)
    
    def sincronizar(self):
        """Sincroniza com opcao de escolha definida no inicio"""
        self.log(f"\n{'='*60}")
        self.log(f"- SINCRONIZANDO (LUGARES CORRETOS)")
        self.log(f"{'='*60}")
        self.log(f"- Origem: {self.origem}")
        self.log(f"- User ID: {self.user_id}")
        self.log(f"- Shared: {self.shared_path}")
        self.log(f"- User: {self.user_path}")
        self.log(f"- Workers: {self.max_workers}")
        self.log(f"{'='*60}\n")
        
        if not self.origem.exists():
            self.log(f"ERRO: Pasta de origem nao existe: {self.origem}")
            return None
        
        # Criar pastas de destino
        self.shared_path.mkdir(parents=True, exist_ok=True)
        self.user_path.mkdir(parents=True, exist_ok=True)
        
        
        # PASSO 1: LISTAR APENAS PASTAS BASE (1o NIVEL)
        
        self.log("- LISTANDO PASTAS BASE...")
        
        pastas_base = []
        for pasta_origem in self.origem.iterdir():
            if pasta_origem.is_dir():
                nome_pasta = pasta_origem.name
                destino_pasta = self.get_destino(nome_pasta)
                destino_tipo = "Shared" if nome_pasta in self.pastas_shared else "User"
                pastas_base.append((pasta_origem, destino_pasta, destino_tipo, nome_pasta))
                
                if destino_pasta.exists():
                    self.log(f"  - {nome_pasta}/ -> {destino_tipo} (JA EXISTE)")
                else:
                    self.log(f"  - {nome_pasta}/ -> {destino_tipo} (NOVA)")
        
        self.log(f"\n  Total de pastas base: {len(pastas_base)}")
        
        if not pastas_base:
            self.log("Nenhuma pasta base encontrada!")
            return None
        
        
        # PASSO 2: PERGUNTAR MODO DE SOBRESCRITA (APENAS NO INICIO)
        
        print("\n" + "="*60)
        print("MODO DE SOBRESCRITA PARA ITENS DO SEGUNDO NIVEL")
        print("="*60)
        print()
        print("Escolha como lidar com os itens que ja existem:")
        print("  [S] Sobrescrever TUDO (todos os itens existentes)")
        print("  [I] Ignorar TUDO (manter o que ja existe)")
        print("  [P] Perguntar a cada item (recomendado)")
        print()
        
        while True:
            escolha = input("Opcao (S/I/P): ").lower()
            if escolha in ['s', 'i', 'p']:
                if escolha == 's':
                    self.modo_sobrescrita = 'all'
                    self.log("  Modo: SOBRESCREVER TODOS os itens", mostrar=True)
                elif escolha == 'i':
                    self.modo_sobrescrita = 'none'
                    self.log("  Modo: IGNORAR TODOS os itens existentes", mostrar=True)
                else:
                    self.modo_sobrescrita = 'ask'
                    self.log("  Modo: PERGUNTAR para cada item", mostrar=True)
                break
            print("Opcao invalida! Digite S, I ou P")
        
        
        # PASSO 3: LISTAR ITENS DO SEGUNDO NIVEL
        
        self.log(f"\n- LISTANDO ITENS DO SEGUNDO NIVEL...")
        
        itens_para_processar = []
        
        for pasta_origem, pasta_destino, destino_tipo, nome_pasta in pastas_base:
            if not pasta_destino.exists():
                self.log(f"  - {nome_pasta}/ -> copiar pasta inteira (NOVA)")
                itens_para_processar.append((pasta_origem, pasta_destino))
                continue
            
            self.log(f"  - Verificando: {nome_pasta}/")
            
            for item in pasta_origem.iterdir():
                destino_item = pasta_destino / item.name
                itens_para_processar.append((item, destino_item))
                
                if destino_item.exists():
                    self.log(f"    - {item.name} (JA EXISTE)")
                else:
                    self.log(f"    - {item.name} (NOVO)")
        
        self.total_itens = len(itens_para_processar)
        self.log(f"\n  Total de itens a processar: {self.total_itens}")
        
        if self.total_itens == 0:
            self.log("Nenhum item para processar!")
            return None
        
        
        # PASSO 4: CONFIRMAR
        
        if not Config.SYNC_FORCE:
            resposta = input(f"\nContinuar com a copia de {self.total_itens} itens? (s/N): ")
            if resposta.lower() != 's':
                self.log("Cancelado!")
                return None
        
        
        # PASSO 5: COPIAR EM PARALELO (mas perguntas sao sequenciais)
        
        self.log(f"\nINICIANDO COPIA COM {self.max_workers} WORKERS...")
        inicio = time.time()
        
        # Preparar argumentos
        args_list = []
        for idx, (origem_item, destino_item) in enumerate(itens_para_processar, 1):
            args_list.append((origem_item, destino_item, idx, self.total_itens))
        
        # Se modo for 'ask', processar com menos workers para evitar conflitos
        workers_atuais = 1 if self.modo_sobrescrita == 'ask' else self.max_workers
        
        with ThreadPoolExecutor(max_workers=workers_atuais) as executor:
            futures = {executor.submit(self.copiar_item, args): args for args in args_list}
            
            for future in as_completed(futures):
                resultado = future.result()
                
                if resultado['status'] == 'copiado':
                    self.log(f"  {resultado['progresso']} {resultado['caminho']} (COPIADO: {resultado['mensagem']})")
                elif resultado['status'] == 'sobrescrito':
                    self.log(f"  {resultado['progresso']} {resultado['caminho']} (SOBRESCRITO: {resultado['mensagem']})")
                elif resultado['status'] == 'pulado':
                    pass
                else:
                    self.log(f"  {resultado['progresso']} {resultado['caminho']} (ERRO: {resultado['mensagem']})")
        
        
        # RESUMO FINAL
        
        tempo = time.time() - inicio
        
        self.log(f"\n{'='*60}")
        self.log(f"RESUMO FINAL")
        self.log(f"{'='*60}")
        self.log(f"  - Total itens: {self.total_itens}")
        self.log(f"  - Copiados (novos): {self.itens_copiados}")
        self.log(f"  - Sobrescritos: {self.itens_sobrescritos}")
        self.log(f"  - Mantidos: {self.itens_pulados}")
        self.log(f"  - Erros: {self.erros}")
        self.log(f"  - Tempo: {tempo:.1f} segundos")
        self.log(f"  - Destino Shared: {self.shared_path}")
        self.log(f"  - Destino User: {self.user_path}")
        self.log(f"{'='*60}")
        
        return {
            'total': self.total_itens,
            'copiados': self.itens_copiados,
            'sobrescritos': self.itens_sobrescritos,
            'pulados': self.itens_pulados,
            'erros': self.erros,
            'tempo': tempo
        }

def main():
    parser = argparse.ArgumentParser(
        description='Sincroniza pastas com.mojang para os lugares corretos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Usar caminho padrao e user ID
  python sync_minecraft.py
  
  # Especificar caminho do Minecraft e user ID
  python sync_minecraft.py --path "C:/Users/marci/AppData/Roaming/Minecraft Bedrock" --user 16283763834770312692
  
  # Usar 16 workers
  python sync_minecraft.py --workers 16
  
  # Forcar sem confirmacao
  python sync_minecraft.py --force
        """
    )
    
    # Valores padrao
    DEFAULT_PATH = r"C:\Users\marci\AppData\Roaming\Minecraft Bedrock"
    DEFAULT_USER = "16283763834770312692"
    
    parser.add_argument('-p', '--path', default=DEFAULT_PATH,
                       help=f'Caminho da pasta do Minecraft (padrao: {DEFAULT_PATH})')
    parser.add_argument('-u', '--user', default=DEFAULT_USER,
                       help=f'ID do usuario (padrao: {DEFAULT_USER})')
    parser.add_argument('-w', '--workers', type=int, default=Config.SYNC_WORKERS,
                       help=f'Workers paralelos (padrao: {Config.SYNC_WORKERS})')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Forcar sem confirmacao')
    
    args = parser.parse_args()
    
    if args.force:
        Config.SYNC_FORCE = True
    
    sincronizador = MinecraftWorldSync(
        minecraft_path=args.path,
        user_id=args.user,
        max_workers=args.workers
    )
    
    resultado = sincronizador.sincronizar()
    
    if resultado:
        sys.exit(0 if resultado['erros'] == 0 else 1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()