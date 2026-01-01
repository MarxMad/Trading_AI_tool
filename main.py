"""
Script principal del sistema de trading.
Ejemplo básico de uso del sistema.
"""

from datetime import datetime, timedelta
from utils.config_loader import config
from utils.logger import logger
from data.collectors.yfinance_collector import YFinanceCollector
from risk.risk_manager import RiskManager


def main():
    """Función principal."""
    logger.info("Iniciando sistema de trading...")
    
    # Configuración
    initial_capital = config.get('backtesting.initial_capital', 10000)
    symbols = config.get('data.sources[0].symbols', ['AAPL'])
    
    # Inicializar componentes
    data_collector = YFinanceCollector()
    risk_manager = RiskManager(initial_capital)
    
    # Obtener datos históricos de ejemplo
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    logger.info(f"Obteniendo datos para {symbols[0]}...")
    data = data_collector.fetch_historical_data(
        symbol=symbols[0],
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )
    
    if not data.empty:
        logger.info(f"Datos obtenidos: {len(data)} registros")
        logger.info(f"\nÚltimos 5 registros:\n{data.tail()}")
        
        # Mostrar métricas de riesgo
        metrics = risk_manager.get_current_risk_metrics()
        logger.info(f"\nMétricas de riesgo:\n{metrics}")
    else:
        logger.error("No se pudieron obtener datos")
    
    logger.info("Sistema de trading finalizado")


if __name__ == "__main__":
    main()

