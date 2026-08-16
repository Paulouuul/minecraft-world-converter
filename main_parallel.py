# main_parallel.py
# Ponto de entrada com suporte a conversão paralela

import sys
import time
import argparse
from pathlib import Path

from config import Config
from logger import Logger
from world_finder import WorldFinder
from mcworld_converter_parallel import MCWorldConverterParallel
from utils import format_time, confirm_action

def main():
    parser = argparse.ArgumentParser(
        description='Converte PASTAS de mundo Minecraft para .mcworld em PARALELO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Converter em paralelo (4 mundos por vez)
  python main_parallel.py
  
  # Converter com 8 mundos por vez
  python main_parallel.py --workers 8
  
  # Converter apenas mundos específicos
  python main_parallel.py --only "Mundo1" "Mundo2"
  
  # Listar mundos disponíveis
  python main_parallel.py --list
  
  # Pular confirmação
  python main_parallel.py --no-confirm
        """
    )
    
    parser.add_argument('-p', '--path', help='Caminho para pasta com mundos')
    parser.add_argument('--only', nargs='+', help='Converter apenas mundos específicos')
    parser.add_argument('--no-confirm', action='store_true', help='Pular confirmação')
    parser.add_argument('--list', action='store_true', help='Listar mundos e sair')
    parser.add_argument('--workers', type=int, default=4, help='Número de conversões paralelas (padrão: 4)')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescrever arquivos existentes')
    
    args = parser.parse_args()
    
    # CONFIGURAÇÃO
    Config.create_directories()
    
    # Criar logger
    logger = Logger(Config.LOG_FILE_MCWORLD)
    logger.log_section("CONVERSOR PARALELO PARA .MCWORLD")
    logger.log(f"📁 Base: {Config.BASE_PATH}")
    logger.log(f"⚡ Trabalhadores: {args.workers}")
    
    # Determinar caminho
    if args.path:
        worlds_path = Path(args.path)
        if not worlds_path.is_absolute():
            worlds_path = Config.BASE_PATH / worlds_path
    else:
        worlds_path = Config.DEFAULT_WORLDS_PATH
    
    logger.log(f"📂 Mundos: {worlds_path}")
    
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
    logger.log("\n📋 Mundos encontrados:")
    for i, world in enumerate(worlds, 1):
        logger.log(f"  {i}. {world.name} ({world.world_type}) - {world.size_mb:.1f} MB")
    
    # CONFIRMAÇÃO
    if not args.no_confirm:
        if not confirm_action(f"\n- Converter {len(worlds)} mundo(s) em PARALELO ({args.workers} por vez)?"):
            logger.log("- Cancelado")
            sys.exit(0)
    
    # CONVERSÃO PARALELA
    converter = MCWorldConverterParallel(
        Config.OUTPUT_MCWORLD_PATH, 
        logger, 
        max_workers=args.workers
    )
    
    inicio = time.time()
    stats = converter.convert(worlds, overwrite=args.overwrite)
    tempo = time.time() - inicio
    
    # RESUMO FINAL
    logger.log(f"\n{'='*60}")
    logger.log(f"RESUMO FINAL")
    logger.log(f"{'='*60}")
    logger.log(f"  Total: {stats['total']} mundos")
    logger.log(f"  - Sucessos: {stats['success']}")
    logger.log(f"  - Falhas: {stats['failed']}")
    logger.log(f"  - Tempo: {format_time(tempo)}")
    logger.log(f"  - Trabalhadores: {args.workers}")
    logger.log(f"  - Saída: {converter.output_path}")
    logger.log(f"  - Backup: {Config.BACKUP_PATH}")
    
    logger.log("\n- Os arquivos .mcworld estão prontos para uso no Minecraft Bedrock!")
    logger.log("   Basta dar duplo clique em um arquivo .mcworld para importar.")
    
    logger.save_log()
    
    sys.exit(0 if stats['success'] > 0 else 1)

if __name__ == "__main__":
    main()