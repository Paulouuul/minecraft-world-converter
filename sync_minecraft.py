# sync_minecraft.py
# Sincroniza pastas com.mojang - recebe caminho do Minecraft e User ID
# Uso: python sync_minecraft.py --path "C:/Users/marci/AppData/Roaming/Minecraft Bedrock" --user 16283763834770312692

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
        """
        Args:
            minecraft_path: Caminho para a pasta do Minecraft (ex: .../Minecraft Bedrock)
            user_id: ID do usuário (ex: 16283763834770312692)
            origem: Pasta origem dos arquivos (com.mojang)
            max_workers: Número de workers paralelos
        """
        self.minecraft_path = Path(minecraft_path)
        self.user_id = user_id
        
        # Determinar caminhos
        self.shared_path = self.minecraft_path / "Users" / "Shared" / "games" / "com.mojang"
        self.user_path = self.minecraft_path / "Users" / user_id / "games" / "com.mojang"
        
        # Pasta origem
        self.origem = origem or Config.SOURCE_MCWORLD_PATH
        
        self.max_workers = max_workers or Config.SYNC_WORKERS
        self.lock = threading.Lock()
        
        # Estatísticas
        self.itens_copiados = 0
        self.itens_pulados = 0
        self.itens_sobrescritos = 0
        self.erros = 0
        self.total_itens = 0
        
        # Log
        self.log_file = Config.LOG_FILE_SYNC
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== SINCRONIZAÇÃO INICIADA EM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
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
            # Pastas desconhecidas vão para User
            return self.user_path / nome_pasta
    
    def copiar_item(self, args: tuple) -> dict:
        """Copia um item (pasta ou arquivo)"""
        origem_item, destino_item, idx, total, sobrescrever = args
        nome_item = origem_item.name
        caminho_relativo = str(origem_item.relative_to(self.origem))
        
        try:
            destino_parent = destino_item.parent
            if not destino_parent.exists():
                destino_parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar se item existe
            if destino_item.exists() and not sobrescrever:
                with self.lock:
                    self.itens_pulados += 1
                return {
                    'nome': nome_item,
                    'caminho': caminho_relativo,
                    'status': 'pulado',
                    'progresso': f"[{idx}/{total}]",
                    'mensagem': 'Já existe (mantido)'
                }
            
            # Se existe e vai sobrescrever - remover primeiro
            if destino_item.exists() and sobrescrever:
                if destino_item.is_dir():
                    shutil.rmtree(destino_item)
                else:
                    destino_item.unlink()
                with self.lock:
                    self.itens_sobrescritos += 1
            
            # Copiar
            with self.lock:
                self.itens_copiados += 1
            
            if origem_item.is_dir():
                shutil.copytree(origem_item, destino_item)
                tipo = "- Pasta"
            else:
                shutil.copy2(origem_item, destino_item)
                tipo = "- Arquivo"
            
            # Calcular tamanho
            if origem_item.is_dir():
                tamanho_mb = sum(f.stat().st_size for f in origem_item.rglob('*') if f.is_file()) / (1024 * 1024)
            else:
                tamanho_mb = origem_item.stat().st_size / (1024 * 1024)
            
            status_msg = "SOBRESCRITO" if sobrescrever and destino_item.exists() else "COPIADO"
            destino_tipo = "Shared" if "Shared" in str(destino_item) else "User"
            return {
                'nome': nome_item,
                'caminho': caminho_relativo,
                'status': status_msg.lower(),
                'progresso': f"[{idx}/{total}]",
                'mensagem': f'{tipo} → {destino_tipo} ({tamanho_mb:.1f} MB)'
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
    
    def escolher_sobrescrita(self, itens_existentes: list) -> dict:
        """Menu para escolher quais itens sobrescrever"""
        print("\n" + "="*60)
        print("- ITENS QUE JÁ EXISTEM NO DESTINO")
        print("="*60)
        print()
        
        print("Escolha uma opção:")
        print("  1. Sobrescrever TODOS os itens")
        print("  2. NÃO sobrescrever NENHUM item (apenas copiar novos) RECOMENDADO")
        print("  3. Escolher item por item")
        print("  4. Sobrescrever apenas por TAMANHO (se diferente)")
        print("  5. Sobrescrever apenas por DATA (se mais novo)")
        print()
        
        opcao = input("Opção (1-5): ")
        
        if opcao == "1":
            return {'todos': True, 'nenhum': False, 'individual': False, 'tamanho': False, 'data': False}
        elif opcao == "2":
            return {'todos': False, 'nenhum': True, 'individual': False, 'tamanho': False, 'data': False}
        elif opcao == "3":
            return self.escolher_individual(itens_existentes)
        elif opcao == "4":
            return {'todos': False, 'nenhum': False, 'individual': False, 'tamanho': True, 'data': False}
        elif opcao == "5":
            return {'todos': False, 'nenhum': False, 'individual': False, 'tamanho': False, 'data': True}
        else:
            print("Opção inválida! Usando opção 2 (não sobrescrever)")
            return {'todos': False, 'nenhum': True, 'individual': False, 'tamanho': False, 'data': False}
    
    def escolher_individual(self, itens_existentes: list) -> dict:
        """Escolhe item por item para sobrescrever"""
        print("\n" + "="*60)
        print("- ESCOLHA ITEM POR ITEM")
        print("="*60)
        print()
        print("Digite o número do item para sobrescrever")
        print("Digite 0 para continuar")
        print()
        
        sobrescrever_set = set()
        
        for i, (item, caminho) in enumerate(itens_existentes, 1):
            print(f"[{i}] {caminho}")
        
        print()
        
        while True:
            try:
                escolha = input(f"\nDigite o número (0 para sair): ")
                if escolha == "0":
                    break
                num = int(escolha)
                if 1 <= num <= len(itens_existentes):
                    item, caminho = itens_existentes[num-1]
                    sobrescrever_set.add(str(item))
                    print(f"{caminho} será sobrescrito")
                else:
                    print("Número inválido!")
            except ValueError:
                print("Digite um número válido!")
        
        return {'todos': False, 'nenhum': False, 'individual': True, 
                'sobrescrever_set': sobrescrever_set, 'tamanho': False, 'data': False}
    
    def sincronizar(self):
        """Sincroniza com opção de escolha"""
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
            self.log(f"ERRO: Pasta de origem não existe: {self.origem}")
            return None
        
        # Criar pastas de destino
        self.shared_path.mkdir(parents=True, exist_ok=True)
        self.user_path.mkdir(parents=True, exist_ok=True)
        
        # ============================================================
        # LISTAR ITENS
        # ============================================================
        self.log(f"- LISTANDO ITENS...")
        
        itens_para_processar = []
        itens_existentes = []
        
        for pasta_origem in self.origem.iterdir():
            if pasta_origem.is_dir():
                nome_pasta = pasta_origem.name
                destino_pasta = self.get_destino(nome_pasta)
                destino_tipo = "Shared" if nome_pasta in self.pastas_shared else "User"
                
                if not destino_pasta.exists():
                    # Pasta inteira não existe → copiar tudo
                    itens_para_processar.append((pasta_origem, destino_pasta))
                    self.log(f"  - {nome_pasta}/ → {destino_tipo} (pasta inteira será copiada)")
                    continue
                
                self.log(f"  - Verificando: {nome_pasta}/ → {destino_tipo}")
                
                # Pasta existe → verificar APENAS 1 NÍVEL dentro
                for item in pasta_origem.iterdir():
                    destino_item = destino_pasta / item.name
                    
                    if destino_item.exists():
                        itens_existentes.append((item, destino_item))
                        # Mostrar info
                        if item.is_file():
                            tam_origem = item.stat().st_size / 1024
                            tam_destino = destino_item.stat().st_size / 1024
                            print(f"    - {item.name} ({tam_origem:.1f}KB → {tam_destino:.1f}KB)")
                        else:
                            print(f"    - {item.name}/")
                    else:
                        itens_para_processar.append((item, destino_item))
                        if item.is_dir():
                            self.log(f"    - {item.name}/ (pasta será copiada)")
                        else:
                            self.log(f"    - {item.name} (arquivo será copiado)")
        
        self.total_itens = len(itens_para_processar) + len(itens_existentes)
        self.log(f"\n  Novos itens: {len(itens_para_processar)}")
        self.log(f"  Itens existentes: {len(itens_existentes)}")
        
        if self.total_itens == 0:
            self.log("Nenhum item para processar!")
            return None
        
        # ============================================================
        # ESCOLHER SOBRESCRITA
        # ============================================================
        if itens_existentes:
            escolha = self.escolher_sobrescrita(itens_existentes)
        else:
            escolha = {'todos': False, 'nenhum': True, 'individual': False, 'tamanho': False, 'data': False}
        
        # ============================================================
        # PREPARAR ARGUMENTOS
        # ============================================================
        args_list = []
        idx = 0
        
        # Novos itens (sempre copiar)
        for origem_item, destino_item in itens_para_processar:
            idx += 1
            args_list.append((origem_item, destino_item, idx, self.total_itens, False))
        
        # Itens existentes (copiar se for para sobrescrever)
        for origem_item, destino_item in itens_existentes:
            idx += 1
            sobrescrever = False
            
            if escolha.get('todos', False):
                sobrescrever = True
            elif escolha.get('individual', False):
                if str(origem_item) in escolha.get('sobrescrever_set', set()):
                    sobrescrever = True
            elif escolha.get('tamanho', False):
                tam_origem = sum(f.stat().st_size for f in origem_item.rglob('*') if f.is_file())
                tam_destino = sum(f.stat().st_size for f in destino_item.rglob('*') if f.is_file())
                if tam_origem != tam_destino:
                    sobrescrever = True
            elif escolha.get('data', False):
                if origem_item.stat().st_mtime > destino_item.stat().st_mtime:
                    sobrescrever = True
            
            args_list.append((origem_item, destino_item, idx, self.total_itens, sobrescrever))
        
        # ============================================================
        # CONFIRMAR
        # ============================================================
        print(f"\nRESUMO:")
        print(f"  - Total itens: {self.total_itens}")
        print(f"  - Novos itens: {len(itens_para_processar)}")
        print(f"  - A sobrescrever: {sum(1 for a in args_list if a[4])}")
        
        if not Config.SYNC_FORCE:
            resposta = input(f"\n❓ Continuar? (s/N): ")
            if resposta.lower() != 's':
                self.log("Cancelado!")
                return None
        
        # ============================================================
        # COPIAR EM PARALELO
        # ============================================================
        self.log(f"\n🚀 INICIANDO CÓPIA COM {self.max_workers} WORKERS...")
        inicio = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.copiar_item, args): args for args in args_list}
            
            for future in as_completed(futures):
                resultado = future.result()
                
                if resultado['status'] == 'copiado':
                    self.log(f"  {resultado['progresso']} {resultado['caminho']} (COPIADO: {resultado['mensagem']})")
                elif resultado['status'] == 'sobrescrito':
                    self.log(f"  {resultado['progresso']} - {resultado['caminho']} (SOBRESCRITO: {resultado['mensagem']})")
                elif resultado['status'] == 'pulado':
                    pass
                else:
                    self.log(f"  {resultado['progresso']} {resultado['caminho']} (ERRO: {resultado['mensagem']})")
        
        # ============================================================
        # RESUMO FINAL
        # ============================================================
        tempo = time.time() - inicio
        
        self.log(f"\n{'='*60}")
        self.log(f"RESUMO FINAL")
        self.log(f"{'='*60}")
        self.log(f"  - Total itens: {self.total_itens}")
        self.log(f"  Copiados (novos): {self.itens_copiados - self.itens_sobrescritos}")
        self.log(f"  - Sobrescritos: {self.itens_sobrescritos}")
        self.log(f"  -  Mantidos: {self.itens_pulados}")
        self.log(f"  Erros: {self.erros}")
        self.log(f"  -  Tempo: {tempo:.1f} segundos")
        self.log(f"  - Destino Shared: {self.shared_path}")
        self.log(f"  - Destino User: {self.user_path}")
        self.log(f"{'='*60}")
        
        return {
            'total': self.total_itens,
            'copiados': self.itens_copiados - self.itens_sobrescritos,
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
  # Usar caminho padrão e user ID
  python sync_minecraft.py
  
  # Especificar caminho do Minecraft e user ID
  python sync_minecraft.py --path "C:/Users/marci/AppData/Roaming/Minecraft Bedrock" --user 16283763834770312692
  
  # Usar 16 workers
  python sync_minecraft.py --workers 16
  
  # Forçar sem confirmação (não sobrescreve nada)
  python sync_minecraft.py --force
        """
    )
    
    # Valores padrão
    DEFAULT_PATH = r"C:\Users\marci\AppData\Roaming\Minecraft Bedrock"
    DEFAULT_USER = "16283763834770312692"
    
    parser.add_argument('-p', '--path', default=DEFAULT_PATH,
                       help=f'Caminho da pasta do Minecraft (padrão: {DEFAULT_PATH})')
    parser.add_argument('-u', '--user', default=DEFAULT_USER,
                       help=f'ID do usuário (padrão: {DEFAULT_USER})')
    parser.add_argument('-w', '--workers', type=int, default=Config.SYNC_WORKERS,
                       help=f'Workers paralelos (padrão: {Config.SYNC_WORKERS})')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Forçar sem confirmação')
    
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