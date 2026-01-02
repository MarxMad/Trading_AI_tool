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
    
    /* Header - Tech Style - Asegurar visibilidad */
    header[data-testid="stHeader"] {
        background: #1a1a1a !important;
        border-bottom: 1px solid #333 !important;
        padding: 1rem 2rem !important;
        visibility: visible !important;
        display: flex !important;
        height: auto !important;
        min-height: 3.5rem !important;
        position: relative !important;
        z-index: 999 !important;
        opacity: 1 !important;
    }
    
    header[data-testid="stHeader"] * {
        visibility: visible !important;
        display: block !important;
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
        background: #10b981;
        border-color: #10b981;
        color: #ffffff;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #059669;
        border-color: #059669;
    }
    
    /* Header personalizado - Estilo Tech */
    .main-header {
        background: #1a1a1a;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #333;
        margin-bottom: 2rem;
        color: #e0e0e0;
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        font-family: 'Inter', 'SF Mono', monospace;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: #a0a0a0;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Badge de plan - Tech Style */
    .plan-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid #333;
        position: relative;
        z-index: 1;
        margin-top: 1rem;
        font-family: 'SF Mono', monospace;
    }
    
    .plan-badge-free {
        background: #1a1a1a;
        color: #a0a0a0;
        border-color: #444;
    }
    
    .plan-badge-basic {
        background: #1a1a1a;
        color: #10b981;
        border-color: #10b981;
    }
    
    .plan-badge-pro {
        background: #1a1a1a;
        color: #f59e0b;
        border-color: #f59e0b;
    }
    
    .plan-badge-enterprise {
        background: #1a1a1a;
        color: #fbbf24;
        border-color: #fbbf24;
    }
    
    /* Cards - Estilo Tech Minimalista */
    .premium-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #333;
        transition: all 0.2s ease;
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
        border-color: #4a9eff;
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.15) 0%, rgba(74, 158, 255, 0.05) 100%);
        box-shadow: 0 8px 32px rgba(74, 158, 255, 0.2);
    }
    
    .trading-level-card.entry:hover {
        box-shadow: 0 12px 40px rgba(74, 158, 255, 0.4);
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
    
    .trading-level-card.entry .price {
        color: #4a9eff;
        text-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
    }
    
    .trading-level-card.stop-loss .price {
        color: #f44336;
        text-shadow: 0 0 20px rgba(244, 67, 54, 0.5);
    }
    
    .trading-level-card.take-profit .price {
        color: #10b981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
    }
    
    /* Asset detection card - Mejorado */
    .asset-card {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.15) 0%, rgba(74, 158, 255, 0.05) 100%);
        border: 2px solid #4a9eff;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(74, 158, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .asset-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(74, 158, 255, 0.3);
    }
    
    .asset-card .symbol {
        color: #4a9eff;
        font-size: 3rem;
        font-weight: 700;
        font-family: 'SF Mono', monospace;
        margin: 0.5rem 0;
        text-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
    }
    
    .asset-card .label {
        color: #a0a0a0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    /* Upload area mejorada */
    .upload-area {
        background: #1a1a1a;
        border: 2px dashed #4a9eff;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        background: rgba(74, 158, 255, 0.05);
        border-color: #6bb6ff;
        transform: scale(1.01);
    }
    
    .upload-area .upload-icon {
        font-size: 4rem;
        color: #4a9eff;
        margin-bottom: 1rem;
    }
    
    .upload-area .upload-text {
        color: #e0e0e0;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .upload-area .upload-hint {
        color: #a0a0a0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
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

components = init_components()

# Obtener plan del usuario
user_plan = get_user_plan()
plan_info = get_plan_limits(user_plan)

# Header tech style
st.markdown(f"""
<div class="main-header">
    <h1>Trading AI Pro</h1>
    <p>Professional Trading System with Artificial Intelligence</p>
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
        ["Image Analysis", "Trading Journal", "Plans & Subscription"],
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

# Main content based on mode
if mode == "Image Analysis":
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
        uploaded_file = st.file_uploader(
            "Upload chart image",
            type=['png', 'jpg', 'jpeg'],
            help="PNG, JPG or JPEG format",
            label_visibility="visible"
        )
        
        # Mostrar header y upload area solo si no hay imagen subida
        if uploaded_file is None:
            # Header mejorado
            st.markdown("""
            <div style="text-align: center; margin-bottom: 3rem;">
                <h1 style="color: #ffffff; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; letter-spacing: -1px;">
                    Chart Analysis
                </h1>
                <p style="color: #a0a0a0; font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                    Upload a trading chart screenshot for AI-powered technical analysis. 
                    Get precise entry, stop loss, and take profit levels automatically.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Upload section mejorada con diseño más atractivo
            st.markdown("""
            <div style="position: relative; margin: 2rem 0;">
                <div class="upload-area" style="position: relative; z-index: 1;">
                    <div style="font-size: 5rem; margin-bottom: 1.5rem;">📈</div>
                    <div class="upload-text" style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">
                        Drag & Drop Your Chart Image
                    </div>
                    <div class="upload-hint" style="font-size: 0.95rem;">
                        PNG, JPG or JPEG • Max 200MB
                    </div>
                    <div style="margin-top: 1.5rem; color: #4a9eff; font-size: 0.85rem;">
                        Or click to browse files
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Success message
            st.markdown("""
            <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(74, 158, 255, 0.05) 100%); border-radius: 12px; border-left: 4px solid #4a9eff;">
                <h3 style="color: #4a9eff; margin: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">✓</span> Chart Uploaded Successfully
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Show image preview mejorado
            col_img, col_info = st.columns([2, 1])
            with col_img:
                st.markdown("""
                <div style="background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                    <h4 style="color: #ffffff; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600;">Chart Preview</h4>
                </div>
                """, unsafe_allow_html=True)
                st.image(image, use_container_width=True)
            
            with col_info:
                st.markdown("""
                <div class="chat-message user" style="margin-bottom: 1.5rem;">
                    <h3>Trade Information</h3>
                    <p style="font-size: 0.85rem; color: #a0a0a0; margin-top: 0.5rem; line-height: 1.5;">
                        Configure your trade before analysis
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Position type selector - IMPORTANTE
                position_type = st.selectbox(
                    "Position Type",
                    ["Long", "Short"],
                    label_visibility="visible",
                    help="Select if this is a Long (buy) or Short (sell) position",
                    index=0
                )
                
                # Margin mode selector for futures
                margin_mode = st.selectbox(
                    "Margin Mode",
                    ["Cross Margin", "Isolated Margin"],
                    label_visibility="visible",
                    help="Cross Margin: Uses entire account balance. Isolated Margin: Uses only allocated margin for this position",
                    index=0
                )
                
                # Leverage selector
                leverage = st.selectbox(
                    "Leverage",
                    ["1x", "2x", "3x", "5x", "10x", "20x", "25x", "50x", "100x"],
                    label_visibility="visible",
                    help="Leverage multiplier. Higher leverage = higher risk. AI will adjust stop loss and take profit accordingly",
                    index=0
                )
                
                symbol = st.text_input(
                    "Symbol", 
                    placeholder="BTC/USDT, AAPL, EUR/USD",
                    label_visibility="visible",
                    help="Asset symbol (will be auto-detected if empty)"
                )
                strategy = st.text_input(
                    "Strategy", 
                    placeholder="Breakout, Reversal, Trend",
                    label_visibility="visible",
                    help="Trading strategy type"
                )
                notes = st.text_area(
                    "Notes", 
                    placeholder="Additional observations...",
                    height=80,
                    label_visibility="visible",
                    help="Any additional notes about this trade"
                )
            
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
            
            # Analyze button mejorado
            st.markdown("""
            <div style="margin: 2rem 0;">
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Analyze Chart with AI", type="primary", use_container_width=True):
                with st.spinner("Analyzing chart with AI..."):
                    # Extraer valor numérico del leverage (ej: "10x" -> 10)
                    leverage_value = int(leverage.replace('x', ''))
                    
                    # Pasar el tipo de posición, margin mode y leverage al análisis
                    analysis = components['image_analyzer'].analyze_chart_image(
                        image, 
                        symbol if symbol else None, 
                        position_type.lower(),
                        margin_mode.lower().replace(' ', '_'),
                        leverage_value
                    )
                    
                    # Incrementar contador
                    st.session_state['analyses_today'] = analyses_today + 1
                    
                    # Detectar símbolo (del análisis o del input)
                    detected_symbol = analysis.get('symbol_detected', symbol if symbol else 'N/A')
                    if detected_symbol and detected_symbol != 'N/A':
                        # Actualizar el input con el símbolo detectado
                        symbol = detected_symbol
                    
                    # Obtener tipo de posición, margin mode y leverage del análisis
                    analysis_position = analysis.get('position_type', position_type).upper()
                    analysis_margin = analysis.get('margin_mode', margin_mode.lower().replace(' ', '_'))
                    analysis_leverage = analysis.get('leverage', leverage_value)
                    position_color = "#10b981" if analysis_position == "LONG" else "#f44336"
                    position_icon = "📈" if analysis_position == "LONG" else "📉"
                    
                    # Mostrar activo, posición, margin y leverage de forma prominente
                    col_asset, col_pos, col_margin = st.columns([2, 1, 1])
                    with col_asset:
                        st.markdown(f"""
                        <div class="asset-card">
                            <div class="label">Asset Detected</div>
                            <div class="symbol">{detected_symbol if detected_symbol != 'N/A' else 'Unknown'}</div>
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
                        st.markdown(f"""
                        <div class="chat-message assistant" style="text-align: center;">
                            <h3>Current Price</h3>
                            <p style="font-size: 1.5rem; color: #4a9eff; font-weight: 700; font-family: 'SF Mono', monospace;">${current_price:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Trading Levels con cards gráficas y colores
                    st.markdown("""
                    <div style="text-align: center; margin: 3rem 0 2rem 0;">
                        <h2 style="color: #ffffff; font-size: 2rem; font-weight: 700; margin: 0;">
                            Trading Levels
                        </h2>
                        <p style="color: #a0a0a0; font-size: 0.95rem; margin-top: 0.5rem;">
                            AI-generated entry, stop loss, and take profit levels
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_entry, col_stop, col_take = st.columns(3)
                    
                    with col_entry:
                        st.markdown(f"""
                        <div class="trading-level-card entry">
                            <div class="label">Entry Price</div>
                            <div class="price">${analysis['entry_price']:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_stop:
                        st.markdown(f"""
                        <div class="trading-level-card stop-loss">
                            <div class="label">Stop Loss</div>
                            <div class="price">${analysis['stop_loss']:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_take:
                        st.markdown(f"""
                        <div class="trading-level-card take-profit">
                            <div class="label">Take Profit</div>
                            <div class="price">${analysis['take_profit']:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Métricas adicionales
                    st.markdown("---")
                    col_conf, col_rr = st.columns(2)
                    
                    with col_conf:
                        confidence_pct = analysis['confidence'] * 100
                        conf_color = "#10b981" if confidence_pct > 70 else "#f59e0b" if confidence_pct > 50 else "#f44336"
                        st.markdown(f"""
                        <div class="chat-message assistant" style="text-align: center;">
                            <h3>Confidence</h3>
                            <p style="font-size: 1.8rem; color: {conf_color}; font-weight: 700;">{confidence_pct:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_rr:
                        rr_ratio = analysis.get('risk_reward_ratio', 0)
                        rr_color = "#10b981" if rr_ratio >= 2 else "#f59e0b" if rr_ratio >= 1.5 else "#f44336"
                        st.markdown(f"""
                        <div class="chat-message assistant" style="text-align: center;">
                            <h3>Risk:Reward</h3>
                            <p style="font-size: 1.8rem; color: {rr_color}; font-weight: 700;">1:{rr_ratio:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Pattern y análisis detallado
                    st.markdown("---")
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <h3>Pattern Detected</h3>
                        <p><span class="value">{analysis['pattern_detected']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <h3>Detailed Analysis</h3>
                        <p>{analysis['analysis']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Guardar en sesión para registro
                    st.session_state['last_analysis'] = {
                        'analysis': analysis,
                        'symbol': symbol,
                        'strategy': strategy,
                        'notes': notes,
                        'image': uploaded_file,
                        'position_type': position_type
                    }
                    
                    # Register trade button
                    if st.button("Register Trade", use_container_width=True, type="primary"):
                        if 'last_analysis' in st.session_state:
                            analysis_data = st.session_state['last_analysis']
                            analysis = analysis_data['analysis']
                            
                            # Usar el tipo de posición del análisis
                            side = analysis_data.get('position_type', 'long').lower()
                            
                            # Calcular cantidad basada en riesgo
                            entry = analysis['entry_price']
                            stop = analysis['stop_loss']
                            risk_amount = components['risk_manager'].current_capital * 0.02
                            quantity = components['risk_manager'].calculate_position_size(entry, stop, risk_amount)
                            
                            trade_id = components['journal'].add_trade(
                                symbol=analysis_data['symbol'] or "N/A",
                                side=side,
                                entry_price=entry,
                                quantity=quantity,
                                stop_loss=stop,
                                take_profit=analysis['take_profit'],
                                strategy=analysis_data['strategy'],
                                notes=analysis_data['notes'],
                                image_analysis=analysis
                            )
                            
                            st.markdown(f"""
                            <div class="chat-message assistant" style="background: rgba(16, 185, 129, 0.1); border-left-color: #10b981;">
                                <h3>Trade Registered</h3>
                                <p>Trade ID: <span class="value">{trade_id}</span></p>
                                <p style="margin-top: 0.5rem; color: #a0a0a0; font-size: 0.9rem;">Trade successfully saved to your journal</p>
                            </div>
                            """, unsafe_allow_html=True)
                            del st.session_state['last_analysis']
        
        # Show plan usage
        if plan_info['analyses_per_day'] > 0:
            remaining = plan_info['analyses_per_day'] - analyses_today
            st.markdown(f"""
            <div class="chat-message assistant" style="opacity: 0.7;">
                <p style="font-size: 0.85rem;">Analyses remaining today: {remaining} of {plan_info['analyses_per_day']}</p>
            </div>
            """, unsafe_allow_html=True)

elif mode == "Trading Journal":
    st.markdown("""
    <div class="premium-card">
        <h2 style='color: #1e3c72; margin-top: 0;'>Trading Journal</h2>
        <p style='color: #666;'>Manage and analyze all your trading operations professionally</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Improved filters
    st.markdown("### Search Filters")
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_symbol = st.selectbox(
            "Symbol",
            ["All"] + list(set(t['symbol'] for t in components['journal'].trades)),
            help="Filter by asset symbol"
        )
    with col2:
        filter_status = st.selectbox(
            "Status",
            ["All", "open", "closed", "cancelled"],
            help="Filter by trade status"
        )
    with col3:
        show_stats = st.checkbox("Show Statistics", value=True)
    
    # Get filtered trades
    trades = components['journal'].get_trades(
        symbol=None if filter_symbol == "All" else filter_symbol,
        status=None if filter_status == "All" else filter_status
    )
    
    if show_stats:
        stats = components['journal'].get_statistics()
        
        st.markdown("### General Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total", stats['total_trades'])
        with col2:
            st.metric("Open", stats['open_trades'])
        with col3:
            st.metric("Closed", stats['closed_trades'])
        with col4:
            win_color = "🟢" if stats['win_rate'] > 50 else "🟡" if stats['win_rate'] > 30 else "🔴"
            st.metric("Win Rate", f"{win_color} {stats['win_rate']:.1f}%")
        with col5:
            pnl_color = "🟢" if stats['total_pnl'] > 0 else "🔴" if stats['total_pnl'] < 0 else "⚪"
            st.metric("Total P&L", f"{pnl_color} ${stats['total_pnl']:,.2f}", 
                     delta=f"{stats['total_pnl']:+,.2f}" if stats['total_pnl'] != 0 else None)
        
        st.markdown("---")
    
    # Improved trades table
    if trades:
        st.markdown("### Trades List")
        # Prepare data for table
        table_data = []
        for trade in trades:
            status_emoji = "🟢" if trade['status'] == 'open' else "✅" if trade['status'] == 'closed' else "❌"
            table_data.append({
                'ID': trade['id'],
                'Symbol': trade['symbol'],
                'Side': '📈 Long' if trade['side'] == 'long' else '📉 Short',
                'Entry': f"${trade['entry_price']:,.2f}",
                'Quantity': f"{trade['quantity']:.4f}",
                'Stop Loss': f"${trade['stop_loss']:,.2f}" if trade['stop_loss'] else "N/A",
                'Take Profit': f"${trade['take_profit']:,.2f}" if trade['take_profit'] else "N/A",
                'Status': f"{status_emoji} {trade['status'].title()}",
                'P&L': f"${trade['pnl']:,.2f}" if trade['pnl'] is not None else "N/A",
                'Date': datetime.fromisoformat(trade['entry_time']).strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Selected trade details
        if len(trades) > 0:
            st.markdown("### Selected Trade Details")
            selected_id = st.selectbox(
                "Select a trade to view full details",
                [t['id'] for t in trades],
                label_visibility="visible"
            )
            
            selected_trade = next(t for t in trades if t['id'] == selected_id)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### General Information")
                st.json(selected_trade, expanded=True)
            with col2:
                if selected_trade.get('image_analysis'):
                    st.markdown("#### Image Analysis")
                    st.json(selected_trade['image_analysis'], expanded=True)
    else:
        st.info("""
        **No trades registered yet**
        
        Use the **"Image Analysis"** section to create your first trade.
        """)

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

# Improved premium footer
st.markdown("""
<div class="footer-premium">
    <h3>Trading AI Pro</h3>
    <p>Professional Trading System with Artificial Intelligence</p>
    <p style='font-size: 0.9rem; color: rgba(255,255,255,0.8);'>
        Developed for professional traders | Premium Version 2024
    </p>
    <p style='font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 1rem;'>
        © 2024 Trading AI Pro. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)
