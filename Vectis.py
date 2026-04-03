import streamlit as st
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog
import pandas as pd
from datetime import datetime, timedelta

# 1. Configuración Pro
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")
st.markdown("---")

# Barra lateral: Buscador y Filtro de Apuestas
st.sidebar.header("Configuración de Análisis")
busqueda = st.sidebar.text_input("Jugador (ej: Doncic, Tatum, Embiid):")
linea_apuesta = st.sidebar.number_input("Línea de Puntos (Over/Under):", value=25.5, step=0.5)

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
                # --- PROCESAMIENTO DE DATOS ---
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
                # Calcular Back-to-Back (si jugó el día anterior)
                df['FECHA_PREVIA'] = df['GAME_DATE'].shift(-1)
                df['B2B'] = (df['GAME_DATE'] - df['FECHA_PREVIA']).dt.days == 1

                # --- MÉTRICAS DE APUESTAS (OVER/UNDER) ---
                ultimos_15 = df.head(15)
                overs = (ultimos_15['PTS'] > linea_apuesta).sum()
                porcentaje_over = (overs / 15) * 100

                col1, col2, col3 = st.columns(3)
                col1.metric(f"Overs de {linea_apuesta}", f"{overs}/15", f"{porcentaje_over:.0f}% de éxito")
                col2.metric("Promedio PTS (L10)", f"{df.head(10)['PTS'].mean():.1f}")
                col3.metric("Máximo Temporada", f"{df['PTS'].max()} pts")

                st.markdown("---")

                # --- FILTROS AVANZADOS ---
                c1, c2 = st.columns(2)
                with c1:
                    filtro_b2b = st.checkbox("Mostrar solo partidos en Back-to-Back (Cansancio)")
                with c2:
                    tipo_partido = st.radio("Ubicación:", ["Todos", "Local", "Visitante"], horizontal=True)

                # Aplicar Filtros
                df_final = df.copy()
                if filtro_b2b:
                    df_final = df_final[df_final['B2B'] == True]
                if tipo_partido == "Local":
                    df_final = df_final[df_final['MATCHUP'].str.contains('vs.')]
                elif tipo_partido == "Visitante":
                    df_final = df_final[df_final['MATCHUP'].str.contains('@')]

                # --- ESTILO DE TABLA ---
                def style_results(row):
                    # Color para el Over/Under
                    color = 'background-color: #2ecc71; color: white' if row['PTS'] > linea_apuesta else 'background-color: #e74c3c; color: white'
                    # Estilo para Back-to-Back
                    b2b_style = 'font-weight: bold; color: #f39c12' if row['B2B'] else ''
                    return [None, None, None, color, None, None, b2b_style]

                cols_pro = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'B2B']
                display_df = df_final[cols_pro].head(15)
                
                st.subheader(f"Análisis detallado: {player['full_name']}")
                st.table(display_df.style.apply(style_results, axis=1))

                # Gráfico de puntos vs Línea de Apuesta
                chart_data = display_df[['GAME_DATE', 'PTS']].copy()
                chart_data['LINEA'] = linea_apuesta
                st.line_chart(chart_data.set_index('GAME_DATE'))

            else:
                st.warning("No hay partidos registrados este año.")
        except Exception as e:
            st.error(f"Error al conectar con la NBA: {e}")
    else:
        st.error("Jugador no encontrado.")
else:
    st.info("Escribe un nombre en la izquierda para analizar sus rachas.")
