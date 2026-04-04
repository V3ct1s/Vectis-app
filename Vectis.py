import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES AUXILIARES
def check_special_stats(row):
    """Retorna si es Triple-Doble, Doble-Doble o nada"""
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
linea_apuesta = st.sidebar.number_input("Línea de valor:", value=10.5, step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("🚀 Comunidad")
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café (PayPal)", "https://www.paypal.me/VectisNBA", use_container_width=True)

# 3. CUERPO PRINCIPAL
st.title("🏀 Inteligencia Estadística NBA")

if player_obj:
    try:
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            # Extracción de equipo
            abreviatura_equipo = ""
            if 'TEAM_ABBREVIATION' in df.columns:
                abreviatura_equipo = df.iloc[0]['TEAM_ABBREVIATION']
            elif 'MATCHUP' in df.columns:
                abreviatura_equipo = df.iloc[0]['MATCHUP'].split(' ')[0]
            
            suffix_equipo = f" | {abreviatura_equipo}" if abreviatura_equipo else ""
            
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            # Aplicamos la lógica DD/TD
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)

            st.subheader(f"Análisis detallado: {player_obj['full_name']}{suffix_equipo}")
            
            # Cálculos sobre los últimos 15 partidos (L15)
            u15 = df.head(15)
            total_u15 = len(u15)
            overs = (u15[mercado_real] > linea_apuesta).sum()
            
            # Cálculo de porcentajes DD y TD
            count_dd = (u15['SPECIAL_TYPE'] == 'DD').sum()
            count_td = (u15['SPECIAL_TYPE'] == 'TD').sum()
            
            # El Triple-Doble también cuenta como Doble-Doble estadísticamente en la mayoría de sitios
            # pero aquí los separamos para mayor claridad.
            prob_dd = (count_dd / total_u15) * 100
            prob_td = (count_td / total_u15) * 100
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"Overs {mercado_visual}", f"{overs}/{total_u15}", f"{int((overs/total_u15)*100)}% Acierto")
            m2.metric("Promedio L10", f"{df.head(10)[mercado_real].mean():.1f}")
            m3.metric("DD% (L15)", f"{prob_dd:.1f}%", f"{count_dd} veces")
            m4.metric("TD% (L15)", f"{prob_td:.1f}%", f"{count_td} veces")

            st.markdown("---")
            
            st.write("### Historial Reciente (Últimos 15)")
            # Traducimos para la tabla
            df_tabla = df.rename(columns={'STL': 'ROB', 'BLK': 'TAP', 'SPECIAL_TYPE': 'DD/TD'})
            cols_tabla = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'ROB', 'TAP', 'DD/TD']
            
            st.table(df_tabla[cols_tabla].head(15).style.map(lambda x: color_mercado(x, linea_apuesta), subset=[mercado_visual]))
            
            st.line_chart(df.head(15).set_index('GAME_DATE')[mercado_real])
        else:
            st.warning("Sin datos para la temporada 2025-26.")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Introduce un jugador en el buscador lateral.")

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Solo mayores de 18 años. Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")
