import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES LÓGICAS
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

# 2. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Vectis NBA", layout="wide")

# --- BARRA LATERAL ---
try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.header("🔍 Buscador de Jugadores")
busqueda = st.sidebar.text_input("Escribe un nombre (ej: Curry):")
player_obj = None

if busqueda:
    nba_players = players.find_players_by_full_name(busqueda)
    if nba_players:
        nombres = [p['full_name'] for p in nba_players]
        seleccion = st.sidebar.selectbox("Confirma el jugador:", nombres)
        player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)

st.sidebar.markdown("---")
mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
mercado_real = nombres_api[mercado_visual]
linea_apuesta = st.sidebar.number_input("Línea Winamax:", value=15.5, step=1.0)

# --- BANNER AMAZON ESPAÑA (PROTEGIDO CONTRA ERRORES) ---
st.sidebar.markdown("---")
st.sidebar.write("### 🇪🇸 Ofertas NBA España")
amazon_es_url = "https://www.amazon.es/gp/browse.html?node=2945785031&tag=vectis-21"
amazon_html = f'<a href="{amazon_es_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #232f3e; padding: 15px; border-radius: 12px; text-align: center; color: white; border: 1px solid #ff9900;"><img src="https://m.media-amazon.com/images/I/71IsS6vS6sL._AC_SX679_.jpg" width="85%" style="border-radius: 5px;"><p style="font-size: 14px; margin: 12px 0 5px 0; font-weight: bold; color: #ff9900;">Equipamiento NBA</p><p style="font-size: 12px; margin: 0 0 10px 0; opacity: 0.9;">Balones y Camisetas</p><div style="background-color: #ff9900; color: black; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 14px;">VER EN AMAZON.ES</div></div></a>'
st.sidebar.markdown(amazon_html, unsafe_allow_html=True)

# 3. CUERPO PRINCIPAL
st.title("🏀 Vectis Analytics")

if player_obj:
    try:
        log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
            df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
            promedio_l10 = df.head(10)[mercado_real].mean()

            # Cuadro de Pick Dinámico (UNA SOLA LÍNEA PARA EVITAR SYNTAXERROR)
            pick_html = f'<div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 2px solid #e41b13; margin-bottom: 25px;"><h4 style="color: #e41b13; margin-top: 0; letter-spacing: 1px;">🔥 ANÁLISIS DINÁMICO</h4><p style="margin: 0; font-size: 18px;"><b>{player_obj["full_name"]}</b></p><p style="margin: 5px 0; font-size: 15px; color: #cccccc;">Tendencia L10: {promedio_l10:.1f} {mercado_visual}</p><a href="https://www.winamax.es" target="_blank" style="display: block; background-color: #e41b13; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 15px; font-size: 16px;">VER CUOTA EN WINAMAX</a></div>'
            st.markdown(pick_html, unsafe_allow_html=True)

            st.subheader(f"Rendimiento: {player_obj['full_name']}")
            m1, m2, m3 = st.columns(3)
            overs_l15 = (df.head(15)[mercado_real] > linea_apuesta).sum()
            m1.metric(f"Overs {mercado_visual}", f"{overs_l15}/15", f"{int((overs_l15/15)*100)}%")
            m2.metric("Promedio L10", f"{promedio_l10:.1f}")
            m3.metric("Doble-Doble %", f"{int(((df.head(15)['SPECIAL_TYPE']=='DD').sum()/15)*100)}%")
            
            st.write("### Historial Reciente")
            df_tabla = df.rename(columns={'STL': 'ROB', 'BLK': 'TAP', 'SPECIAL_TYPE': 'DD/TD'})
            cols_ver = ['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'DD/TD']
            st.dataframe(df_tabla[cols_ver].head(15), use_container_width=True)
            st.line_chart(df.head(15).set_index('GAME_DATE')[mercado_real])
        else:
            st.warning("No hay partidos este año para este jugador.")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    welcome_html = '<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border: 1px solid #e41b13; margin-bottom: 25px;"><h3 style="color: #e41b13; margin-top: 0;">🚀 BIENVENIDO A VECTIS NBA</h3><p style="font-size: 16px;">Busca un jugador en el lateral para ver el <b>Pick Automático</b>.</p></div>'
    st.markdown(welcome_html, unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.sidebar.markdown("---")
st.sidebar.link_button("📢 Canal VIP Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.caption("⚠️ +18 | Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")
