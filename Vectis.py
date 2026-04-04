import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
import pandas as pd

# 1. FUNCIONES DE LÓGICA
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

# 2. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

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
        opciones_busqueda = []
        mapping_jugadores = {}
        for p in nba_players[:5]: # Limitamos a 5 para mayor velocidad
            try:
                p_info = commonplayerinfo.CommonPlayerInfo(player_id=p['id']).get_data_frames()[0]
                team = p_info.iloc[0]['TEAM_ABBREVIATION'] or "NBA"
            except:
                team = "NBA"
            label = f"{p['full_name']} ({team})"
            opciones_busqueda.append(label)
            mapping_jugadores[label] = p
        
        seleccion_label = st.sidebar.selectbox("2. Confirma el jugador:", opciones_busqueda)
        player_obj = mapping_jugadores[seleccion_label]
    else:
        st.sidebar.error("Jugador no encontrado.")

st.sidebar.markdown("---")
mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
mercado_real = nombres_api[mercado_visual]
linea_apuesta = st.sidebar.select_slider("Línea de valor (Winamax):", options=[x + 0.5 for x in range(0, 55)], value=15.5)

# --- SECCIÓN AMAZON AFILIADOS (vectis-21) ---
st.sidebar.markdown("---")
st.sidebar.write("### 🏀 Tienda NBA Oficial")
# Este enlace ayuda a generar las 3 ventas necesarias para tu cuenta
url_amazon = "https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21"
st.sidebar.info(f"👉 [Equipamiento y Balones NBA en Amazon]({url_amazon})")

st.title("🏀 Inteligencia Estadística NBA")

if player_obj:
    try:
        # Intentamos cargar temporada actual 2025-26
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        # Lógica de equipo robusta
        equipo_abr = "NBA"
        if not df.empty and 'TEAM_ABBREVIATION' in df.columns:
            equipo_abr = df.iloc[0]['TEAM_ABBREVIATION']
        else:
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_obj['id']).get_data_frames()[0]
            equipo_abr = info.iloc[0]['TEAM_ABBREVIATION'] or "NBA"
        
        nombre_display = f"{player_obj['full_name']} | {equipo_abr}"

        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
            promedio_l10 = df.head(10)[mercado_real].mean()

            # Banner de Análisis
            st.markdown(f'<div style="background-color:#1e1e1e;padding:20px;border-radius:15px;border:1px solid #e41b13;margin-bottom:25px;"><h3 style="color:#e41b13;margin-top:0;">🔥 ANÁLISIS DINÁMICO</h3><div style="display:flex;justify-content:space-between;align-items:center;"><div><p style="font-size:18px;"><b>{nombre_display}</b></p><p>Tendencia L10: {promedio_l10:.1f} {mercado_visual}</p></div><a href="https://www.winamax.es" target="_blank" style="background-color:#e41b13;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;font-weight:bold;">VER CUOTA</a></div></div>', unsafe_allow_html=True)

            st.subheader(f"Estadísticas Recientes: {nombre_display}")
            
            m1, m2, m3, m4 = st.columns(4)
            u15 = df.head(15)
            overs = (u15[mercado_real] > linea_apuesta).sum()
            
            m1.metric(f"Overs {mercado_visual}", f"{overs}/15", f"{int((overs/15)*100)}% Acierto")
            m2.metric("Promedio L10", f"{promedio_l10:.1f}")
            m3.metric("DD% (L15)", f"{((u15['SPECIAL_TYPE'] == 'DD').sum() / 15) * 100:.1f}%")
            m4.metric("Equipo Actual", equipo_abr)
            
            st.markdown("---")
            st.write("### Historial de Partidos (L15)")
            df_tabla = df.rename(columns={'STL': 'ROB', 'BLK': 'TAP', 'SPECIAL_TYPE': 'DD/TD'})
            cols_show = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'ROB', 'TAP', 'DD/TD']
            st.dataframe(df_tabla[cols_show].head(15).style.map(lambda x: color_mercado(x, linea_apuesta), subset=[mercado_visual]), use_container_width=True)
            st.line_chart(df.head(15).set_index('GAME_DATE')[mercado_real])
        else:
            st.warning(f"No hay partidos registrados para {nombre_display} en la temporada 2025-26.")
            
    except Exception as e:
        st.error(f"Error al procesar los datos del jugador: {e}")
else:
    st.info("👋 Selecciona un jugador en el buscador de la izquierda para ver su análisis.")

st.sidebar.markdown("---")
st.sidebar.link_button("📢 VIP Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.caption("⚠️ +18 | Vectis NBA Analytics")
