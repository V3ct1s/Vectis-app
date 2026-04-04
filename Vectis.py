import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, leaguestandings
import pandas as pd

# --- FUNCIONES CORE ---
@st.cache_data(ttl=3600)
def get_nba_standings():
    try:
        std_data = leaguestandings.LeagueStandings().get_data_frames()[0]
        dict_std = {}
        for _, row in std_data.iterrows():
            pct = row['WinPCT'] * 100
            dict_std[row['TeamAbbreviation']] = f"{row['Record']} ({pct:.1f}%)"
        return dict_std
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
st.sidebar.link_button("📢 Únete al VIP en Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invita a un café", "https://www.paypal.me/VectisNBA", use_container_width=True)
st.sidebar.info("🛒 [Tienda NBA Amazon](https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21)")

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ +18 | Vectis es una herramienta estadística informativa. Los datos ofrecidos son estadísticos y no garantizan resultados. Juega con responsabilidad.")

# --- CUERPO PRINCIPAL ---
st.title("🏀 Inteligencia Estadística NBA")
t1, t2 = st.tabs(["📊 Análisis", "🧮 Calculadora"])

with t1:
    if p_obj:
        try:
            log = playergamelog.PlayerGameLog(player_id=p_obj['id'], season='2025-26', timeout=60)
            df = log.get_data_frames()[0]
            stds = get_nba_standings()
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
                
                eq = df.iloc[0]['TEAM_ABBREVIATION'] if 'TEAM_ABBREVIATION' in df.columns else ""
                rec = stds.get(eq, "N/A")
                full_n = f"{p_obj['full_name']} | {eq}"

                u15 = df.head(15)
                ovs = (u15[m_real] > l_ap).sum()
                p_i = (ovs / 15)

                if st.button(f"➕ Añadir pick a la Calculadora"):
                    # GUARDADO DE DATOS (Asegurando nombres de llaves)
                    st.session_state.calculadora.append({
                        "j": full_n, 
                        "m": m_vis, 
                        "l": l_ap, 
                        "p": p_i, 
                        "w": rec
                    })
                    st.success("¡Añadido!")

                html = f'<div style="background-color:#1e1e1e;padding:20px;border-radius:15px;border:1px solid #e41b13;margin-bottom:25px;"><h3 style="color:#e41b13;margin-top:0;">🔥 ANÁLISIS DINÁMICO</h3><div style="display:flex;justify-content:space-between;align-items:center;"><div><p><b>{full_n}</b></p><p>Récord: {rec}</p></div><a href="https://www.winamax.es" target="_blank" style="background-color:#e41b13;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;font-weight:bold;">VER CUOTA</a></div></div>'
                st.markdown(html, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Overs {m_vis}", f"{ovs}/15", f"{int(p_i*100)}%")
                c2.metric("Promedio L10", f"{df.head(10)[m_real].mean():.1f}")
                
                w_val = rec.split("(")[-1].split(")")[0] if "(" in rec else "N/A"
                c3.metric("Win% Equipo", w_val)
                c4.metric("DD% (L15)", f"{((u15['SPECIAL_TYPE'] == 'DD').sum()/15)*100:.1f}%")
                
                st.write("### Historial Reciente")
                df_s = df.rename(columns={'STL':'ROB','BLK':'TAP','SPECIAL_TYPE':'DD/TD'})
                st.dataframe(df_s[['GAME_DATE','MATCHUP','WL','PTS','REB','AST','ROB','TAP','DD/TD']].head(15).style.map(lambda x: color_mercado(x, l_ap), subset=[m_vis]), use_container_width=True)
                st.line_chart(df.head(15).set_index('GAME_DATE')[m_real])
            else:
                st.warning("Sin datos esta temporada.")
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
    else:
        st.info("Busca un jugador para empezar.")

with t2:
    st.header("🧮 Calculadora")
    if not st.session_state.calculadora:
        st.info("La calculadora está vacía.")
    else:
        pt, ct = 1.0, 1.0
        # USAMOS UNA COPIA PARA EVITAR ERRORES AL BORRAR
        for i, it in enumerate(st.session_state.calculadora):
            with st.container(border=True):
                ca, cb, cc = st.columns([2, 1, 0.5])
                ca.write(f"**{it['j']}**")
                # LÍNEA 125 CORREGIDA: Acceso seguro a las llaves 'm', 'l' y 'w'
                ca.caption(f"{it['m']} > {it['l']} | Eq: {it['w']}")
                
                cuo = cb.number_input("Cuota:", 1.01, 100.0, 1.85, 0.05, key=f"k_{i}")
                if cc.button("🗑️", key=f"r_{i}"):
                    st.session_state.calculadora.pop(i)
                    st.rerun()
                pt *= it['p']
                ct *= cuo
        st.markdown("---")
        r1, r2 = st.columns(2)
        r1.metric("Probabilidad Real", f"{int(pt*100)}%")
        r2.metric("Cuota Total", f"{ct:.2f}")
        if st.button("Limpiar Calculadora"):
            st.session_state.calculadora = []
            st.rerun()
