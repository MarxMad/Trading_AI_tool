"""
Sistema de registro de trading (Trading Journal).
Mantiene un registro completo de todas las operaciones.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
from utils.logger import logger
from utils.config_loader import config


class TradingJournal:
    """Mantiene un registro de todas las operaciones de trading."""
    
    def __init__(self, journal_file: str = "data/trading_journal.json"):
        """
        Inicializa el diario de trading.
        
        Args:
            journal_file: Ruta al archivo JSON del diario
        """
        self.journal_file = Path(journal_file)
        self.journal_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger.bind(name="TradingJournal")
        self.trades = self._load_journal()
    
    def _load_journal(self) -> List[Dict]:
        """Carga el diario desde el archivo."""
        if self.journal_file.exists():
            try:
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('trades', [])
            except Exception as e:
                self.logger.error(f"Error cargando diario: {str(e)}")
                return []
        return []
    
    def _save_journal(self) -> None:
        """Guarda el diario en el archivo."""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_trades': len(self.trades),
                'trades': self.trades
            }
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando diario: {str(e)}")
    
    def add_trade(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        strategy: Optional[str] = None,
        notes: Optional[str] = None,
        image_analysis: Optional[Dict] = None
    ) -> str:
        """
        Añade una nueva operación al diario.
        
        Args:
            symbol: Símbolo del activo
            side: 'long' o 'short'
            entry_price: Precio de entrada
            quantity: Cantidad
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
            strategy: Estrategia usada
            notes: Notas adicionales
            image_analysis: Análisis de imagen si fue usado
            
        Returns:
            ID de la operación
        """
        trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.trades)}"
        
        trade = {
            'id': trade_id,
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'strategy': strategy,
            'notes': notes,
            'image_analysis': image_analysis,
            'entry_time': datetime.now().isoformat(),
            'exit_time': None,
            'exit_price': None,
            'pnl': None,
            'pnl_percentage': None,
            'status': 'open'  # open, closed, cancelled
        }
        
        self.trades.append(trade)
        self._save_journal()
        self.logger.info(f"Operación añadida al diario: {trade_id}")
        
        return trade_id
    
    def update_trade(
        self,
        trade_id: str,
        exit_price: Optional[float] = None,
        pnl: Optional[float] = None,
        pnl_percentage: Optional[float] = None,
        status: str = 'closed',
        notes: Optional[str] = None
    ) -> bool:
        """
        Actualiza una operación existente.
        
        Args:
            trade_id: ID de la operación
            exit_price: Precio de salida
            pnl: Profit & Loss
            pnl_percentage: P&L en porcentaje
            status: Estado de la operación
            notes: Notas adicionales
            
        Returns:
            True si se actualizó correctamente
        """
        for trade in self.trades:
            if trade['id'] == trade_id:
                if exit_price is not None:
                    trade['exit_price'] = exit_price
                if pnl is not None:
                    trade['pnl'] = pnl
                if pnl_percentage is not None:
                    trade['pnl_percentage'] = pnl_percentage
                trade['status'] = status
                trade['exit_time'] = datetime.now().isoformat()
                if notes:
                    trade['notes'] = (trade.get('notes', '') or '') + f"\n{notes}"
                
                self._save_journal()
                self.logger.info(f"Operación actualizada: {trade_id}")
                return True
        
        self.logger.warning(f"Operación no encontrada: {trade_id}")
        return False
    
    def get_trades(
        self,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Obtiene operaciones filtradas.
        
        Args:
            symbol: Filtrar por símbolo
            status: Filtrar por estado ('open', 'closed', 'cancelled')
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de operaciones
        """
        filtered = self.trades
        
        if symbol:
            filtered = [t for t in filtered if t['symbol'] == symbol]
        
        if status:
            filtered = [t for t in filtered if t['status'] == status]
        
        if start_date:
            filtered = [
                t for t in filtered
                if datetime.fromisoformat(t['entry_time']) >= start_date
            ]
        
        if end_date:
            filtered = [
                t for t in filtered
                if datetime.fromisoformat(t['entry_time']) <= end_date
            ]
        
        return sorted(filtered, key=lambda x: x['entry_time'], reverse=True)
    
    def get_statistics(self) -> Dict:
        """
        Calcula estadísticas del diario.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'open_trades': 0,
                'closed_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'average_pnl': 0.0,
                'best_trade': None,
                'worst_trade': None
            }
        
        closed_trades = [t for t in self.trades if t['status'] == 'closed' and t['pnl'] is not None]
        open_trades = [t for t in self.trades if t['status'] == 'open']
        
        if closed_trades:
            winning_trades = [t for t in closed_trades if t['pnl'] > 0]
            losing_trades = [t for t in closed_trades if t['pnl'] <= 0]
            
            total_pnl = sum(t['pnl'] for t in closed_trades)
            win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0.0
            
            best_trade = max(closed_trades, key=lambda x: x['pnl'] or 0)
            worst_trade = min(closed_trades, key=lambda x: x['pnl'] or 0)
        else:
            total_pnl = 0.0
            win_rate = 0.0
            best_trade = None
            worst_trade = None
        
        return {
            'total_trades': len(self.trades),
            'open_trades': len(open_trades),
            'closed_trades': len(closed_trades),
            'win_rate': win_rate * 100,
            'total_pnl': total_pnl,
            'average_pnl': total_pnl / len(closed_trades) if closed_trades else 0.0,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'winning_trades': len([t for t in closed_trades if t['pnl'] and t['pnl'] > 0]) if closed_trades else 0,
            'losing_trades': len([t for t in closed_trades if t['pnl'] and t['pnl'] <= 0]) if closed_trades else 0
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Exporta el diario a un DataFrame de pandas.
        
        Returns:
            DataFrame con todas las operaciones
        """
        if not self.trades:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.trades)
        if 'entry_time' in df.columns:
            df['entry_time'] = pd.to_datetime(df['entry_time'])
        if 'exit_time' in df.columns:
            df['exit_time'] = pd.to_datetime(df['exit_time'])
        
        return df

