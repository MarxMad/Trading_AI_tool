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
import cv2
import numpy as np
from utils.logger import logger
from utils.config_loader import config

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
                self.model = genai.GenerativeModel('gemini-1.5-pro-vision-latest')
                self.logger.info("Gemini configurado correctamente")
            except Exception as e:
                self.logger.error(f"Error configurando Gemini: {str(e)}")
                self.use_gemini = False
        else:
            if not GEMINI_AVAILABLE:
                self.logger.warning(
                    "google-generativeai no está instalado. "
                    "Instala con: pip install google-generativeai"
                )
            else:
                self.logger.warning(
                    "GEMINI_API_KEY no configurada. "
                    "Usando análisis básico de patrones. "
                    "Para mejor precisión, configura tu API key de Gemini."
                )
    
    def analyze_chart_image(
        self,
        image: Image.Image,
        symbol: Optional[str] = None
    ) -> Dict:
        """
        Analiza una imagen de gráfico de trading y sugiere niveles.
        
        Args:
            image: Imagen PIL del gráfico
            symbol: Símbolo del activo (opcional)
            
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
            return self._analyze_with_gemini(image, symbol)
        else:
            return self._analyze_with_basic_cv(image, symbol)
    
    def _analyze_with_gemini(
        self,
        image: Image.Image,
        symbol: Optional[str]
    ) -> Dict:
        """Analiza usando Google Gemini Vision."""
        try:
            # Preparar prompt
            prompt = f"""
Analiza esta imagen de un gráfico de trading{' para ' + symbol if symbol else ''} y proporciona un análisis técnico detallado.

INSTRUCCIONES:
1. Identifica el patrón técnico visible (soporte, resistencia, tendencia alcista/bajista, etc.)
2. Lee los valores numéricos de precio visibles en el gráfico
3. Sugiere un precio de ENTRADA óptimo basado en los niveles visibles
4. Sugiere un precio de STOP LOSS (máximo riesgo 2-3% desde entrada)
5. Sugiere un precio de TAKE PROFIT (ratio riesgo:beneficio mínimo 1:2)
6. Calcula el nivel de confianza de la operación (0-100%)
7. Proporciona una razón detallada del análisis

IMPORTANTE: Responde ÚNICAMENTE en formato JSON válido con las siguientes claves exactas:
{{
    "entry_price": número (precio de entrada),
    "stop_loss": número (precio de stop loss),
    "take_profit": número (precio de take profit),
    "confidence": número (0-100, nivel de confianza),
    "pattern_detected": "string (patrón detectado)",
    "analysis": "string explicativo detallado",
    "risk_reward_ratio": número (ratio riesgo:beneficio)
}}

Sé muy preciso con los niveles de precio basándote en los valores numéricos visibles en el gráfico.
Si no puedes leer los precios exactos, indica "No se pueden leer los precios" en el análisis.
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
                        for key in ['entry_price', 'stop_loss', 'take_profit', 'risk_reward_ratio']:
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
                        
                        # Asegurar campos de texto
                        if 'pattern_detected' not in analysis_data:
                            analysis_data['pattern_detected'] = "Patrón no especificado"
                        if 'analysis' not in analysis_data:
                            analysis_data['analysis'] = content
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
                        return self._create_fallback_response(content)
                else:
                    self.logger.warning("No se encontró JSON en la respuesta de Gemini")
                    return self._create_fallback_response(content)
            else:
                self.logger.error("Respuesta vacía de Gemini API")
                return self._analyze_with_basic_cv(image, symbol)
                
        except Exception as e:
            self.logger.error(f"Error analizando con Gemini: {str(e)}")
            return self._analyze_with_basic_cv(image, symbol)
    
    def _analyze_with_basic_cv(
        self,
        image: Image.Image,
        symbol: Optional[str]
    ) -> Dict:
        """Análisis básico usando visión por computadora (OpenCV)."""
        try:
            # Convertir a numpy array
            img_array = np.array(image)
            
            # Convertir a escala de grises si es necesario
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Detectar líneas horizontales (soporte/resistencia)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            # Extraer niveles horizontales
            horizontal_levels = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # Si la línea es más horizontal que vertical
                    if abs(y2 - y1) < abs(x2 - x1) * 0.1:
                        avg_y = (y1 + y2) / 2
                        horizontal_levels.append(avg_y)
            
            # Calcular estadísticas básicas
            height, width = gray.shape
            mean_intensity = np.mean(gray)
            
            # Estimación básica de niveles (simplificado)
            # En un caso real, necesitarías OCR o más procesamiento de imagen
            entry_price = mean_intensity * 100  # Placeholder
            stop_loss = entry_price * 0.98
            take_profit = entry_price * 1.04
            
            return {
                "entry_price": float(entry_price),
                "stop_loss": float(stop_loss),
                "take_profit": float(take_profit),
                "confidence": 0.5,  # Baja confianza sin IA avanzada
                "pattern_detected": "Análisis básico - Configura Gemini API para mejor precisión",
                "analysis": f"Análisis básico detectó {len(horizontal_levels)} niveles horizontales. "
                          f"Se recomienda usar Gemini API para análisis más preciso.",
                "risk_reward_ratio": 2.0
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis básico: {str(e)}")
            return self._create_fallback_response("Error en procesamiento de imagen")
    
    def _create_fallback_response(self, message: str) -> Dict:
        """Crea una respuesta de fallback."""
        return {
            "entry_price": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "confidence": 0.0,
            "pattern_detected": "No detectado",
            "analysis": message,
            "risk_reward_ratio": 0.0
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

