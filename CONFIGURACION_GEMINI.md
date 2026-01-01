# 🤖 Configuración de Google Gemini para Análisis de Imágenes

## 📋 Pasos para Configurar Gemini

### 1. Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Get API Key" o "Create API Key"
4. Copia tu API key (comienza con `AIza...`)

### 2. Configurar Variable de Entorno

Añade a tu archivo `.env`:

```bash
# Google Gemini API (para análisis de imágenes)
GEMINI_API_KEY=tu_api_key_aqui
```

**⚠️ IMPORTANTE:** 
- **NUNCA** commitees tu API key al repositorio
- El archivo `.env` está en `.gitignore`
- Mantén tu API key segura

### 3. Instalar Dependencias

```bash
pip install google-generativeai>=0.3.0
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

### 4. Verificar Configuración

Una vez configurado, el sistema usará automáticamente Gemini para analizar imágenes de gráficos de trading.

## 🎯 Modelo Utilizado

- **Modelo:** `gemini-1.5-pro-vision-latest`
- **Capacidades:**
  - Análisis avanzado de imágenes
  - Detección de patrones técnicos
  - Lectura de valores numéricos en gráficos
  - Sugerencias de entrada, stop loss y take profit

## 💡 Ventajas de Gemini

- ✅ **Gratis hasta cierto límite** (generoso free tier)
- ✅ **Análisis de imágenes de alta calidad**
- ✅ **Rápido y eficiente**
- ✅ **Buena comprensión de contexto**

## 🔧 Solución de Problemas

### Error: "google-generativeai no está instalado"
```bash
pip install google-generativeai
```

### Error: "GEMINI_API_KEY no configurada"
- Verifica que la variable esté en tu archivo `.env`
- Asegúrate de que el archivo `.env` esté en la raíz del proyecto
- Reinicia la aplicación después de añadir la variable

### Error: "Error configurando Gemini"
- Verifica que tu API key sea válida
- Asegúrate de tener conexión a internet
- Revisa los logs para más detalles

## 📚 Recursos

- [Google AI Studio](https://makersuite.google.com/)
- [Documentación de Gemini](https://ai.google.dev/docs)
- [Gemini API Python SDK](https://github.com/google/generative-ai-python)

