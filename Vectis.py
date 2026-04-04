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

# BANNER WINAMAX
st.sidebar.markdown("""<div style="background-color:#1a1a1a; padding:20px; border-radius:12px; border: 2px solid #e74c3c; text-align:center;"><h3 style="color:white; margin:0; font-size:18px;">🔴 BONO WINAMAX</h3><p style="color:#ffffff; font-size:13px; margin:10px 0;">¡Duplica tu primer depósito para apostar en la NBA!</p><a href="TU_LINK_AQUI" target="_blank"><button style="width:100%; background-color:#e74c3c; color:white; border:none; padding:12px; border-radius:6px; cursor:pointer; font-weight:bold; font-size:15px;">👉 REGISTRARSE AQUÍ</button></a><p style="color:#888888; font-size:9px; margin-top:12px;">Solo nuevos usuarios. +18 Juega con responsabilidad.</p></div>""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Análisis")
busqueda = st.sidebar.text_input("Buscar Jugador:")
mercado = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado}:", value=10.5, step=0.5)

# PIE LEGAL
st.sidebar.markdown("---")
st.sidebar.markdown("""<div style="text-align:center; opacity:0.8;"><img src="https://www.jugarbien.es/sites/default/files/images/logotipos/logo_18.png" width="30" style="margin-right:10px;"><img src="https://www.jugarbien.es/sites/default/files/images/logotipos/logo_jugarbien.png" width="80"><p style="font-size:10px; color:#666; margin-top:10px;">VectisNBA es un portal estadístico. Juega con responsabilidad.</p></div>""", unsafe_allow_html=True)

# 3. DATOS
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
                overs = (u15[mercado] > linea_apuesta).sum()
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Overs {mercado}", f"{overs}/15", f"{int((overs/15)*100)}% Win Rate")
                c2.metric("Promedio L10", f"{df.head(10)[mercado].mean():.1f}")
                c3.metric("D-D / T-D (L15)", f"{(u15['SPECIAL'] != '-').sum()}")
                c4.metric("Máximo", f"{df[mercado].max()}")
                st.table(df[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'SPECIAL']].head(15).style.applymap(lambda x: color_mercado(x, linea_apuesta), subset=[mercado]))
                st.line_chart(df.head(15).set_index('GAME_DATE')[mercado])
        except Exception as e: st.error(f"Error: {e}")
