import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES DE CÁLCULO
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

# 2. CONFIGURACIÓN DE INTERFAZ
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.header("🔍 Buscador de Patrones")
busqueda = st.sidebar.text_input("1. Escribe nombre (ej: Luka Doncic):")
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

# Configuración de líneas por defecto
opciones = [x + 0.5 for x in range(0, 55)]
linea_apuesta = st.sidebar.select_slider("Línea de valor (Winamax):", options=opciones, value=15.5)

# --- BANNER AMAZON ESPAÑA (ID: vectis-21) ---
st.sidebar.markdown("---")
st.sidebar.write("### 🇪🇸 Ofertas NBA España")
amazon_es_url = "https://www.amazon.es/gp/browse.html?node=2945785031&tag=vectis-21"
amazon_html = f'<a href="{amazon_es_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #232f3e; padding: 15px; border-radius: 12px; text-align: center; color: white; border: 1px solid #ff9900;"><img src="https://m.media-amazon.com/images/I/71IsS6vS6sL._AC_SX679_.jpg" width="85%" style="border-radius: 5px;"><p style="font-size: 14px; margin: 12px 0 5px 0; font-weight: bold; color: #ff9900;">Equipamiento NBA</p><p style="font-size: 12px; margin: 0 0 10px 0; opacity: 0.9;">Balones y Camisetas</p><div style="background-color: #ff9900; color: black; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 14px;">VER EN AMAZON.ES</div></div></a>'
st.sidebar.markdown(amazon_html, unsafe_allow_html=True)

st.title("🏀 Inteligencia Estadística NBA")

if player_obj:
    try:
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
            promedio_l10 = df.head(10)[mercado_real].mean()
            equipo = df.iloc[0]['TEAM_ABBREVIATION'] if 'TEAM_ABBREVIATION' in df.columns else "N/A"

            # BLOQUE PICK DINÁMICO (PROTEGIDO)
            pick_text = f'<div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #e41b13; margin-bottom: 25px;"><h3 style="color: #e41b13; margin-top: 0;">🔥 ANÁLISIS DINÁMICO</h3><div style="display: flex; justify-content: space-between; align-items: center;"><div><p style="margin-bottom: 5px; font-size: 18px;"><b>{player_obj["full_name"]} | {equipo}</b></p><p style="margin-top: 0; font-size: 16px;">Tendencia L10: {promedio_l10:.1f} {mercado_visual}</p></div><a href="https://www.winamax.es" target="_blank" style="background-color: #e41b13; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;">VER CUOTA</a></div></div>'
            st.markdown(pick_text, unsafe_allow_html=True)

            # ESTADÍSTICAS
            st.subheader(f"Análisis: {player_obj['full_name']} | {equipo}")
            
            u15 = df.head(15)
            overs = (u15[mercado_real] > linea_apuesta).sum()
            prob_dd = ((u15['SPECIAL_TYPE'] == 'DD').sum() / 15) * 100
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric(f"Overs {mercado_visual}", f"{overs}/15", f"{int((overs/15)*100)}% Acierto")
            col_m2.metric("Promedio L10", f"{promedio_l10:.1f}")
            col_m3.metric("DD% (L15)", f"{prob_dd:.1f}%")
            col_m4.metric("Equipo", equipo)
            
            st.markdown("---")
            st.write("### Historial Reciente (L15)")
            df_tabla = df.rename(columns={'STL': 'ROB', 'BLK': 'TAP', 'SPECIAL_TYPE': 'DD/TD'})
            cols_show = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'ROB', 'TAP', 'DD/TD']
            st.dataframe(df_tabla[cols_show].head(15), use_container_width=True)
            st.line_chart(df.head(15).set_index('GAME_DATE')[mercado_real])
        else:
            st.warning("No hay datos disponibles para esta temporada.")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
else:
    welcome_html = '<div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #e41b13; margin-bottom: 25px;"><h3 style="color: #e41b13; margin
