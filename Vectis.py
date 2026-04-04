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
st.sidebar.header("🔍 Buscador")

busqueda = st.sidebar.text_input("Escribe el nombre (ej: Stephen Curry):")
player_obj = None

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Confirma el jugador:", nombres)
        player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)
    else:
        st.sidebar.error("Jugador no encontrado.")

st.sidebar.markdown("---")

# PASO 3: Slider Inteligente (Solo valores .5 como Winamax)
mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
mercado_real = nombres_api[mercado_visual]

# Definimos los rangos de .5 en .5
if mercado_visual == "PTS":
    opciones = [x + 0.5 for x in range(5, 51)] # 5.5, 6.5 ... 50.5
    idx_default = 15 # Empieza en 20.5
elif mercado_visual == "REB":
    opciones = [x + 0.5 for x in range(1, 21)] # 1.5, 2.5 ... 20.5
    idx_default = 7 # Empieza en 8.5
elif mercado_visual == "AST":
    opciones = [x + 0.5 for x in range(0, 19)] # 0.5, 1.5 ... 18.5
    idx_default = 5 # Empieza en 5.5
else: # ROB y TAP
    opciones = [x + 0.5 for x in range(0, 8)] # 0.5, 1.5 ... 7.5
    idx_default = 1 # Empieza en 1.5

# Usamos select_slider para forzar que solo elija valores de la lista .5
linea_apuesta = st.sidebar.select_slider(
    "Línea de valor (Winamax):",
    options=opciones,
    value=opciones[idx_default],
    help="Solo valores .5 para evitar empates, tal y como en la mayoria de las casas de apuestas."
)

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
            equipo_str = ""
            if 'TEAM_ABBREVIATION' in df.columns:
                equipo_str = f" | {df.iloc[0]['TEAM_ABBREVIATION']}"
            elif 'MATCHUP' in df.columns:
                equipo_str = f" | {df.iloc[0]['MATCHUP'].split(' ')[0]}"
            
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)

            st.subheader(f"Análisis detallado: {player_obj['full_name']}{equipo_str}")
            
            u15 = df.head(15)
            total_partidos = len(u15)
            overs = (u15[mercado_real] > linea_apuesta).sum()
            
            prob_dd = ((u15['SPECIAL_TYPE'] == 'DD').sum() / total_partidos) * 100
            prob_td = ((u15['SPECIAL_TYPE'] == 'TD').sum() / total_partidos) * 100
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"Overs {mercado_visual}", f"{overs}/{total_partidos}", f"{int((overs/total_partidos)*100)}% Acierto")
            m2.metric("Promedio L10", f"{df.head(10)[mercado_real].mean():.1f}")
            m3.metric("DD% (L15)", f"{prob_dd:.1f}%")
            m4.metric("TD% (L15)", f"{prob_td:.1f}%")

            st.markdown("---")
            
            st.write("### Historial Reciente (Últimos 15)")
            df_tabla = df.rename(columns={'STL': 'ROB', 'BLK': 'TAP', 'SPECIAL_TYPE': 'DD/TD'})
            cols_tabla = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'ROB', 'TAP', 'DD/TD']
            
            st.table(df_tabla[cols_tabla].head(15).style.map(lambda x: color_mercado(x, linea_apuesta), subset=[mercado_visual]))
            st.line_chart(df.head(15).set_index('GAME_DATE')[mercado_real])
        else:
            st.warning("No hay datos disponibles para la temporada actual.")
            
    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")
else:
    st.info("Utiliza el buscador lateral para seleccionar un jugador.")

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Solo mayores de 18 años. Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")
