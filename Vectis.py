import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Configuración Pro
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# Barra lateral: Configuración
st.sidebar.header("Configuración de Análisis")
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
                # Un doble-doble es 10+ en al menos dos de estas categorías
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

                # --- TABLA CON ESTILO ---
                def style_results(row):
                    # Color basado en el mercado seleccionado
                    color = 'background-color: #2ecc71; color: white' if row[mercado] > linea_apuesta else 'background-color: #e74c3c; color: white'
                    # Resaltar si hizo Doble o Triple Doble
                    sp_style = 'font-weight: bold; color: #f39c12' if row['SPECIAL'] != "-" else ''
                    return [None, None, None, 
                            color if mercado == "PTS" else '', 
                            color if mercado == "REB" else '', 
                            color if mercado == "AST" else '', 
                            color if mercado == "STL" else '', 
                            color if mercado == "BLK" else '', 
                            sp_style]

                cols_pro = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'SPECIAL']
                display_df = df_final[cols_pro].head(15)
                
                st.subheader(f"Historial detallado: {player['full_name']}")
                st.table(display_df.style.apply(style_results, axis=1))

                # Gráfico dinámico según mercado
                st.line_chart(display_df.set_index('GAME_DATE')[mercado])

            else:
                st.warning("No hay datos este año.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Jugador no encontrado.")
else:
    st.info("Escribe un nombre a la izquierda.")
