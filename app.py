import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN Y DATOS ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"
ADMIN_PIN = "1234"  # <--- CAMBIA TU PIN AQUÍ

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

# --- 2. SERVICIOS RESTAURADOS ---
SERVICES = {
    "CAPPING": {"title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
    "MAINTENANCE": {"title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
    "SEMIPERMANENT": {"title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
    "SOFT_GEL": {"title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
}

# --- 3. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    
    .booked-date { 
        background: repeating-linear-gradient(45deg, #ffebeb, #ffebeb 5px, #ffdbdb 5px, #ffdbdb 10px);
        color: #d00000; padding: 5px; border-radius: 5px; border: 1px solid #ffb3b3; 
        text-align: center; font-size: 0.7rem; font-weight: bold; margin-bottom: 5px;
    }

    .header-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; text-align: center; text-transform: uppercase; margin-bottom: 0; }
    .mini-card { text-align: center; padding: 10px; background: white; border-radius: 12px; border: 1px solid #F0F0F0; margin-bottom: 10px; }
    .admin-footer-link { margin-top: 100px; text-align: center; font-size: 0.6rem; color: #f0f0f0; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE CLIENTE ---
def booking_interface():
    st.markdown('<div style="padding:30px 0;"><h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:10px; color:#D4AF37; font-size:0.8rem;">ATELIER</p></div>', unsafe_allow_html=True)
    
    booked_dates = [a['date'] for a in st.session_state.data['appointments']]
    
    # Catálogo Visual con Imágenes
    cols = st.columns(4)
    for idx, (key, s) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(s["img"], use_container_width=True)
            st.markdown(f'<div class="mini-card"><div style="font-size:0.75rem; font-weight:600;">{s["title"]}</div><div style="color:#D4AF37; font-weight:bold;">₲{s["price"]:,}</div></div>', unsafe_allow_html=True)
            if st.button("Seleccionar", key=f"btn_{key}"):
                st.session_state.pre_selected = s['title']
                st.toast(f"Elegiste {s['title']}")

    st.divider()
    
    # Fechas Bloqueadas (Estilo Airbnb)
    if booked_dates:
        with st.expander("📅 Ver Calendario de Fechas Ocupadas"):
            c = st.columns(6)
            for i, d in enumerate(sorted(list(set(booked_dates)))):
                c[i % 6].markdown(f'<div class="booked-date">🚫 {d}</div>', unsafe_allow_html=True)

    # Formulario de Reserva
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            
            service_list = [s['title'] for s in SERVICES.values()]
            idx_p = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            selected_service = st.selectbox("Servicio seleccionado", service_list, index=idx_p)
            payment = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia / Pix"])
            
            if st.form_submit_button("Confirmar Cita"):
                if str(date) in booked_dates:
                    st.error("Esta fecha ya tiene una reserva con rayas rojas. Elige otra.")
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
    st.markdown(f"""
    <div style='text-align:center; padding:30px; background:white; border-radius:15px; border:1px solid #D4AF37;'>
        <h2 style='color:#D4AF37;'>¡RESERVA REGISTRADA!</h2>
        <p>Tu código es: <b>{res['id']}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] == "Transferencia / Pix":
        st.info("Banco Familiar: 815643114 | Ueno Alias: 4437206")

    msg = f"✨ *NAILS BY DIVA*\n*Cita:* {res['service']}\n*ID:* {res['id']}\n*Fecha:* {res['date']}"
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{url}" target="_blank"><div style="background:#25D366; color:white; padding:15px; border-radius:30px; text-align:center; font-weight:bold; margin-top:20px;">🚀 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
    if st.button("Volver al Inicio"): st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMIN MINI CON PIN ---
def mini_admin_panel():
    st.markdown('<div class="admin-footer-link">.</div>', unsafe_allow_html=True)
    with st.expander("Admin"):
        pin = st.text_input("Ingresar PIN de Seguridad", type="password")
        if pin == ADMIN_PIN:
            apts = st.session_state.data['appointments']
            exps = st.session_state.data['expenses']
            
            in_r = sum(a['price'] for a in apts if a.get('status') == 'Concluido')
            gst = sum(e['amount'] for e in exps)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingreso Real", f"₲{in_r:,}")
            c2.metric("Gastos", f"₲{gst:,}")
            c3.metric("Balance Neto", f"₲{in_r-gst:,}")
            
            st.divider()
            t1, t2 = st.tabs(["Citas Pendientes", "Registrar Gasto"])
            with t1:
                for i, a in enumerate(apts):
                    if a.get('status') == 'Pendiente':
                        if st.button(f"Concluir: {a['client']} ({a['date']})", key=f"c_{i}"):
                            st.session_state.data['appointments'][i]['status'] = 'Concluido'
                            save_data(st.session_state.data); st.rerun()
            with t2:
                with st.form("gastos"):
                    d = st.text_input("Concepto")
                    m = st.number_input("Monto", step=1000)
                    if st.form_submit_button("Guardar Gasto"):
                        st.session_state.data['expenses'].append({"desc": d, "amount": m, "date": str(datetime.date.today())})
                        save_data(st.session_state.data); st.rerun()
        elif pin != "2026":
            st.error("Acceso denegado")

# --- 6. EJECUCIÓN ---
if st.session_state.view == 'booking':
    booking_interface()
else:
    success_view()

mini_admin_panel()