import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    d10 = sum(1 for x in stats if x >= 10)
    if d10 >= 3: return "TD"
    if d10 >= 2: return "DD"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

if 'calculadora' not in st.session_state:
    st.session_state.calculadora = []

n_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}

try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Buscador")

busqueda = st.sidebar.text_input("1. Escribe nombre:")
p_obj = None

if busqueda:
    nba_p = players.find_players_by_full_name(busqueda)
    if nba_p:
        nombres = [p['full_name'] for p in nba_p]
        sel = st.sidebar.selectbox("2. Confirma:", nombres)
        p_obj = next((p for p in nba_p if p['full_name'] == sel), None)
    else:
        st.sidebar.error("No encontrado.")

st.sidebar.markdown("---")
m_vis = st.sidebar.selectbox("Mercado:", ["PTS", "REB", "AST", "ROB", "TAP"])
m_real = n_api[m_vis]

if m_vis == "PTS":
    opts, i_def = [x + 0.5 for x in range(5, 51)], 15
elif m_vis == "REB":
    opts, i_def = [x + 0.5 for x in range(1, 21)], 7
elif m_vis == "AST":
    opts, i_def = [x + 0.5 for x in range(0, 19)], 5
else:
    opts, i_def = [x + 0.5 for x in range(0, 8)], 1

l_ap = st.sidebar.select_slider("Línea:", options=opts, value=opts[i_def])

st.sidebar.markdown("---")
st.sidebar.info("🛒 [Tienda NBA Amazon](https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21)")
st.sidebar.header("🚀 Comunidad")
st.sidebar.link_button("📢 VIP Telegram", "https://t.me/+FWyCJmqSojVhMjVk", use_container_width=True)
st.sidebar.link_button("☕ Invitar Café", "https://www.paypal.me/VectisNBA", use_container_width=True)
st.sidebar.caption("⚠️ +18 | Juega con responsabilidad.")

st.title("🏀 Inteligencia Estadística NBA")

t1, t2 = st.tabs(["📊 Análisis", "🧮 Calculadora"])

with t1:
    if p_obj:
        try:
            log = playergamelog.PlayerGameLog(player_id=p_obj['id'], season='2025-26')
            df = log.get_data_frames()[0]
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
                prom_l10 = df.head(10)[m_real].mean()
                
                # --- LÍNEA CORREGIDA PARA EVITAR SYNTAX ERROR ---
                eq = df.iloc[0]['TEAM_ABBREVIATION'] if 'TEAM_ABBREVIATION' in df.columns else ""
                nom_comp = f"{p_obj['full_name']} | {eq}"

                u15 = df.head(15)
                ovs = (u15[m_real] > l_ap).sum()
                prob_i = (ovs / 15)

                if st.button(f"➕ Añadir pick a Calculadora"):
                    st.session_state.calculadora.append({
                        "j": nom_comp, "m": m_vis, "l": l_ap, "p": prob_i
                    })
                    st.success("¡Añadido!")

                html = f'<div style="background-color:#1e1e1e;padding:20px;border-radius:15px;border:1px solid #e41b13;margin-bottom:25px;"><h3 style="color:#e41b13;margin-top:0;">🔥 ANÁLISIS DINÁMICO</h3><div style="display:flex;justify-content:space-between;align-items:center;"><div><p><b>{nom_comp}</b></p><p>Tendencia L10: {prom_l10:.1f} {m_vis}</p></div><a href="https://www.winamax.es" target="_blank" style="background-color:#e41b13;color:white;padding:12px 25px;border-radius:8px;text-decoration:none;font-weight:bold;">APOSTAR</a></div></div>'
                st.markdown(html, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Overs {m_vis}", f"{ovs}/15", f"{int(prob_i*100)}%")
                c2.metric("Promedio L10", f"{prom_l10:.1f}")
                c3.metric("DD%", f"{((u15['SPECIAL_TYPE'] == 'DD').sum()/15)*100:.1f}%")
                c4.metric("TD%", f"{((u15['SPECIAL_TYPE'] == 'TD').sum()/15)*100:.1f}%")
                
                st.write("### Historial Reciente")
                df_t = df.rename(columns={'STL':'ROB','BLK':'TAP','SPECIAL_TYPE':'DD/TD'})
                st.dataframe(df_t[['GAME_DATE','MATCHUP','WL','PTS','REB','AST','ROB','TAP','DD/TD']].head(15).style.map(lambda x: color_mercado(x, l_ap), subset=[m_vis]), use_container_width=True)
                st.line_chart(df.head(15).set_index('GAME_DATE')[m_real])
            else:
                st.warning("Sin datos esta temporada.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Busca un jugador para empezar.")

with t2:
    st.header("🧮 Calculadora")
    if not st.session_state.calculadora:
        st.info("Añade picks desde la pestaña de Análisis.")
    else:
        p_t, c_t = 1.0, 1.0
        for i, it in enumerate(st.session_state.calculadora):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,1,1])
                col1.write(f"**{it['j']}**")
                col1.caption(f"{it['m']} > {it['l']} ({int(it['p']*100)}%)")
                cuo = col2.number_input("Cuota:", 1.01, 100.0, 1.85, 0.05, key=f"c{i}")
                if col3.button("🗑️", key=f"b{i}"):
                    st.session_state.calculadora.pop(i)
                    st.rerun()
                p_t *= it['p']
                c_t *= cuo
        st.markdown("---")
        r1, r2 = st.columns(2)
        r1.metric("Probabilidad Real", f"{int(p_t*100)}%")
        r2.metric("Cuota Total", f"{c_t:.2f}")
        if st.button("Limpiar"):
            st.session_state.calculadora = []
            st.rerun()
