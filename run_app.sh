#!/bin/bash
# Script para iniciar la interfaz gráfica del sistema de trading

echo "🚀 Iniciando Sistema de Trading con IA..."
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "⚠️  No se encontró el entorno virtual. Creando uno nuevo..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
else
    echo "✅ Activando entorno virtual..."
    source venv/bin/activate
fi

# Verificar si streamlit está instalado
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Instalando Streamlit..."
    pip install streamlit
fi

echo ""
echo "🌐 Iniciando interfaz gráfica..."
echo "La aplicación se abrirá en: http://localhost:8501"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

streamlit run app.py

