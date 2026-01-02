"""
Interfaz gráfica principal del sistema de trading con Streamlit.
Incluye análisis de imágenes con IA y registro de trading.
Versión Premium - Lista para producción y suscripciones.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
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
# CoinW integration removed for security reasons

# Configuración de la página
st.set_page_config(
    page_title="Trading AI Pro - Premium Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://tradingaipro.com/support',
        'Report a bug': 'https://tradingaipro.com/bug-report',
        'About': "Trading AI Pro - Professional Trading System with AI"
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
            'name': 'Free',
            'analyses_per_day': 5,
            'trades_per_month': 10,
            'features': ['Basic analysis', 'Limited journal'],
            'color': '#9e9e9e',
            'price': 0.00,
            'price_display': 'Free'
        },
        'basic': {
            'name': 'Basic',
            'analyses_per_day': 20,
            'trades_per_month': 50,
            'features': ['Advanced analysis', 'Full journal', 'Email support'],
            'color': '#10b981',
            'price': 5.00,
            'price_display': '$5.00/month'
        },
        'pro': {
            'name': 'Pro',
            'analyses_per_day': 100,
            'trades_per_month': 500,
            'features': ['Advanced AI analysis', 'Unlimited journal', 'Priority support', 'API access'],
            'color': '#f59e0b',
            'price': 7.00,
            'price_display': '$7.00/month'
        },
        'enterprise': {
            'name': 'Enterprise',
            'analyses_per_day': -1,  # Unlimited
            'trades_per_month': -1,
            'features': ['Unlimited everything', '24/7 support', 'Full API', 'Custom integrations', 'Dedicated account manager'],
            'color': '#fbbf24',
            'price': 9.00,
            'price_display': '$9.00/month'
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
    
    /* Header - Tech Style - Asegurar visibilidad completa */
    header[data-testid="stHeader"] {
        background: #1a1a1a !important;
        border-bottom: 1px solid #333 !important;
        padding: 1rem 2rem !important;
        visibility: visible !important;
        display: block !important;
        height: auto !important;
        min-height: 3.5rem !important;
        position: relative !important;
        z-index: 999 !important;
        opacity: 1 !important;
        width: 100% !important;
    }
    
    /* Contenedor principal del header */
    header[data-testid="stHeader"] > div {
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        height: 100% !important;
        overflow: visible !important;
    }
    
    /* Título del header */
    header[data-testid="stHeader"] .css-1v0mbdj,
    header[data-testid="stHeader"] h1,
    header[data-testid="stHeader"] a {
        color: white !important;
        visibility: visible !important;
        display: inline-block !important;
    }
    
    /* Menú hamburguesa y botones visibles */
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] [data-baseweb="button"],
    [data-testid="stHeader"] [role="button"] {
        color: white !important;
        visibility: visible !important;
        display: inline-flex !important;
        opacity: 1 !important;
        background: transparent !important;
        border: none !important;
    }
    
    /* Menú de Streamlit visible */
    #MainMenu {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
    }
    
    /* Asegurar que los elementos del menú sean visibles */
    [data-testid="stHeader"] svg,
    [data-testid="stHeader"] path {
        fill: white !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Toolbar de Streamlit */
    [data-testid="stToolbar"] {
        visibility: visible !important;
        display: flex !important;
    }
    
    /* Estilos generales - Tech Dark Theme */
    .main {
        background: #0d1117;
        padding: 2rem;
        color: #e0e0e0;
    }
    
    /* Botones estilo tech */
    .stButton > button {
        background: #1a1a1a;
        color: #ffffff;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        text-transform: none;
        letter-spacing: 0;
    }
    
    .stButton > button:hover {
        background: #252525;
        border-color: #444;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: none;
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
        padding: 1rem 2rem;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button[kind="primary"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
    
    .stButton > button[kind="primary"]:hover::before {
        left: 100%;
    }
    
    /* Header personalizado - Estilo Tech con contornos dorados */
    .main-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        padding: 2.5rem;
        border-radius: 12px;
        border: 3px solid #d4af37;
        margin-bottom: 2rem;
        color: #e0e0e0;
        box-shadow: 0 8px 32px rgba(212, 175, 55, 0.2), inset 0 0 20px rgba(212, 175, 55, 0.05);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4af37, transparent);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        font-family: 'Inter', 'SF Mono', monospace;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
    }
    
    .main-header p {
        color: #d0d0d0;
        font-size: 1rem;
        margin-top: 0.75rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    .main-header .subtitle {
        color: #d4af37;
        font-size: 0.95rem;
        margin-top: 1rem;
        font-weight: 500;
        line-height: 1.7;
    }
    
    /* Badge de plan - Tech Style con contornos dorados */
    .plan-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 2px solid #d4af37;
        position: relative;
        z-index: 1;
        margin-top: 1.5rem;
        font-family: 'SF Mono', monospace;
        background: rgba(212, 175, 55, 0.1);
        color: #d4af37;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
    }
    
    .plan-badge-free {
        background: rgba(212, 175, 55, 0.1);
        color: #d4af37;
        border-color: #d4af37;
    }
    
    .plan-badge-basic {
        background: rgba(212, 175, 55, 0.15);
        color: #d4af37;
        border-color: #d4af37;
    }
    
    .plan-badge-pro {
        background: rgba(212, 175, 55, 0.2);
        color: #f4d03f;
        border-color: #f4d03f;
    }
    
    .plan-badge-enterprise {
        background: rgba(212, 175, 55, 0.25);
        color: #f4d03f;
        border-color: #f4d03f;
    }
    
    /* Cards - Estilo Tech Minimalista con contornos dorados */
    .premium-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #0f0f0f 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #d4af37;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);
    }
    
    .premium-card h2,
    .premium-card h3,
    .premium-card p,
    .premium-card li {
        color: #e0e0e0 !important;
    }
    
    .premium-card h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        color: #ffffff !important;
    }
    
    .premium-card:hover {
        border-color: #444;
    }
    
    /* Chat message style */
    .chat-message {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .chat-message.user {
        background: #252525;
        border-left: 3px solid #4a9eff;
    }
    
    .chat-message.assistant {
        background: #1a1a1a;
        border-left: 3px solid #10b981;
    }
    
    .chat-message h3 {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.75rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.75rem;
    }
    
    .chat-message p {
        color: #d0d0d0;
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    .chat-message .value {
        color: #ffffff;
        font-weight: 600;
        font-family: 'SF Mono', monospace;
    }
    
    /* Trading level cards - Mejorado con efectos */
    .trading-level-card {
        background: #1a1a1a;
        border: 2px solid;
        border-radius: 12px;
        padding: 2rem 1.5rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .trading-level-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    
    .trading-level-card:hover::before {
        left: 100%;
    }
    
    .trading-level-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    
    .trading-level-card.entry {
        border-color: #d4af37;
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
        box-shadow: 0 8px 32px rgba(212, 175, 55, 0.25);
    }
    
    .trading-level-card.entry:hover {
        box-shadow: 0 12px 40px rgba(212, 175, 55, 0.4);
        border-color: #f4d03f;
    }
    
    .trading-level-card.entry .price {
        color: #d4af37;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
    }
    
    .trading-level-card.stop-loss {
        border-color: #f44336;
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(244, 67, 54, 0.05) 100%);
        box-shadow: 0 8px 32px rgba(244, 67, 54, 0.2);
    }
    
    .trading-level-card.stop-loss:hover {
        box-shadow: 0 12px 40px rgba(244, 67, 54, 0.4);
    }
    
    .trading-level-card.take-profit {
        border-color: #10b981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.2);
    }
    
    .trading-level-card.take-profit:hover {
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.4);
    }
    
    .trading-level-card .label {
        color: #a0a0a0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .trading-level-card .price {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'SF Mono', monospace;
        text-shadow: 0 0 20px rgba(255,255,255,0.3);
    }
    
    
    .trading-level-card.stop-loss .price {
        color: #f44336;
        text-shadow: 0 0 20px rgba(244, 67, 54, 0.5);
    }
    
    .trading-level-card.take-profit .price {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
    }
    
    /* Asset detection card - Mejorado con contornos dorados */
    .asset-card {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
        border: 2px solid #d4af37;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(212, 175, 55, 0.25);
        transition: all 0.3s ease;
    }
    
    .asset-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(212, 175, 55, 0.4);
        border-color: #f4d03f;
    }
    
    .asset-card .symbol {
        color: #d4af37;
        font-size: 3rem;
        font-weight: 700;
        font-family: 'SF Mono', monospace;
        margin: 0.5rem 0;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
    }
    
    .asset-card .label {
        color: #d4af37;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    /* Upload area mejorada - Más atractiva */
    .upload-area {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(74, 158, 255, 0.05) 100%);
        border: 3px dashed #4a9eff;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .upload-area::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(74, 158, 255, 0.1) 0%, transparent 70%);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    .upload-area:hover {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.2) 0%, rgba(74, 158, 255, 0.1) 100%);
        border-color: #6bb6ff;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(74, 158, 255, 0.3);
    }
    
    .upload-area .upload-icon {
        font-size: 5rem;
        color: #4a9eff;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 0 20px rgba(74, 158, 255, 0.5));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .upload-area .upload-text {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0.5rem 0;
        letter-spacing: 0.5px;
    }
    
    .upload-area .upload-hint {
        color: #a0a0a0;
        font-size: 0.95rem;
        margin-top: 0.75rem;
    }
    
    /* Sidebar - Tech Style */
    [data-testid="stSidebar"] {
        background: #1a1a1a !important;
        border-right: 1px solid #333 !important;
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
    
    /* Títulos en sidebar - Tech Style */
    [data-testid="stSidebar"] h3 {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin: 1rem 0 !important;
        text-align: left !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.75rem;
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
        color: #e0e0e0;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #e0e0e0;
    }
    
    /* Inputs estilo tech */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333 !important;
        border-radius: 6px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1) !important;
    }
    
    .stSelectbox > div > div > select {
        color: #e0e0e0 !important;
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
    image_analyzer = ImageAnalyzer()
    # Asegurar que use_gemini esté siempre disponible
    if not hasattr(image_analyzer, 'use_gemini'):
        image_analyzer.use_gemini = False
    return {
        'data_collector': YFinanceCollector(),
        'risk_manager': RiskManager(initial_capital),
        'image_analyzer': image_analyzer,
        'journal': TradingJournal(),
        'technical_indicators': TechnicalIndicators(),
        'stripe_handler': StripeHandler(),
        'db_handler': DatabaseHandler()
    }

def generate_share_message(analysis: dict) -> str:
    """
    Genera un mensaje formateado para compartir el análisis.
    
    Args:
        analysis: Diccionario con los datos del análisis
        
    Returns:
        Mensaje formateado para compartir
    """
    symbol = analysis.get('symbol_detected', 'N/A')
    current_price = analysis.get('current_price_read', 0)
    entry = analysis.get('entry_price', 0)
    stop_loss = analysis.get('stop_loss', 0)
    take_profit = analysis.get('take_profit', 0)
    position_type = analysis.get('position_type', 'N/A')
    leverage = analysis.get('recommended_leverage', 'N/A')
    strategy = analysis.get('trading_strategy', 'N/A')
    
    message = f"""📊 Trading Analysis - {symbol}

