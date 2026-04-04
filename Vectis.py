import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Configuración Pro
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# --- BARRA LATERAL: CONFIGURACIÓN Y COMUNIDAD ---
st.sidebar.header("🚀 Comunidad & Apoyo")

# Botón de Telegram (Cámbialo por tu link real)
st.sidebar.markdown("""
<a href="https://t.me/TU_CANAL_DE_TELEGRAM" target="_blank">
    <button style="width:100%; background-color:#0088cc; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">
        📢 Unirse al Telegram Pro
    </button>
</a>
""", unsafe_allow_index=True)

st.sidebar.markdown("---")

# Botón de Donación (PayPal / Ko-fi / BuyMeACoffee)
st.sidebar.markdown("""
<a href="https://www.paypal.me/TU_USUARIO" target="_blank">
    <button style="width:100%; background-color:#ffc439; color:black; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">
        ☕ Invítame a un café (PayPal)
    </button>
</a>
""", unsafe_allow_index=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Configuración de Análisis")
busqueda = st.sidebar.text_input("Jugador (ej: Doncic, Tatum, Wembanyama):")

# Selector de Mercado
mercado = st.sidebar.selectbox("Seleccionar Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado} (Over/Under):", value=1.5 if mercado in ["STL", "BLK"] else 10.5, step=0.5)

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Selecciona el jugador:", nombres)
        player = [p for p in nba_players if p['full_name'] == seleccion][0]
        
        try:
            log = playergamelog.PlayerGameLog(player_id=player['id'], season='2025-26')
            df = log.get_data_frames()[0]
            
            if not df.empty:
                # --- LIMPIEZA DE DATOS (Solo Fecha) ---
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                
                # --- CÁLCULO DE DOBLES Y TRIPLES DOBLES ---
                def check_double_triple(row):
                    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
                    diez_o_mas = sum(1 for x in stats if x >= 10)
                    return "Triple-Double" if diez_o_mas >= 3 else ("Double-Double" if diez_o_mas >= 2 else "-")

                df['SPECIAL'] = df.apply(check_double_triple, axis=1)

                # --- MÉTRICAS PRINCIPALES ---
                ultimos_15 = df.head(15)
                overs = (ultimos_15[mercado] > linea_apuesta).sum()
                dd_count = (df.head(15)['SPECIAL'] != "-").sum()

                col1, col2, col3, col4 = st.columns(4)
                col1.metric(f"Overs {mercado} ({linea_apuesta})", f"{overs}/15")
                col2.metric(f"Promedio {mercado} (L10)", f"{df.head(10)[mercado].mean():.1f}")
                col3.metric("Dobles/Triples (L15)", f"{dd_count}")
                col4.metric(f"Récord {mercado}", f"{df[mercado].max()}")

                st.markdown("---")

                # --- FILTROS ---
                tipo_partido = st.radio("Ubicación:", ["Todos", "Local", "Visitante"], horizontal=True)
                df_final = df.copy()
                if tipo_partido == "Local":
                    df_final = df_final[df_final['MATCHUP'].str.contains('vs.')]
                elif tipo_partido == "Visitante":
                    df_final = df_final[df_final['MATCHUP'].str.contains('@')]

                # --- TABLA CON ESTILO
