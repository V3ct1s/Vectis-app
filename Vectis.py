import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. FUNCIONES LÓGICAS
def check_double_triple(row):
    stats = [row['PTS'], row['REB'], row['AST'], row['STL'], row['BLK']]
    diez_o_mas = sum(1 for x in stats if x >= 10)
    if diez_o_mas >= 3: return "Triple-Double"
    if diez_o_mas >= 2: return "Double-Double"
    return "-"

def color_mercado(val, linea):
    color = '#2ecc71' if val > linea else '#e74c3c'
    return f'background-color: {color}; color: white'

# 2. CONFIGURACIÓN DE INTERFAZ
st.set_page_config(page_title="Vectis NBA Pro", layout="wide")
st.title("🏀 Vectis: NBA Intelligence Dashboard")

# --- BARRA LATERAL: COMUNIDAD, DONACIONES Y AFILIACIÓN ---
st.sidebar.header("🚀 Mi Comunidad")

# BOTÓN TELEGRAM
st.sidebar.markdown("""
<a href="https://t.me/+FWyCJmqSojVhMjVk" target="_blank">
    <button style="width:100%; background-color:#0088cc; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">
        📢 Unirse al Telegram Pro
    </button>
</a>
""", unsafe_allow_html=True)

# BOTÓN PAYPAL
st.sidebar.markdown("""
<a href="https://www.paypal.me/VectisNBA" target="_blank">
    <button style="width:100%; background-color:#ffc439; color:#003087; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">
        ☕ Invítame a un café (PayPal)
    </button>
</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# BANNER DE AFILIACIÓN (DISEÑO WINAMAX)
st.sidebar.markdown("""
<div style="background-color:#1a1a1a; padding:20px; border-radius:12px; border: 2px solid #e74c3c; text-align:center;">
    <h3 style="color:white; margin:0; font-size:18px;">🔴 BONO WINAMAX</h3>
    <p style="color:#ffffff; font-size:13px; margin:10px 0;">¡Duplica tu primer depósito para apostar en la NBA!</p>
    <a href="TU_LINK_AQUI" target="_blank">
        <button style="width:100%; background-color:#e74c3c; color:white;
