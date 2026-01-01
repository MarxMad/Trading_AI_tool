# Guía de Inicio Rápido

## 🚀 Configuración Inicial

### 1. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Nota**: Para `ta-lib`, puede que necesites instalar primero la librería C:
- macOS: `brew install ta-lib`
- Linux: `sudo apt-get install ta-lib`
- Windows: Descargar desde [TA-Lib](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 4. Ejecutar ejemplo básico

```bash
python main.py
```

### 5. Iniciar Interfaz Gráfica

```bash
streamlit run app.py
```

La interfaz se abrirá automáticamente en tu navegador. Incluye:
- 🔍 Análisis de imágenes con IA
- 📝 Registro de trading
- 📊 Dashboard de performance
- 📈 Análisis de mercado en tiempo real

## 📚 Próximos Pasos

### Fase 1: Recolección de Datos (Semana 1-2)
- [ ] Implementar más recolectores (Binance, Alpha Vantage)
- [ ] Configurar almacenamiento en base de datos
- [ ] Implementar actualización automática de datos

### Fase 2: Análisis Técnico (Semana 2-3)
- [ ] Implementar cálculo de indicadores técnicos
- [ ] Crear estrategias básicas (media móvil, RSI, MACD)
- [ ] Visualizar datos e indicadores

### Fase 3: Modelos de IA (Semana 3-6)
- [ ] Implementar modelo LSTM para predicción
- [ ] Entrenar modelo con datos históricos
- [ ] Validar y optimizar modelo
- [ ] Integrar modelo con estrategias

### Fase 4: Backtesting (Semana 4-5)
- [ ] Implementar motor de backtesting
- [ ] Probar estrategias con datos históricos
- [ ] Calcular métricas de performance
- [ ] Optimizar parámetros de estrategias

### Fase 5: Gestión de Riesgo (Semana 5-6)
- [ ] Implementar cálculo de tamaño de posición
- [ ] Añadir stop loss y take profit automático
- [ ] Implementar límites de riesgo diario
- [ ] Monitoreo de drawdown

### Fase 6: Ejecución (Semana 6-8)
- [ ] Integrar con broker (empezar con paper trading)
- [ ] Implementar ejecución de órdenes
- [ ] Añadir gestión de órdenes pendientes
- [ ] Implementar reintentos y manejo de errores

### Fase 7: Monitoreo (Semana 7-8)
- [ ] Crear dashboard con Streamlit/Dash
- [ ] Implementar sistema de alertas
- [ ] Generar reportes de performance
- [ ] Logging y auditoría

## 🎯 Estrategia de Desarrollo Recomendada

1. **Empezar Simple**: Comienza con una estrategia básica de media móvil
2. **Validar Primero**: Siempre haz backtesting antes de trading en vivo
3. **Paper Trading**: Usa paper trading por al menos 1-2 meses antes de usar capital real
4. **Capital Pequeño**: Empieza con el mínimo posible cuando vayas a live
5. **Iterar y Mejorar**: Analiza resultados, ajusta y mejora continuamente

## 📖 Recursos Adicionales

- **Documentación Python**: https://docs.python.org/3/
- **Pandas**: https://pandas.pydata.org/docs/
- **TensorFlow**: https://www.tensorflow.org/learn
- **Backtrader**: https://www.backtrader.com/
- **yfinance**: https://pypi.org/project/yfinance/

## ⚠️ Recordatorios Importantes

- **Nunca arriesgues más de lo que puedes permitirte perder**
- **El trading es riesgoso, no hay garantías de ganancia**
- **La IA es una herramienta, no una solución mágica**
- **Siempre valida tus estrategias con backtesting**
- **Mantén un diario de trading para aprender de tus decisiones**

