import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES
def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "TD"
    if diez_o_mas >= 2: return "DD"
    return "-"

nombres_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}

# 2. CONFIGURACIÓN
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

# --- BARRA LATERAL ---
if st.sidebar.button("🏠 Inicio / Reset"):
    st.rerun()

st.sidebar.header("🔍 Buscador")
busqueda = st.sidebar.text_input("1. Nombre del jugador:")
player_obj = None

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("2. Confirma:", nombres)
        player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)
    else:
        st.sidebar.error("Jugador no encontrado.")

st.sidebar.markdown("---")
mercado_visual = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "ROB", "TAP"])
linea_apuesta = st.sidebar.number_input("Línea Winamax:", value=15.5, step=1.0)

# --- PUBLICIDAD AMAZON ESPAÑA (SINTAXIS SEGURA) ---
st.sidebar.markdown("---")
st.sidebar.write("### 🇪🇸 Ofertas NBA")
link_amzn = "https://www.amazon.es/gp/browse.html?node=2945785031&tag=vectis-21"
st.sidebar.info(f"👉 [Ver Equipamiento NBA en Amazon.es]({link_amzn})")

# 3. CUERPO PRINCIPAL
st.title("🏀 Inteligencia Estadística NBA")

if player_obj:
    try:
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
            
            # Datos clave
            equipo = df.iloc[0]['TEAM_ABBREVIATION']
            nombre_completo = f"{player_obj['full_name']} | {equipo}"
            promedio_l10 = df.head(10)[nombres_api[mercado_visual]].mean()
            
            # Bloque de Análisis (Sintaxis ultra-segura)
            st.success(f"🔥 **ANÁLISIS PARA: {nombre_completo}**")
            col_a, col_b = st.columns([2, 1])
            col_a.write(f"**Tendencia L10:** Promediando {promedio_l10:.1f} en {mercado_visual}")
            col_b.link_button("🎰 VER CUOTA WINAMAX", "https://www.winamax.es")

            st.markdown("---")
            
            # Métricas
            st.subheader(f"Dashboard: {nombre_completo}")
            m1, m2, m3, m4 = st.columns(4)
            overs = (df.head(15)[nombres_api[mercado_visual]] > linea_apuesta).sum()
            
            m1.metric(f"Overs {mercado_visual}", f"{overs}/15")
            m2.metric("Promedio L10", f"{promedio_l10:.1f}")
            m3.metric("Equipo", equipo)
            m4.metric("Doble-Doble (L15)", (df.head(15)['SPECIAL_TYPE'] == 'DD').sum())
            
            # Tabla y Gráfico
            st.write("### Historial Reciente")
            cols_show = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'SPECIAL_TYPE']
            st.dataframe(df.head(15)[cols_show], use_container_width=True)
            st.line_chart(df.head(15).set_index('GAME_DATE')[nombres_api[mercado_visual]])
            
        else:
            st.warning("No hay datos para este jugador en la temporada actual.")
    except Exception as e:
        st.error(f"Error en la API: {e}")
else:
    st.info("👋 Bienvenido. Busca un jugador en el menú de la izquierda para empezar.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.link_button
