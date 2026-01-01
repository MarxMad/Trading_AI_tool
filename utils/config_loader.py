"""Cargador de configuración desde archivos YAML y variables de entorno."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class ConfigLoader:
    """Carga y gestiona la configuración del sistema."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializa el cargador de configuración.
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Carga la configuración desde el archivo YAML."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de puntos.
        
        Args:
            key: Clave en formato 'section.subsection.key'
            default: Valor por defecto si no se encuentra
            
        Returns:
            Valor de configuración o default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de variable de entorno.
        
        Args:
            key: Nombre de la variable de entorno
            default: Valor por defecto
            
        Returns:
            Valor de la variable de entorno o default
        """
        return os.getenv(key, default)
    
    def update(self, key: str, value: Any) -> None:
        """
        Actualiza un valor de configuración.
        
        Args:
            key: Clave en formato 'section.subsection.key'
            value: Nuevo valor
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value


# Instancia global de configuración
config = ConfigLoader()

