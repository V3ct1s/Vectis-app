import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES AUXILIARES
def check_double_triple(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "Triple-Doble"
    if diez_o_mas >= 2: return "Doble-Doble"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# Diccionario para nombres internos de la API
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

# PASO 1: Buscar nombre
busqueda = st.sidebar.text_input("1. Escribe nombre (ej: Doncic):")
player_obj = None

# PASO 2: Confirmar jugador (Entre buscador y mercado)
if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("2. Confirma el jugador:", nombres)
        player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)
    else:
        st.sidebar.error("Jugador no encontrado.")

st.sidebar.markdown("---")

# PASO 3: Mercado
mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
mercado_real = nombres_api[mercado_visual]
linea_apuesta = st.sidebar.number_input(f"Estadística de {mercado_visual}:", value=10.5, step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("🚀 Comunidad")
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café (PayPal)", "https://www.paypal.me/VectisNBA", use_container_width=True)

# 3. CUERPO PRINCIPAL
st.title("🏀 Inteligencia Estadística NBA")

if player_obj:
    try:
        # Petición a la API
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL'] = df.apply(check_double_triple, axis=1)

            st.subheader(f"Análisis detallado: {player_obj['full_name']}")
            
            u15 = df.head(15)
            overs = (u15[mercado_real] > linea_apuesta).sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"Overs {mercado_visual}", f"{overs}/15", f"{int((overs/15)*100)}% de acierto")
            m2.metric("Promedio (L10)", f"{df.head(10)[mercado_real].mean():.1f}")
            m3.metric("Doble/Triple-Doble", f"{(u15['SPECIAL'] != '-').sum()}")
            m4.metric("Máximo Temp.", f"{df[mercado_real].max()}")

            st.markdown("---")
            
            st.write("### Últimos 15 encuentros")
            # Preparar tabla con nombres en español
            df_tabla = df.rename(columns={'STL': 'ROB', 'BLK': 'TAP'})
            cols_tabla = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'ROB', 'TAP', 'SPECIAL']
            
            st.table(df_tabla[cols_tabla].head(15).style.map(lambda x: color_mercado(x, linea_apuesta), subset=[mercado_visual]))
            
            st.line_chart(df.head(15).set_index('GAME_DATE')[mercado_real])
        else:
            st.warning("No hay datos disponibles para esta temporada.")
            
    except Exception as e:
        st.error(f"Error en la conexión con la API: {e}")
else:
    st.info("Utiliza el buscador de la izquierda para empezar.")

# --- PIE DE PÁGINA LEGAL ---
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Solo mayores de 18 años. Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")
