# main.py
# Ponto de entrada principal - converte mundos para .mcworld

import sys
import time
import argparse
from pathlib import Path

from config import Config
from logger import Logger
from world_finder import WorldFinder
from mcworld_converter import MCWorldConverter
from bedrock_java_converter import BedrockJavaConverter
from utils import format_time, confirm_action

def main():
    parser = argparse.ArgumentParser(
        description='Converte PASTAS de mundo Minecraft para .mcworld (Bedrock)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Converter para .mcworld (padrão)
  python main.py
  
  # Converter para Java (requer MCC Toolchest)
  python main.py --java
  
  # Converter apenas mundos específicos
  python main.py --only "Mundo1" "Mundo2"
  
  # Listar mundos disponíveis
  python main.py --list
  
  # Especificar caminho personalizado
  python main.py -p "C:/Minecraft/saves"
  
  # Pular confirmação
  python main.py --no-confirm
        """
    )
    
    parser.add_argument('-p', '--path', help='Caminho para pasta com mundos')
    parser.add_argument('--only', nargs='+', help='Converter apenas mundos específicos')
    parser.add_argument('--no-confirm', action='store_true', help='Pular confirmação')
    parser.add_argument('--list', action='store_true', help='Listar mundos e sair')
    parser.add_argument('--java', action='store_true', help='Converter para Java (não .mcworld)')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescrever arquivos existentes')
    
    args = parser.parse_args()
    
    # CONFIGURAÇÃO
    Config.create_directories()
    
    # Criar logger
    if args.java:
        log_file = Config.LOG_FILE_JAVA
    else:
        log_file = Config.LOG_FILE_MCWORLD
    
    logger = Logger(log_file)
    logger.log_section("CONVERSOR DE MUNDOS MINECRAFT")
    logger.log(f"- Base: {Config.BASE_PATH}")
    
    # Determinar caminho
    if args.path:
        worlds_path = Path(args.path)
        if not worlds_path.is_absolute():
            worlds_path = Config.BASE_PATH / worlds_path
    else:
        worlds_path = Config.DEFAULT_WORLDS_PATH
    
    logger.log(f"- Mundos: {worlds_path}")
    
    # ENCONTRAR MUNDOS
    finder = WorldFinder(worlds_path)
    worlds = finder.find_worlds()
    
    if not worlds:
        logger.log_error("Nenhum mundo encontrado!")
        logger.log_info(f"Verifique: {worlds_path}")
        sys.exit(1)
    
    # Filtrar mundos
    if args.only:
        worlds = [w for w in worlds if w.name in args.only]
        if not worlds:
            logger.log_error("Nenhum dos mundos especificados foi encontrado")
            sys.exit(1)
    
    # LISTAR MUNDOS
    if args.list:
        print(finder.get_summary())
        sys.exit(0)
    
    # RESUMO
    logger.log("Mundos encontrados:")
    for i, world in enumerate(worlds, 1):
        logger.log(f"  {i}. {world.name} ({world.world_type}) - {world.size_mb:.1f} MB")
    
    # CONFIRMAÇÃO
    if not args.no_confirm:
        tipo = "Java" if args.java else ".mcworld"
        if not confirm_action(f"\n- Converter {len(worlds)} mundo(s) para {tipo}?"):
            logger.log("Cancelado")
            sys.exit(0)
    
    # CONVERSÃO
    if args.java:
        converter = BedrockJavaConverter(Config.OUTPUT_JAVA_PATH, logger)
    else:
        converter = MCWorldConverter(Config.OUTPUT_MCWORLD_PATH, logger)
    
    sucessos = 0
    falhas = 0
    inicio = time.time()
    
    for i, world in enumerate(worlds, 1):
        logger.log(f"\n[{i}/{len(worlds)}] Processando: {world.name}")
        if converter.convert(world, overwrite=args.overwrite):
            sucessos += 1
        else:
            falhas += 1
    
    # RESUMO FINAL
    tempo = time.time() - inicio
    logger.log(f"\n{'='*60}")
    logger.log("RESUMO FINAL")
    logger.log(f"{'='*60}")
    logger.log(f"  Total: {len(worlds)} mundos")
    logger.log(f"  - Sucessos: {sucessos}")
    logger.log(f"  - Falhas: {falhas}")
    logger.log(f"  - Tempo: {format_time(tempo)}")
    logger.log(f"  - Saída: {converter.output_path}")
    logger.log(f"  - Backup: {Config.BACKUP_PATH}")
    
    if not args.java:
        logger.log("\n💡 Os arquivos .mcworld estão prontos para uso no Minecraft Bedrock!")
        logger.log("   Basta dar duplo clique em um arquivo .mcworld para importar.")
    
    logger.save_log()
    
    sys.exit(0 if sucessos > 0 else 1)

if __name__ == "__main__":
    main()