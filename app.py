import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse

# --- CONFIGURACIÓN Y DATOS ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"
ADMIN_PIN = "1234"  # CAMBIA TU PIN AQUÍ

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "expenses": []}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"appointments": [], "expenses": []}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    
    /* Calendario Bloqueado Estilo Airbnb */
    .booked-date { 
        background: repeating-linear-gradient(45deg, #ffebeb, #ffebeb 5px, #ffdbdb 5px, #ffdbdb 10px);
        color: #d00000; padding: 4px; border-radius: 4px; border: 1px solid #ffb3b3; 
        text-align: center; font-size: 0.75rem; font-weight: bold;
    }

    /* Footer Admin Minimalista */
    .admin-footer-link { 
        margin-top: 100px; text-align: center; font-size: 0.6rem; color: #eee; 
    }
    
    .header-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; text-align: center; text-transform: uppercase; margin-bottom: 0; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE CLIENTE ---
def booking_interface():
    st.markdown('<div style="padding:20px 0;"><h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:8px; color:#D4AF37; font-size:0.7rem;">ATELIER</p></div>', unsafe_allow_html=True)
    
    booked_dates = [a['date'] for a in st.session_state.data['appointments']]
    
    # Catálogo simple
    cols = st.columns(4)
    services = [("CAPPING", 120000), ("MANTENIMIENTO", 80000), ("SEMIPERMANENTE", 70000), ("SOFT GEL", 150000)]
    for i, (name, price) in enumerate(services):
        with cols[i]:
            st.markdown(f"<div style='text-align:center; font-size:0.7rem;'><b>{name}</b><br><span style='color:#D4AF37;'>₲{price:,}</span></div>", unsafe_allow_html=True)
            if st.button("Elegir", key=f"s_{i}"): st.session_state.serv = name

    st.markdown("---")
    
    # Mostrar fechas bloqueadas
    if booked_dates:
        with st.expander("📅 Ver Fechas Ocupadas"):
            c = st.columns(6)
            for i, d in enumerate(sorted(list(set(booked_dates)))):
                c[i % 6].markdown(f'<div class="booked-date">{d}</div>', unsafe_allow_html=True)

    # Formulario
    with st.form("book"):
        col1, col2 = st.columns(2)
        n = col1.text_input("Nombre")
        f = col2.date_input("Fecha", min_value=datetime.date.today())
        p = st.selectbox("Pago", ["Efectivo", "Transferencia / Pix"])
        
        if st.form_submit_button("Confirmar"):
            if str(f) in booked_dates: st.error("Fecha ocupada")
            elif n:
                res = {"id": str(uuid.uuid4())[:4].upper(), "client": n, "service": st.session_state.get('serv', 'Capping'), "price": 100000, "date": str(f), "status": "Pendiente", "payment": p}
                st.session_state.data['appointments'].append(res)
                save_data(st.session_state.data)
                st.success(f"Registrado! ID: {res['id']}")
                msg = f"Reserva Nails by Diva: {n} - {f}"
                st.markdown(f'[Enviar WhatsApp](https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)})')

# --- PANEL ADMIN MINI CON PIN ---
def mini_admin_panel():
    st.markdown('<div class="admin-footer-link">.</div>', unsafe_allow_html=True)
    
    with st.expander("Admin"):
        pin = st.text_input("Ingresar PIN", type="password")
        if pin == ADMIN_PIN:
            st.success("Acceso Autorizado")
            apts = st.session_state.data['appointments']
            exps = st.session_state.data['expenses']
            
            # Métricas
            in_r = sum(a['price'] for a in apts if a.get('status') == 'Concluido')
            gst = sum(e['amount'] for e in exps)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos", f"₲{in_r:,}")
            c2.metric("Gastos", f"₲{gst:,}")
            c3.metric("Neto", f"₲{in_r-gst:,}")
            
            # Gestión rápida
            st.divider()
            tab1, tab2 = st.tabs(["Citas", "Gastos"])
            with tab1:
                for i, a in enumerate(apts):
                    if a.get('status') == 'Pendiente':
                        if st.button(f"Concluir {a['client']} {a['date']}", key=f"c_{i}"):
                            st.session_state.data['appointments'][i]['status'] = 'Concluido'
                            save_data(st.session_state.data); st.rerun()
            with tab2:
                with st.form("g"):
                    desc = st.text_input("Gasto")
                    monto = st.number_input("Monto", step=1000)
                    if st.form_submit_button("Ok"):
                        st.session_state.data['expenses'].append({"desc": desc, "amount": monto})
                        save_data(st.session_state.data); st.rerun()
        elif pin != "2026":
            st.error("PIN Incorrecto")

# EJECUCIÓN
booking_interface()
mini_admin_panel()