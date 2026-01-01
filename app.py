"""
Interfaz gráfica principal del sistema de trading con Streamlit.
Incluye análisis de imágenes con IA y registro de trading.
Versión Premium - Lista para producción y suscripciones.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from PIL import Image
import io

from utils.config_loader import config
from utils.logger import logger
from data.collectors.yfinance_collector import YFinanceCollector
from data.processors.technical_indicators import TechnicalIndicators
from risk.risk_manager import RiskManager
from monitoring.image_analyzer import ImageAnalyzer
from monitoring.trading_journal import TradingJournal
from payment.stripe_handler import StripeHandler, STRIPE_PRICE_IDS
from database.db_handler import DatabaseHandler

# Configuración de la página
st.set_page_config(
    page_title="Trading AI Pro - Plataforma Premium",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://tradingaipro.com/support',
        'Report a bug': 'https://tradingaipro.com/bug-report',
        'About': "Trading AI Pro - Sistema de Trading Profesional con IA"
    }
)

# Sistema de suscripciones (simulado - en producción conectar con base de datos)
def get_user_plan():
    """Obtiene el plan del usuario. En producción, esto vendría de una BD."""
    return st.session_state.get('user_plan', 'free')  # free, basic, pro, enterprise

def get_plan_limits(plan):
    """Retorna los límites según el plan."""
    limits = {
        'free': {
            'name': 'Gratis',
            'analyses_per_day': 5,
            'trades_per_month': 10,
            'features': ['Análisis básico', 'Registro limitado'],
            'color': '#9e9e9e',
            'price': 0.00,
            'price_display': 'Gratis'
        },
        'basic': {
            'name': 'Básico',
            'analyses_per_day': 20,
            'trades_per_month': 50,
            'features': ['Análisis avanzado', 'Registro completo', 'Soporte email'],
            'color': '#10b981',
            'price': 5.00,
            'price_display': '$5.00/mes'
        },
        'pro': {
            'name': 'Pro',
            'analyses_per_day': 100,
            'trades_per_month': 500,
            'features': ['Análisis IA avanzado', 'Registro ilimitado', 'Soporte prioritario', 'API access'],
            'color': '#f59e0b',
            'price': 7.00,
            'price_display': '$7.00/mes'
        },
        'enterprise': {
            'name': 'Enterprise',
            'analyses_per_day': -1,  # Ilimitado
            'trades_per_month': -1,
            'features': ['Todo ilimitado', 'Soporte 24/7', 'API completa', 'Custom integrations', 'Dedicated account manager'],
            'color': '#fbbf24',
            'price': 9.00,
            'price_display': '$9.00/mes'
        }
    }
    return limits.get(plan, limits['free'])

# CSS personalizado mejorado para producción
st.markdown("""
<style>
    /* Importar fuentes premium */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header visible y mejorado - Verde/Dorado */
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        padding: 1rem 2rem !important;
        visibility: visible !important;
        display: block !important;
        height: auto !important;
        min-height: 3.5rem !important;
        position: relative !important;
        z-index: 999 !important;
    }
    
    header[data-testid="stHeader"] .css-1v0mbdj {
        color: white !important;
        visibility: visible !important;
    }
    
    /* Menú hamburguesa visible */
    [data-testid="stHeader"] button {
        color: white !important;
        visibility: visible !important;
    }
    
    /* Asegurar que el menú no se corte */
    [data-testid="stHeader"] > div {
        visibility: visible !important;
        display: flex !important;
        width: 100% !important;
        overflow: visible !important;
    }
    
    /* Menú de Streamlit visible */
    #MainMenu {
        visibility: visible !important;
        display: block !important;
    }
    
    /* Botones del header visibles */
    [data-testid="stHeader"] [data-baseweb="button"] {
        visibility: visible !important;
        color: white !important;
    }
    
    /* Estilos generales */
    .main {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 2rem;
    }
    
    /* Header personalizado premium - Verde/Dorado */
    .main-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #f59e0b 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.3);
        margin-bottom: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Badge de plan premium */
    .plan-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
        margin-top: 1rem;
    }
    
    .plan-badge-free {
        background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%);
        color: white;
    }
    
    .plan-badge-basic {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .plan-badge-pro {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .plan-badge-enterprise {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
    }
    
    /* Cards premium mejoradas - Verde/Dorado */
    .premium-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-top: 4px solid #10b981;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #10b981, #f59e0b, #10b981);
        background-size: 200% 100%;
        animation: shimmer 3s linear infinite;
    }
    
    /* Texto oscuro en cards para mejor contraste */
    .premium-card h2,
    .premium-card h3,
    .premium-card p,
    .premium-card li {
        color: #1f2937 !important;
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .premium-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Sidebar premium - Verde/Dorado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #047857 0%, #065f46 100%) !important;
        box-shadow: 2px 0 15px rgba(0,0,0,0.1) !important;
        overflow: hidden !important;
    }
    
    /* Asegurar ancho completo cuando está expandido */
    [data-testid="stSidebar"] > div {
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 1rem !important;
    }
    
    /* Cuando el sidebar está colapsado, ocultar todo el contenido */
    section[data-testid="stSidebar"][aria-expanded="false"] > div[data-testid="stSidebarContent"],
    section[data-testid="stSidebar"][aria-expanded="false"] > div > div:not([data-testid="collapsedControl"]) {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    /* Asegurar que el contenido no se corte cuando está expandido */
    [data-testid="stSidebar"]:not([aria-expanded="false"]) {
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    /* Cuando está colapsado, solo mostrar el botón de toggle */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 5.5rem !important;
        min-width: 5.5rem !important;
        max-width: 5.5rem !important;
    }
    
    /* Títulos en sidebar - CLAROS Y VISIBLES */
    [data-testid="stSidebar"] h3 {
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        margin: 1rem 0 !important;
        text-align: center !important;
    }
    
    /* Métricas en sidebar - MUY CLARAS Y VISIBLES */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #1f2937 !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        line-height: 1.2 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #1f2937 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        font-weight: 800 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stSidebar"] .stMetric {
        background: white !important;
        padding: 1.2rem 1rem !important;
        border-radius: 10px !important;
        margin: 0.7rem 0 !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.25) !important;
        border: 2px solid #d1d5db !important;
        width: 100% !important;
    }
    
    /* Columnas en sidebar más anchas */
    [data-testid="stSidebar"] [data-testid="column"] {
        width: 48% !important;
        padding: 0 0.4rem !important;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white;
    }
    
    /* Botones premium - Verde/Dorado */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.6);
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    }
    
    /* Botón premium especial - Dorado */
    .premium-button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4) !important;
    }
    
    .premium-button:hover {
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.6) !important;
    }
    
    /* Métricas premium - Verde/Dorado */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: #059669;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 700;
    }
    
    /* Inputs premium */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        font-size: 1rem;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
        outline: none;
    }
    
    /* Info boxes premium - Verde */
    .stInfo {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 5px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        color: #1f2937 !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 5px solid #4caf50;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
    }
    
    .stError {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 5px solid #f44336;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.2);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #ff9800;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
    }
    
    /* Dataframe premium */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Límite de plan warning - Dorado */
    .limit-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        color: #1f2937 !important;
    }
    
    .limit-warning h3 {
        color: #d97706;
        margin: 0 0 0.5rem 0;
    }
    
    .upgrade-button {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.75rem 2rem;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
        transition: all 0.3s ease;
    }
    
    .upgrade-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6);
    }
    
    /* Feature list premium */
    .feature-list {
        list-style: none;
        padding: 0;
    }
    
    .feature-list li {
        padding: 0.75rem 0;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        align-items: center;
    }
    
    .feature-list li:before {
        content: '✓';
        color: #4caf50;
        font-weight: bold;
        margin-right: 1rem;
        font-size: 1.2rem;
    }
    
    /* Gráficos premium */
    .js-plotly-plot {
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        background: white;
        padding: 1rem;
    }
    
    /* Footer premium - Verde/Dorado */
    .footer-premium {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #047857 0%, #065f46 50%, #f59e0b 100%);
        color: white;
        border-radius: 15px;
        margin-top: 3rem;
    }
    
    .footer-premium h3 {
        color: white;
        margin-bottom: 1rem;
    }
    
    .footer-premium p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0;
    }
    
    /* Stats card premium */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border-top: 3px solid;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Ocultar elementos de Streamlit no necesarios pero mantener menú */
    footer {visibility: hidden;}
    
    /* Mejorar scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #10b981 0%, #f59e0b 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #f59e0b 0%, #10b981 100%);
    }
</style>
""", unsafe_allow_html=True)

# Inicializar componentes (con caché)
@st.cache_resource
def init_components():
    """Inicializa los componentes del sistema."""
    initial_capital = config.get('backtesting.initial_capital', 10000)
    return {
        'data_collector': YFinanceCollector(),
        'risk_manager': RiskManager(initial_capital),
        'image_analyzer': ImageAnalyzer(),
        'journal': TradingJournal(),
        'technical_indicators': TechnicalIndicators(),
        'stripe_handler': StripeHandler(),
        'db_handler': DatabaseHandler()
    }

components = init_components()

# Obtener plan del usuario
user_plan = get_user_plan()
plan_info = get_plan_limits(user_plan)

# Header premium mejorado
st.markdown(f"""
<div class="main-header">
    <h1>🚀 Trading AI Pro</h1>
    <p>Sistema de Trading Profesional con Inteligencia Artificial</p>
    <span class="plan-badge plan-badge-{user_plan}">Plan {plan_info['name']}</span>
</div>
""", unsafe_allow_html=True)

# Sidebar premium mejorado
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 1.5rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>⚙️ Panel de Control</h2>
        <p style='color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Versión Premium</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de modo con iconos
    mode = st.selectbox(
        "📊 Selecciona el Modo",
        ["🔍 Análisis de Imagen", "📝 Registro de Trading", "📊 Dashboard", "📈 Análisis de Mercado", "💎 Planes y Suscripción"],
        label_visibility="visible"
    )
    
    # Extraer modo sin emoji
    mode = mode.split(" ", 1)[1] if " " in mode else mode
    
    st.markdown("---")
    
    # Estadísticas rápidas - Diseño limpio y profesional
    stats = components['journal'].get_statistics()
    
    st.markdown("### 📊 Estadísticas Rápidas")
    
    # Métricas en 2 columnas con mejor espaciado
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📈 Total", stats['total_trades'], delta=None)
        st.metric("✅ Win Rate", f"{stats['win_rate']:.1f}%", delta=None)
    with col2:
        st.metric("🔄 Abiertos", stats['open_trades'], delta=None)
        pnl_delta = f"{stats['total_pnl']:+,.2f}" if stats['total_pnl'] != 0 else None
        st.metric("💰 P&L Total", f"${stats['total_pnl']:,.2f}", delta=pnl_delta)
    
    # Información del plan
    st.markdown("---")
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 10px;'>
        <p style='color: white; margin: 0; font-size: 0.9rem; text-align: center;'>
            <strong>Plan Actual:</strong> {plan_info['name'].upper()}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Contenido principal según el modo
if mode == "Análisis de Imagen":
    # Verificar límites del plan
    analyses_today = st.session_state.get('analyses_today', 0)
    if plan_info['analyses_per_day'] > 0 and analyses_today >= plan_info['analyses_per_day']:
        st.markdown(f"""
        <div class="limit-warning">
            <h3>⚠️ Límite de Análisis Alcanzado</h3>
            <p>Has alcanzado tu límite diario de {plan_info['analyses_per_day']} análisis.</p>
            <a href="#" class="upgrade-button" onclick="alert('Funcionalidad de upgrade en desarrollo')">🚀 Actualizar Plan</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="premium-card">
            <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>🔍 Análisis de Gráficos con IA</h2>
            <p style='color: #1f2937 !important; font-size: 1.1rem; font-weight: 500;'>
                Sube una captura de pantalla de un gráfico de trading y nuestra IA avanzada analizará automáticamente:
            </p>
            <ul class="feature-list" style='color: #1f2937 !important;'>
                <li style='color: #1f2937 !important;'>🎯 Patrones técnicos visibles (soporte, resistencia, tendencias)</li>
                <li style='color: #1f2937 !important;'>📊 Nivel de entrada sugerido con precisión</li>
                <li style='color: #1f2937 !important;'>🛡️ Stop Loss recomendado basado en riesgo</li>
                <li style='color: #1f2937 !important;'>🎯 Take Profit objetivo optimizado</li>
                <li style='color: #1f2937 !important;'>📈 Nivel de confianza de la operación</li>
                <li style='color: #1f2937 !important;'>⚖️ Ratio riesgo:beneficio calculado</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📤 Subir Gráfico")
            uploaded_file = st.file_uploader(
                "Arrastra y suelta tu imagen aquí",
                type=['png', 'jpg', 'jpeg'],
                help="Captura de pantalla de tu plataforma de trading",
                label_visibility="collapsed"
            )
            
            st.markdown("### 📝 Información del Trade")
            symbol = st.text_input(
                "Símbolo del activo", 
                placeholder="Ej: BTC/USDT, AAPL, EUR/USD",
                help="Símbolo del activo que estás analizando"
            )
            strategy = st.text_input(
                "Estrategia", 
                placeholder="Ej: Breakout, Reversión, Trend Following",
                help="Tipo de estrategia que estás usando"
            )
            notes = st.text_area(
                "Notas adicionales", 
                placeholder="Observaciones sobre el trade, razones de entrada, etc...",
                height=100
            )
        
        with col2:
            if uploaded_file is not None:
                st.markdown("### 📊 Vista Previa del Gráfico")
                image = Image.open(uploaded_file)
                st.image(image, caption="Gráfico subido", use_container_width=True)
                
                # Botón de análisis mejorado
                if st.button("🔍 Analizar con IA", type="primary", use_container_width=True):
                    with st.spinner("🤖 Analizando gráfico con IA avanzada... Esto puede tomar unos segundos"):
                        analysis = components['image_analyzer'].analyze_chart_image(
                            image, symbol if symbol else None
                        )
                        
                        # Incrementar contador
                        st.session_state['analyses_today'] = analyses_today + 1
                        
                        # Mostrar resultados con mejor diseño
                        st.success("✅ Análisis completado exitosamente!")
                        
                        # Métricas principales en cards premium
                        st.markdown("### 💡 Resultados del Análisis")
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric(
                                "💰 Entrada", 
                                f"${analysis['entry_price']:,.2f}",
                                help="Precio sugerido para entrar al mercado"
                            )
                        with col_b:
                            st.metric(
                                "🛡️ Stop Loss", 
                                f"${analysis['stop_loss']:,.2f}",
                                help="Precio de stop loss recomendado"
                            )
                        with col_c:
                            st.metric(
                                "🎯 Take Profit", 
                                f"${analysis['take_profit']:,.2f}",
                                help="Precio objetivo para tomar ganancias"
                            )
                        with col_d:
                            confidence_color = "🟢" if analysis['confidence'] > 0.7 else "🟡" if analysis['confidence'] > 0.5 else "🔴"
                            st.metric(
                                "📈 Confianza", 
                                f"{confidence_color} {analysis['confidence']*100:.1f}%",
                                help="Nivel de confianza de la operación"
                            )
                        
                        # Análisis detallado en card premium
                        st.markdown("""
                        <div class="premium-card">
                        """, unsafe_allow_html=True)
                        st.markdown("### 📋 Análisis Detallado")
                        st.markdown("""
                        <style>
                        .premium-card h3 {
                            color: #1f2937 !important;
                            font-weight: 700;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Patrón detectado
                        pattern_badge = f'<span class="badge badge-info">{analysis["pattern_detected"]}</span>'
                        st.markdown(f"**Patrón detectado:** {pattern_badge}", unsafe_allow_html=True)
                        
                        st.markdown("**Análisis:**")
                        st.info(analysis['analysis'])
                        
                        if 'risk_reward_ratio' in analysis:
                            rr_color = "🟢" if analysis['risk_reward_ratio'] >= 2 else "🟡" if analysis['risk_reward_ratio'] >= 1.5 else "🔴"
                            st.metric("⚖️ Ratio Riesgo:Beneficio", f"{rr_color} 1:{analysis['risk_reward_ratio']:.2f}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Guardar en sesión para registro
                        st.session_state['last_analysis'] = {
                            'analysis': analysis,
                            'symbol': symbol,
                            'strategy': strategy,
                            'notes': notes,
                            'image': uploaded_file
                        }
                        
                        # Botón para registrar trade
                        st.markdown("---")
                        if st.button("💾 Registrar Trade en Diario", use_container_width=True, type="primary"):
                            if 'last_analysis' in st.session_state:
                                analysis_data = st.session_state['last_analysis']
                                analysis = analysis_data['analysis']
                                
                                # Calcular cantidad basada en riesgo
                                entry = analysis['entry_price']
                                stop = analysis['stop_loss']
                                risk_amount = components['risk_manager'].current_capital * 0.02
                                quantity = components['risk_manager'].calculate_position_size(entry, stop, risk_amount)
                                
                                trade_id = components['journal'].add_trade(
                                    symbol=analysis_data['symbol'] or "N/A",
                                    side='long',
                                    entry_price=entry,
                                    quantity=quantity,
                                    stop_loss=stop,
                                    take_profit=analysis['take_profit'],
                                    strategy=analysis_data['strategy'],
                                    notes=analysis_data['notes'],
                                    image_analysis=analysis
                                )
                                
                                st.success(f"✅ Trade registrado exitosamente! ID: {trade_id}")
                                st.balloons()
                                del st.session_state['last_analysis']
            else:
                st.info("👆 Sube una imagen del gráfico para comenzar el análisis")
        
        # Mostrar uso del plan
        if plan_info['analyses_per_day'] > 0:
            remaining = plan_info['analyses_per_day'] - analyses_today
            st.info(f"📊 Análisis restantes hoy: {remaining} de {plan_info['analyses_per_day']}")

elif mode == "Registro de Trading":
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1e3c72; margin-top: 0;'>📝 Diario de Trading</h2>
        <p style='color: #666;'>Gestiona y analiza todas tus operaciones de trading de forma profesional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros mejorados
    st.markdown("### 🔍 Filtros de Búsqueda")
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_symbol = st.selectbox(
            "📊 Símbolo",
            ["Todos"] + list(set(t['symbol'] for t in components['journal'].trades)),
            help="Filtrar por símbolo del activo"
        )
    with col2:
        filter_status = st.selectbox(
            "📈 Estado",
            ["Todos", "open", "closed", "cancelled"],
            help="Filtrar por estado de la operación"
        )
    with col3:
        show_stats = st.checkbox("📊 Mostrar Estadísticas", value=True)
    
    # Obtener trades filtrados
    trades = components['journal'].get_trades(
        symbol=None if filter_symbol == "Todos" else filter_symbol,
        status=None if filter_status == "Todos" else filter_status
    )
    
    if show_stats:
        stats = components['journal'].get_statistics()
        
        st.markdown("### 📊 Estadísticas Generales")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📈 Total", stats['total_trades'])
        with col2:
            st.metric("🔄 Abiertos", stats['open_trades'])
        with col3:
            st.metric("✅ Cerrados", stats['closed_trades'])
        with col4:
            win_color = "🟢" if stats['win_rate'] > 50 else "🟡" if stats['win_rate'] > 30 else "🔴"
            st.metric("🎯 Win Rate", f"{win_color} {stats['win_rate']:.1f}%")
        with col5:
            pnl_color = "🟢" if stats['total_pnl'] > 0 else "🔴" if stats['total_pnl'] < 0 else "⚪"
            st.metric("💰 P&L Total", f"{pnl_color} ${stats['total_pnl']:,.2f}", 
                     delta=f"{stats['total_pnl']:+,.2f}" if stats['total_pnl'] != 0 else None)
        
        st.markdown("---")
    
    # Tabla de trades mejorada
    if trades:
        st.markdown("### 📋 Lista de Operaciones")
        # Preparar datos para tabla
        table_data = []
        for trade in trades:
            status_emoji = "🟢" if trade['status'] == 'open' else "✅" if trade['status'] == 'closed' else "❌"
            table_data.append({
                'ID': trade['id'],
                'Símbolo': trade['symbol'],
                'Lado': '📈 Long' if trade['side'] == 'long' else '📉 Short',
                'Entrada': f"${trade['entry_price']:,.2f}",
                'Cantidad': f"{trade['quantity']:.4f}",
                'Stop Loss': f"${trade['stop_loss']:,.2f}" if trade['stop_loss'] else "N/A",
                'Take Profit': f"${trade['take_profit']:,.2f}" if trade['take_profit'] else "N/A",
                'Estado': f"{status_emoji} {trade['status'].title()}",
                'P&L': f"${trade['pnl']:,.2f}" if trade['pnl'] is not None else "N/A",
                'Fecha': datetime.fromisoformat(trade['entry_time']).strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Detalles de trade seleccionado
        if len(trades) > 0:
            st.markdown("### 📊 Detalles del Trade Seleccionado")
            selected_id = st.selectbox(
                "Selecciona un trade para ver detalles completos",
                [t['id'] for t in trades],
                label_visibility="visible"
            )
            
            selected_trade = next(t for t in trades if t['id'] == selected_id)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📝 Información General")
                st.json(selected_trade, expanded=True)
            with col2:
                if selected_trade.get('image_analysis'):
                    st.markdown("#### 🤖 Análisis de Imagen")
                    st.json(selected_trade['image_analysis'], expanded=True)
    else:
        st.info("""
        📌 **No hay operaciones registradas aún**
        
        Usa la sección **"Análisis de Imagen"** para crear tu primer trade.
        """)

elif mode == "Dashboard":
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>📊 Dashboard de Performance</h2>
        <p style='color: #1f2937 !important; font-weight: 500;'>Visualiza el rendimiento de tus operaciones en tiempo real</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = components['journal'].get_statistics()
    
    # Sección de Capital Editable
    st.markdown("### 💰 Gestión de Capital")
    col_cap1, col_cap2, col_cap3 = st.columns([2, 1, 1])
    
    with col_cap1:
        current_capital = components['risk_manager'].current_capital
        st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #10b981;'>
            <h3 style='color: #1f2937; margin: 0 0 0.5rem 0; font-size: 1.1rem;'>💵 Capital Actual</h3>
            <p style='color: #059669; font-size: 2rem; font-weight: 800; margin: 0;'>${current_capital:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_cap2:
        st.markdown("<br>", unsafe_allow_html=True)
        edit_capital = st.button("✏️ Editar Capital", use_container_width=True, type="secondary")
    
    with col_cap3:
        risk_metrics = components['risk_manager'].get_current_risk_metrics()
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #f59e0b;'>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Capital Inicial</p>
            <p style='color: #1f2937; font-size: 1.2rem; font-weight: 700; margin: 0;'>${risk_metrics['initial_capital']:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Modal/Formulario para editar capital
    if edit_capital or st.session_state.get('show_edit_capital', False):
        st.session_state['show_edit_capital'] = True
        st.markdown("---")
        st.markdown("### ✏️ Editar Capital")
        
        with st.form("edit_capital_form"):
            col_form1, col_form2 = st.columns([2, 1])
            
            with col_form1:
                new_capital = st.number_input(
                    "Nuevo Capital ($)",
                    min_value=100.0,
                    max_value=10000000.0,
                    value=float(current_capital),
                    step=100.0,
                    format="%.2f",
                    help="Ingresa el nuevo capital disponible"
                )
            
            with col_form2:
                st.markdown("<br>", unsafe_allow_html=True)
                difference = new_capital - current_capital
                if difference != 0:
                    diff_color = "#10b981" if difference > 0 else "#f44336"
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 8px; border-left: 3px solid {diff_color};'>
                        <p style='color: #666; margin: 0; font-size: 0.85rem;'>Diferencia</p>
                        <p style='color: {diff_color}; margin: 0; font-weight: 700;'>${difference:+,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_capital = st.form_submit_button("✅ Guardar Cambios", use_container_width=True, type="primary")
            with col_btn2:
                cancel_capital = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit_capital:
                success, message = components['risk_manager'].update_capital(new_capital)
                if success:
                    st.success(message)
                    st.balloons()
                    st.session_state['show_edit_capital'] = False
                    st.rerun()
                else:
                    st.error(message)
            
            if cancel_capital:
                st.session_state['show_edit_capital'] = False
                st.rerun()
    
    st.markdown("---")
    
    # Métricas principales mejoradas
    st.markdown("### 📊 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "💵 Capital Actual", 
            f"${components['risk_manager'].current_capital:,.2f}",
            help="Capital disponible actualmente"
        )
    with col2:
        st.metric(
            "📈 Total Trades", 
            stats['total_trades'],
            help="Número total de operaciones realizadas"
        )
    with col3:
        win_color = "🟢" if stats['win_rate'] > 50 else "🟡" if stats['win_rate'] > 30 else "🔴"
        st.metric(
            "🎯 Win Rate", 
            f"{win_color} {stats['win_rate']:.1f}%",
            help="Porcentaje de operaciones ganadoras"
        )
    with col4:
        pnl_color = "🟢" if stats['total_pnl'] > 0 else "🔴" if stats['total_pnl'] < 0 else "⚪"
        st.metric(
            "💰 P&L Total", 
            f"{pnl_color} ${stats['total_pnl']:,.2f}",
            delta=f"{stats['total_pnl']:+,.2f}" if stats['total_pnl'] != 0 else None,
            help="Profit & Loss total acumulado"
        )
    
    st.markdown("---")
    
    # Gráficos mejorados
    if stats['total_trades'] > 0:
        # Gráfico de P&L acumulado
        closed_trades = components['journal'].get_trades(status='closed')
        if closed_trades:
            pnl_data = []
            cumulative = 0
            for trade in sorted(closed_trades, key=lambda x: x['entry_time']):
                if trade['pnl'] is not None:
                    cumulative += trade['pnl']
                    pnl_data.append({
                        'date': datetime.fromisoformat(trade['exit_time']),
                        'pnl': trade['pnl'],
                        'cumulative': cumulative
                    })
            
            if pnl_data:
                df_pnl = pd.DataFrame(pnl_data)
                
                fig = go.Figure()
                color = '#10b981' if df_pnl['cumulative'].iloc[-1] > 0 else '#f44336'
                fig.add_trace(go.Scatter(
                    x=df_pnl['date'],
                    y=df_pnl['cumulative'],
                    mode='lines+markers',
                    name='P&L Acumulado',
                    line=dict(color=color, width=3),
                    marker=dict(size=6),
                    fill='tonexty',
                    fillcolor=f'{color}33'
                ))
                fig.update_layout(
                    title={
                        'text': "📈 Evolución del P&L Acumulado",
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 20}
                    },
                    xaxis_title="Fecha",
                    yaxis_title="P&L ($)",
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#333'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Distribución de trades por símbolo
        if stats['total_trades'] > 0:
            df = components['journal'].export_to_dataframe()
            if not df.empty and 'symbol' in df.columns:
                symbol_counts = df['symbol'].value_counts()
                fig = go.Figure(data=[go.Bar(
                    x=symbol_counts.index, 
                    y=symbol_counts.values,
                    marker_color='#10b981',
                    text=symbol_counts.values,
                    textposition='auto'
                )])
                fig.update_layout(
                    title={
                        'text': "📊 Distribución de Trades por Símbolo",
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 20}
                    },
                    xaxis_title="Símbolo",
                    yaxis_title="Cantidad de Trades",
                    height=350,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#333')
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No hay datos suficientes para mostrar gráficos. Realiza algunas operaciones primero.")
    
    # Información adicional de capital
    st.markdown("---")
    st.markdown("### 📈 Información de Capital")
    risk_metrics = components['risk_manager'].get_current_risk_metrics()
    
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;'>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Retorno Total</p>
            <p style='color: #1f2937; margin: 0; font-size: 1.3rem; font-weight: 700;'>${risk_metrics['total_return']:+,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;'>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Retorno %</p>
            <p style='color: #1f2937; margin: 0; font-size: 1.3rem; font-weight: 700;'>{risk_metrics['total_return_percentage']:+.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    with col_info3:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;'>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>P&L Diario</p>
            <p style='color: #1f2937; margin: 0; font-size: 1.3rem; font-weight: 700;'>${risk_metrics['daily_pnl']:+,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_info4:
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;'>
            <p style='color: #666; margin: 0; font-size: 0.9rem;'>Posiciones Abiertas</p>
            <p style='color: #1f2937; margin: 0; font-size: 1.3rem; font-weight: 700;'>{risk_metrics['open_positions']}</p>
        </div>
        """, unsafe_allow_html=True)

elif mode == "Análisis de Mercado":
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>📈 Análisis de Mercado en Tiempo Real</h2>
        <p style='color: #1f2937 !important; font-weight: 500;'>Análisis profesional con indicadores técnicos avanzados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controles
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.text_input(
            "🔍 Símbolo del Activo", 
            value="AAPL", 
            placeholder="Ej: AAPL, MSFT, BTC/USDT, EUR/USD",
            help="Ingresa el símbolo del activo que deseas analizar"
        )
    with col2:
        interval = st.selectbox(
            "⏱️ Intervalo", 
            ["1d", "1h", "5m", "1m"],
            help="Intervalo de tiempo para los datos"
        )
    with col3:
        days_back = st.selectbox(
            "📅 Período",
            [7, 30, 90, 180, 365],
            index=1,
            help="Días de datos históricos"
        )
    
    show_indicators = st.checkbox("📊 Mostrar Indicadores Técnicos", value=True)
    show_volume = st.checkbox("📈 Mostrar Gráfico de Volumen", value=True)
    
    if st.button("📊 Analizar Mercado", type="primary", use_container_width=True):
        with st.spinner("🔄 Obteniendo y analizando datos del mercado..."):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            data = components['data_collector'].fetch_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            
            if not data.empty:
                st.success(f"✅ Datos obtenidos exitosamente: {len(data)} registros")
                
                # Calcular indicadores técnicos
                if show_indicators:
                    data = components['technical_indicators'].calculate_all(data)
                
                # Análisis de tendencia
                trend_analysis = components['technical_indicators'].get_trend_analysis(data)
                support_resistance = components['technical_indicators'].get_support_resistance_levels(data)
                
                # Mostrar análisis de tendencia
                st.markdown("### 📊 Análisis de Tendencias")
                col_trend1, col_trend2, col_trend3, col_trend4 = st.columns(4)
                with col_trend1:
                    trend_color = "#10b981" if trend_analysis['trend'] == 'alcista' else "#f44336" if trend_analysis['trend'] == 'bajista' else "#f59e0b"
                    trend_emoji = "📈" if trend_analysis['trend'] == 'alcista' else "📉" if trend_analysis['trend'] == 'bajista' else "➡️"
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid {trend_color};'>
                        <p style='color: #666; margin: 0; font-size: 0.9rem;'>Tendencia</p>
                        <p style='color: {trend_color}; margin: 0; font-size: 1.3rem; font-weight: 700;'>{trend_emoji} {trend_analysis['trend'].title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_trend2:
                    signal_color = "#10b981" if trend_analysis['signal'] == 'buy' else "#f44336" if trend_analysis['signal'] == 'sell' else "#f59e0b"
                    signal_emoji = "🟢" if trend_analysis['signal'] == 'buy' else "🔴" if trend_analysis['signal'] == 'sell' else "🟡"
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid {signal_color};'>
                        <p style='color: #666; margin: 0; font-size: 0.9rem;'>Señal</p>
                        <p style='color: {signal_color}; margin: 0; font-size: 1.3rem; font-weight: 700;'>{signal_emoji} {trend_analysis['signal'].upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_trend3:
                    rsi_value = trend_analysis.get('rsi', 50)
                    rsi_color = "#f44336" if rsi_value > 70 else "#10b981" if rsi_value < 30 else "#f59e0b"
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid {rsi_color};'>
                        <p style='color: #666; margin: 0; font-size: 0.9rem;'>RSI</p>
                        <p style='color: {rsi_color}; margin: 0; font-size: 1.3rem; font-weight: 700;'>{rsi_value:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_trend4:
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #10b981;'>
                        <p style='color: #666; margin: 0; font-size: 0.9rem;'>Precio Actual</p>
                        <p style='color: #1f2937; margin: 0; font-size: 1.3rem; font-weight: 700;'>${trend_analysis['current_price']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Gráfico principal con indicadores
                fig = make_subplots(
                    rows=2 if show_volume else 1,
                    cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    row_heights=[0.7, 0.3] if show_volume else [1.0],
                    subplot_titles=(
                        [f"{symbol} - Precio y Indicadores", "Volumen"] if show_volume 
                        else [f"{symbol} - Precio y Indicadores"]
                    )
                )
                
                # Gráfico de velas
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data['open'],
                        high=data['high'],
                        low=data['low'],
                        close=data['close'],
                        name="Precio",
                        increasing_line_color='#10b981',
                        decreasing_line_color='#f44336'
                    ),
                    row=1, col=1
                )
                
                # Añadir indicadores técnicos
                if show_indicators:
                    if 'sma_20' in data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data['sma_20'],
                                name='SMA 20',
                                line=dict(color='#f59e0b', width=2)
                            ),
                            row=1, col=1
                        )
                    if 'sma_50' in data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data['sma_50'],
                                name='SMA 50',
                                line=dict(color='#10b981', width=2)
                            ),
                            row=1, col=1
                        )
                    if 'bb_upper' in data.columns and 'bb_lower' in data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data['bb_upper'],
                                name='BB Superior',
                                line=dict(color='rgba(16, 185, 129, 0.3)', width=1, dash='dash'),
                                showlegend=False
                            ),
                            row=1, col=1
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data['bb_lower'],
                                name='BB Inferior',
                                line=dict(color='rgba(16, 185, 129, 0.3)', width=1, dash='dash'),
                                fill='tonexty',
                                fillcolor='rgba(16, 185, 129, 0.1)',
                                showlegend=False
                            ),
                            row=1, col=1
                        )
                
                # Gráfico de volumen
                if show_volume:
                    colors = ['#10b981' if data['close'].iloc[i] >= data['open'].iloc[i] else '#f44336' 
                             for i in range(len(data))]
                    fig.add_trace(
                        go.Bar(
                            x=data.index,
                            y=data['volume'],
                            name='Volumen',
                            marker_color=colors,
                            opacity=0.6
                        ),
                        row=2, col=1
                    )
                
                fig.update_layout(
                    height=800 if show_volume else 600,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#333'),
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified'
                )
                
                fig.update_xaxes(title_text="Fecha", row=2 if show_volume else 1, col=1)
                fig.update_yaxes(title_text="Precio ($)", row=1, col=1)
                if show_volume:
                    fig.update_yaxes(title_text="Volumen", row=2, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Indicadores técnicos en tablas
                if show_indicators:
                    st.markdown("### 📊 Indicadores Técnicos")
                    col_ind1, col_ind2 = st.columns(2)
                    
                    with col_ind1:
                        st.markdown("#### Medias Móviles")
                        ma_data = []
                        if 'sma_20' in data.columns:
                            ma_data.append({'Indicador': 'SMA 20', 'Valor': f"${data['sma_20'].iloc[-1]:,.2f}"})
                        if 'sma_50' in data.columns:
                            ma_data.append({'Indicador': 'SMA 50', 'Valor': f"${data['sma_50'].iloc[-1]:,.2f}"})
                        if 'ema_12' in data.columns:
                            ma_data.append({'Indicador': 'EMA 12', 'Valor': f"${data['ema_12'].iloc[-1]:,.2f}"})
                        if 'ema_26' in data.columns:
                            ma_data.append({'Indicador': 'EMA 26', 'Valor': f"${data['ema_26'].iloc[-1]:,.2f}"})
                        
                        if ma_data:
                            st.dataframe(pd.DataFrame(ma_data), use_container_width=True, hide_index=True)
                    
                    with col_ind2:
                        st.markdown("#### Osciladores")
                        osc_data = []
                        if 'rsi' in data.columns:
                            rsi_val = data['rsi'].iloc[-1]
                            rsi_status = "Sobrecompra" if rsi_val > 70 else "Sobreventa" if rsi_val < 30 else "Neutral"
                            osc_data.append({'Indicador': 'RSI (14)', 'Valor': f"{rsi_val:.2f}", 'Estado': rsi_status})
                        if 'macd' in data.columns:
                            osc_data.append({'Indicador': 'MACD', 'Valor': f"${data['macd'].iloc[-1]:,.2f}"})
                        if 'macd_signal' in data.columns:
                            osc_data.append({'Indicador': 'MACD Signal', 'Valor': f"${data['macd_signal'].iloc[-1]:,.2f}"})
                        
                        if osc_data:
                            st.dataframe(pd.DataFrame(osc_data), use_container_width=True, hide_index=True)
                
                # Niveles de soporte y resistencia
                if support_resistance['support'] or support_resistance['resistance']:
                    st.markdown("### 🎯 Niveles Clave")
                    col_sr1, col_sr2 = st.columns(2)
                    with col_sr1:
                        st.markdown("#### 🛡️ Soporte")
                        if support_resistance['support']:
                            for level in support_resistance['support']:
                                st.markdown(f"- **${level:,.2f}**")
                        else:
                            st.info("No se identificaron niveles de soporte")
                    with col_sr2:
                        st.markdown("#### 🚀 Resistencia")
                        if support_resistance['resistance']:
                            for level in support_resistance['resistance']:
                                st.markdown(f"- **${level:,.2f}**")
                        else:
                            st.info("No se identificaron niveles de resistencia")
                
                # Datos recientes
                st.markdown("### 📋 Últimos Registros")
                display_data = data[['open', 'high', 'low', 'close', 'volume']].tail(10).copy()
                if 'rsi' in data.columns:
                    display_data['rsi'] = data['rsi'].tail(10)
                st.dataframe(
                    display_data.style.format({
                        'open': '${:,.2f}',
                        'high': '${:,.2f}',
                        'low': '${:,.2f}',
                        'close': '${:,.2f}',
                        'volume': '{:,.0f}',
                        'rsi': '{:.2f}'
                    }),
                    use_container_width=True
                )
                
                # Botón para exportar
                csv = data.to_csv()
                st.download_button(
                    label="📥 Descargar Datos CSV",
                    data=csv,
                    file_name=f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ No se pudieron obtener datos para este símbolo. Verifica que el símbolo sea correcto.")
    
    # Sección de Tecnologías
    st.markdown("---")
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>🛠️ Tecnologías Utilizadas</h2>
        <p style='color: #1f2937 !important; font-weight: 500;'>Stack tecnológico profesional para análisis de mercado</p>
    </div>
    """, unsafe_allow_html=True)
    
    tech_cols = st.columns(3)
    
    with tech_cols[0]:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #10b981;'>
            <h3 style='color: #1f2937; margin-top: 0;'>🐍 Python & Data Science</h3>
            <ul style='color: #1f2937; padding-left: 1.5rem;'>
                <li><strong>Python 3.10+</strong> - Lenguaje principal</li>
                <li><strong>Pandas</strong> - Manipulación de datos</li>
                <li><strong>NumPy</strong> - Cálculos numéricos</li>
                <li><strong>yfinance</strong> - Datos de mercado</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_cols[1]:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #f59e0b;'>
            <h3 style='color: #1f2937; margin-top: 0;'>🤖 Inteligencia Artificial</h3>
            <ul style='color: #1f2937; padding-left: 1.5rem;'>
                <li><strong>Google Gemini</strong> - Análisis de imágenes</li>
                <li><strong>TensorFlow</strong> - Deep Learning</li>
                <li><strong>scikit-learn</strong> - Machine Learning</li>
                <li><strong>Computer Vision</strong> - Procesamiento de imágenes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_cols[2]:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #10b981;'>
            <h3 style='color: #1f2937; margin-top: 0;'>📊 Visualización & UI</h3>
            <ul style='color: #1f2937; padding-left: 1.5rem;'>
                <li><strong>Streamlit</strong> - Interfaz web</li>
                <li><strong>Plotly</strong> - Gráficos interactivos</li>
                <li><strong>Pandas TA</strong> - Indicadores técnicos</li>
                <li><strong>OpenCV</strong> - Procesamiento de imágenes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 1rem; border-left: 4px solid #f59e0b;'>
        <h3 style='color: #1f2937; margin-top: 0;'>💡 ¿Cómo Funciona?</h3>
        <p style='color: #1f2937; line-height: 1.8;'>
            <strong>1. Recolección de Datos:</strong> Utilizamos APIs profesionales (yfinance, Alpha Vantage) para obtener datos de mercado en tiempo real.<br>
            <strong>2. Procesamiento:</strong> Los datos se procesan con Pandas y NumPy para calcular indicadores técnicos avanzados (RSI, MACD, Bollinger Bands, etc.).<br>
            <strong>3. Análisis con IA:</strong> Para análisis de gráficos, usamos Google Gemini Vision que analiza patrones visuales y sugiere niveles de entrada/salida.<br>
            <strong>4. Visualización:</strong> Plotly genera gráficos interactivos y profesionales para facilitar la toma de decisiones.<br>
            <strong>5. Gestión de Riesgo:</strong> El sistema calcula automáticamente tamaños de posición, stop loss y take profit basados en tu capital y tolerancia al riesgo.
        </p>
    </div>
    """, unsafe_allow_html=True)

elif mode == "Planes y Suscripción":
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>💎 Planes y Suscripciones</h2>
        <p style='color: #1f2937 !important; font-weight: 500;'>Elige el plan que mejor se adapte a tus necesidades de trading</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar plan actual
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {plan_info['color']} 0%, {plan_info['color']}dd 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.2);'>
        <h3 style='color: white; margin: 0 0 1rem 0;'>Tu Plan Actual</h3>
        <h2 style='color: white; margin: 0; font-size: 2.5rem; font-weight: 800;'>{plan_info['name']}</h2>
        {f"<p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.2rem;'>{plan_info.get('price_display', 'Gratis')}</p>" if plan_info.get('price') else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar estado de Stripe
    stripe_enabled = components['stripe_handler'].enabled
    if not stripe_enabled:
        st.warning("⚠️ Stripe no está configurado. Los pagos no estarán disponibles. Configura STRIPE_SECRET_KEY y STRIPE_PUBLIC_KEY en .env")
    
    # Planes disponibles
    plans = ['free', 'basic', 'pro', 'enterprise']
    plan_cols = st.columns(4)
    
    for idx, plan in enumerate(plans):
        plan_data = get_plan_limits(plan)
        with plan_cols[idx]:
            is_current = plan == user_plan
            border_color = plan_data['color'] if not is_current else '#10b981'
            border_width = '3px' if is_current else '2px'
            
            st.markdown(f"""
            <div style='
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                border: {border_width} solid {border_color};
                text-align: center;
                height: 100%;
                transition: all 0.3s ease;
            '>
                <h3 style='color: {plan_data['color']}; margin-top: 0; font-size: 1.5rem;'>{plan_data['name']}</h3>
                {f"<p style='color: #1f2937; font-size: 2rem; font-weight: 800; margin: 1rem 0;'>{plan_data.get('price_display', 'Gratis')}</p>" if plan != 'free' else "<p style='color: #1f2937; font-size: 2rem; font-weight: 800; margin: 1rem 0;'>Gratis</p>"}
                <ul class="feature-list" style='text-align: left; color: #1f2937;'>
            """, unsafe_allow_html=True)
            
            for feature in plan_data['features']:
                st.markdown(f"<li style='color: #1f2937;'>{feature}</li>", unsafe_allow_html=True)
            
            analyses_text = "Ilimitado" if plan_data['analyses_per_day'] == -1 else f"{plan_data['analyses_per_day']}/día"
            trades_text = "Ilimitado" if plan_data['trades_per_month'] == -1 else f"{plan_data['trades_per_month']}/mes"
            
            st.markdown(f"""
                </ul>
                <p style='color: #666; margin: 0.5rem 0;'><strong>Análisis:</strong> {analyses_text}</p>
                <p style='color: #666; margin: 0.5rem 0;'><strong>Trades:</strong> {trades_text}</p>
            """, unsafe_allow_html=True)
            
            if is_current:
                st.button(f"✓ Plan Actual", disabled=True, use_container_width=True, key=f"current_{plan}")
            elif plan == 'free':
                if st.button(f"🔄 Cambiar a {plan_data['name']}", use_container_width=True, key=f"downgrade_{plan}"):
                    st.session_state['user_plan'] = plan
                    st.success(f"✅ Plan cambiado a {plan_data['name']}")
                    st.rerun()
            else:
                # Botón de pago
                if stripe_enabled:
                    if st.button(f"💳 Suscribirse - {plan_data.get('price_display', f'${plan_data.get('price', 0):.2f}/mes')}", 
                               use_container_width=True, key=f"subscribe_{plan}"):
                        st.session_state['selected_plan'] = plan
                        st.session_state['show_checkout'] = True
                        st.rerun()
                else:
                    # Modo demo sin Stripe
                    if st.button(f"🚀 Probar {plan_data['name']} (Demo)", use_container_width=True, key=f"demo_{plan}"):
                        st.session_state['user_plan'] = plan
                        st.success(f"✅ Plan actualizado a {plan_data['name']} (modo demo)")
                        st.rerun()
    
    # Checkout modal
    if st.session_state.get('show_checkout', False):
        selected_plan = st.session_state.get('selected_plan')
        if selected_plan and selected_plan != 'free':
            plan_data = get_plan_limits(selected_plan)
            
            st.markdown("---")
            st.markdown("""
            <div class="premium-card">
                <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>💳 Checkout - Suscripción</h2>
            </div>
            """, unsafe_allow_html=True)
            
            col_check1, col_check2 = st.columns([2, 1])
            
            with col_check1:
                st.markdown(f"""
                <div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid {plan_data['color']};'>
                    <h3 style='color: #1f2937; margin-top: 0;'>Plan: {plan_data['name']}</h3>
                    <p style='color: #1f2937; font-size: 1.5rem; font-weight: 700;'>{plan_data.get('price_display', f'${plan_data.get('price', 0):.2f}/mes')}</p>
                    <p style='color: #666;'>Facturación mensual recurrente</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Formulario de checkout
                with st.form("checkout_form"):
                    email = st.text_input("📧 Email", placeholder="tu@email.com", help="Email para la factura")
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        submit_payment = st.form_submit_button("💳 Proceder al Pago", use_container_width=True, type="primary")
                    with col_btn2:
                        cancel_payment = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    if submit_payment:
                        if email and '@' in email:
                            # Crear sesión de checkout en Stripe
                            price_id = STRIPE_PRICE_IDS.get(selected_plan)
                            if price_id:
                                result = components['stripe_handler'].create_checkout_session(
                                    plan_name=selected_plan,
                                    price_id=price_id,
                                    user_email=email,
                                    success_url=f"http://localhost:8501/?payment=success&plan={selected_plan}",
                                    cancel_url="http://localhost:8501/?payment=cancelled"
                                )
                                
                                if result.get('url'):
                                    st.success("✅ Redirigiendo a Stripe Checkout...")
                                    st.markdown(f"""
                                    <a href="{result['url']}" target="_blank" style='
                                        display: inline-block;
                                        padding: 1rem 2rem;
                                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                                        color: white;
                                        text-decoration: none;
                                        border-radius: 10px;
                                        font-weight: 700;
                                        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
                                    '>🔒 Ir a Stripe Checkout Seguro</a>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error(f"❌ Error: {result.get('error', 'No se pudo crear la sesión de pago')}")
                            else:
                                st.error(f"❌ Price ID no configurado para el plan {selected_plan}")
                        else:
                            st.error("❌ Por favor ingresa un email válido")
                    
                    if cancel_payment:
                        st.session_state['show_checkout'] = False
                        st.session_state['selected_plan'] = None
                        st.rerun()
            
            with col_check2:
                st.markdown("""
                <div style='background: #f0fdf4; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #10b981;'>
                    <h4 style='color: #1f2937; margin-top: 0;'>🔒 Pago Seguro</h4>
                    <p style='color: #1f2937; font-size: 0.9rem;'>
                        Tus pagos están protegidos por Stripe, el procesador de pagos más seguro del mundo.
                    </p>
                    <p style='color: #666; font-size: 0.85rem; margin-top: 1rem;'>
                        ✓ Pago seguro con SSL<br>
                        ✓ Sin almacenar datos de tarjeta<br>
                        ✓ Cancelación en cualquier momento
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Manejar callbacks de pago
    query_params = st.query_params
    if 'payment' in query_params:
        if query_params['payment'] == 'success':
            plan = query_params.get('plan', 'basic')
            st.success(f"✅ ¡Pago exitoso! Tu plan ha sido actualizado a {get_plan_limits(plan)['name']}")
            st.session_state['user_plan'] = plan
            st.balloons()
        elif query_params['payment'] == 'cancelled':
            st.info("ℹ️ Pago cancelado. No se realizó ningún cargo.")

# Footer premium mejorado
st.markdown("""
<div class="footer-premium">
    <h3>🚀 Trading AI Pro</h3>
    <p>Sistema de Trading Profesional con Inteligencia Artificial</p>
    <p style='font-size: 0.9rem; color: rgba(255,255,255,0.8);'>
        Desarrollado para traders profesionales | Versión Premium 2024
    </p>
    <p style='font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 1rem;'>
        © 2024 Trading AI Pro. Todos los derechos reservados.
    </p>
</div>
""", unsafe_allow_html=True)
