import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# --- FUNCIONES ---
def check_special_stats(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    return "TD" if diez_o_mas >= 3 else ("DD" if diez_o_mas >= 2 else "-")

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vectis | NBA Analytics", layout="wide")

# Inicializar el "Carrito" de apuestas en la sesión
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# Sidebar
try:
    st.sidebar.image("vectis.png", use_container_width=True)
except:
    st.sidebar.title("VECTIS NBA")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Buscador")
busqueda = st.sidebar.text_input("1. Escribe nombre:")

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2 = st.tabs(["📊 Análisis de Jugador", "🧮 Calculadora de Combinadas"])

with tab1:
    player_obj = None
    if busqueda:
        nba_players = players.find_players_by_full_name(busqueda)
        if nba_players:
            nombres = [p['full_name'] for p in nba_players]
            seleccion = st.sidebar.selectbox("2. Confirma el jugador:", nombres)
            player_obj = next((p for p in nba_players if p['full_name'] == seleccion), None)

    st.sidebar.markdown("---")
    mercado_visual = st.sidebar.selectbox("Mercado a analizar:", ["PTS", "REB", "AST", "ROB", "TAP"])
    nombres_api = {"PTS": "PTS", "REB": "REB", "AST": "AST", "ROB": "STL", "TAP": "BLK"}
    
    linea_apuesta = st.sidebar.select_slider("Línea de valor:", options=[x + 0.5 for x in range(0, 55)], value=15.5)

    if player_obj:
        try:
            log = playergamelog.PlayerGameLog(player_id=player_obj['id'], season='2025-26')
            df = log.get_data_frames()[0]
            
            if not df.empty:
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE']).dt.date
                df['SPECIAL_TYPE'] = df.apply(check_special_stats, axis=1)
                
                equipo_abr = df.iloc[0]['TEAM_ABBREVIATION'] if 'TEAM_ABBREVIATION' in df.columns else ""
                nombre_completo = f"{player_obj['full_name']} | {equipo_abr}"
                
                # Estadísticas
                u15 = df.head(15)
                overs = (u15[nombres_api[mercado_visual]] > linea_apuesta).sum()
                porcentaje_exito = (overs / 15)

                # BOTÓN PARA AÑADIR A LA CALCULADORA
                if st.button(f"➕ Añadir {nombre_display if 'nombre_display' in locals() else nombre_completo} a la Combinada"):
                    st.session_state.carrito.append({
                        "jugador": nombre_completo,
                        "mercado": mercado_visual,
                        "linea": linea_apuesta,
                        "prob": porcentaje_exito
                    })
                    st.toast(f"Añadido: {nombre_completo}")

                # (Aquí va todo tu diseño visual de gráficas y tablas que ya tenías...)
                st.subheader(f"Análisis: {nombre_completo}")
                st.metric("Probabilidad de Éxito (L15)", f"{int(porcentaje_exito*100)}%")
                st.dataframe(df.head(15)[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST']], use_container_width=True)
                
            else:
                st.warning("No hay datos disponibles.")
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.header("🧮 Simulador de Probabilidad Real")
    
    if not st.session_state.carrito:
        st.info("El carrito está vacío. Ve a la pestaña de análisis y añade jugadores.")
    else:
        col_calc1, col_calc2 = st.columns([2, 1])
        
        with col_calc1:
            st.write("### Tus Selecciones")
            prob_acumulada = 1.0
            cuota_total = 1.0
            
            for i, pick in enumerate(st.session_state.carrito):
                with st.expander(f"{pick['jugador']} - Over {pick['linea']} {pick['mercado']}"):
                    cuota = st.number_input(f"Cuota de este pick:", min_value=1.01, value=1.85, key=f"cuota_{i}")
                    st.write(f"Probabilidad estadística: **{int(pick['prob']*100)}%**")
                    prob_acumulada *= pick['prob']
                    cuota_total *= cuota
                    if st.button("Eliminar", key=f"del_{i}"):
                        st.session_state.carrito.pop(i)
                        st.rerun()

        with col_calc2:
            st.write("### Resultado Final")
            st.metric("Probabilidad Combinada", f"{int(prob_acumulada*100)}%")
            st.metric("Cuota Total Estimada", f"{cuota_total:.2f}")
            
            ganancia_potencial = 10 * cuota_total
            st.write(f"Si apuestas 10€, ganarías **{ganancia_potencial:.2f}€**")
            
            if st.button("Limpiar Calculadora"):
                st.session_state.carrito = []
                st.rerun()

# Sidebar Final
st.sidebar.markdown("---")
st.sidebar.info("🛒 [Tienda NBA Amazon](https://www.amazon.es/nba-oficial/s?k=nba+oficial&tag=vectis-21)")
