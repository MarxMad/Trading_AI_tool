"""
Analizador de imágenes con IA para detectar estrategias de trading.
Analiza capturas de pantalla de gráficos y sugiere niveles de entrada, stop loss y take profit.
Usa Google Gemini para análisis avanzado de imágenes.
"""

import base64
import io
import json
import re
from typing import Dict, Optional, List
from PIL import Image
import numpy as np
from utils.logger import logger
from utils.config_loader import config

# Importación de Gemini (requerida para análisis de imágenes)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai no está instalado. Instala con: pip install google-generativeai")


class ImageAnalyzer:
    """Analiza imágenes de gráficos de trading usando IA (Google Gemini)."""
    
    def __init__(self):
        """Inicializa el analizador de imágenes."""
        self.logger = logger.bind(name="ImageAnalyzer")
        self.gemini_api_key = config.get_env('GEMINI_API_KEY')
        self.use_gemini = GEMINI_AVAILABLE and self.gemini_api_key is not None
        
        if self.use_gemini:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Usar el modelo gemini-2.5-flash-lite como solicitado
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
                    self.logger.info(f"Gemini configurado con modelo gemini-2.5-flash-lite")
                except Exception as model_error:
                    # Fallback a otros modelos si el solicitado no está disponible
                    try:
                        self.model = genai.GenerativeModel('gemini-1.5-pro')
                        self.logger.warning(f"Modelo gemini-2.5-flash-lite no disponible, usando gemini-1.5-pro (fallback)")
                    except Exception as e1:
                        try:
                            self.model = genai.GenerativeModel('gemini-1.5-flash')
                            self.logger.warning(f"Usando gemini-1.5-flash (fallback)")
                        except Exception as e2:
                            self.model = genai.GenerativeModel('gemini-pro')
                            self.logger.warning(f"Usando gemini-pro (último fallback)")
                self.logger.info(f"Gemini API Key configurada: {self.gemini_api_key[:10]}...")
            except Exception as e:
                self.logger.error(f"Error configurando Gemini: {str(e)}")
                self.use_gemini = False
        else:
            if not GEMINI_AVAILABLE:
                self.logger.warning(
                    "google-generativeai no está instalado. "
                    "Instala con: pip install google-generativeai"
                )
            elif not self.gemini_api_key:
                self.logger.warning(
                    "GEMINI_API_KEY no configurada. "
                    "Usando análisis básico de patrones. "
                    "Para mejor precisión, configura tu API key de Gemini en .env"
                )
            else:
                self.logger.warning(
                    f"Gemini no disponible. API Key presente: {bool(self.gemini_api_key)}"
                )
    
    def analyze_chart_image(
        self,
        image: Image.Image,
        symbol: Optional[str] = None,
        position_type: Optional[str] = None,
        margin_mode: str = "cross_margin",
        leverage: Optional[int] = None,
        trading_style: str = "swing_trading"
    ) -> Dict:
        """
        Analiza una imagen de gráfico de trading y sugiere niveles.
        
        Args:
            image: Imagen PIL del gráfico
            symbol: Símbolo del activo (opcional)
            position_type: Tipo de posición (opcional)
            margin_mode: Modo de margen (cross_margin o isolated_margin)
            leverage: Leverage sugerido (opcional)
            trading_style: Estilo de trading (scalpers, swing_trading, long_term)
            
        Returns:
            Diccionario con:
                - entry_price: Precio de entrada sugerido
                - stop_loss: Precio de stop loss
                - take_profit: Precio de take profit
                - confidence: Nivel de confianza (0-1)
                - pattern_detected: Patrón detectado
                - analysis: Análisis detallado
        """
        if self.use_gemini:
            self.logger.info(f"Usando Gemini para análisis de {symbol or 'gráfico'} con estilo {trading_style}")
            return self._analyze_with_gemini(image, symbol, position_type, margin_mode, leverage, trading_style)
        else:
            self.logger.warning("Gemini no disponible. Por favor, configura GEMINI_API_KEY para usar el análisis de imágenes.")
            return self._create_fallback_response(
                "Gemini API no está configurada. Por favor, configura GEMINI_API_KEY en tus variables de entorno o secrets de Streamlit Cloud.",
                symbol
            )
    
    def _analyze_with_gemini(
        self,
        image: Image.Image,
        symbol: Optional[str],
        position_type: Optional[str] = None,
        margin_mode: str = "cross_margin",
        leverage: Optional[int] = None,
        trading_style: str = "swing_trading"
    ) -> Dict:
        """Analiza usando Google Gemini Vision."""
        try:
            # Preparar contexto de configuración
            margin_context = f" Margin Mode: {margin_mode.replace('_', ' ').title()}"
            trading_style_display = trading_style.replace('_', ' ').title()
            
            # Definir optimizaciones según el estilo de trading
            style_guidelines = {
                "scalpers": {
                    "timeframe": "minutes to hours",
                    "leverage_range": "10-50x (higher leverage for quick profits)",
                    "stop_loss": "Very tight (0.2-0.5% from entry)",
                    "take_profit": "Quick targets (0.5-1% from entry), multiple small targets",
                    "entry": "Precise entry on quick breakouts, pullbacks, or support/resistance bounces",
                    "focus": "Short-term price action, order flow, quick reversals, scalping patterns"
                },
                "swing_trading": {
                    "timeframe": "days to weeks",
                    "leverage_range": "5-20x (moderate leverage)",
                    "stop_loss": "Moderate (1-2% from entry)",
                    "take_profit": "Medium targets (2-5% from entry), 2:1 to 3:1 risk:reward",
                    "entry": "Entry on trend confirmations, pattern breakouts, or swing points",
                    "focus": "Trend following, chart patterns, support/resistance levels, technical indicators"
                },
                "long_term": {
                    "timeframe": "weeks to months",
                    "leverage_range": "1-10x (conservative leverage)",
                    "stop_loss": "Wider stops (2-5% from entry)",
                    "take_profit": "Large targets (5-15%+ from entry), 3:1 to 5:1 risk:reward",
                    "entry": "Entry on major trend changes, significant support/resistance, accumulation zones",
                    "focus": "Major trends, fundamental analysis support, long-term patterns, macro trends"
                }
            }
            
            style_guide = style_guidelines.get(trading_style, style_guidelines["swing_trading"])
            
            prompt = f"""You are an expert AI trading analyst. Analyze this trading chart image and AUTOMATICALLY DETECT AND PROVIDE all trading parameters optimized for {trading_style_display} trading style. The user has selected {margin_context}. You must determine everything else from the chart.

TRADING STYLE OPTIMIZATION - {trading_style_display.upper()}:
- Timeframe Focus: {style_guide['timeframe']}
- Leverage Range: {style_guide['leverage_range']}
- Stop Loss Style: {style_guide['stop_loss']}
- Take Profit Style: {style_guide['take_profit']}
- Entry Strategy: {style_guide['entry']}
- Analysis Focus: {style_guide['focus']}

AUTOMATIC DETECTION REQUIRED - YOU MUST DETERMINE:

1. ASSET SYMBOL: Identify the asset being traded (e.g., ETH/USDT, BTC/USDT, AAPL, EUR/USD) from chart labels, title, or visible text.

2. POSITION TYPE: Analyze the chart pattern and determine if this should be a LONG (buy) or SHORT (sell) position based on:
   - Trend direction (uptrend = Long, downtrend = Short)
   - Support/resistance levels
   - Chart patterns (breakouts, reversals, etc.)
   - Technical indicators visible on the chart
   - Consider the {trading_style_display} timeframe when determining position direction

3. OPTIMAL LEVERAGE: Recommend the best leverage based on the {trading_style_display} style:
   - MUST follow the leverage range guidelines: {style_guide['leverage_range']}
   - For Scalpers: Higher leverage (10-50x) for quick profits, but adjust for volatility
   - For Swing Trading: Moderate leverage (5-20x) for balanced risk/reward
   - For Long Term: Conservative leverage (1-10x) for position holding
   - Also consider: volatility of the asset, chart patterns, and the margin mode selected ({margin_mode.replace('_', ' ').title()})

4. TRADING STRATEGY: Identify the strategy from the chart:
   - Breakout, Reversal, Trend Following, Range Trading, etc.

5. PRICE LEVELS (OPTIMIZED FOR {trading_style_display.upper()}):
   - FIRST: Read the ACTUAL CURRENT PRICE from the chart
   - Entry price: {style_guide['entry']}
   - Stop Loss: {style_guide['stop_loss']} - MUST follow the {trading_style_display} stop loss guidelines
   - Take Profit: {style_guide['take_profit']} - MUST follow the {trading_style_display} take profit guidelines
   - For Scalpers: Look for quick entry points, tight stops, multiple small profit targets
   - For Swing Trading: Look for swing points, moderate stops, medium profit targets
   - For Long Term: Look for major support/resistance, wider stops, large profit targets

6. TRADING STYLE-SPECIFIC GUIDELINES:
   - Scalpers: Focus on {style_guide['focus']} - prioritize quick execution and tight risk management
   - Swing Trading: Focus on {style_guide['focus']} - prioritize trend confirmation and pattern recognition
   - Long Term: Focus on {style_guide['focus']} - prioritize major trends and fundamental alignment

7. CONFIDENCE LEVEL: 0-100% based on pattern clarity and market conditions

8. DETAILED REASONING: Explain why you chose each parameter

PRICE VALIDATION:
- Entry price MUST be within 10% of the current price visible on the chart
- If current price is around 3000, entry should be between 2700-3300, NOT 22000
- Read the price axis carefully - check both left and right sides of the chart
- Look for price labels, current price displays, or recent candle closes

RESPOND ONLY IN VALID JSON FORMAT:
{{
    "symbol_detected": "string (the asset symbol you identified, e.g., ETH/USDT, BTC/USDT)",
    "position_type": "string (either 'long' or 'short' - your recommendation based on chart analysis)",
    "recommended_leverage": number (your recommended leverage from 1 to 100),
    "trading_strategy": "string (e.g., Breakout, Reversal, Trend Following, Range Trading)",
    "entry_price": number (entry price - MUST be realistic based on chart),
    "stop_loss": number (stop loss price - adjusted for recommended leverage),
    "take_profit": number (take profit price - at least 2:1 risk:reward),
    "confidence": number (0-100, confidence level),
    "pattern_detected": "string (detected chart pattern)",
    "analysis": "string (detailed explanation of all your decisions: why this position type, why this leverage, why these levels)",
    "risk_reward_ratio": number (risk:reward ratio),
    "current_price_read": number (the actual current price you read from the chart)
}}

IMPORTANT: If you cannot read the prices accurately, set all prices to 0 and explain in the analysis field why you couldn't read them.
"""
            
            # Llamar a Gemini API
            response = self.model.generate_content(
                [prompt, image],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            
            if response and response.text:
                content = response.text.strip()
                
                # Limpiar el contenido (puede tener markdown code blocks)
                content = re.sub(r'```json\s*', '', content)
                content = re.sub(r'```\s*', '', content)
                content = content.strip()
                
                # Buscar JSON en la respuesta
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    try:
                        analysis_data = json.loads(json_match.group())
                        
                        # Validar y convertir tipos
                        if 'confidence' in analysis_data:
                            conf = analysis_data['confidence']
                            if isinstance(conf, str):
                                conf = float(re.search(r'\d+', conf).group()) if re.search(r'\d+', conf) else 50
                            analysis_data['confidence'] = min(100, max(0, float(conf))) / 100.0
                        else:
                            analysis_data['confidence'] = 0.5
                        
                        # Asegurar que todos los campos numéricos sean float
                        for key in ['entry_price', 'stop_loss', 'take_profit', 'risk_reward_ratio', 'current_price_read']:
                            if key in analysis_data:
                                if isinstance(analysis_data[key], str):
                                    # Extraer número de string
                                    num_match = re.search(r'[\d,]+\.?\d*', analysis_data[key].replace(',', ''))
                                    if num_match:
                                        analysis_data[key] = float(num_match.group().replace(',', ''))
                                    else:
                                        analysis_data[key] = 0.0
                                else:
                                    analysis_data[key] = float(analysis_data[key])
                        
                        # VALIDACIÓN CRÍTICA: Verificar que los precios sean razonables
                        current_price = analysis_data.get('current_price_read', 0)
                        entry_price = analysis_data.get('entry_price', 0)
                        
                        # Si tenemos el precio actual leído, validar que entry esté cerca
                        if current_price > 0 and entry_price > 0:
                            # Entry debe estar dentro del 15% del precio actual
                            price_diff_percent = abs(entry_price - current_price) / current_price * 100
                            if price_diff_percent > 15:
                                self.logger.warning(
                                    f"Precio de entrada ({entry_price}) está muy lejos del precio actual ({current_price}). "
                                    f"Diferencia: {price_diff_percent:.1f}%. Ajustando..."
                                )
                                # Ajustar entry al precio actual si está muy lejos
                                if entry_price > current_price * 1.5 or entry_price < current_price * 0.5:
                                    analysis_data['entry_price'] = current_price
                                    analysis_data['stop_loss'] = current_price * 0.97  # 3% stop
                                    analysis_data['take_profit'] = current_price * 1.06  # 2:1 RR
                                    analysis_data['confidence'] = 0.3  # Bajar confianza
                                    analysis_data['analysis'] += f" [ADVERTENCIA: Precios ajustados. Precio actual leído: {current_price}]"
                        
                        # Validar que stop loss y take profit sean razonables respecto a entry
                        if entry_price > 0:
                            if analysis_data.get('stop_loss', 0) > 0:
                                stop_pct = abs(entry_price - analysis_data['stop_loss']) / entry_price * 100
                                if stop_pct > 10:  # Stop loss no debe ser más del 10%
                                    analysis_data['stop_loss'] = entry_price * 0.97
                                    self.logger.warning(f"Stop loss ajustado a 3% del entry")
                            
                            if analysis_data.get('take_profit', 0) > 0:
                                take_pct = abs(analysis_data['take_profit'] - entry_price) / entry_price * 100
                                if take_pct < 1:  # Take profit debe ser al menos 1%
                                    analysis_data['take_profit'] = entry_price * 1.06
                                    self.logger.warning(f"Take profit ajustado a 6% del entry")
                        
                        # Asegurar campos de texto
                        if 'symbol_detected' not in analysis_data:
                            analysis_data['symbol_detected'] = symbol if symbol else "N/A"
                        if 'pattern_detected' not in analysis_data:
                            analysis_data['pattern_detected'] = "Pattern not specified"
                        if 'analysis' not in analysis_data:
                            analysis_data['analysis'] = content
                        # Añadir tipo de posición, margin mode y leverage
                        if 'position_type' not in analysis_data or not analysis_data.get('position_type'):
                            analysis_data['position_type'] = position_type if position_type else 'long'
                        analysis_data['margin_mode'] = margin_mode
                        analysis_data['trading_style'] = trading_style
                        if 'recommended_leverage' in analysis_data:
                            analysis_data['leverage'] = analysis_data['recommended_leverage']
                        elif 'leverage' not in analysis_data:
                            analysis_data['leverage'] = leverage if leverage else 10  # Default 10x si no se especifica
                        if 'risk_reward_ratio' not in analysis_data:
                            # Calcular si tenemos entry, stop y take
                            if all(k in analysis_data for k in ['entry_price', 'stop_loss', 'take_profit']):
                                entry = analysis_data['entry_price']
                                stop = analysis_data['stop_loss']
                                take = analysis_data['take_profit']
                                if entry > 0 and stop > 0:
                                    risk = abs(entry - stop)
                                    reward = abs(take - entry)
                                    analysis_data['risk_reward_ratio'] = reward / risk if risk > 0 else 0.0
                            else:
                                analysis_data['risk_reward_ratio'] = 0.0
                        
                        self.logger.info(f"Análisis completado con Gemini para {symbol or 'gráfico'}")
                        return analysis_data
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Error parseando JSON de Gemini: {str(e)}")
                        self.logger.debug(f"Contenido recibido: {content[:500]}")
                        return self._create_fallback_response(content, symbol)
                else:
                    self.logger.warning("No se encontró JSON en la respuesta de Gemini")
                    return self._create_fallback_response(content, symbol)
            else:
                self.logger.error("Respuesta vacía de Gemini API")
                return self._create_fallback_response("Gemini API devolvió una respuesta vacía. Por favor, intenta con otra imagen.", symbol)
                
        except Exception as e:
            self.logger.error(f"Error analizando con Gemini: {str(e)}")
            return self._create_fallback_response(f"Error al analizar con Gemini: {str(e)}. Por favor, verifica tu configuración de API key.", symbol)
    
    
    def _create_fallback_response(self, message: str, symbol: Optional[str] = None) -> Dict:
        """Crea una respuesta de fallback cuando Gemini no está disponible."""
        return {
            "entry_price": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "confidence": 0.0,
            "pattern_detected": "No detectado - Gemini no disponible",
            "analysis": message,
            "risk_reward_ratio": 0.0,
            "current_price_read": 0.0,
            "symbol_detected": symbol if symbol else "N/A",
            "position_type": "long",
            "recommended_leverage": 1,
            "trading_strategy": "N/A",
            "margin_mode": "cross_margin"
        }
    
    def extract_price_levels_from_text(self, text: str) -> Dict:
        """
        Extrae niveles de precio de texto usando procesamiento de lenguaje natural.
        Útil cuando la IA devuelve texto en lugar de JSON estructurado.
        
        Args:
            text: Texto con información de niveles
            
        Returns:
            Diccionario con niveles extraídos
        """
        import re
        
        # Patrones para buscar precios
        patterns = {
            'entry': r'entrada[:\s]+([\d,]+\.?\d*)',
            'stop_loss': r'stop\s*loss[:\s]+([\d,]+\.?\d*)',
            'take_profit': r'take\s*profit[:\s]+([\d,]+\.?\d*)',
        }
        
        result = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result[key] = float(match.group(1).replace(',', ''))
                except:
                    pass
        
        return result

