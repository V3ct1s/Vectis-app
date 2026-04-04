import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES AUXILIARES
def check_double_triple(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "Triple-Double"
    if diez_o_mas >= 2: return "Double-Double"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")

# --- BARRA LATERAL ---
# Mostrar tu logo de empresa (Asegúrate de que el archivo esté en GitHub)
try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("Vectis NBA")

st.sidebar.header("🚀 Mi Comunidad")

# Botones con enlaces directos (Sin HTML complejo para evitar errores)
st.sidebar.link_button("📢 Telegram Pro", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ PayPal (Apoyar proyecto)", "https://www.paypal.me/VectisNBA", use_container_width=True)

st.sidebar.markdown("---")

# CONFIGURACIÓN DE ANÁLISIS
st.sidebar.header("🔍 Análisis")
busqueda = st.sidebar.text_input("Buscar Jugador (ej: Doncic):")
mercado = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado}:", value=10.5, step=0.5)

# --- SECCIÓN LEGAL (LOGOS +18 Y JUGAR BIEN) ---
st.sidebar.markdown("---")
with st.sidebar.container():
    st.markdown("### ⚠️ Juego Responsable")
    col_logo1, col_logo2 = st.columns(2)
    with col_logo1:
        st.image("https://www.jugarbien.es/sites/default/files/images/logotipos/logo_18.png", width=50)
    with col_logo2:
        st.image("https://www.jugarbien.es/sites/default/files/images/logotipos/logo_jugarbien.png", width=100)
    
    st.caption("Solo mayores de 18 años. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con moderación.")

# 3. CUERPO PRINCIPAL
st.title("🏀 NBA Intelligence Dashboard")

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Confirmar jugador:", nombres)
        player = [p for p in nba_players if p['full_name'] == seleccion][0]
        
        try:
            log = playergamelog.PlayerGameLog(player_id=player['id'], season='2025-26')
            df = log.get_data_frames()[0]
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL'] = df.apply(check_double_triple, axis=1)

                st.subheader(f"Análisis: {player['full_name']}")
                u15 = df.head(15)
                overs = (u15[mercado] > linea_apuesta).sum()
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(f"Overs {mercado}", f"{overs}/15", f"{int((overs/15)*100)}% Win Rate")
                m2.metric("Promedio L10", f"{df.head(10)[mercado].mean():.1f}")
                m3.metric("D-D / T-D (L15)", f"{(u15['SPECIAL'] != '-').sum()}")
                m4.metric("Máximo Temp.", f"{df[mercado].max()}")

                st.markdown("---")
                
                # Tabla de datos
                st.write("### Últimos 15 Partidos")
                cols = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'SPECIAL']
                st.table(df[cols].head(15).style.applymap(lambda x: color_mercado(x, linea_apuesta), subset=[mercado]))
                
                # Gráfico
                st.line_chart(df.head(15).set_index('GAME_DATE')[mercado])
            else:
                st.warning("No hay datos para esta temporada.")
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
    else:
        st.error("Jugador no encontrado.")
else:
    st.info("Introduce un jugador en la barra lateral para ver su racha.")
