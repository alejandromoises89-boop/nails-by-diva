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

# --- 3. CATÁLOGO DE SERVICIOS (LINKS ACTUALIZADOS) ---
SERVICES = {
    "CAPPING": {
        "title": "Capping Gel",
        "price": 120000,
        "desc": "Fortalecimiento natural.",
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"
    },
    "MAINTENANCE": {
        "title": "Mantenimiento",
        "price": 80000,
        "desc": "Relleno técnico.",
        "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"
    },
    "SEMIPERMANENT": {
        "title": "Semipermanente",
        "price": 70000,
        "desc": "Color de alta duración.",
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"
    },
    "SOFT_GEL": {
        "title": "Soft Gel",
        "price": 150000,
        "desc": "Extensiones premium.",
        "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"
    }
}

# --- 4. ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    
    /* Header Minimalista */
    .header-container { text-align: center; padding: 20px 0; margin-bottom: 20px; }
    .header-title { font-family: 'Playfair Display', serif; font-size: 3rem; letter-spacing: 8px; margin: 0; }
    .header-subtitle { font-size: 0.7rem; letter-spacing: 10px; color: #D4AF37; text-transform: uppercase; }

    /* Tarjetas de Catálogo */
    .mini-card {
        text-align: center;
        padding: 10px;
        background: white;
        border-radius: 12px;
        border: 1px solid #F0F0F0;
        margin-bottom: 10px;
    }
    .service-title { font-size: 0.8rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-top: 10px; }
    .service-price { font-family: 'Playfair Display', serif; font-style: italic; color: #D4AF37; font-size: 1.1rem; margin-bottom: 5px; }

    /* Botones */
    div.stButton > button {
        background-color: transparent !important; color: #333 !important;
        border: 1px solid #ddd !important; border-radius: 20px !important;
        font-size: 0.7rem !important; width: 100% !important; transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #D4AF37 !important; color: #D4AF37 !important; }

    /* Ocultar elementos de Streamlit */
    #MainMenu, header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 5. DEFINICIÓN DE FUNCIONES DE INTERFAZ ---

def header():
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">DIVA</h1>
            <p class="header-subtitle">Nail Atelier</p>
        </div>
    """, unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            # Imagen cargada nativamente para evitar errores de renderizado
            st.image(service["img"], use_container_width=True)
            st.markdown(f"""
                <div class="mini-card">
                    <div class="service-title">{service['title']}</div>
                    <div class="service-price">₲{service['price']:,}</div>
                </div>
            """, unsafe_allow_html=True)
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
            
            c1, c2 = st.columns(2)
            date = c1.date_input("Fecha", min_value=datetime.date.today())
            
            service_list = [s['title'] for s in SERVICES.values()]
            idx_default = 0
            if 'pre_selected' in st.session_state:
                if st.session_state.pre_selected in service_list:
                    idx_default = service_list.index(st.session_state.pre_selected)
            
            selected_service = c2.selectbox("Servicio", service_list, index=idx_default)
            time = st.select_slider("Horario Sugerido", options=[f"{h:02d}:00" for h in range(8, 20)])
            payment = st.selectbox("Preferencia de Pago", ["Efectivo", "Transferencia", "Pix"])
            
            if st.form_submit_button("CONFIRMAR MI EXPERIENCIA"):
                if name and phone:
                    res_id = str(uuid.uuid4())[:6].upper()
                    new_apt = {
                        "id": res_id, "client": name, "phone": phone,
                        "date": str(date), "time": time, "service": selected_service,
                        "payment": payment
                    }
                    st.session_state.data['appointments'].append(new_apt)
                    save_data(st.session_state.data)
                    st.session_state.last_res = new_apt
                    st.session_state.view = 'success'
                    st.rerun()
                else:
                    st.error("Por favor, completa nombre y teléfono.")

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; padding:40px; background:white; border-radius:15px; border:1px solid #D4AF37;'>
        <h2 style='font-family:serif; color:#D4AF37;'>¡RESERVA SOLICITADA!</h2>
        <p style='letter-spacing:2px; font-size:0.8rem;'>ID: {res['id']}</p>
        <hr style='border: 0.1px solid #F0F0F0; width: 50%; margin: 20px auto;'>
        <h4>{res['service']}</h4>
        <p>{res['date']} — {res['time']} hs</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅ VOLVER AL CATÁLOGO"):
        st.session_state.view = 'booking'
        st.rerun()

def admin_panel():
    with st.sidebar:
        st.title("Admin")
        if st.checkbox("Ver Citas"):
            st.write(st.session_state.data['appointments'])

# --- 6. FLUJO PRINCIPAL ---

admin_panel()
header()  # Función llamada correctamente después de ser definida

if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()
