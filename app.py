import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

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

# --- 2. SERVICIOS ---
SERVICES = {
    "CAPPING": {"title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
    "MAINTENANCE": {"title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
    "SEMIPERMANENT": {"title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
    "SOFT_GEL": {"title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
}

# --- 3. ESTILOS CSS (ESTILO AIRBNB / PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    
    /* Calendario Estilo Airbnb */
    .booked-date { 
        background: repeating-linear-gradient(45deg, #ffcccc, #ffcccc 10px, #ff9999 10px, #ff9999 20px);
        color: #b30000; padding: 5px; border-radius: 5px; border: 1px solid #ff0000; text-align: center; font-size: 0.8rem; margin-top: 5px;
    }

    /* Footer Admin */
    .admin-footer { 
        margin-top: 150px; padding: 20px; border-top: 1px solid #eaeaea; 
        background-color: #f9f9f9; color: #999; text-align: center; font-size: 0.7rem;
    }
    
    .header-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; letter-spacing: 3px; text-align: center; text-transform: uppercase; }
    .mini-card { text-align: center; padding: 10px; background: white; border-radius: 12px; border: 1px solid #F0F0F0; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE CALENDARIO ---
def get_booked_dates():
    return [a['date'] for a in st.session_state.data['appointments']]

# --- 5. INTERFAZ CLIENTE ---
def header():
    st.markdown('<div style="padding:40px 0;"><h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:10px; color:#D4AF37;">ATELIER</p></div>', unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service["img"], use_container_width=True)
            st.markdown(f'<div class="mini-card"><div style="font-size:0.7rem; font-weight:600;">{service["title"]}</div><div style="color:#D4AF37;">₲{service["price"]:,}</div></div>', unsafe_allow_html=True)
            if st.button("SELECCIONAR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Elegiste {service['title']}")

def booking_section():
    booked_dates = get_booked_dates()
    
    st.markdown("<h3 style='text-align:center; font-size:0.9rem; letter-spacing:3px; margin-top:50px;'>RESERVAR EXPERIENCIA</h3>", unsafe_allow_html=True)
    
    # Mostrar fechas bloqueadas visualmente (Estilo Airbnb con rayas rojas)
    if booked_dates:
        with st.expander("📅 Ver Fechas No Disponibles"):
            cols = st.columns(5)
            for i, d in enumerate(sorted(list(set(booked_dates)))):
                with cols[i % 5]:
                    st.markdown(f'<div class="booked-date">🚫 {d}</div>', unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Selecciona Fecha", min_value=datetime.date.today())
            
            # Bloqueo lógico
            is_date_taken = str(date) in booked_dates
            
            service_list = [s['title'] for s in SERVICES.values()]
            idx_p = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            selected_service = st.selectbox("Servicio", service_list, index=idx_p)
            payment = st.selectbox("Pago", ["Efectivo", "Transferencia / Pix"])
            
            if st.form_submit_button("CONFIRMAR CITA"):
                if is_date_taken:
                    st.error("❌ Esta fecha ya está reservada. Por favor elige otra.")
                elif name and phone:
                    res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": name, "phone": phone, "service": selected_service,
                        "price": next(s['price'] for s in SERVICES.values() if s['title'] == selected_service),
                        "date": str(date), "payment": payment, "status": "Pendiente"
                    }
                    st.session_state.data['appointments'].append(res)
                    save_data(st.session_state.data)
                    st.session_state.last_res = res
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"<div style='text-align:center; padding:30px; background:white; border-radius:15px; border:1px solid #25D366;'><h2>¡CITA AGENDADA!</h2><p>Ref: <b>{res['id']}</b></p></div>", unsafe_allow_html=True)
    
    msg = f"✨ *NAILS BY DIVA*\n*ID:* {res['id']}\n*Servicio:* {res['service']}\n*Fecha:* {res['date']}"
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<br><a href="{url}" target="_blank"><div style="background:#25D366; color:white; padding:15px; border-radius:30px; text-align:center; font-weight:bold;">🚀 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
    if st.button("VOLVER"): st.session_state.view = 'booking'; st.rerun()

# --- 6. PANEL ADMINISTRATIVO (PIE DE PÁGINA) ---
def admin_footer():
    st.markdown('<div class="admin-footer">NAILS BY DIVA v2.0 - SISTEMA INTERNO</div>', unsafe_allow_html=True)
    with st.expander("⚙️ PANEL DE CONTROL (ADMIN)"):
        apts = st.session_state.data['appointments']
        exps = st.session_state.data['expenses']
        
        # Dashboard rápido
        in_real = sum(a['price'] for a in apts if a.get('status') == 'Concluido')
        in_pend = sum(a['price'] for a in apts if a.get('status') == 'Pendiente')
        gst = sum(e['amount'] for e in exps)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ingreso Real", f"₲{in_real:,}")
        c2.metric("Pendiente", f"₲{in_pend:,}")
        c3.metric("Gastos", f"₲{gst:,}")
        c4.metric("Neto", f"₲{in_real-gst:,}")

        

        st.divider()
        col_L, col_R = st.columns(2)
        with col_L:
            st.subheader("Ingresar Gasto")
            with st.form("g_form"):
                con = st.text_input("Concepto")
                mon = st.number_input("Monto", step=1000)
                if st.form_submit_button("Guardar"):
                    st.session_state.data['expenses'].append({"desc": con, "amount": mon, "date": str(datetime.date.today())})
                    save_data(st.session_state.data); st.rerun()
        with col_R:
            st.subheader("Citas")
            for i, a in enumerate(apts):
                if a.get('status') == 'Pendiente':
                    if st.button(f"Concluir {a['client']} ({a['date']})", key=f"fin_{i}"):
                        st.session_state.data['appointments'][i]['status'] = 'Concluido'
                        save_data(st.session_state.data); st.rerun()

# --- 7. FLUJO ---
header()
if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()

# Llamada al pie de página administrativo
admin_footer()