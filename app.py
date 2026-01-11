import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Diva | Nail Atelier",
    page_icon="💅",
    layout="wide"
)

# --- 2. LÓGICA DE DATOS ---
DB_FILE = "nails_db.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- 3. CATÁLOGO DE SERVICIOS CON PRECIOS ---
SERVICES = {
    "CAPPING": {"title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
    "MAINTENANCE": {"title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
    "SEMIPERMANENT": {"title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
    "SOFT_GEL": {"title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
}

# --- 4. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    .header-container { text-align: center; padding: 20px 0; }
    .header-title { font-family: 'Playfair Display', serif; font-size: 3rem; letter-spacing: 8px; margin: 0; }
    .header-subtitle { font-size: 0.7rem; letter-spacing: 10px; color: #D4AF37; text-transform: uppercase; }
    .mini-card { text-align: center; padding: 10px; background: white; border-radius: 12px; border: 1px solid #F0F0F0; }
    .service-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-top: 10px; }
    .service-price { font-family: 'Playfair Display', serif; font-style: italic; color: #D4AF37; font-size: 1.1rem; }
    .bank-card { background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #D4AF37; margin-bottom: 10px; }
    div.stButton > button { background-color: transparent !important; color: #333 !important; border: 1px solid #ddd !important; border-radius: 20px !important; font-size: 0.7rem !important; width: 100% !important; }
    div.stButton > button:hover { border-color: #D4AF37 !important; color: #D4AF37 !important; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES ---

def header():
    st.markdown('<div class="header-container"><h1 class="header-title">DIVA</h1><p class="header-subtitle">Nail Atelier</p></div>', unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service["img"], use_container_width=True)
            st.markdown(f'<div class="mini-card"><div class="service-title">{service["title"]}</div><div class="service-price">₲{service["price"]:,}</div></div>', unsafe_allow_html=True)
            if st.button("SELECCIONAR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Elegiste {service['title']}")

def booking_section():
    st.markdown("<h3 style='text-align:center; font-size:1rem; letter-spacing:3px; margin: 40px 0 20px 0;'>RESERVAR CITA</h3>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            
            service_list = [s['title'] for s in SERVICES.values()]
            idx_default = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            selected_service = st.selectbox("Servicio", service_list, index=idx_default)
            
            # Obtener precio dinámicamente
            current_price = 0
            for s in SERVICES.values():
                if s['title'] == selected_service: current_price = s['price']
            
            st.markdown(f"<p style='text-align:right; color:#D4AF37; font-weight:600;'>Total: ₲ {current_price:,}</p>", unsafe_allow_html=True)
            
            payment = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Pix"])
            
            if st.form_submit_button("CONFIRMAR RESERVA"):
                if name and phone:
                    res = {"id": str(uuid.uuid4())[:6].upper(), "client": name, "service": selected_service, "price": current_price, "date": str(date), "payment": payment}
                    st.session_state.last_res = res
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; padding:30px; background:white; border-radius:15px; border:1px solid #D4AF37;'>
        <h2 style='font-family:serif; color:#D4AF37;'>¡RESERVA SOLICITADA!</h2>
        <p><b>{res['service']}</b> - ₲ {res['price']:,}</p>
        <p>ID: {res['id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<h4 style='margin-top:20px;'>Datos para el Pago:</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="bank-card"><b>BANCO FAMILIAR</b><br>Cta: 815643114<br>Diva Atelier</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="bank-card"><b>UENO / PIX</b><br>Alias: 4437206<br>Diva Atelier</div>', unsafe_allow_html=True)

    if st.button("⬅ VOLVER"):
        st.session_state.view = 'booking'
        st.rerun()

# --- 6. FLUJO ---
header()
if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()
