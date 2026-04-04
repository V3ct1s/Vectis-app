import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES AUXILIARES
def check_double_triple(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "Triple-Double"
    if diez_o_mas >= 2: return "Double-Double"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# --- BARRA LATERAL ---
st.sidebar.header("🚀 Mi Comunidad")

# Botones de contacto
st.sidebar.markdown("""<a href="https://t.me/+FWyCJmqSojVhMjVk" target="_blank"><button style="width:100%; background-color:#0088cc; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">📢 Telegram Pro</button></a>""", unsafe_allow_html=True)
st.sidebar.markdown("""<a href="https://www.paypal.me/VectisNBA" target="_blank"><button style="width:100%; background-color:#ffc439; color:#003087; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">☕ Invítame a un café</button></a>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Análisis")
busqueda = st.sidebar.text_input("Buscar Jugador:")
mercado = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado}:", value=10.5, step=0.5)

# --- BLOQUE LEGAL (Para revisión de Winamax) ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center; background-color:#f9f9f9; padding:10px; border-radius:10px; border: 1px solid #eee;">
    <p style="font-size:11px; font-weight:bold; color:#444;">CONTENIDO +18</p>
    <img src="https://www.jugarbien.es/sites/default/files/images/logotipos/logo_18.png" width="30">
    <img src="https://www.jugarbien.es/sites/default/files/images/logotipos/logo_jugarbien.png" width="80" style="margin-left:10px;">
    <p style="font-size:10px; color:#777; margin-top:10px;">Juega con responsabilidad. Los datos son informativos.</p>
</div>
""", unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
if busqueda:
    nba_players = players.find_players_by_full_name
