import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import urllib.parse
from streamlit.components.v1 import html

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nails by Diva | Premium Booking",
    page_icon="💅",
    layout="wide"
)

# Archivo de base de datos
DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

# Datos Estáticos
SERVICES = {
    "CAPPING": {
        "title": "💅 Capping Gel",
        "price": 120000,
        "desc": "Recubrimiento de gel sobre la uña natural para mayor resistencia.",
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&q=80&w=800"
    },
    "MAINTENANCE": {
        "title": "✨ Mantenimiento",
        "price": 80000,
        "desc": "Relleno y corrección del servicio anterior.",
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?auto=format&fit=crop&q=80&w=800"
    },
    "SEMIPERMANENT": {
        "title": "🎨 Semipermanente",
        "price": 70000,
        "desc": "Esmaltado de larga duración con curado UV/LED.",
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?auto=format&fit=crop&q=80&w=800"
    },
    "SOFT_GEL": {
        "title": "💎 Soft Gel",
        "price": 150000,
        "desc": "Extensión completa con tips de gel.",
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&q=80&w=800"
    }
}

# --- ESTILOS CSS (Blanco y Negro Luxury) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@700&family=Montserrat:wght@300;400;600&display=swap');
    
    .stApp {
        background-color: #FFFFFF; /* Fondo Blanco */
        color: #1a1a1a;
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Bodoni Moda', serif !important;
        color: #000000 !important;
        letter-spacing: -1px;
    }

    /* Tarjetas de Servicio Negras */
    .service-card {
        background-color: #000000; /* Fondo Negro */
        border-radius: 0px;
        padding: 25px;
        transition: 0.3s;
        margin-bottom: 10px;
        text-align: center;
    }
    .service-card h4 { color: #D4AF37 !important; margin-bottom: 5px; }
    .service-card p { color: #888888 !important; font-size: 0.85rem; }

    /* Botones Dorados */
    div.stButton > button {
        background-color: #D4AF37 !important;
        color: white !important;
        border: none !important;
        border-radius: 0px !important;
        font-weight: 600;
        width: 100%;
        padding: 12px;
    }

    /* Formulario */
    [data-testid="stForm"] {
        background-color: #f9f9f9;
        border: 2px solid #000;
        border-radius: 0px;
        padding: 40px;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu, header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- UI COMPONENTES ---

def header():
    st.markdown("<div style='text-align:center; padding: 40px 0;'><h1 style='font-size:5rem;'>DIVA</h1><p style='letter-spacing:10px; color:#D4AF37;'>NAIL ATELIER</p></div>", unsafe_allow_html=True)

def service_catalog():
    cols = st.columns(len(SERVICES))
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service['img'])
            st.markdown(f"""
            <div class="service-card">
                <h4>{service['title']}</h4>
                <p>{service['desc']}</p>
                <h3 style="color:#D4AF37 !important;">₲ {service['price']:,}</h3>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Reservar", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                # Script para bajar al formulario
                html("<script>window.parent.document.getElementById('booking_section').scrollIntoView({behavior: 'smooth'});</script>")

def booking_form():
    st.markdown("<div id='booking_section'></div>", unsafe_allow_html=True)
    st.markdown("<br><br><h2 style='text-align:center;'>RESERVAR TURNO</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("main_form"):
            name = st.text_input("Nombre y Apellido")
            phone = st.text_input("WhatsApp (ej: 0992...)")
            
            col_a, col_b = st.columns(2)
            date = col_a.date_input("Fecha", min_value=datetime.date.today())
            
            service_options = [s['title'] for s in SERVICES.values()]
            idx = 0
            if 'pre_selected' in st.session_state:
                idx = service_options.index(st.session_state.pre_selected)
            
            service = col_b.selectbox("Servicio", service_options, index=idx)
            time = st.selectbox("Hora", [f"{h:02d}:{m}" for h in range(8, 20) for m in ["00", "30"]])
            payment = st.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
            
            if st.form_submit_button("CONFIRMAR MI LUGAR"):
                if name and phone:
                    res_id = str(uuid.uuid4())[:6].upper()
                    new_apt = {
                        "id": res_id, "client": name, "phone": phone,
                        "date": str(date), "time": time, "service": service,
                        "payment": payment, "status": "PENDIENTE"
                    }
                    st.session_state.data['appointments'].append(new_apt)
                    save_data(st.session_state.data)
                    st.session_state.last_res = new_apt
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; background:#000; color:#fff; padding:50px; border-radius:0px;'>
        <h1 style='color:#D4AF37 !important;'>¡RESERVA EXITOSA!</h1>
        <p>Código: {res['id']}</p>
        <hr style='border-color:#333'>
        <h3>{res['service']} | {res['date']} | {res['time']} hs</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br><h2 style='text-align:center;'>REALIZAR PAGO</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='text-align:center; padding:20px; border:1px solid #ddd;'>", unsafe_allow_html=True)
            st.subheader("Banco Familiar")
            st.write("Cuenta: 815643114")
            qr_f = st.session_state.data['settings'].get('qr_familiar')
            if qr_f: st.image(base64.b64decode(qr_f), width=250)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div style='text-align:center; padding:20px; border:1px solid #ddd;'>", unsafe_allow_html=True)
            st.subheader("Ueno Bank / Pix")
            st.write("Alias: 4437206")
            qr_u = st.session_state.data['settings'].get('qr_ueno')
            if qr_u: st.image(base64.b64decode(qr_u), width=250)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Volver al Inicio"):
        st.session_state.view = 'booking'
        st.rerun()

# --- MAIN ---
header()
if st.session_state.view == 'booking':
    service_catalog()
    booking_form()
else:
    success_view()

import uuid # Importante para generar IDs