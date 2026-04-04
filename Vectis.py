import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, leagstandings
import pandas as pd

# --- FUNCIONES CORE ---
@st.cache_data(ttl=3600)
def get_nba_standings():
    try:
        # Traemos la clasificación completa
        standings = leagstandings.LeagueStandings().get_data_frames()[0]
        dict_standings = {}
        for _, row in standings.iterrows():
            # Usamos TeamAbbreviation como llave
            abbr = row['TeamAbbreviation']
            win_pct = row['WinPCT'] * 100
            record = f"{row['Record']} ({win_pct:.1f}%)"
            dict_standings[abbr] = record
        return dict_standings
    except:
        return {}

def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    d10 = sum(1 for x in stats if x >= 10)
    return "TD" if d10 >= 3 else ("DD" if d10 >= 2 else "-")

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")
if 'calculadora' not in st.session_state:
    st.session_state.calculadora = []

n_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}

# --- SIDEBAR (INAMOVIBLE) ---
try: 
    st.sidebar.image("vectis.png", use_container_width=True)
except: 
    st.sidebar.title("VECTIS NBA")

st.sidebar.header("🔍 Buscador de Patrones")
busqueda = st.sidebar.text_input("1. Escribe nombre (ej: Stephen Curry):")
p_obj = None

if busqueda:
    nba_p = players.find_players_by_full_name(busqueda)
    if nba_p:
        n_list = [p['full_name'] for p in nba_p]
        sel = st.sidebar.selectbox("2. Confirma el jugador:", n_list)
        p_obj = next((p for p in nba_p if p['full_name'] == sel), None)

st.sidebar.markdown("---")
m_vis = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
m_real = n_api[m_vis]
l_ap = st.sidebar.select_slider("Línea de valor (Winamax):", options=[x + 0.5 for x in range(0, 55)], value=15.5)

st.sidebar.markdown("---")
st.sidebar.header("🚀 Comunidad")
# BOTONES INAMOVIBLES
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café", "https://www.paypal.me/VectisNBA", use_container_width=True)
st.sidebar.info("🛒 [Tienda NBA Amazon](https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21)")

st.sidebar.markdown("---")
# AVISO LEGAL INAMOVIBLE
st.sidebar.caption("⚠️ +18 | Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")

# --- CUERPO PRINCIPAL ---
st.title("🏀 Inteligencia Estadística NBA")
t1, t2 = st.tabs(["📊 Análisis", "🧮 Calculadora"])

with t1:
    if p_obj:
        try:
            # Aumentamos timeout para evitar el "Read timed out" de la foto
            log = playergamelog.PlayerGameLog(player_id=p_obj['id'], season='2025-26', timeout=60)
            df = log.get_data_frames()[0]
            standings = get_nba_standings()
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
                
                # Identificar equipo
                eq_abbr = df.iloc[0]['TEAM_ABBREVIATION'] if 'TEAM_ABBREVIATION' in df.columns else "N/A"
                rec_info = standings.get(eq_abbr, "N/A")
                
                full_name_eq = f"{p_obj['full_name']} | {eq_abbr}"

                u15 = df.head(15)
                ovs = (u15[m_real] > l_ap).sum()
                p_ind = (ovs / 15)

                if st.button(f"➕ Añadir pick a la Calculadora"):
                    st.session_state.calculadora.append({
                        "j": full_name_eq, "m": m_vis, "l": l_ap, "p": p_ind, "win": rec_info
                    })
                    st.success(f"Añadido: {p_obj['full_name']}")

                # Banner Principal
                html = f'''
                <div style="background-color:#1e1e1e;padding:20px;border-radius:15px;border:1px solid #e41b13;margin-bottom:25px;">
                    <h3 style="color:#e41b13;margin-top:0;">🔥 ANÁLISIS DINÁMICO</h3>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <p style="margin:0; font-size:18px;"><b>{full_name_eq}</b></p>
                            <p style="margin:0; color:#888;">Récord Equipo: {rec_info}</p>
                        </div>
                        <a href="https://www.winamax.es" target="_blank" style="background-color:#e41b13;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;font-weight:bold;">VER CUOTA</a>
                    </div>
                </div>
                '''
                st.markdown(html, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Overs {m_vis}", f"{ovs}/15", f"{int(p_ind*100)}% Éxito")
                c2.metric("Promedio L10", f"{df.head(10)[m_real].mean():.1f}")
                
                # Mostrar Win% del equipo extraído del récord
                w_disp = rec_info.split("(")[-1].replace("
