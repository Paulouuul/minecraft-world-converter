# save as: converter_para_mcworld.py
# Coloque este arquivo na raiz do seu projeto
# Exemplo: C:\Users\marci\Desktop\Projetos Pessoais\minecraft-world-converter\converter_para_mcworld.py

import os
import sys
import shutil
import zipfile
import json
import time
from pathlib import Path
from datetime import datetime
import argparse

class MinecraftWorldToMCWorld:
    """
    Converte pastas de mundo Minecraft para arquivos .mcworld
    (Formato compatível com Bedrock Edition)
    """
    
    def __init__(self, worlds_path=None):
        """Inicializa o conversor"""
        self.base_path = Path.cwd()
        self.log_file = self.base_path / "conversao_mcworld_log.txt"
        self.output_path = self.base_path / "MUNDOS_MCWORLD"
        self.backup_path = self.base_path / "BACKUP_MUNDOS"
        
        # Determinar caminho dos mundos
        if worlds_path:
            self.bedrock_worlds_path = Path(worlds_path)
            if not self.bedrock_worlds_path.is_absolute():
                self.bedrock_worlds_path = self.base_path / worlds_path
        else:
            # Caminho padrão
            self.bedrock_worlds_path = self.base_path / "MINECRAFTDATA" / "com.mojang" / "minecraftWorlds"
        
        # Criar diretórios
        self.output_path.mkdir(exist_ok=True)
        self.backup_path.mkdir(exist_ok=True)
        
        self.setup_logging()
        
    def setup_logging(self):
        """Configura logs"""
        self.log_lines = []
        self.log(f"{'='*60}")
        self.log(f"🎮 CONVERSOR PARA .MCWORLD")
        self.log(f"📅 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"📁 Base: {self.base_path}")
        self.log(f"📂 Mundos fonte: {self.bedrock_worlds_path}")
        self.log(f"📦 Destino: {self.output_path}")
        self.log(f"{'='*60}")
        
    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_lines.append(log_entry)
        print(log_entry)
        
    def save_log(self):
        """Salva log em arquivo"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_lines))
            self.log(f"📝 Log salvo em: {self.log_file}")
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
    
    def find_worlds(self):
        """Encontra todas as pastas de mundo"""
        worlds = []
        
        # Verificar se o caminho existe
        if not self.bedrock_worlds_path.exists():
            self.log(f"❌ Caminho não encontrado: {self.bedrock_worlds_path}")
            return worlds
        
        # Verificar se é uma pasta de mundo diretamente
        if self.bedrock_worlds_path.is_dir():
            # Verificar se a própria pasta é um mundo
            if (self.bedrock_worlds_path / "level.dat").exists():
                worlds.append(self.bedrock_worlds_path)
                return worlds
            
            # Verificar se tem arquivo .mcworld (não precisa converter)
            if any(self.bedrock_worlds_path.glob("*.mcworld")):
                self.log(f"ℹ️ Arquivos .mcworld encontrados, mas este conversor só processa pastas")
                return worlds
            
            # Procurar por mundos dentro da pasta
            for item in self.bedrock_worlds_path.iterdir():
                if item.is_dir():
                    # Verificar se é um mundo válido
                    if (item / "level.dat").exists():
                        worlds.append(item)
                    elif (item / "db").exists() and (item / "db").is_dir():
                        # Pode ser um mundo Bedrock com LevelDB
                        worlds.append(item)
                elif item.is_file() and item.suffix == '.mcworld':
                    # Já é .mcworld, não precisa converter
                    self.log(f"ℹ️ {item.name} já é .mcworld - ignorando")
        
        return worlds
    
    def get_world_info(self, world_path):
        """Obtém informações do mundo"""
        info = {
            'name': world_path.name,
            'path': world_path,
            'size': 0,
            'last_modified': datetime.fromtimestamp(world_path.stat().st_mtime),
            'type': 'Desconhecido'
        }
        
        # Determinar tipo
        if (world_path / "db").exists() and (world_path / "db").is_dir():
            info['type'] = 'Bedrock (LevelDB)'
        elif (world_path / "region").exists() and (world_path / "region").is_dir():
            info['type'] = 'Java (Anvil)'
        elif any(world_path.glob("region/*.mcr")):
            info['type'] = 'Java (Alpha)'
        elif (world_path / "level.dat").exists():
            info['type'] = 'Minecraft (genérico)'
        
        # Calcular tamanho
        try:
            total_size = 0
            for file in world_path.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
            info['size'] = total_size
        except:
            pass
        
        return info
    
    def backup_world(self, world_path):
        """Faz backup da pasta do mundo"""
        backup_dir = self.backup_path / world_path.name
        if backup_dir.exists():
            self.log(f"  💾 Backup já existe: {world_path.name}")
            return True
            
        try:
            self.log(f"  💾 Fazendo backup de {world_path.name}...")
            shutil.copytree(world_path, backup_dir)
            size_mb = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / (1024*1024)
            self.log(f"  ✅ Backup criado: {size_mb:.1f} MB")
            return True
        except Exception as e:
            self.log(f"  ❌ Erro no backup: {e}")
            return False
    
    def convert_to_mcworld(self, world_path):
        """
        Converte uma pasta de mundo para .mcworld
        Usa a MESMA lógica do primeiro script (compactação ZIP)
        """
        world_name = world_path.name
        output_file = self.output_path / f"{world_name}.mcworld"
        
        self.log(f"\n{'─'*50}")
        self.log(f"📁 Convertendo: {world_name}")
        
        # Info do mundo
        info = self.get_world_info(world_path)
        size_mb = info['size'] / (1024*1024)
        self.log(f"  📊 Tamanho: {size_mb:.1f} MB")
        self.log(f"  📂 Tipo: {info['type']}")
        self.log(f"  📅 Modificado: {info['last_modified'].strftime('%Y-%m-%d %H:%M')}")
        
        # Verificar se é um mundo válido
        if not (world_path / "level.dat").exists():
            self.log(f"  ⚠️ ATENÇÃO: 'level.dat' não encontrado!")
            self.log(f"  ⚠️ Pode não ser um mundo válido. Continuando mesmo assim...")
        
        # Backup
        if not self.backup_world(world_path):
            return False
        
        # Verificar se arquivo de saída já existe
        if output_file.exists():
            self.log(f"  ⚠️ Arquivo de saída já existe: {output_file.name}")
            resposta = input("  Sobrescrever? (s/N): ")
            if resposta.lower() != 's':
                self.log("  ⏭️ Pulando")
                return False
            output_file.unlink()  # Remove o arquivo antigo
        
        # ========================================
        # AQUI ESTÁ A LÓGICA DO PRIMEIRO SCRIPT
        # ========================================
        self.log(f"  🔄 Compactando mundo...")
        
        try:
            # Contador para progresso
            arquivos_total = 0
            
            # Cria o arquivo compactado (exatamente como no primeiro script)
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for raiz, dirs, arquivos in os.walk(world_path):
                    for arquivo in arquivos:
                        caminho_completo = os.path.join(raiz, arquivo)
                        # Mantém a estrutura de pastas interna correta
                        caminho_relativo = os.path.relpath(caminho_completo, world_path)
                        zipf.write(caminho_completo, caminho_relativo)
                        arquivos_total += 1
                        
                        # Mostra progresso a cada 100 arquivos
                        if arquivos_total % 100 == 0:
                            self.log(f"    📁 {arquivos_total} arquivos compactados...")
            
            # Verificar se o arquivo foi criado
            if output_file.exists():
                tamanho_mb = output_file.stat().st_size / (1024 * 1024)
                self.log(f"  ✅ CONVERSÃO CONCLUÍDA!")
                self.log(f"  📦 Arquivo: {output_file.name}")
                self.log(f"  📊 Tamanho: {tamanho_mb:.2f} MB")
                self.log(f"  📄 Arquivos: {arquivos_total}")
                
                # Salvar info de conversão
                info_file = self.output_path / f"{world_name}_info.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"Mundo original: {world_name}\n")
                    f.write(f"Data conversão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Tamanho original: {size_mb:.1f} MB\n")
                    f.write(f"Tamanho .mcworld: {tamanho_mb:.2f} MB\n")
                    f.write(f"Total arquivos: {arquivos_total}\n")
                    f.write(f"Tipo original: {info['type']}\n")
                
                return True
            else:
                self.log(f"  ❌ Arquivo de saída não foi criado!")
                return False
                
        except Exception as e:
            self.log(f"  ❌ Erro na compactação: {e}")
            import traceback
            self.log(f"  Detalhes: {traceback.format_exc()[:300]}")
            return False
    
    def run(self, worlds_to_convert=None, no_confirm=False):
        """Executa a conversão"""
        try:
            # Encontrar mundos
            worlds = self.find_worlds()
            
            if not worlds:
                self.log("❌ Nenhuma pasta de mundo encontrada!")
                self.log(f"   Verifique: {self.bedrock_worlds_path}")
                self.log("   Este conversor processa PASTAS de mundo, não arquivos .mcworld")
                return False
            
            # Filtrar
            if worlds_to_convert:
                worlds = [w for w in worlds if w.name in worlds_to_convert]
                if not worlds:
                    self.log(f"❌ Nenhum dos mundos especificados encontrado")
                    return False
            
            # Mostrar resumo
            self.log(f"\n📋 Mundos encontrados (pastas):")
            for i, world in enumerate(worlds, 1):
                info = self.get_world_info(world)
                size_mb = info['size'] / (1024*1024)
                self.log(f"  {i}. {world.name} 📁 ({size_mb:.1f} MB) - {info['type']}")
            
            # Confirmar
            if not no_confirm:
                resposta = input(f"\n❓ Converter {len(worlds)} mundo(s) para .mcworld? (s/N): ")
                if resposta.lower() != 's':
                    self.log("⏹️ Cancelado")
                    return False
            
            # Converter
            sucessos = 0
            falhas = 0
            inicio = time.time()
            
            for i, world in enumerate(worlds, 1):
                self.log(f"\n[{i}/{len(worlds)}] Processando: {world.name}")
                if self.convert_to_mcworld(world):
                    sucessos += 1
                else:
                    falhas += 1
            
            # Resumo final
            tempo = time.time() - inicio
            self.log(f"\n{'='*60}")
            self.log(f"📊 RESUMO FINAL")
            self.log(f"{'='*60}")
            self.log(f"  Total: {len(worlds)} mundos")
            self.log(f"  ✅ Sucessos: {sucessos}")
            self.log(f"  ❌ Falhas: {falhas}")
            self.log(f"  ⏱️ Tempo: {tempo/60:.1f} minutos")
            self.log(f"  📁 Saída: {self.output_path}")
            self.log(f"  💾 Backup: {self.backup_path}")
            self.log(f"\n💡 Os arquivos .mcworld estão prontos para uso no Minecraft Bedrock!")
            
            self.save_log()
            return sucessos > 0
            
        except KeyboardInterrupt:
            self.log("\n⚠️ Interrompido pelo usuário!")
            self.save_log()
            return False
        except Exception as e:
            self.log(f"❌ Erro: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.save_log()
            return False

def main():
    parser = argparse.ArgumentParser(
        description='Converte PASTAS de mundo Minecraft para .mcworld (Bedrock)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Usar caminho padrão (WORLDSMINECRAFT/com.mojang/minecraftWorlds)
  python converter_para_mcworld.py
  
  # Especificar caminho de uma pasta com mundos
  python converter_para_mcworld.py -p "C:/Minecraft/saves"
  
  # Especificar uma única pasta de mundo
  python converter_para_mcworld.py -p "C:/Minecraft/saves/MeuMundo"
  
  # Converter apenas mundos específicos
  python converter_para_mcworld.py --only "Mundo1" "Mundo2"
  
  # Pular confirmação
  python converter_para_mcworld.py --no-confirm
  
  # Listar mundos disponíveis
  python converter_para_mcworld.py --list

NOTA: Este conversor processa PASTAS de mundo e as compacta em .mcworld
      (NÃO converte Bedrock -> Java, apenas empacota para .mcworld)
        """
    )
    
    parser.add_argument('-p', '--path', help='Caminho para pasta com mundos ou pasta de mundo específica')
    parser.add_argument('--only', nargs='+', help='Converter apenas mundos específicos')
    parser.add_argument('--no-confirm', action='store_true', help='Pular confirmação')
    parser.add_argument('--list', action='store_true', help='Listar mundos e sair')
    
    args = parser.parse_args()
    
    # Criar conversor
    converter = MinecraftWorldToMCWorld(args.path)
    
    # Listar mundos
    if args.list:
        worlds = converter.find_worlds()
        if worlds:
            print(f"\n📋 Pastas de mundo encontradas em: {converter.bedrock_worlds_path}")
            for i, world in enumerate(worlds, 1):
                info = converter.get_world_info(world)
                size_mb = info['size'] / (1024*1024)
                print(f"  {i}. {world.name} 📁 ({size_mb:.1f} MB) - {info['type']}")
        else:
            print("❌ Nenhuma pasta de mundo encontrada")
            print("   Este conversor procura por PASTAS com level.dat")
        return
    
    # Executar conversão
    success = converter.run(
        worlds_to_convert=args.only,
        no_confirm=args.no_confirm
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()