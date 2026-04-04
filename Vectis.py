import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, leaguestandings
import pandas as pd

# --- FUNCIONES CORE ---
@st.cache_data(ttl=3600)
def get_nba_standings():
    try:
        standings = leaguestandings.LeagueStandings().get_data_frames()[0]
        dict_standings = {}
        for _, row in standings.iterrows():
            win_pct = row['WinPCT'] * 100
            record = f"{row['Record']} ({win_pct:.1f}%)"
            dict_standings[row['TeamAbbreviation']] = record
        return dict_standings
    except:
        return {}

def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    d10 = sum(1 for x in stats if x >= 10)
    return "TD" if d10 >= 3 else ("DD" if d10 >= 2 else "-")

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")
if 'calculadora' not in st.session_state:
    st.session_state.calculadora = []

n_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}

# --- SIDEBAR (LOS INAMOVIBLES) ---
try: 
    st.sidebar.image("vectis.png", use_container_width=True)
except: 
    st.sidebar.title("VECTIS NBA")

st.sidebar.header("🔍 Buscador de Patrones")
busqueda = st.sidebar.text_input("1. Escribe nombre (ej: Stephen Curry):")
p_obj = None

if busqueda:
    nba_p = players.find_players_by_full_name(busqueda)
    if nba_p:
        nombres = [p['full_name'] for p in nba_p]
        sel = st.sidebar.selectbox("2. Confirma el jugador:", nombres)
        p_obj = next((p for p in nba_p if p['full_name'] == sel), None)

st.sidebar.markdown("---")
m_vis = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
m_real = n_api[m_vis]
l_ap = st.sidebar.select_slider("Línea de valor (Winamax):", options=[x + 0.5 for x in range(0, 55)], value=15.5)

st.sidebar.markdown("---")
st.sidebar.header("🚀 Comunidad")
# RESTAURADOS BOTONES PAYPAL Y TELEGRAM
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café", "https://www.paypal.me/VectisNBA", use_container_width=True)
st.sidebar.info("🛒 [Tienda NBA Amazon](https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21)")

st.sidebar.markdown("---")
# MENSAJE DE PRECAUCIÓN INAMOVIBLE (EL DE LA FOTO)
st.sidebar.caption("⚠️ +18 | Vectis
