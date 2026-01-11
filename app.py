import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nails | by Diva",
    page_icon="💅",
    layout="wide"
)

# Archivo de base de datos
DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

# --- LÓGICA DE DATOS ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'view' not in st.session_state:
    st.session_state.view = 'booking'

# --- DATOS DE SERVICIOS (LINKS CORREGIDOS) ---
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

# --- ESTILOS CSS MINIMALISTAS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    
    /* Contenedor de Catálogo */
    .mini-card {
        text-align: center;
        padding: 10px;
        background: white;
        border-radius: 12px;
        transition: transform 0.2s ease;
    }
    
    .mini-card:hover { transform: translateY(-5px); }

    .service-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 10px;
        color: #1a1a1a;
    }
    
    .service-price {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.1rem;
        color: #D4AF37;
        margin-bottom: 10px;
    }

    /* Botón Minimalista */
    div.stButton > button {
        background-color: transparent !important;
        color: #333 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 20px !important;
        font-size: 0.7rem !important;
        padding: 5px 15px !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block;
    }
    
    div.stButton > button:hover {
        border-color: #D4AF37 !important;
        color: #D4AF37 !important;
    }

    /* Ocultar elementos innecesarios */
    [data-testid="stHeader"], footer {display: none;}
</style>
""", unsafe_allow_html=True)

def show_catalog():
    # Usamos 4 columnas para que las tarjetas sean pequeñas
    cols = st.columns(4) 
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            # Imagen con bordes redondeados y aspecto cuadrado
            st.markdown(f"""
                <div class="mini-card">
                    <img src="{service['img']}" style="width:100%; height:150px; object-fit:cover; border-radius:10px;">
                    <div class="service-title">{service['title']}</div>
                    <div class="service-price">₲{service['price']:,}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("ELEGIR", key=f"mini_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Añadido: {service['title']}")

def booking_section():
    st.markdown("<br><br><h2 style='text-align:center; letter-spacing:3px;'>RESERVAR CITA</h2>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre y Apellido")
            phone = st.text_input("WhatsApp")
            c1, c2 = st.columns(2)
            date = c1.date_input("Fecha", min_value=datetime.date.today())
            service_list = [s['title'] for s in SERVICES.values()]
            default_idx = 0
            if 'pre_selected' in st.session_state:
                if st.session_state.pre_selected in service_list:
                    default_idx = service_list.index(st.session_state.pre_selected)
            selected_service = c2.selectbox("Servicio", service_list, index=default_idx)
            time_slots = [f"{h:02d}:{m}" for h in range(8, 20) for m in ["00", "30"]]
            time = c1.selectbox("Horario", time_slots)
            payment = c2.selectbox("Pago", ["Transferencia", "Pix", "Efectivo"])
            
            if st.form_submit_button("CONFIRMAR CITA"):
                if name and phone:
                    res_id = str(uuid.uuid4())[:6].upper()
                    new_apt = {"id": res_id, "client": name, "phone": phone, "date": str(date), "time": time, "service": selected_service, "payment": payment}
                    st.session_state.data['appointments'].append(new_apt)
                    save_data(st.session_state.data)
                    st.session_state.last_res = new_apt
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"<div style='text-align:center; background:#000; color:#fff; padding:40px;'><h1>¡RESERVA OK!</h1><p>ID: {res['id']}</p><h2>{res['service']}</h2></div>", unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.subheader("Datos de Pago")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Banco Familiar: 815643114")
            qr_f = st.session_state.data['settings'].get('qr_familiar')
            if qr_f: st.image(f"data:image/png;base64,{qr_f}")
        with c2:
            st.write("Ueno / Pix: Alias 4437206")
            qr_u = st.session_state.data['settings'].get('qr_ueno')
            if qr_u: st.image(f"data:image/png;base64,{qr_u}")

    if st.button("VOLVER"):
        st.session_state.view = 'booking'
        st.rerun()

def admin_panel():
    with st.sidebar:
        if st.checkbox("Panel Admin"):
            st.header("Cargar QRs")
            up_f = st.file_uploader("QR Familiar")
            if up_f:
                st.session_state.data['settings']['qr_familiar'] = base64.b64encode(up_f.read()).decode()
                save_data(st.session_state.data)
                st.success("QR Familiar Guardado")
            
            up_u = st.file_uploader("QR Ueno")
            if up_u:
                st.session_state.data['settings']['qr_ueno'] = base64.b64encode(up_u.read()).decode()
                save_data(st.session_state.data)
                st.success("QR Ueno Guardado")

# --- FLUJO PRINCIPAL (ORDENADO) ---
admin_panel()
header() # Llamada a la función

if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()