import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES
def check_double_triple(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "Triple-Double"
    if diez_o_mas >= 2: return "Double-Double"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# 2. CONFIGURACIÓN
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# --- BARRA LATERAL ---
st.sidebar.header("🚀 Mi Comunidad")

# BOTÓN TELEGRAM
st.sidebar.markdown("""<a href="https://t.me/+FWyCJmqSojVhMjVk" target="_blank"><button style="width:100%; background-color:#0088cc; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">📢 Unirse al Telegram Pro</button></a>""", unsafe_allow_html=True)

# BOTÓN PAYPAL
st.sidebar.markdown("""<a href="https://www.paypal.me/VectisNBA" target="_blank"><button style="width:100%; background-color:#ffc439; color:#003087; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">☕ Invítame a un café (PayPal)</button></a>""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# SECCIÓN DE ESTADO (En lugar del bono de Winamax)
st.sidebar.success("✅ Herramienta de Análisis Estadístico Activa")
st.sidebar.write("Datos actualizados de la API oficial de la NBA.")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Análisis de Jugador")
busqueda = st.sidebar.text_input("Buscar Jugador (ej: Doncic):")
mercado = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado}:", value=10.5, step=0.5)

# --- AVISOS LEGALES Y JUEGO RESPONSABLE (CLAVE PARA AFILIACIÓN) ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center; background-color:#f0f2f6; padding:10px; border-radius:10px; border: 1px solid #ddd;">
    <p style="font-size:11px; font-weight:bold; color:#333; margin-bottom:5px;">CONTENIDO PARA +18 AÑOS</p>
    <div style="display:flex; justify-content:center; gap:10px; margin-bottom:10px;">
        <img src="https://www.jugarbien.es/sites/default/files/images/logotipos/logo_18.png" width="35">
        <img src="https://www.jugarbien.es/sites/default/files/images/logotipos/logo_jugarbien.png" width="85">
    </div>
    <p style="font-size:10px; color:#666; line-height:1.2;">
        VectisNBA es una plataforma informativa de estadísticas. El juego debe ser una forma de ocio, no una fuente de ingresos.
    </p>
    <p style="font-size:10px; font-weight:bold; color:#e74c3c; margin-top:5px;">SIN DIVERSIÓN NO HAY JUEGO</p>
</div>
""", unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        player = [p for p in nba_players if p['full_name'] == st.sidebar.selectbox("Selecciona:", [p['full_name'] for p in nba_players])][0]
        try:
            log = playergamelog.PlayerGameLog(player_id=player['id'], season='2025-26')
            df = log.get_data_frames()[0]
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL'] = df.apply(check_double_triple, axis=1)
                st.subheader(f"Dashboard: {player['full_name']}")
                u15 = df.head(15)
                overs = (u
