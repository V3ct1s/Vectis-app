import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# --- BARRA LATERAL: COMUNIDAD & APOYO ---
st.sidebar.header("🚀 Comunidad & Apoyo")

# Botón de Telegram
st.sidebar.markdown("""
<a href="https://t.me/TU_CANAL_DE_TELEGRAM" target="_blank">
    <button style="width:100%; background-color:#0088cc; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">
        📢 Unirse al Telegram Pro
    </button>
</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Botón de Donación (PayPal)
st.sidebar.markdown("""
<a href="https://www.paypal.me/TU_USUARIO" target="_blank">
    <button style="width:100%; background-color:#ffc439; color:black; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">
        ☕ Invítame a un café (PayPal)
    </button>
</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Configuración de Análisis")
busqueda = st.sidebar.text_input("Jugador (ej: Doncic, Tatum, Wembanyama):")

# Selector de Mercado
mercado = st.sidebar.selectbox("Seleccionar Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado}:", value=1.5 if mercado in ["STL", "BLK"] else 10.5, step=0.5)

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Selecciona el jugador:", nombres)
        player = [p for p in nba_players if p['full_name'] == seleccion][0]
        
        try:
            # Consultar temporada actual
            log = playergamelog.PlayerGameLog(player_id=player['id'], season='2025-26')
            df = log.get_data_frames()[0]
            
            if not df.empty:
                # --- PROCESAMIENTO ---
