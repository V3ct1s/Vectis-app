import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES AUXILIARES
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

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

# --- BARRA LATERAL ---
try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Buscador de Patrones")

busqueda = st.sidebar.text_input("1. Escribe nombre (ej: Stephen Curry):")
player_obj = None

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("2. Confirma el jugador:", nombres)
        player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)
    else:
        st.sidebar.error("Jugador no encontrado.")

st.sidebar.markdown("---")

mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
mercado_real = nombres_api[mercado_visual]

if mercado_visual == "PTS":
    opciones = [x + 0.5 for x in range(5, 51)]
    idx_default = 15
elif mercado_visual == "REB":
    opciones = [x + 0.5 for x in range(1, 21)]
    idx_default = 7
elif mercado_visual == "AST":
    opciones = [x + 0.5 for x in range(0, 19)]
    idx_default = 5
else:
    opciones = [x + 0.5 for x in range(0, 8)]
    idx_default = 1

linea_apuesta = st.sidebar.select_slider("Línea de valor (Winamax):", options=opciones, value=opciones[idx_default])

st.sidebar.markdown("---")
st.sidebar.header("🚀 Comunidad")
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café", "https://www.paypal.me/VectisNBA", use_container_width=True)

# 3. CUERPO PRINCIPAL
st.title("🏀 Inteligencia Estadística NBA")

# Lógica de Datos y Pick Dinámico
if player_obj:
    try:
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
            promedio_l10 = df.head(10)[mercado_real].mean()

            # --- Cuadro Pick Dinámico Automático ---
            st.markdown(f"""
                <div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #e41b13; margin-bottom: 25px;">
                    <h3 style="color: #e41b13; margin-top: 0;">🔥 ANÁLISIS DINÁMICO (Winamax)</h3>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="margin-bottom: 5px; font-size: 18px;"><b>Basado en búsqueda:</b> {player_obj['full_name']}</p>
                            <p style="margin-top: 0; font-size: 16px;"><b>Tendencia L10:</b> Promediando {promedio_l10:.1f} en {mercado_visual}</
