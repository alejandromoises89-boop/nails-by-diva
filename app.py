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
ADMIN_PIN = "2026" 

# Horarios disponibles en el atelier
TIME_SLOTS = ["08:00", "09:30", "11:00", "13:00", "14:30", "16:00", "17:30"]

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

# --- 2. LÓGICA DE BLOQUEO DE HORARIOS ---
def get_blocked_slots(selected_date):
    # Un horario se bloquea si ya existe una cita "Concluida" o "Pendiente" para ese día y hora
    date_str = str(selected_date)
    return [a['time'] for a in st.session_state.data['appointments'] 
            if a['date'] == date_str]

# --- 3. SERVICIOS ---
SERVICES = {
    "CAPPING": {"title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
    "MAINTENANCE": {"title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
    "SEMIPERMANENT": {"title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
    "SOFT_GEL": {"title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
}

# --- 4. ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .header-title { font-family: serif; font-size: 2.5rem; text-align: center; color: #333; }
    .whatsapp-btn {
        background-color: #25D366; color: white !important; padding: 15px 25px;
        border-radius: 50px; text-align: center; text-decoration: none;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; margin: 20px auto; max-width: 300px;
    }
    .whatsapp-icon { width: 22px; margin-right: 10px; }
    .admin-footer { font-size: 0.4rem; color: #F0F0F0; text-align: center; margin-top: 150px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 5. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:8px; color:#D4AF37; font-size:0.7rem; margin-top:-10px;">ATELIER</p>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for idx, (key, s) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(s["img"], use_container_width=True)
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"btn_{key}"):
                st.session_state.pre_selected = s['title']

    st.divider()
    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        with st.form("main_booking"):
            n = st.text_input("Nombre y Apellido")
            p = st.text_input("WhatsApp")
            d = st.date_input("Fecha", min_value=datetime.date.today())
            
            # Filtrar horarios disponibles
            blocked = get_blocked_slots(d)
            available_slots = [s for s in TIME_SLOTS if s not in blocked]
            
            t = st.selectbox("Horario Disponible", available_slots if available_slots else ["Sin horarios disponibles"])
            
            s_list = [s['title'] for s in SERVICES.values()]
            idx_s = s_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            serv = st.selectbox("Servicio", s_list, index=idx_s)
            pay = st.radio("Método de Pago", ["Efectivo", "Transferencia / Pix"], horizontal=True)
            
            if st.form_submit_button("REVISAR DISPONIBILIDAD"):
                if n and p and t != "Sin horarios disponibles":
                    st.session_state.temp_res = {
                        "id": str(uuid.uuid4())[:6].upper(), "client": n, "phone": p, 
                        "service": serv, "price": next(s['price'] for s in SERVICES.values() if s['title'] == serv), 
                        "date": str(d), "time": t, "payment": pay, "status": "Pendiente"
                    }
                    st.session_state.view = 'confirm'; st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown(f"<h3 style='text-align:center;'>Reserva para el {res['date']} a las {res['time']}</h3>", unsafe_allow_html=True)
    
    pago_ok = True
    if res['payment'] == "Transferencia / Pix":
        pago_ok = False
        st.warning(f"Total: ₲{res['price']:,} | Familiar: 815643114 | Ueno: 4437206")
        file = st.file_uploader("SUBIR COMPROBANTE", type=['jpg', 'png', 'jpeg'])
        if file: pago_ok = True

    if pago_ok:
        msg = f"💅 *RESERVA NAILS BY DIVA*\n*ID:* #{res['id']}\n*Fecha:* {res['date']}\n*Hora:* {res['time']}\n*Servicio:* {res['service']}"
        url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-icon">ENVIAR Y BLOQUEAR HORARIO</a>', unsafe_allow_html=True)
        if st.button("Finalizar"):
            st.session_state.data['appointments'].append(res); save_data(st.session_state.data)
            st.session_state.view = 'booking'; st.rerun()

# --- 6. PANEL ADMIN ---
def admin_footer():
    st.markdown('<div class="admin-footer">.</div>', unsafe_allow_html=True)
    with st.expander("⚙️"):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            apts = st.session_state.data['appointments']
            
            # Métricas
            in_r = sum(a['price'] for a in apts if a.get('status') == 'Concluido')
            pend = sum(a['price'] for a in apts if a.get('status') == 'Pendiente')
            st.metric("INGRESOS COBRADOS", f"₲{in_r:,}")
            st.metric("PENDIENTE POR COBRAR", f"₲{pend:,}")

            st.subheader("Citas de Hoy / Pendientes")
            for i, a in enumerate(apts):
                if a['status'] == 'Pendiente':
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"📌 {a['date']} - {a['time']} | {a['client']} ({a['service']})")
                    if col2.button(f"Cobrado ✅", key=f"f_{i}"):
                        st.session_state.data['appointments'][i]['status'] = 'Concluido'
                        save_data(st.session_state.data); st.rerun()

if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_footer()