💰 Current Price: ${current_price:.4f}
📈 Position: {position_type.upper()}
⚡ Leverage: {leverage}x

🎯 Entry: ${entry:.4f}
🛑 Stop Loss: ${stop_loss:.4f}
🎯 Take Profit: ${take_profit:.4f}

📋 Strategy: {strategy}

🤖 Analysis by Trading AI Pro"""
    
    return message

components = init_components()

# Función helper para formatear precios con decimales apropiados
def format_price(price: float, min_decimals: int = 2, max_decimals: int = 8) -> str:
    """
    Formatea un precio con el número apropiado de decimales basado en su valor.
    
    Args:
        price: Precio a formatear
        min_decimals: Mínimo de decimales a mostrar
        max_decimals: Máximo de decimales a mostrar
        
    Returns:
        String formateado del precio
    """
    if price == 0:
        return "$0.00"
    
    # Determinar número de decimales basado en el precio
    if price < 0.0001:
        decimals = max_decimals  # Para precios muy pequeños (ej: $0.00001)
    elif price < 0.01:
        decimals = 6  # Para precios pequeños (ej: $0.03)
    elif price < 1:
        decimals = 4  # Para precios menores a 1 (ej: $0.50)
    elif price < 1000:
        decimals = 2  # Para precios normales (ej: $100)
    else:
        decimals = 2  # Para precios altos (ej: $5000)
    
    # Asegurar que esté entre min y max
    decimals = max(min_decimals, min(decimals, max_decimals))
    
    # Formatear con separadores de miles si es necesario
    if price >= 1000:
        return f"${price:,.{decimals}f}"
    else:
        return f"${price:.{decimals}f}"

# Obtener plan del usuario
user_plan = get_user_plan()
plan_info = get_plan_limits(user_plan)

# Header tech style con contornos dorados
st.markdown(f"""
<div class="main-header">
    <h1>Trading AI Pro</h1>
    <p>Professional Trading System with Artificial Intelligence</p>
    <p class="subtitle">
        💰 With the help of AI, we can generate excellent returns while maintaining proper risk management. 
        Our intelligent system analyzes market patterns and provides optimal entry, stop-loss, and take-profit levels 
        to maximize your trading performance with controlled risk.
    </p>
    <span class="plan-badge plan-badge-{user_plan}">Plan {plan_info['name']}</span>
