import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES DE APOYO (Fuera para evitar errores de espacios)
def check_double_triple(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "Triple-Double"
    if diez_o_mas >= 2: return "Double-Double"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# 2. CONFIGURACIÓN APP
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# --- BARRA LATERAL ---
st.sidebar.header("🚀 Comunidad & Apoyo")
st.sidebar.markdown("""
<a href="https://t.me/+FWyCJmqSojVhMjVk" target="_blank">
    <button style="width:100%; background-color:#0088cc; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">📢 Unirse al Telegram Pro</button>
</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<a href="https://www.paypal.me/VectisNBA" target="_blank">
    <button style="width:100%; background-color:#ffc439; color:black; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">☕ Invítame a un café (PayPal)</button>
</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Configuración")
busqueda = st.sidebar.text_input("Jugador (ej: Doncic, Tatum):")
mercado = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "STL", "BLK"])
linea_apuesta = st.sidebar.number_input(f"Línea de {mercado}:", value=1.5 if mercado in ["STL", "BLK"] else 10.5, step=0.5)

# 3. LÓGICA PRINCIPAL
if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Selecciona:", nombres)
        player = [p for p in nba_players if p['full_name'] == seleccion][0]
        
        try:
            log = playergamelog.PlayerGameLog(player_id=player['id'], season='2025-26')
            df = log.get_data_frames()[0]
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL'] = df.apply(check_double_triple, axis=1)

                # Métricas
                u15 = df.head(15)
                overs = (u15[mercado] > linea_apuesta).sum()
                prom_l10 = df.head(10)[mercado].mean()

                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Overs {mercado}", f"{overs}/15")
                c2.metric("Promedio L10", f"{prom_l10:.1f}")
                c3.metric("D-D / T-D", f"{(u15['SPECIAL'] != '-').sum()}")
                c4.metric("Máximo", f"{df[mercado].max()}")

                st.markdown("---")
                
                # Filtros
                ubi = st.radio("Ubicación:", ["Todos", "Local", "Visitante"], horizontal=True)
                df_f = df.copy()
                if ubi == "Local": df_f = df_f[df_f['MATCHUP'].str.contains('vs.')]
                elif ubi == "Visitante": df_f = df_f[df_f['MATCHUP'].str.contains('@')]

                # Tabla
                cols = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'SPECIAL']
                display = df_f[cols].head(15)
                st.subheader(f"Análisis de {player['full_name']}")
                
                # Pintar tabla
                st.table(display.style.applymap(lambda x: color_mercado(x, linea_apuesta), subset=[mercado]))
                st.line_chart(display.set_index('GAME_DATE')[mercado])
            else:
                st.warning("No hay datos.")
        except Exception as e:
            st.error(f"Error API: {e}")
    else:
        st.error("No encontrado.")
else:
    st.info("Escribe un nombre a la izquierda.")
