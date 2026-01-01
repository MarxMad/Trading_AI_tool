"""Clase base para recolectores de datos de mercado."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from utils.logger import logger


class BaseDataCollector(ABC):
    """Clase base abstracta para todos los recolectores de datos."""
    
    def __init__(self, name: str):
        """
        Inicializa el recolector.
        
        Args:
            name: Nombre del recolector
        """
        self.name = name
        self.logger = logger.bind(name=f"DataCollector.{name}")
    
    @abstractmethod
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos para un símbolo.
        
        Args:
            symbol: Símbolo del activo (ej: 'AAPL', 'BTC/USDT')
            start_date: Fecha de inicio
            end_date: Fecha de fin
            interval: Intervalo de tiempo ('1m', '5m', '1h', '1d', etc.)
            
        Returns:
            DataFrame con columnas: open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def fetch_realtime_data(self, symbol: str) -> Dict:
        """
        Obtiene datos en tiempo real para un símbolo.
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Diccionario con datos actuales del mercado
        """
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> List[str]:
        """
        Obtiene lista de símbolos disponibles.
        
        Returns:
            Lista de símbolos disponibles
        """
        pass
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Valida que los datos tengan el formato correcto.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            True si los datos son válidos
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        if df.empty:
            self.logger.warning("DataFrame está vacío")
            return False
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.logger.error(f"Faltan columnas requeridas: {missing_columns}")
            return False
        
        # Verificar que high >= low, high >= open, high >= close, etc.
        if not (df['high'] >= df['low']).all():
            self.logger.error("Datos inválidos: high < low")
            return False
        
        if not (df['high'] >= df['open']).all():
            self.logger.error("Datos inválidos: high < open")
            return False
        
        if not (df['high'] >= df['close']).all():
            self.logger.error("Datos inválidos: high < close")
            return False
        
        if not (df['low'] <= df['open']).all():
            self.logger.error("Datos inválidos: low > open")
            return False
        
        if not (df['low'] <= df['close']).all():
            self.logger.error("Datos inválidos: low > close")
            return False
        
        return True

