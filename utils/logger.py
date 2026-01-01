"""Sistema de logging para el trading system."""

import sys
from pathlib import Path
from loguru import logger
from utils.config_loader import config

# Configurar logging
log_level = config.get('logging.level', 'INFO')
log_file = config.get('logging.file', 'logs/trading.log')
max_file_size = config.get('logging.max_file_size_mb', 100) * 1024 * 1024
backup_count = config.get('logging.backup_count', 5)

# Crear directorio de logs si no existe
log_path = Path(log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)

# Remover handler por defecto
logger.remove()

# Añadir handler para consola
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=log_level,
    colorize=True
)

# Añadir handler para archivo
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level=log_level,
    rotation=max_file_size,
    retention=backup_count,
    compression="zip"
)

__all__ = ['logger']

