"""Gestor de riesgo para el sistema de trading."""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from utils.logger import logger
from utils.config_loader import config


class RiskManager:
    """Gestiona el riesgo del sistema de trading."""
    
    def __init__(self, initial_capital: float):
        """
        Inicializa el gestor de riesgo.
        
        Args:
            initial_capital: Capital inicial
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = config.get('risk_management.max_position_size', 0.02)
        self.max_daily_loss = config.get('risk_management.max_daily_loss', 0.05)
        self.max_open_positions = config.get('risk_management.max_open_positions', 5)
        self.stop_loss_percentage = config.get('risk_management.stop_loss_percentage', 0.02)
        self.take_profit_percentage = config.get('risk_management.take_profit_percentage', 0.04)
        
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        self.open_positions = {}
        
        self.logger = logger.bind(name="RiskManager")
        self.logger.info(f"RiskManager inicializado con capital: ${initial_capital:,.2f}")
    
    def reset_daily_metrics(self) -> None:
        """Resetea las métricas diarias."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = today
            self.logger.info("Métricas diarias reseteadas")
    
    def can_open_position(self, symbol: str, price: float, quantity: float) -> Tuple[bool, str]:
        """
        Verifica si se puede abrir una nueva posición.
        
        Args:
            symbol: Símbolo del activo
            price: Precio del activo
            quantity: Cantidad deseada
            
        Returns:
            Tupla (puede_abrir, razón)
        """
        self.reset_daily_metrics()
        
        # Verificar si ya hay una posición abierta para este símbolo
        if symbol in self.open_positions:
            return False, f"Ya existe una posición abierta para {symbol}"
        
        # Verificar número máximo de posiciones
        if len(self.open_positions) >= self.max_open_positions:
            return False, f"Máximo de posiciones abiertas alcanzado ({self.max_open_positions})"
        
        # Calcular valor de la posición
        position_value = price * quantity
        
        # Verificar tamaño máximo de posición
        max_position_value = self.current_capital * self.max_position_size
        if position_value > max_position_value:
            return False, f"Tamaño de posición excede el máximo permitido (${max_position_value:,.2f})"
        
        # Verificar pérdida diaria máxima
        max_daily_loss_amount = self.initial_capital * self.max_daily_loss
        if abs(self.daily_pnl) >= max_daily_loss_amount:
            return False, f"Pérdida diaria máxima alcanzada (${max_daily_loss_amount:,.2f})"
        
        return True, "OK"
    
    def calculate_position_size(
        self,
        price: float,
        stop_loss_price: float,
        risk_amount: Optional[float] = None
    ) -> float:
        """
        Calcula el tamaño de posición basado en el riesgo.
        
        Args:
            price: Precio de entrada
            stop_loss_price: Precio de stop loss
            risk_amount: Cantidad de capital a arriesgar (opcional)
            
        Returns:
            Cantidad de acciones/contratos
        """
        if risk_amount is None:
            risk_amount = self.current_capital * self.max_position_size
        
        # Calcular riesgo por unidad
        risk_per_unit = abs(price - stop_loss_price)
        
        if risk_per_unit == 0:
            self.logger.warning("Stop loss igual al precio de entrada, usando porcentaje por defecto")
            risk_per_unit = price * self.stop_loss_percentage
        
        # Calcular cantidad
        quantity = risk_amount / risk_per_unit
        
        # Asegurar que no exceda el máximo permitido
        max_quantity = (self.current_capital * self.max_position_size) / price
        quantity = min(quantity, max_quantity)
        
        return quantity
    
    def calculate_stop_loss(self, entry_price: float, side: str = 'long') -> float:
        """
        Calcula el precio de stop loss.
        
        Args:
            entry_price: Precio de entrada
            side: 'long' o 'short'
            
        Returns:
            Precio de stop loss
        """
        if side == 'long':
            return entry_price * (1 - self.stop_loss_percentage)
        else:
            return entry_price * (1 + self.stop_loss_percentage)
    
    def calculate_take_profit(self, entry_price: float, side: str = 'long') -> float:
        """
        Calcula el precio de take profit.
        
        Args:
            entry_price: Precio de entrada
            side: 'long' o 'short'
            
        Returns:
            Precio de take profit
        """
        if side == 'long':
            return entry_price * (1 + self.take_profit_percentage)
        else:
            return entry_price * (1 - self.take_profit_percentage)
    
    def register_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        stop_loss: float,
        take_profit: float
    ) -> None:
        """
        Registra una nueva posición.
        
        Args:
            symbol: Símbolo del activo
            side: 'long' o 'short'
            entry_price: Precio de entrada
            quantity: Cantidad
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
        """
        position_value = entry_price * quantity
        self.current_capital -= position_value  # Asumimos que se reserva el capital
        
        self.open_positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now()
        }
        
        self.logger.info(
            f"Posición registrada: {symbol} {side} {quantity} @ {entry_price}, "
            f"SL: {stop_loss}, TP: {take_profit}"
        )
    
    def close_position(
        self,
        symbol: str,
        exit_price: float
    ) -> Dict:
        """
        Cierra una posición y actualiza el capital.
        
        Args:
            symbol: Símbolo del activo
            exit_price: Precio de salida
            
        Returns:
            Información de la posición cerrada
        """
        if symbol not in self.open_positions:
            self.logger.warning(f"No se encontró posición para {symbol}")
            return {}
        
        position = self.open_positions.pop(symbol)
        entry_price = position['entry_price']
        quantity = position['quantity']
        side = position['side']
        
        # Calcular P&L
        if side == 'long':
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        # Actualizar capital
        position_value = entry_price * quantity
        self.current_capital += position_value + pnl
        
        # Actualizar P&L diario
        self.daily_pnl += pnl
        
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now()
        position['pnl'] = pnl
        position['pnl_percentage'] = (pnl / position_value) * 100
        
        self.logger.info(
            f"Posición cerrada: {symbol} {side} @ {exit_price}, "
            f"P&L: ${pnl:,.2f} ({position['pnl_percentage']:.2f}%)"
        )
        
        return position
    
    def update_capital(self, new_capital: float) -> Tuple[bool, str]:
        """
        Actualiza el capital actual.
        
        Args:
            new_capital: Nuevo capital
            
        Returns:
            Tupla (éxito, mensaje)
        """
        if new_capital <= 0:
            return False, "El capital debe ser mayor a cero"
        
        if new_capital < 100:
            return False, "El capital mínimo es $100"
        
        # Calcular diferencia
        difference = new_capital - self.current_capital
        
        # Actualizar capital
        self.current_capital = new_capital
        
        # Si el nuevo capital es mayor, actualizar también el inicial
        if new_capital > self.initial_capital:
            self.initial_capital = new_capital
        
        self.logger.info(f"Capital actualizado: ${self.current_capital:,.2f} (diferencia: ${difference:+,.2f})")
        
        return True, f"Capital actualizado exitosamente a ${new_capital:,.2f}"
    
    def get_current_risk_metrics(self) -> Dict:
        """
        Obtiene métricas de riesgo actuales.
        
        Returns:
            Diccionario con métricas de riesgo
        """
        total_position_value = sum(
            pos['entry_price'] * pos['quantity']
            for pos in self.open_positions.values()
        )
        
        return {
            'current_capital': self.current_capital,
            'initial_capital': self.initial_capital,
            'total_return': self.current_capital - self.initial_capital,
            'total_return_percentage': ((self.current_capital - self.initial_capital) / self.initial_capital) * 100 if self.initial_capital > 0 else 0,
            'daily_pnl': self.daily_pnl,
            'open_positions': len(self.open_positions),
            'total_position_value': total_position_value,
            'position_value_percentage': (total_position_value / self.current_capital) * 100 if self.current_capital > 0 else 0
        }

