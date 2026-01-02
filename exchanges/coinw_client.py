"""
Cliente para la API de CoinW Exchange.
Maneja autenticación, órdenes, balance y posiciones.
"""

import hmac
import hashlib
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import logger
from utils.config_loader import config


class CoinWClient:
    """Cliente para interactuar con la API de CoinW."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Inicializa el cliente de CoinW.
        
        Args:
            api_key: API Key de CoinW (o se obtiene de config)
            api_secret: API Secret de CoinW (o se obtiene de config)
        """
        self.logger = logger.bind(name="CoinWClient")
        
        # Obtener credenciales de config o parámetros
        self.api_key = api_key or config.get_env('COINW_API_KEY')
        self.api_secret = api_secret or config.get_env('COINW_API_SECRET')
        
        # URL base de la API de CoinW (ajustar según documentación real)
        # Nota: Estas URLs son ejemplos, deben ajustarse según la documentación oficial
        self.base_url = config.get('exchanges', {}).get('coinw_base_url', 'https://api.coinw.com')
        self.futures_base_url = config.get('exchanges', {}).get('coinw_futures_url', 'https://api.coinw.com/futures')
        
        if not self.api_key or not self.api_secret:
            self.logger.warning("CoinW API credentials not configured. Trading features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.logger.info("CoinW client initialized")
    
    def _generate_signature(self, params: Dict, timestamp: int) -> str:
        """
        Genera la firma HMAC para autenticación.
        
        Args:
            params: Parámetros de la solicitud
            timestamp: Timestamp en milisegundos
            
        Returns:
            Firma HMAC-SHA256
        """
        # Crear string de parámetros ordenados
        param_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        message = f"{param_string}&timestamp={timestamp}"
        
        # Generar firma HMAC-SHA256
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = True,
        is_futures: bool = True
    ) -> Dict:
        """
        Realiza una solicitud a la API de CoinW.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            params: Parámetros de la solicitud
            signed: Si requiere autenticación
            is_futures: Si es True, usa la URL de futuros; si es False, usa la URL de spot
            
        Returns:
            Respuesta de la API como diccionario
        """
        if not self.enabled:
            raise Exception("CoinW API credentials not configured")
        
        if params is None:
            params = {}
        
        # Usar la URL base correcta según el tipo de cuenta
        base_url = self.futures_base_url if is_futures else self.base_url
        url = f"{base_url}{endpoint}"
        
        headers = {
            'X-COINW-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        if signed:
            timestamp = int(time.time() * 1000)
            params['timestamp'] = timestamp
            signature = self._generate_signature(params, timestamp)
            params['signature'] = signature
        
        # Timeout aumentado a 30 segundos y reintentos
        max_retries = 3
        timeout = 30
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, headers=headers, timeout=timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, json=params, headers=headers, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Esperar 2, 4, 6 segundos
                    self.logger.warning(f"Timeout en intento {attempt + 1}/{max_retries}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Error: Timeout después de {max_retries} intentos. La API de CoinW no responde.")
                    raise Exception(f"CoinW API timeout: La conexión tardó más de {timeout} segundos. Por favor, verifica tu conexión a internet o intenta más tarde.")
            
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    self.logger.warning(f"Error de conexión en intento {attempt + 1}/{max_retries}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"Error de conexión después de {max_retries} intentos.")
                    raise Exception(f"CoinW API connection error: No se pudo conectar con la API de CoinW. Verifica tu conexión a internet.")
            
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error making request to CoinW API: {str(e)}")
                raise Exception(f"CoinW API error: {str(e)}")
        
        # Este punto no debería alcanzarse, pero por seguridad:
        raise Exception("Error desconocido al realizar la solicitud a CoinW API")
    
    def get_account_balance(self, account_type: str = 'futures') -> Dict:
        """
        Obtiene el balance de la cuenta.
        
        Args:
            account_type: 'spot' o 'futures' (default: 'futures')
        
        Returns:
            Diccionario con información del balance
        """
        try:
            # Usar endpoint diferente según el tipo de cuenta
            is_futures = account_type != 'spot'
            response = self._make_request('GET', '/account/balance', signed=True, is_futures=is_futures)
            
            # Ajustar según estructura real de respuesta de CoinW
            return {
                'available_balance': response.get('available', 0.0),
                'total_balance': response.get('total', 0.0),
                'frozen_balance': response.get('frozen', 0.0),
                'currency': response.get('currency', 'USDT'),
                'account_type': account_type,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting {account_type} account balance: {str(e)}")
            return {
                'available_balance': 0.0,
                'total_balance': 0.0,
                'frozen_balance': 0.0,
                'currency': 'USDT',
                'account_type': account_type,
                'error': str(e)
            }
    
    def get_spot_balance(self) -> Dict:
        """
        Obtiene el balance de la cuenta spot.
        
        Returns:
            Diccionario con información del balance spot
        """
        return self.get_account_balance(account_type='spot')
    
    def get_futures_balance(self) -> Dict:
        """
        Obtiene el balance de la cuenta de futuros.
        
        Returns:
            Diccionario con información del balance de futuros
        """
        return self.get_account_balance(account_type='futures')
    
    def check_symbol_available(self, symbol: str) -> Dict:
        """
        Verifica si un símbolo está disponible para trading en CoinW.
        
        Args:
            symbol: Símbolo del activo (ej: ETHUSDT)
            
        Returns:
            Diccionario con información sobre la disponibilidad del símbolo
        """
        try:
            # Intentar obtener información del símbolo
            # Ajustar endpoint según documentación real de CoinW
            response = self._make_request('GET', f'/symbol/info', {'symbol': symbol}, signed=False, is_futures=True)
            
            # Si la respuesta es exitosa, el símbolo está disponible
            if response and not response.get('error'):
                return {
                    'available': True,
                    'symbol': symbol,
                    'message': f'{symbol} is available for trading'
                }
            else:
                return {
                    'available': False,
                    'symbol': symbol,
                    'message': f'{symbol} is not available on CoinW',
                    'error': response.get('error', 'Symbol not found')
                }
        except Exception as e:
            # Si hay error, asumimos que el símbolo podría no estar disponible
            # Pero no bloqueamos completamente - dejamos que el place_order lo valide
            self.logger.warning(f"Could not verify symbol availability for {symbol}: {str(e)}")
            return {
                'available': None,  # None significa que no se pudo verificar
                'symbol': symbol,
                'message': f'Could not verify if {symbol} is available',
                'error': str(e)
            }
    
    def get_open_positions(self) -> List[Dict]:
        """
        Obtiene las posiciones abiertas.
        
        Returns:
            Lista de posiciones abiertas
        """
        try:
            response = self._make_request('GET', '/position/list', signed=True, is_futures=True)
            
            # Ajustar según estructura real de respuesta de CoinW
            positions = response.get('data', []) if isinstance(response, dict) else response
            
            formatted_positions = []
            for pos in positions:
                formatted_positions.append({
                    'symbol': pos.get('symbol', ''),
                    'side': 'long' if pos.get('side', 1) == 1 else 'short',
                    'size': float(pos.get('size', 0)),
                    'entry_price': float(pos.get('entryPrice', 0)),
                    'mark_price': float(pos.get('markPrice', 0)),
                    'leverage': int(pos.get('leverage', 1)),
                    'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                    'margin': float(pos.get('margin', 0)),
                    'liquidation_price': float(pos.get('liquidationPrice', 0))
                })
            
            return formatted_positions
            
        except Exception as e:
            self.logger.error(f"Error getting open positions: {str(e)}")
            return []
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        leverage: int = 1,
        margin_mode: str = 'cross',
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict:
        """
        Coloca una orden en CoinW.
        
        Args:
            symbol: Símbolo del activo (ej: ETHUSDT)
            side: 'buy' o 'sell' (long o short)
            order_type: 'market' o 'limit'
            quantity: Cantidad a operar
            price: Precio (requerido para órdenes limit)
            leverage: Apalancamiento (1-100)
            margin_mode: 'cross' o 'isolated'
            stop_loss: Precio de stop loss (opcional)
            take_profit: Precio de take profit (opcional)
            
        Returns:
            Información de la orden creada
        """
        try:
            # Convertir side a formato de CoinW (1 = long/buy, 2 = short/sell)
            position_side = 1 if side.lower() in ['buy', 'long'] else 2
            
            params = {
                'symbol': symbol,
                'side': position_side,
                'type': order_type.upper(),
                'quantity': quantity,
                'leverage': leverage,
                'marginMode': margin_mode
            }
            
            if order_type.lower() == 'limit' and price:
                params['price'] = price
            
            # Colocar orden principal
            response = self._make_request('POST', '/order/place', params, signed=True, is_futures=True)
            
            order_id = response.get('orderId') or response.get('id')
            
            result = {
                'success': True,
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price if order_type.lower() == 'limit' else 'market',
                'leverage': leverage,
                'margin_mode': margin_mode,
                'timestamp': datetime.now().isoformat()
            }
            
            # Si se especificaron stop loss o take profit, colocarlos como órdenes condicionales
            if stop_loss:
                try:
                    sl_params = {
                        'symbol': symbol,
                        'side': 2 if position_side == 1 else 1,  # Lado opuesto
                        'type': 'STOP_MARKET',
                        'stopPrice': stop_loss,
                        'quantity': quantity
                    }
                    sl_response = self._make_request('POST', '/order/stop', sl_params, signed=True, is_futures=True)
                    result['stop_loss_order_id'] = sl_response.get('orderId')
                except Exception as e:
                    self.logger.warning(f"Could not place stop loss order: {str(e)}")
                    result['stop_loss_error'] = str(e)
            
            if take_profit:
                try:
                    tp_params = {
                        'symbol': symbol,
                        'side': 2 if position_side == 1 else 1,  # Lado opuesto
                        'type': 'TAKE_PROFIT_MARKET',
                        'stopPrice': take_profit,
                        'quantity': quantity
                    }
                    tp_response = self._make_request('POST', '/order/stop', tp_params, signed=True, is_futures=True)
                    result['take_profit_order_id'] = tp_response.get('orderId')
                except Exception as e:
                    self.logger.warning(f"Could not place take profit order: {str(e)}")
                    result['take_profit_error'] = str(e)
            
            self.logger.info(f"Order placed successfully: {order_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error placing order: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'side': side,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        Obtiene el estado de una orden.
        
        Args:
            order_id: ID de la orden
            
        Returns:
            Estado de la orden
        """
        try:
            response = self._make_request('GET', f'/order/status', {'orderId': order_id}, signed=True, is_futures=True)
            return response
        except Exception as e:
            self.logger.error(f"Error getting order status: {str(e)}")
            return {'error': str(e)}
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancela una orden.
        
        Args:
            order_id: ID de la orden a cancelar
            
        Returns:
            Resultado de la cancelación
        """
        try:
            response = self._make_request('POST', '/order/cancel', {'orderId': order_id}, signed=True, is_futures=True)
            return {'success': True, 'order_id': order_id, 'response': response}
        except Exception as e:
            self.logger.error(f"Error canceling order: {str(e)}")
            return {'success': False, 'error': str(e)}

