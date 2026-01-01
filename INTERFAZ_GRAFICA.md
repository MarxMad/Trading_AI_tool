# 🖥️ Guía de la Interfaz Gráfica

## 🚀 Iniciar la Interfaz

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📋 Funcionalidades Principales

### 1. 🔍 Análisis de Imagen con IA

**¿Qué hace?**
- Subes una captura de pantalla de un gráfico de trading
- La IA analiza la imagen y detecta:
  - Patrones técnicos (soporte, resistencia, tendencias)
  - Nivel de entrada óptimo
  - Stop Loss recomendado
  - Take Profit objetivo
  - Nivel de confianza de la operación

**Cómo usar:**
1. Selecciona "Análisis de Imagen" en el sidebar
2. Sube una imagen (PNG, JPG, JPEG)
3. Opcionalmente, ingresa el símbolo del activo
4. Haz clic en "Analizar con IA"
5. Revisa los resultados
6. Si te gusta, haz clic en "Registrar Trade en Diario"

**Configuración de Google Gemini (Recomendado):**
Para mejor precisión, configura tu API key de Gemini:
```bash
# En tu archivo .env
GEMINI_API_KEY=tu_api_key_aqui
```

Obtén tu API key en: https://makersuite.google.com/app/apikey

Sin la API key, el sistema usará análisis básico de visión por computadora (menos preciso).

### 2. 📝 Registro de Trading

**¿Qué hace?**
- Mantiene un registro completo de todas tus operaciones
- Filtra por símbolo, estado, fecha
- Muestra estadísticas de performance
- Permite ver detalles de cada trade

**Características:**
- ✅ Registro automático desde análisis de imagen
- ✅ Filtros avanzados
- ✅ Estadísticas en tiempo real
- ✅ Exportación a DataFrame (para análisis posterior)

### 3. 📊 Dashboard

**Métricas mostradas:**
- Capital actual
- Total de trades
- Win Rate (tasa de aciertos)
- P&L Total (Profit & Loss)
- Gráfico de P&L acumulado
- Distribución de trades por símbolo

### 4. 📈 Análisis de Mercado

**¿Qué hace?**
- Obtiene datos en tiempo real de cualquier símbolo
- Muestra gráfico de velas (candlestick)
- Últimos registros de precios

**Símbolos soportados:**
- Acciones: AAPL, MSFT, GOOGL, etc.
- Crypto: BTC/USDT, ETH/USDT (requiere configuración adicional)

## 🎯 Flujo de Trabajo Recomendado

1. **Análisis de Oportunidad:**
   - Toma una captura de tu gráfico favorito
   - Sube la imagen en "Análisis de Imagen"
   - Revisa las sugerencias de la IA

2. **Registro del Trade:**
   - Si la oportunidad es buena, registra el trade
   - El sistema calculará automáticamente el tamaño de posición basado en riesgo

3. **Seguimiento:**
   - Usa "Registro de Trading" para ver tus trades abiertos
   - Actualiza cuando cierres posiciones

4. **Análisis de Performance:**
   - Revisa el Dashboard regularmente
   - Analiza qué funciona y qué no
   - Ajusta tus estrategias

## 🔧 Configuración Avanzada

### Análisis de Imagen sin Gemini

Si no tienes API key de Gemini, el sistema usará análisis básico. Para mejor precisión:
- Configura Gemini API key (ver CONFIGURACION_GEMINI.md)
- O implementa tu propio modelo de visión por computadora entrenado

### Personalización

Puedes modificar:
- `monitoring/image_analyzer.py` - Lógica de análisis
- `monitoring/trading_journal.py` - Estructura del diario
- `app.py` - Interfaz y diseño

## 📱 Características Adicionales

### Exportación de Datos
```python
# En Python
from monitoring.trading_journal import TradingJournal
journal = TradingJournal()
df = journal.export_to_dataframe()
df.to_csv('mis_trades.csv')
```

### Integración con Otros Componentes
La interfaz está integrada con:
- ✅ Sistema de gestión de riesgo
- ✅ Recolectores de datos
- ✅ Sistema de logging
- ✅ Configuración centralizada

## 🐛 Solución de Problemas

**La interfaz no inicia:**
```bash
pip install streamlit
streamlit run app.py
```

**Error con Gemini API:**
- Verifica que tu API key esté en `.env`
- Instala la librería: `pip install google-generativeai`
- El sistema funcionará sin ella, pero con menor precisión
- Ver CONFIGURACION_GEMINI.md para más detalles

**No se ven los trades:**
- Verifica que el directorio `data/` exista
- Los trades se guardan en `data/trading_journal.json`

## 💡 Tips

1. **Screenshots claros:** Asegúrate de que las capturas muestren claramente los niveles de precio
2. **Anota tus razones:** Usa el campo de notas para recordar por qué tomaste la decisión
3. **Revisa regularmente:** Analiza tus trades cerrados para aprender
4. **Backup:** Haz backup regular de `data/trading_journal.json`

## 🚀 Próximas Mejoras

- [ ] Análisis de múltiples timeframes simultáneos
- [ ] Alertas en tiempo real
- [ ] Integración con brokers para ejecución automática
- [ ] Análisis de sentimiento de noticias
- [ ] Backtesting desde la interfaz
- [ ] Exportación de reportes PDF

---

¡Disfruta de tu sistema de trading profesional! 📈

