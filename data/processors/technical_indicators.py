"""
Calculadora de indicadores técnicos para análisis de mercado.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from utils.logger import logger

try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    logger.warning("pandas_ta no está instalado. Algunos indicadores no estarán disponibles.")


class TechnicalIndicators:
    """Calcula indicadores técnicos para análisis de mercado."""
    
    def __init__(self):
        """Inicializa el calculador de indicadores."""
        self.logger = logger.bind(name="TechnicalIndicators")
    
    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos los indicadores técnicos disponibles.
        
        Args:
            data: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con indicadores añadidos
        """
        df = data.copy()
        
        # Indicadores básicos
        df = self.calculate_moving_averages(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_volume_indicators(df)
        
        return df
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula medias móviles simples y exponenciales."""
        df = data.copy()
        
        # SMA
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # EMA
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        return df
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calcula el RSI (Relative Strength Index)."""
        df = data.copy()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula el MACD (Moving Average Convergence Divergence)."""
        df = data.copy()
        
        if 'ema_12' not in df.columns or 'ema_26' not in df.columns:
            df = self.calculate_moving_averages(df)
        
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Calcula las Bandas de Bollinger."""
        df = data.copy()
        
        if 'sma_20' not in df.columns:
            df['sma_20'] = df['close'].rolling(window=period).mean()
        
        df['bb_middle'] = df['sma_20']
        df['bb_std'] = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
        
        return df
    
    def calculate_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de volumen."""
        df = data.copy()
        
        # Media móvil de volumen
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        
        # Volume Rate of Change
        df['volume_roc'] = df['volume'].pct_change(periods=10) * 100
        
        return df
    
    def get_trend_analysis(self, data: pd.DataFrame) -> Dict:
        """
        Analiza la tendencia del mercado.
        
        Args:
            data: DataFrame con datos e indicadores
            
        Returns:
            Diccionario con análisis de tendencia
        """
        if data.empty or len(data) < 50:
            return {
                'trend': 'indeterminado',
                'strength': 0,
                'signal': 'hold'
            }
        
        latest = data.iloc[-1]
        
        # Análisis de medias móviles
        if 'sma_20' in data.columns and 'sma_50' in data.columns:
            sma_20_current = latest['sma_20']
            sma_50_current = latest['sma_50']
            price_current = latest['close']
            
            # Tendencias
            if price_current > sma_20_current > sma_50_current:
                trend = 'alcista'
                strength = 0.8
                signal = 'buy'
            elif price_current < sma_20_current < sma_50_current:
                trend = 'bajista'
                strength = 0.8
                signal = 'sell'
            else:
                trend = 'lateral'
                strength = 0.5
                signal = 'hold'
        else:
            trend = 'indeterminado'
            strength = 0
            signal = 'hold'
        
        # Análisis RSI
        rsi_signal = 'neutral'
        if 'rsi' in data.columns:
            rsi = latest['rsi']
            if rsi > 70:
                rsi_signal = 'sobrecompra'
                if signal == 'buy':
                    signal = 'hold'  # Sobrecarga, no comprar
            elif rsi < 30:
                rsi_signal = 'sobreventa'
                if signal == 'sell':
                    signal = 'hold'  # Sobreventa, no vender
        
        return {
            'trend': trend,
            'strength': strength,
            'signal': signal,
            'rsi_signal': rsi_signal,
            'current_price': float(latest['close']),
            'sma_20': float(latest.get('sma_20', 0)),
            'sma_50': float(latest.get('sma_50', 0)),
            'rsi': float(latest.get('rsi', 50))
        }
    
    def get_support_resistance_levels(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """
        Identifica niveles de soporte y resistencia.
        
        Args:
            data: DataFrame con datos OHLCV
            window: Ventana para identificar niveles
            
        Returns:
            Diccionario con niveles de soporte y resistencia
        """
        if data.empty or len(data) < window:
            return {
                'support': [],
                'resistance': []
            }
        
        recent_data = data.tail(window)
        
        # Identificar máximos y mínimos locales
        highs = recent_data['high'].rolling(window=5, center=True).max()
        lows = recent_data['low'].rolling(window=5, center=True).min()
        
        # Niveles de resistencia (máximos)
        resistance_levels = []
        for i in range(2, len(highs) - 2):
            if highs.iloc[i] == highs.iloc[i-2:i+3].max():
                resistance_levels.append(float(highs.iloc[i]))
        
        # Niveles de soporte (mínimos)
        support_levels = []
        for i in range(2, len(lows) - 2):
            if lows.iloc[i] == lows.iloc[i-2:i+3].min():
                support_levels.append(float(lows.iloc[i]))
        
        # Eliminar duplicados y ordenar
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:3]
        support_levels = sorted(list(set(support_levels)))[:3]
        
        return {
            'support': support_levels,
            'resistance': resistance_levels
        }

