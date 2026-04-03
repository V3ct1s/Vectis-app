import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")
st.markdown("---")

busqueda = st.sidebar.text_input("Escribe el nombre del jugador (ej: Doncic, Curry, Shai):")

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    
    if nba_players:
        # Si hay varios (como los Curry), dejamos que elijas en un desplegable
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Selecciona el jugador exacto:", nombres)
        
        # Filtramos el ID del que has elegido
        player = [p for p in nba_players if p['full_name'] == seleccion][0]
        
        st.subheader(f"Análisis de racha: {player['full_name']}")
        # ... (el resto del código sigue igual)
        st.subheader(f"Análisis de racha: {player['full_name']}")
        try:
            log = playergamelog.PlayerGameLog(player_id=player['id'], season='2025-26')
            df = log.get_data_frames()[0]
            if not df.empty:
                cols_pro = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'FG3M', 'MIN']
                df_display = df[cols_pro].head(10)
                df_display.columns = ['FECHA', 'PARTIDO', 'W/L', 'PTS', 'REB', 'AST', '3P', 'MIN']
                st.table(df_display)
                st.line_chart(df_display.set_index('FECHA')['PTS'])
            else:
                st.warning("No hay partidos registrados esta temporada.")
        except Exception as e:
            st.error("Error al conectar con la API de la NBA.")
    else:
        st.error("Jugador no encontrado.")
else:
    st.info("Escribe un nombre a la izquierda.")