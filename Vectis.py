import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES LÓGICAS (IDENTACIÓN ESTRICTA)
def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "TD"
    if diez_o_mas >= 2: return "DD"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

nombres_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}

# 2. CONFIGURACIÓN DE LA PÁGINA (ESTILO APP)
st.set_page_config(page_title="Vectis NBA", layout="wide")

# --- BARRA LATERAL (MENÚ DE LA APP) ---
try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.header("🔍 Buscador de Jugadores")
busqueda = st.sidebar.text_input("Escribe un nombre (ej: Curry):")
player_obj = None

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Confirma el jugador:", nombres)
        player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)

st.sidebar.markdown("---")
mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
mercado_real = nombres_api[mercado_visual]
linea_apuesta = st.sidebar.number_input("Línea Winamax:", value=15.5, step=1.0)

# --- BANNER AMAZON ESPAÑA (ID: vectis-21) ---
st.sidebar.markdown("---")
st.sidebar.write("### 🇪🇸 Ofertas NBA España")
amazon_es_url = "https://www.amazon.es/gp/browse.html?node=2945785031&tag=vectis-21"
amazon_html = f'''
<a href="{amazon_es_url}" target="_blank" style="text-decoration: none;">
    <div style="background-color: #232f3e; padding: 15px; border-radius: 12px; text-align: center; color: white; border: 1px solid #ff9900;">
        <img src="https://m.media-amazon.com/images/I/71IsS6vS6sL._AC_SX679_.jpg" width="85%" style="border-radius: 5px;">
        <p style="font-size: 14px; margin: 12px 0 5px 0; font-weight: bold; color: #ff9900;">Equipamiento NBA</p>
        <p style="font-size: 12px; margin: 0 0 10px 0; opacity: 0.9;">Balones, Camisetas y Accesorios</p>
        <div style="background-color: #ff9900; color: black; padding: 10px; border-radius: 8px; font-weight: bold; font
