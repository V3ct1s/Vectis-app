import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, leaguestandings
import pandas as pd

# --- FUNCIONES CORE ---
@st.cache_data(ttl=3600)
def get_nba_standings():
    try:
        standings = leaguestandings.LeagueStandings().get_data_frames()[0]
        dict_standings = {}
        for _, row in standings.iterrows():
            win_pct = row['WinPCT'] * 100
            record = f"{row['Record']} ({win_pct:.1f}%)"
            dict_standings[row['TeamAbbreviation']] = record
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

# --- SIDEBAR (LOS INAMOVIBLES) ---
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
        nombres = [p['full_name'] for p in nba_p]
        sel = st.sidebar.selectbox("2. Confirma el jugador:", nombres)
        p_obj = next((p for p in nba_p if p['full_name'] == sel), None)

st.sidebar.markdown("---")
m_vis = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
m_real = n_api[m_vis]
l_ap = st.sidebar.select_slider("Línea de valor (Winamax):", options=[x + 0.5 for x in range(0, 55)], value=15.5)

st.sidebar.markdown("---")
st.sidebar.header("🚀 Comunidad")
# RESTAURADOS BOTONES PAYPAL Y TELEGRAM
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café", "https://www.paypal.me/VectisNBA", use_container_width=True)
st.sidebar.info("🛒 [Tienda NBA Amazon](https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21)")

st.sidebar.markdown("---")
# MENSAJE DE PRECAUCIÓN INAMOVIBLE (EL DE LA FOTO)
st.sidebar.caption("⚠️ +18 | Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")

# --- CUERPO PRINCIPAL ---
st.title("🏀 Inteligencia Estadística NBA")
t1, t2 = st.tabs(["📊 Análisis", "🧮 Calculadora"])

with t1:
    if p_obj:
        try:
            # Añadimos un timeout para evitar el error de conexión de la foto
            log = playergamelog.PlayerGameLog(player_id=p_obj['id'], season='2025-26', timeout=30)
            df = log.get_data_frames()[0]
            standings = get_nba_standings()
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
                
                # CORRECCIÓN ERROR 'TEAM_ABBREVIATION'
                eq = ""
                if 'TEAM_ABBREVIATION' in df.columns:
                    eq = df.iloc[0]['TEAM_ABBREVIATION']
                
                record_eq = standings.get(eq, "N/A")
                nom_comp = f"{p_obj['full_name']} | {eq}"

                u15 = df.head(15)
                ovs = (u15[m_real] > l_ap).sum()
                prob_i = (ovs / 15)

                if st.button(f"➕ Añadir pick a Calculadora"):
                    st.session_state.calculadora.append({
                        "j": nom_comp, "m": m_vis, "l": l_ap, "p": prob_i, "win": record_eq
                    })
                    st.success("¡Añadido a la calculadora!")

                # Banner Principal
                html = f'<div style="background-color:#1e1e1e;padding:20px;border-radius:15px;border:1px solid #e41b13;margin-bottom:25px;"><h3 style="color:#e41b13;margin-top:0;">🔥 ANÁLISIS DINÁMICO</h3><div style="display:flex;justify-content:space-between;align-items:center;"><div><p><b>{nom_comp}</b></p><p>Récord Equipo: {record_eq}</p></div><a href="https://www.winamax.es" target="_blank" style="background-color:#e41b13;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;font-weight:bold;">VER CUOTA</a></div></div>'
                st.markdown(html, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Overs {m_vis}", f"{ovs}/15", f"{int(prob_i*100)}% Acierto")
                c2.metric("Promedio L10", f"{df.head(10)[m_real].mean():.1f}")
                c3.metric("Win% Equipo", record_eq.split("(")[-1].replace(")", "") if "(" in record_eq else "N/A")
                c4.metric("DD% (L15)", f"{((u15['SPECIAL_TYPE'] == 'DD').sum()/15)*100:.1f}%")
                
                st.write("### Historial Reciente (L15)")
                df_t = df.rename(columns={'STL':'ROB','BLK':'TAP','SPECIAL_TYPE':'DD/TD'})
                st.dataframe(df_t[['GAME_DATE','MATCHUP','WL','PTS','REB','AST','ROB','TAP','DD/TD']].head(15).style.map(lambda x: color_mercado(x, l_ap), subset=[m_vis]), use_container_width=True)
                st.line_chart(df.head(15).set_index('GAME_DATE')[m_real])
            else:
                st.warning("Sin datos esta temporada.")
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
    else:
        st.markdown('<div style="background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #e41b13; margin-bottom: 25px;"><h3 style="color: #e41b13; margin-top: 0;">🚀 BIENVENIDO A VECTIS NBA</h3><p style="font-size: 16px;">Busca un jugador en el menú lateral para generar un <b>Pick Estadístico</b> automáticamente.</p></div>', unsafe_allow_html=True)
        st.info("Utiliza el buscador lateral para empezar el análisis.")

with t2:
    st.header("🧮 Calculadora de Probabilidades")
    if not st.session_state.calculadora:
        st.info("La calculadora está vacía. Añade picks desde la pestaña de Análisis.")
    else:
        p_t, c_t = 1.0, 1.0
        for i, it in enumerate(st.session_state.calculadora):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,1,1])
                col1.write(f"**{it['j']}**")
                col1.caption(f"{it['m']} > {it['l']} | Eq: {it['win']}")
                cuo = col2.number_input(f"Cuota {i}:", 1.01, 100.0, 1.85, 0.05, key=f"cuo_{i}")
                if col3.button("🗑️", key=f"btn_{i}"):
                    st.session_state.calculadora.pop(i)
                    st.rerun()
                p_t *= it['p']
                c_t *= cuo
        st.markdown("---")
        r1, r2 = st.columns(2)
        r1.metric("Probabilidad Real", f"{int(p_t*100)}%")
        r2.metric("Cuota Total", f"{c_t:.2f}")
        
        if st.button("Limpiar Calculadora"):
            st.session_state.calculadora = []
            st.rerun()
