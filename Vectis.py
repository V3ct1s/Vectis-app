import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
import pandas as pd
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

# --- FUNCIONES CON CACHÉ PARA EVITAR EL "READ TIMEOUT" ---
@st.cache_data(ttl=7200)  # Guarda los datos 2 horas
def get_player_logs(p_id):
    # Reintento simple si falla la conexión
    for _ in range(2):
        try:
            log = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', timeout=60)
            return log.get_data_frames()[0]
        except:
            time.sleep(1)
    return pd.DataFrame()

@st.cache_data(ttl=86400) # Guarda el equipo 24 horas
def get_team_abr(p_id):
    try:
        info = commonplayerinfo.CommonPlayerInfo(player_id=p_id, timeout=60)
        return info.get_data_frames()[0].iloc[0]['TEAM_ABBREVIATION']
    except:
        return "NBA"

def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "TD"
    if diez_o_mas >= 2: return "DD"
    return "-"

# --- INTERFAZ LATERAL ---
try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.header("🔍 Buscador de Patrones")
busqueda = st.sidebar.text_input("1. Escribe nombre:")

player_obj = None
if busqueda and len(busqueda) > 3:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        # Simplificamos el desplegable para evitar llamadas masivas a la API
        opciones = {p['full_name']: p for p in nba_players[:5]}
        seleccion = st.sidebar.selectbox("2. Confirma el jugador:", list(opciones.keys()))
        player_obj = opciones[seleccion]

st.sidebar.markdown("---")
mercado_visual = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "ROB", "TAP"])
nombres_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}
linea_apuesta = st.sidebar.select_slider("Línea:", options=[x + 0.5 for x in range(0, 55)], value=15.5)

# --- ENLACE AMAZON (vectis-21) ---
st.sidebar.markdown("---")
url_amz = "https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21"
st.sidebar.info(f"🛒 [Tienda NBA Amazon.es]({url_amz})")

# --- CUERPO PRINCIPAL ---
st.title("🏀 Inteligencia Estadística NBA")

if player_obj:
    with st.spinner('Consultando base de datos de la NBA...'):
        df = get_player_logs(player_obj['id'])
        equipo_abr = get_team_abr(player_obj['id'])
        nombre_display = f"{player_obj['full_name']} | {equipo_abr}"

        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
            
            # Cálculo de tendencia
            val_mercado = nombres_api[mercado_visual]
            promedio_l10 = df.head(10)[val_mercado].mean()

            # Banner Análisis
            st.markdown(f'<div style="background-color:#1e1e1e;padding:20px;border-radius:15px;border:1px solid #e41b13;margin-bottom:25px;"><h3 style="color:#e41b13;margin-top:0;">🔥 ANÁLISIS DINÁMICO</h3><div style="display:flex;justify-content:space-between;align-items:center;"><div><p style="font-size:18px;"><b>{nombre_display}</b></p><p>Tendencia L10: {promedio_l10:.1f} {mercado_visual}</p></div><a href="https://www.winamax.es" target="_blank" style="background-color:#e41b13;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;font-weight:bold;">VER CUOTA</a></div></div>', unsafe_allow_html=True)

            # Métricas
            col1, col2, col3 = st.columns(3)
            overs = (df.head(15)[val_mercado] > linea_apuesta).sum()
            col1.metric(f"Overs {mercado_visual}", f"{overs}/15")
            col2.metric("Promedio L10", f"{promedio_l10:.1f}")
            col3.metric("Equipo", equipo_abr)

            # Gráfico
            st.line_chart(df.head(15).set_index('GAME_DATE')[val_mercado])
            
            # Historial
            st.write("### Últimos partidos")
            st.dataframe(df.head(15)[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'STL', 'BLK']], use_container_width=True)
        else:
            st.error("La NBA no ha respondido a tiempo. Por favor, intenta refrescar la página en unos segundos.")
else:
    st.info("Escribe el nombre de un jugador en el buscador para analizar sus estadísticas.")

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ +18 | Vectis Analytics")
