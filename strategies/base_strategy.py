"""Clase base para estrategias de trading."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd
from utils.logger import logger


class BaseStrategy(ABC):
    """Clase base abstracta para todas las estrategias de trading."""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        Inicializa la estrategia.
        
        Args:
            name: Nombre de la estrategia
            config: Configuración de la estrategia
        """
        self.name = name
        self.config = config or {}
        self.logger = logger.bind(name=f"Strategy.{name}")
        self.positions = {}  # Símbolo -> información de posición
        self.signals_history = []  # Historial de señales
    
    @abstractmethod
    def generate_signal(
        self,
        data: pd.DataFrame,
        symbol: str,
        current_price: float
    ) -> Dict:
        """
        Genera una señal de trading basada en los datos.
        
        Args:
            data: DataFrame con datos históricos OHLCV
            symbol: Símbolo del activo
            current_price: Precio actual
            
        Returns:
            Diccionario con:
                - action: 'buy', 'sell', 'hold'
                - confidence: float entre 0 y 1
                - price: precio objetivo
                - stop_loss: precio de stop loss
                - take_profit: precio de take profit
                - reason: razón de la señal
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores técnicos necesarios para la estrategia.
        
        Args:
            data: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con indicadores añadidos
        """
        pass
    
    def should_exit_position(
        self,
        symbol: str,
        current_price: float,
        data: pd.DataFrame
    ) -> bool:
        """
        Determina si se debe cerrar una posición existente.
        
        Args:
            symbol: Símbolo del activo
            current_price: Precio actual
            data: DataFrame con datos históricos
            
        Returns:
            True si se debe cerrar la posición
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        
        # Verificar stop loss
        if 'stop_loss' in position:
            if position['side'] == 'long' and current_price <= position['stop_loss']:
                self.logger.info(f"Stop loss activado para {symbol} a {current_price}")
                return True
            elif position['side'] == 'short' and current_price >= position['stop_loss']:
                self.logger.info(f"Stop loss activado para {symbol} a {current_price}")
                return True
        
        # Verificar take profit
        if 'take_profit' in position:
            if position['side'] == 'long' and current_price >= position['take_profit']:
                self.logger.info(f"Take profit activado para {symbol} a {current_price}")
                return True
            elif position['side'] == 'short' and current_price <= position['take_profit']:
                self.logger.info(f"Take profit activado para {symbol} a {current_price}")
                return True
        
        return False
    
    def update_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> None:
        """
        Actualiza o crea una posición.
        
        Args:
            symbol: Símbolo del activo
            side: 'long' o 'short'
            entry_price: Precio de entrada
            quantity: Cantidad
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
        """
        self.positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'quantity': quantity,
            'entry_time': datetime.now(),
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
        self.logger.info(f"Posición actualizada: {symbol} {side} @ {entry_price}")
    
    def close_position(self, symbol: str) -> Optional[Dict]:
        """
        Cierra una posición.
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Información de la posición cerrada o None
        """
        if symbol in self.positions:
            position = self.positions.pop(symbol)
            position['exit_time'] = datetime.now()
            self.logger.info(f"Posición cerrada: {symbol}")
            return position
        return None
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Obtiene información de una posición.
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Información de la posición o None
        """
        return self.positions.get(symbol)

