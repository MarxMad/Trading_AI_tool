"""Recolector de datos usando yfinance (Yahoo Finance)."""

from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import yfinance as yf
from data.collectors.base_collector import BaseDataCollector
from utils.logger import logger


class YFinanceCollector(BaseDataCollector):
    """Recolector de datos de Yahoo Finance usando yfinance."""
    
    # Mapeo de intervalos
    INTERVAL_MAP = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '60m',
        '1d': '1d',
        '1w': '1wk',
        '1mo': '1mo'
    }
    
    def __init__(self):
        """Inicializa el recolector de Yahoo Finance."""
        super().__init__("YFinance")
        self.logger.info("YFinance collector inicializado")
    
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos de Yahoo Finance.
        
        Args:
            symbol: Símbolo del activo (ej: 'AAPL')
            start_date: Fecha de inicio
            end_date: Fecha de fin
            interval: Intervalo de tiempo
            
        Returns:
            DataFrame con datos OHLCV
        """
        try:
            # Mapear intervalo
            yf_interval = self.INTERVAL_MAP.get(interval, '1d')
            
            # Obtener ticker
            ticker = yf.Ticker(symbol)
            
            # Descargar datos
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=yf_interval
            )
            
            if df.empty:
                self.logger.warning(f"No se obtuvieron datos para {symbol}")
                return pd.DataFrame()
            
            # Renombrar columnas a minúsculas
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Seleccionar columnas necesarias
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in required_cols if col in df.columns]]
            
            # Validar datos
            if not self.validate_data(df):
                return pd.DataFrame()
            
            self.logger.info(f"Datos obtenidos para {symbol}: {len(df)} registros")
            return df
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos para {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_realtime_data(self, symbol: str) -> Dict:
        """
        Obtiene datos en tiempo real.
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Diccionario con datos actuales
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Obtener datos más recientes
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return {}
            
            latest = hist.iloc[-1]
            
            return {
                'symbol': symbol,
                'price': float(info.get('currentPrice', latest['close'])),
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'close': float(latest['close']),
                'volume': int(latest['volume']),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos en tiempo real para {symbol}: {str(e)}")
            return {}
    
    def get_available_symbols(self) -> List[str]:
        """
        Retorna símbolos populares disponibles.
        Nota: yfinance no tiene un método directo para listar todos los símbolos.
        
        Returns:
            Lista de símbolos populares
        """
        # Símbolos populares de ejemplo
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'META', 'NVDA', 'JPM', 'V', 'JNJ',
            'WMT', 'PG', 'MA', 'UNH', 'HD',
            'DIS', 'PYPL', 'BAC', 'NFLX', 'ADBE'
        ]

