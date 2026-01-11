import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid

# 1. CONFIGURACIÓN (Debe ser lo primero)
st.set_page_config(
    page_title="Diva | Nail Atelier",
    page_icon="💅",
    layout="wide"
)

# 2. DATOS Y DB
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

# 3. DEFINICIÓN DE SERVICIOS (Links actualizados)
SERVICES = {
    "CAPPING": {
        "title": "Capping Gel",
        "price": 120000,
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"
    },
    "MAINTENANCE": {
        "title": "Mantenimiento",
        "price": 80000,
        "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"
    },
    "SEMIPERMANENT": {
        "title": "Semipermanente",
        "price": 70000,
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?w=400&q=80"
    },
    "SOFT_GEL": {
        "title": "Soft Gel",
        "price": 150000,
        "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"
    }
}

# 4. ESTILOS CSS MINIMALISTAS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    .mini-card { text-align: center; padding: 10px; background: white; border-radius: 12px; margin-bottom: 10px; }
    .service-title { font-size: 0.8rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-top: 10px; }
    .service-price { font-family: 'Playfair Display', serif; font-style: italic; color: #D4AF37; font-size: 1rem; }
    div.stButton > button { 
        background-color: transparent !important; color: #333 !important; border: 1px solid #ddd !important;
        border-radius: 20px !important; font-size: 0.7rem !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #D4AF37 !important; color: #D4AF37 !important; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# 5. TODAS LAS FUNCIONES (Definidas antes del flujo principal)

def header():
    st.markdown("<div style='text-align:center; padding: 20px 0;'><h1 style='font-family:serif; letter-spacing:5px; font-size:2.5rem;'>DIVA</h1><p style='letter-spacing:8px; color:#D4AF37; font-size:0.7rem;'>NAIL ATELIER</p></div>", unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.markdown(f"""
                <div class="mini-card">
                    <img src="{service['img']}" style="width:100%; height:140px; object-fit:cover; border-radius:8px;">
                    <div class="service-title">{service['title']}</div>
                    <div class="service-price">₲{service['price']:,}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("ELEGIR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Seleccionado: {service['title']}")

def booking_section():
    st.markdown("<h3 style='text-align:center; font-size:1rem; letter-spacing:2px; margin-top:30px;'>RESERVAR</h3>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        with st.form("form_reserva"):
            name = st.text_input("Nombre")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            
            # Auto-selección si eligió en el catálogo
            service_list = [s['title'] for s in SERVICES.values()]
            idx_p = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            
            service = st.selectbox("Servicio", service_list, index=idx_p)
            time = st.select_slider("Hora Sugerida", options=[f"{h:02d}:00" for h in range(8, 20)])
            
            if st.form_submit_button("CONFIRMAR CITA"):
                if name and phone:
                    res = {"id": str(uuid.uuid4())[:6].upper(), "client": name, "service": service, "date": str(date), "time": time}
                    st.session_state.last_res = res
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; padding:40px; background:white; border-radius:15px; border:1px solid #D4AF37;'>
        <h2 style='color:#D4AF37;'>¡SOLICITUD ENVIADA!</h2>
        <p>Cita: {res['service']} - {res['date']} a las {res['time']}</p>
        <p style='font-size:0.8rem; color:grey;'>ID: {res['id']}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("VOLVER"):
        st.session_state.view = 'booking'
        st.rerun()

# 6. FLUJO DE EJECUCIÓN (Aquí es donde llamas a las funciones)

header() # Ahora sí la encuentra porque está definida arriba

if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()