</div>
""", unsafe_allow_html=True)

# Sidebar premium mejorado
with st.sidebar:
    st.markdown("""
    <div class="chat-message assistant" style="margin-bottom: 1.5rem;">
        <h3>Control Panel</h3>
        <p style="font-size: 0.85rem; opacity: 0.7;">Trading AI Pro</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mode selector
    mode = st.selectbox(
        "Select Mode",
        ["Image Analysis", "Plans & Subscription"],
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    # Estadísticas rápidas - Diseño limpio y profesional
    stats = components['journal'].get_statistics()
    
    st.markdown("### Statistics")
    
    # Metrics in 2 columns with better spacing
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", stats['total_trades'], delta=None)
        st.metric("Win Rate", f"{stats['win_rate']:.1f}%", delta=None)
    with col2:
        st.metric("Open", stats['open_trades'], delta=None)
        pnl_delta = f"{stats['total_pnl']:+,.2f}" if stats['total_pnl'] != 0 else None
        st.metric("Total P&L", f"${stats['total_pnl']:,.2f}", delta=pnl_delta)
    
    # Información del plan
    st.markdown("---")
    st.markdown(f"""
    <div class="chat-message assistant" style="opacity: 0.8;">
        <p style='margin: 0; font-size: 0.85rem;'>Current Plan: <span class="value">{plan_info['name'].upper()}</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    # CoinW integration removed for security reasons

# Main content based on mode
if mode == "Image Analysis":
    # Removed trade confirmation logic and CoinW funding warning - replaced with share functionality
    
    # Verificar límites del plan
    analyses_today = st.session_state.get('analyses_today', 0)
    if plan_info['analyses_per_day'] > 0 and analyses_today >= plan_info['analyses_per_day']:
        st.markdown(f"""
        <div class="chat-message assistant">
            <h3>Limit Reached</h3>
            <p>You have reached your daily limit of {plan_info['analyses_per_day']} analyses.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Limpiar estado si se registró un trade (solo si NO hay confirmación activa)
        if st.session_state.get('trade_registered', False):
            # Limpiar todos los estados relacionados
            if 'last_analysis' in st.session_state:
                del st.session_state['last_analysis']
            if 'current_uploaded_file' in st.session_state:
                del st.session_state['current_uploaded_file']
            st.session_state['trade_registered'] = False
        
        # File uploader (solo se muestra si NO hay confirmación activa)
        uploaded_file = st.file_uploader(
            "Upload chart image",
            type=['png', 'jpg', 'jpeg'],
            help="PNG, JPG or JPEG format",
            label_visibility="visible",
            key="chart_image_uploader"
        )
        
        # Mostrar header y upload area solo si no hay imagen subida - más compacto
        if uploaded_file is None:
            # Header compacto
            col_title, col_upload = st.columns([1, 1.5])
            
            with col_title:
                st.markdown("""
                <div style="padding: 1rem 0;">
                    <h1 style="color: #ffffff; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -1px;">
                        Chart Analysis
                    </h1>
                    <p style="color: #a0a0a0; font-size: 0.9rem; line-height: 1.4;">
                        Upload a chart for AI-powered analysis
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_upload:
                # Upload section mejorada y más atractiva
                st.markdown("""
                <div class="upload-area" style="background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(74, 158, 255, 0.05) 100%); border: 3px dashed #4a9eff; border-radius: 16px; padding: 3rem 2rem; text-align: center; position: relative; overflow: hidden;">
                    <div class="upload-icon" style="font-size: 5rem; color: #4a9eff; margin-bottom: 1.5rem; filter: drop-shadow(0 0 20px rgba(74, 158, 255, 0.5)); animation: float 3s ease-in-out infinite;">📈</div>
                    <div class="upload-text" style="color: #ffffff; font-size: 1.3rem; font-weight: 600; margin: 0.5rem 0; letter-spacing: 0.5px;">
                        Drag & Drop Chart Image
                    </div>
                    <div class="upload-hint" style="color: #a0a0a0; font-size: 0.95rem; margin-top: 0.75rem;">
                        PNG, JPG, JPEG • Max 200MB
                    </div>
                    <div style="color: #4a9eff; font-size: 0.9rem; margin-top: 1rem; font-weight: 500;">
                        or click to browse
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Si llegamos aquí, mostrar el análisis normal
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Success message mejorado
            st.markdown("""
            <div style="margin: 1.5rem 0; padding: 1rem 1.5rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%); border-radius: 12px; border-left: 4px solid #10b981; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);">
                <p style="color: #10b981; margin: 0; font-size: 1rem; display: flex; align-items: center; gap: 0.75rem; font-weight: 600;">
                    <span style="font-size: 1.3rem;">✓</span> Chart uploaded successfully
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show image preview más compacto
            col_img, col_info = st.columns([2, 1])
            with col_img:
                st.image(image, use_container_width=True)
            
            with col_info:
                st.markdown("""
                <div class="chat-message user" style="margin-bottom: 1.5rem;">
                    <h3>Trade Configuration</h3>
                    <p style="font-size: 0.85rem; color: #a0a0a0; margin-top: 0.5rem; line-height: 1.5;">
                        AI will automatically detect position type, leverage, symbol, and strategy from the chart
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Solo margin mode - todo lo demás lo detecta la AI
                margin_mode = st.selectbox(
                    "Margin Mode",
                    ["Cross Margin", "Isolated Margin"],
                    label_visibility="visible",
                    help="Cross Margin: Uses entire account balance. Isolated Margin: Uses only allocated margin for this position",
                    index=0
                )
                
                st.markdown("""
                <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(74, 158, 255, 0.1); border-radius: 8px; border-left: 3px solid #4a9eff;">
                    <p style="font-size: 0.85rem; color: #a0a0a0; margin: 0; line-height: 1.5;">
                        <strong style="color: #4a9eff;">AI Auto-Detection:</strong><br>
                        • Position Type (Long/Short)<br>
                        • Optimal Leverage<br>
                        • Asset Symbol<br>
                        • Trading Strategy<br>
                        • Entry, Stop Loss & Take Profit
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Check if Gemini is being used (safe access for cached objects)
            try:
                gemini_status = components['image_analyzer'].use_gemini
            except (AttributeError, KeyError):
                # Fallback: verificar si tiene modelo configurado
                gemini_status = hasattr(components['image_analyzer'], 'model') and \
                               components['image_analyzer'].model is not None
            
            if gemini_status:
                st.markdown("""
                <div class="chat-message assistant" style="opacity: 0.8; margin-bottom: 1rem;">
                    <p style="font-size: 0.85rem;">Using Gemini AI for analysis</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="chat-message assistant" style="opacity: 0.8; margin-bottom: 1rem; border-left-color: #f59e0b;">
                    <p style="font-size: 0.85rem; color: #f59e0b;">Warning: Using basic analysis. Configure GEMINI_API_KEY for accurate results.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Analyze button - Mejorado con estilo premium
            st.markdown("""
            <div style="margin: 2.5rem 0 1.5rem 0;">
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de análisis mejorado
            analyze_button = st.button("🚀 Analyze Chart with AI", type="primary", use_container_width=True)
            
            if analyze_button:
                with st.spinner("AI is analyzing the chart and detecting all trade parameters..."):
                    # Solo pasar margin mode - la AI detectará todo lo demás
                    analysis = components['image_analyzer'].analyze_chart_image(
                        image, 
                        None,  # La AI detectará el símbolo
                        None,  # La AI determinará el tipo de posición
                        margin_mode.lower().replace(' ', '_'),
                        None  # La AI recomendará el leverage
                    )
                    
                    # Incrementar contador
                    st.session_state['analyses_today'] = analyses_today + 1
                    
                    # Guardar la imagen en sesión para que persista después del análisis
                    st.session_state['current_uploaded_file'] = uploaded_file
                    
                    # Obtener todos los valores detectados por la AI
                    detected_symbol = analysis.get('symbol_detected', 'N/A')
                    analysis_position = analysis.get('position_type', 'long').upper()
                    analysis_margin = analysis.get('margin_mode', margin_mode.lower().replace(' ', '_'))
                    analysis_leverage = analysis.get('recommended_leverage', analysis.get('leverage', 10))
                    detected_strategy = analysis.get('trading_strategy', 'Not specified')
                    position_color = "#10b981" if analysis_position == "LONG" else "#f44336"
                    position_icon = "📈" if analysis_position == "LONG" else "📉"
                    
                    # Mostrar activo, posición, margin y leverage de forma prominente
                    col_asset, col_pos, col_margin = st.columns([2, 1, 1])
                    with col_asset:
                        st.markdown(f"""
                        <div class="asset-card" style="border-color: #d4af37; background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%); box-shadow: 0 8px 32px rgba(212, 175, 55, 0.25);">
                            <div class="label" style="color: #d4af37;">Asset Detected</div>
                            <div class="symbol" style="color: #d4af37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.6);">{detected_symbol if detected_symbol != 'N/A' else 'Unknown'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_pos:
                        st.markdown(f"""
                        <div class="asset-card" style="border-color: {position_color}; background: linear-gradient(135deg, {position_color}15 0%, {position_color}05 100%);">
                            <div class="label">Position Type</div>
                            <div class="symbol" style="color: {position_color}; font-size: 1.8rem;">{position_icon} {analysis_position}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_margin:
                        margin_display = analysis_margin.replace('_', ' ').title()
                        leverage_color = "#f59e0b" if analysis_leverage >= 20 else "#4a9eff"
                        st.markdown(f"""
                        <div class="asset-card" style="border-color: {leverage_color}; background: linear-gradient(135deg, {leverage_color}15 0%, {leverage_color}05 100%);">
                            <div class="label">Leverage & Margin</div>
                            <div class="symbol" style="color: {leverage_color}; font-size: 1.5rem; margin-bottom: 0.3rem;">{analysis_leverage}x</div>
                            <div style="color: #a0a0a0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">{margin_display}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Mostrar precio actual si está disponible
                    current_price = analysis.get('current_price_read', 0)
                    if current_price > 0:
                        formatted_current = format_price(current_price)
                        st.markdown(f"""
                        <div class="chat-message assistant" style="text-align: center;">
                            <h3>Current Price</h3>
                            <p style="font-size: 1.5rem; color: #4a9eff; font-weight: 700; font-family: 'SF Mono', monospace;">{formatted_current}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Trading Levels con cards gráficas y colores - Mejorado con contornos dorados
                    st.markdown("""
                    <div style="text-align: center; margin: 4rem 0 2.5rem 0; padding: 2rem; background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%); border-radius: 16px; border: 2px solid #d4af37; box-shadow: 0 8px 32px rgba(212, 175, 55, 0.2);">
                        <h2 style="color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; letter-spacing: -1px; text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);">
                            Trading Levels
                        </h2>
                        <p style="color: #d4af37; font-size: 1rem; margin-top: 0.75rem; font-weight: 500;">
                            AI-generated entry, stop loss, and take profit levels
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_entry, col_stop, col_take = st.columns(3)
                    
                    with col_entry:
                        formatted_entry = format_price(analysis['entry_price'])
                        st.markdown(f"""
                        <div class="trading-level-card entry">
                            <div class="label">Entry Price</div>
                            <div class="price">{formatted_entry}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stop:
                        formatted_stop = format_price(analysis['stop_loss'])
                        st.markdown(f"""
                        <div class="trading-level-card stop-loss">
                            <div class="label">Stop Loss</div>
                            <div class="price">{formatted_stop}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_take:
                        formatted_take = format_price(analysis['take_profit'])
                        st.markdown(f"""
                        <div class="trading-level-card take-profit">
                            <div class="label">Take Profit</div>
                            <div class="price">{formatted_take}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Métricas adicionales - Mejoradas
                    st.markdown("""
                    <div style="margin: 3rem 0 2rem 0;">
                        <div style="text-align: center; padding: 1.5rem; background: rgba(74, 158, 255, 0.05); border-radius: 12px; border: 1px solid rgba(74, 158, 255, 0.2);">
                            <h3 style="color: #ffffff; font-size: 1.3rem; font-weight: 600; margin: 0 0 1.5rem 0;">Performance Metrics</h3>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_conf, col_rr = st.columns(2)
                    
                    with col_conf:
                        confidence_pct = analysis['confidence'] * 100
                        conf_color = "#10b981" if confidence_pct > 70 else "#f59e0b" if confidence_pct > 50 else "#f44336"
                        st.markdown(f"""
                        <div style="padding: 2rem; background: linear-gradient(135deg, {conf_color}15 0%, {conf_color}05 100%); border-radius: 16px; border: 2px solid {conf_color}; text-align: center; box-shadow: 0 8px 25px {conf_color}30;">
                            <div style="color: #a0a0a0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem; font-weight: 600;">Confidence</div>
                            <div style="font-size: 3rem; color: {conf_color}; font-weight: 700; font-family: 'SF Mono', monospace; text-shadow: 0 0 20px {conf_color}50;">{confidence_pct:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_rr:
                        rr_ratio = analysis.get('risk_reward_ratio', 0)
                        rr_color = "#10b981" if rr_ratio >= 2 else "#f59e0b" if rr_ratio >= 1.5 else "#f44336"
                        st.markdown(f"""
                        <div style="padding: 2rem; background: linear-gradient(135deg, {rr_color}15 0%, {rr_color}05 100%); border-radius: 16px; border: 2px solid {rr_color}; text-align: center; box-shadow: 0 8px 25px {rr_color}30;">
                            <div style="color: #a0a0a0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem; font-weight: 600;">Risk:Reward</div>
                            <div style="font-size: 3rem; color: {rr_color}; font-weight: 700; font-family: 'SF Mono', monospace; text-shadow: 0 0 20px {rr_color}50;">1:{rr_ratio:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Pattern y análisis detallado - Mejorados
                    st.markdown("""
                    <div style="margin: 3rem 0 2rem 0;">
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="padding: 2rem; background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(74, 158, 255, 0.05) 100%); border-radius: 16px; border-left: 4px solid #4a9eff; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(74, 158, 255, 0.2);">
                        <h3 style="color: #ffffff; font-size: 1.3rem; font-weight: 600; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <span>🔍</span> Pattern Detected
                        </h3>
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0; font-family: 'SF Mono', monospace;"><span class="value">{analysis['pattern_detected']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="padding: 2rem; background: #1a1a1a; border-radius: 16px; border: 1px solid #333; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                        <h3 style="color: #ffffff; font-size: 1.3rem; font-weight: 600; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <span>📊</span> Detailed Analysis
                        </h3>
                        <p style="color: #d0d0d0; font-size: 1rem; line-height: 1.8; margin: 0;">{analysis['analysis']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Guardar en sesión para registro - todo viene de la AI
                    st.session_state['last_analysis'] = {
                        'analysis': analysis,
                        'symbol': detected_symbol,
                        'strategy': detected_strategy,
                        'notes': f"AI Auto-detected: {detected_strategy} strategy",
                        'image': st.session_state.get('current_uploaded_file', uploaded_file),
                        'position_type': analysis_position.lower(),
                        'margin_mode': margin_mode,
                        'leverage': analysis_leverage
                    }
                    
                    # Share section - Mejorada y más atractiva
                    st.markdown("""
                    <div style="margin: 3rem 0 2rem 0; padding: 2rem; background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%); border-radius: 16px; border: 2px solid rgba(74, 158, 255, 0.3);">
                        <h3 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700; text-align: center; letter-spacing: -0.5px;">
                            📤 Share Your Analysis
                        </h3>
                        <p style="color: #a0a0a0; text-align: center; font-size: 0.9rem; margin: 0.5rem 0 1.5rem 0;">
                            Share your trading analysis with friends and colleagues
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Generate share message
                    share_message = generate_share_message(analysis)
                    
                    # Share buttons in columns - Mejorados con efectos
                    col_whatsapp, col_telegram, col_twitter = st.columns(3)
                    
                    with col_whatsapp:
                        whatsapp_url = f"https://wa.me/?text={share_message.replace(chr(10), '%0A').replace(' ', '%20')}"
                        st.markdown(f"""
                        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; display: block;">
                            <div style="padding: 1.5rem; background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); border-radius: 12px; text-align: center; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3); position: relative; overflow: hidden;">
                                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📱</div>
                                <div style="font-size: 1.1rem; letter-spacing: 0.5px;">WhatsApp</div>
                                <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: left 0.5s;"></div>
                            </div>
                        </a>
                        <style>
                            a[href*="wa.me"] > div:hover {{
                                transform: translateY(-4px);
                                box-shadow: 0 8px 25px rgba(37, 211, 102, 0.5);
                            }}
                            a[href*="wa.me"] > div:hover > div:last-child {{
                                left: 100%;
                            }}
                        </style>
                        """, unsafe_allow_html=True)
                    
                    with col_telegram:
                        telegram_url = f"https://t.me/share/url?url=&text={share_message.replace(chr(10), '%0A').replace(' ', '%20')}"
                        st.markdown(f"""
                        <a href="{telegram_url}" target="_blank" style="text-decoration: none; display: block;">
                            <div style="padding: 1.5rem; background: linear-gradient(135deg, #0088cc 0%, #005f8c 100%); border-radius: 12px; text-align: center; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 15px rgba(0, 136, 204, 0.3); position: relative; overflow: hidden;">
                                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✈️</div>
                                <div style="font-size: 1.1rem; letter-spacing: 0.5px;">Telegram</div>
                                <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: left 0.5s;"></div>
                            </div>
                        </a>
                        <style>
                            a[href*="t.me"] > div:hover {{
                                transform: translateY(-4px);
                                box-shadow: 0 8px 25px rgba(0, 136, 204, 0.5);
                            }}
                            a[href*="t.me"] > div:hover > div:last-child {{
                                left: 100%;
                            }}
                        </style>
                        """, unsafe_allow_html=True)
                    
                    with col_twitter:
                        twitter_url = f"https://twitter.com/intent/tweet?text={share_message.replace(chr(10), '%0A').replace(' ', '%20')}"
                        st.markdown(f"""
                        <a href="{twitter_url}" target="_blank" style="text-decoration: none; display: block;">
                            <div style="padding: 1.5rem; background: linear-gradient(135deg, #1DA1F2 0%, #0d8bd9 100%); border-radius: 12px; text-align: center; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 15px rgba(29, 161, 242, 0.3); position: relative; overflow: hidden;">
                                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🐦</div>
                                <div style="font-size: 1.1rem; letter-spacing: 0.5px;">Twitter</div>
                                <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: left 0.5s;"></div>
                            </div>
                        </a>
                        <style>
                            a[href*="twitter.com"] > div:hover {{
                                transform: translateY(-4px);
                                box-shadow: 0 8px 25px rgba(29, 161, 242, 0.5);
                            }}
                            a[href*="twitter.com"] > div:hover > div:last-child {{
                                left: 100%;
                            }}
                        </style>
                        """, unsafe_allow_html=True)
                    
                    # Copy to clipboard option - Mejorado
                    st.markdown("""
                    <div style="margin: 2rem 0;">
                        <div style="text-align: center; padding: 1.5rem; background: rgba(74, 158, 255, 0.05); border-radius: 12px; border: 1px dashed rgba(74, 158, 255, 0.3);">
                            <p style="color: #a0a0a0; font-size: 0.9rem; margin: 0 0 1rem 0;">Or copy the message manually</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📋 Copy Message to Clipboard", use_container_width=True, key="copy_message", type="secondary"):
                        st.code(share_message, language=None)
                        st.success("✅ Message copied! You can now paste it anywhere.")
        
        # Show plan usage
        if plan_info['analyses_per_day'] > 0:
            remaining = plan_info['analyses_per_day'] - analyses_today
            st.markdown(f"""
            <div class="chat-message assistant" style="opacity: 0.7;">
                <p style="font-size: 0.85rem;">Analyses remaining today: {remaining} of {plan_info['analyses_per_day']}</p>
            </div>
            """, unsafe_allow_html=True)

elif mode == "Plans & Subscription":
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>Plans & Subscriptions</h2>
        <p style='color: #1f2937 !important; font-weight: 500;'>Choose the plan that best fits your trading needs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current plan
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {plan_info['color']} 0%, {plan_info['color']}dd 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.2);'>
        <h3 style='color: white; margin: 0 0 1rem 0;'>Your Current Plan</h3>
        <h2 style='color: white; margin: 0; font-size: 2.5rem; font-weight: 800;'>{plan_info['name']}</h2>
        {f"<p style='color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.2rem;'>{plan_info.get('price_display', 'Free')}</p>" if plan_info.get('price') else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Check Stripe status
    stripe_enabled = components['stripe_handler'].enabled
    if not stripe_enabled:
        st.warning("⚠️ Stripe is not configured. Payments will not be available. Configure STRIPE_SECRET_KEY and STRIPE_PUBLIC_KEY in .env")
    
    # Available plans
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
                {f"<p style='color: #1f2937; font-size: 2rem; font-weight: 800; margin: 1rem 0;'>{plan_data.get('price_display', 'Free')}</p>" if plan != 'free' else "<p style='color: #1f2937; font-size: 2rem; font-weight: 800; margin: 1rem 0;'>Free</p>"}
                <ul class="feature-list" style='text-align: left; color: #1f2937;'>
            """, unsafe_allow_html=True)
            
            for feature in plan_data['features']:
                st.markdown(f"<li style='color: #1f2937;'>{feature}</li>", unsafe_allow_html=True)
            
            analyses_text = "Unlimited" if plan_data['analyses_per_day'] == -1 else f"{plan_data['analyses_per_day']}/day"
            trades_text = "Unlimited" if plan_data['trades_per_month'] == -1 else f"{plan_data['trades_per_month']}/month"
            
            st.markdown(f"""
                </ul>
                <p style='color: #666; margin: 0.5rem 0;'><strong>Analyses:</strong> {analyses_text}</p>
                <p style='color: #666; margin: 0.5rem 0;'><strong>Trades:</strong> {trades_text}</p>
            """, unsafe_allow_html=True)
            
            if is_current:
                st.button(f"✓ Current Plan", disabled=True, use_container_width=True, key=f"current_{plan}")
            elif plan == 'free':
                if st.button(f"🔄 Switch to {plan_data['name']}", use_container_width=True, key=f"downgrade_{plan}"):
                    st.session_state['user_plan'] = plan
                    st.success(f"✅ Plan changed to {plan_data['name']}")
                    st.rerun()
            else:
                # Payment button
                if stripe_enabled:
                    if st.button(f"💳 Subscribe - {plan_data.get('price_display', f'${plan_data.get('price', 0):.2f}/month')}", 
                               use_container_width=True, key=f"subscribe_{plan}"):
                        st.session_state['selected_plan'] = plan
                        st.session_state['show_checkout'] = True
                        st.rerun()
                else:
                    # Demo mode without Stripe
                    if st.button(f"🚀 Try {plan_data['name']} (Demo)", use_container_width=True, key=f"demo_{plan}"):
                        st.session_state['user_plan'] = plan
                        st.success(f"✅ Plan updated to {plan_data['name']} (demo mode)")
                        st.rerun()
    
    # Checkout modal
    if st.session_state.get('show_checkout', False):
        selected_plan = st.session_state.get('selected_plan')
        if selected_plan and selected_plan != 'free':
            plan_data = get_plan_limits(selected_plan)
            
            st.markdown("---")
            st.markdown("""
            <div class="premium-card">
                <h2 style='color: #1f2937 !important; margin-top: 0; font-weight: 700;'>Checkout - Subscription</h2>
            </div>
            """, unsafe_allow_html=True)
            
            col_check1, col_check2 = st.columns([2, 1])
            
            with col_check1:
                st.markdown(f"""
                <div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid {plan_data['color']};'>
                    <h3 style='color: #1f2937; margin-top: 0;'>Plan: {plan_data['name']}</h3>
                    <p style='color: #1f2937; font-size: 1.5rem; font-weight: 700;'>{plan_data.get('price_display', f'${plan_data.get('price', 0):.2f}/month')}</p>
                    <p style='color: #666;'>Monthly recurring billing</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Checkout form
                with st.form("checkout_form"):
                    email = st.text_input("Email", placeholder="your@email.com", help="Email for invoice")
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        submit_payment = st.form_submit_button("Proceed to Payment", use_container_width=True, type="primary")
                    with col_btn2:
                        cancel_payment = st.form_submit_button("Cancel", use_container_width=True)
                    
                    if submit_payment:
                        if email and '@' in email:
                            # Create Stripe checkout session
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
                                    st.success("✅ Redirecting to Stripe Checkout...")
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
                                    '>🔒 Go to Secure Stripe Checkout</a>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error(f"❌ Error: {result.get('error', 'Could not create payment session')}")
                            else:
                                st.error(f"❌ Price ID not configured for plan {selected_plan}")
                        else:
                            st.error("❌ Please enter a valid email")
                    
                    if cancel_payment:
                        st.session_state['show_checkout'] = False
                        st.session_state['selected_plan'] = None
                        st.rerun()
            
            with col_check2:
                st.markdown("""
                <div style='background: #f0fdf4; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #10b981;'>
                    <h4 style='color: #1f2937; margin-top: 0;'>🔒 Secure Payment</h4>
                    <p style='color: #1f2937; font-size: 0.9rem;'>
                        Your payments are protected by Stripe, the world's most secure payment processor.
                    </p>
                    <p style='color: #666; font-size: 0.85rem; margin-top: 1rem;'>
                        ✓ Secure payment with SSL<br>
                        ✓ No card data stored<br>
                        ✓ Cancel anytime
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Handle payment callbacks
    query_params = st.query_params
    if 'payment' in query_params:
        if query_params['payment'] == 'success':
            plan = query_params.get('plan', 'basic')
            st.success(f"✅ Payment successful! Your plan has been updated to {get_plan_limits(plan)['name']}")
            st.session_state['user_plan'] = plan
            st.balloons()
        elif query_params['payment'] == 'cancelled':
            st.info("ℹ️ Payment cancelled. No charge was made.")

# Footer con créditos
st.markdown("""
<div style="margin-top: 4rem; padding: 2rem 0; border-top: 1px solid #333; text-align: center;">
    <div style="margin-bottom: 1rem;">
        <h3 style="color: #ffffff; font-size: 1.2rem; margin: 0 0 0.5rem 0;">Trading AI Pro</h3>
        <p style="color: #a0a0a0; font-size: 0.9rem; margin: 0;">Professional Trading System with Artificial Intelligence</p>
    </div>
    <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #2a2a2a;">
        <p style="color: #666; font-size: 0.85rem; margin: 0.5rem 0;">
            Made with ❤️ by <strong style="color: #4a9eff;">marxmad</strong>
        </p>
        <div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 1rem; flex-wrap: wrap;">
            <a href="https://github.com/MarxMad" target="_blank" style="color: #4a9eff; text-decoration: none; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; transition: color 0.3s;">
                <span>🔗</span> GitHub
            </a>
            <a href="https://x.com/gerapedrizco" target="_blank" style="color: #4a9eff; text-decoration: none; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; transition: color 0.3s;">
                <span>🐦</span> X (Twitter)
            </a>
        </div>
        <p style="color: #555; font-size: 0.75rem; margin-top: 1.5rem;">
            © 2024 Trading AI Pro. All rights reserved.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
