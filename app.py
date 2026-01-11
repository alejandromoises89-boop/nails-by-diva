import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Diva | Nail Atelier",
    page_icon="💅",
    layout="wide"
)

# Archivo de base de datos
DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

# --- DATOS ESTÁTICOS (IMÁGENES ACTUALIZADAS) ---
SERVICES = {
    "CAPPING": {
        "title": "💅 Capping Gel",
        "price": 120000,
        "desc": "Recubrimiento de gel para máxima resistencia.",
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800&q=80"
    },
    "MAINTENANCE": {
        "title": "✨ Mantenimiento",
        "price": 80000,
        "desc": "Relleno y perfección de tu set actual.",
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&q=80"
    },
    "SEMIPERMANENT": {
        "title": "🎨 Semipermanente",
        "price": 70000,
        "desc": "Color impecable con brillo espejo.",
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?w=800&q=80"
    },
    "SOFT_GEL": {
        "title": "💎 Soft Gel",
        "price": 150000,
        "desc": "Extensiones premium ultra ligeras.",
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?w=800&q=80"
    }
}

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@700&family=Montserrat:wght@300;400;600&display=swap');
    
    .stApp { background-color: #FFFFFF; color: #1a1a1a; font-family: 'Montserrat', sans-serif; }
    h1, h2, h3 { font-family: 'Bodoni Moda', serif !important; color: #000000 !important; }

    /* Tarjetas Negras */
    .service-card {
        background-color: #000000;
        padding: 25px;
        text-align: center;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #111;
    }
    .service-card h4 { color: #D4AF37 !important; margin-top: 0; }
    .service-card p { color: #888 !important; font-size: 0.85rem; }

    /* Botón Reservar */
    div.stButton > button {
        background-color: #D4AF37 !important;
        color: white !important;
        border-radius: 0px !important;
        font-weight: 600;
        letter-spacing: 2px;
        width: 100%;
        border: none !important;
        padding: 15px;
    }
    
    /* Inputs */
    input, select, textarea {
        border-radius: 0px !important;
        border: 1px solid #000 !important;
    }

    #MainMenu, header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except:
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- VISTA PRINCIPAL ---

def header():
    st.markdown("<div style='text-align:center; padding: 40px 0;'><h1 style='font-size:4.5rem; margin:0;'>DIVA</h1><p style='letter-spacing:10px; color:#D4AF37; margin-top:-10px;'>NAIL ATELIER</p></div>", unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(len(SERVICES))
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            # Imagen con altura fija para uniformidad
            st.markdown(f'<img src="{service["img"]}" style="width:100%; height:250px; object-fit:cover;">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="service-card">
                <h4>{service['title']}</h4>
                <p>{service['desc']}</p>
                <h3 style="color:#D4AF37 !important; margin:10px 0;">₲ {service['price']:,}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Al hacer clic, se guarda el servicio y se recarga la página con el ancla en la URL
            if st.button(f"ELEGIR {key}", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                # Esta es la forma más efectiva de hacer scroll en Streamlit sin JS externo
                st.markdown('<script>window.location.href="#formulario";</script>', unsafe_allow_html=True)
                st.rerun()

def booking_section():
    st.markdown("<div id='formulario'></div>", unsafe_allow_html=True)
    st.markdown("<br><br><br><h2 style='text-align:center;'>RESERVAR MI TURNO</h2>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            phone = st.text_input("WhatsApp (ej: 0992698406)")
            
            c1, c2 = st.columns(2)
            date = c1.date_input("Fecha", min_value=datetime.date.today())
            
            service_list = [s['title'] for s in SERVICES.values()]
            default_idx = 0
            if 'pre_selected' in st.session_state:
                if st.session_state.pre_selected in service_list:
                    default_idx = service_list.index(st.session_state.pre_selected)
            
            selected_service = c2.selectbox("Servicio", service_list, index=default_idx)
            
            time_slots = []
            for h in range(8, 20):
                time_slots.append(f"{h:02d}:00")
                time_slots.append(f"{h:02d}:30")
                
            time = c1.selectbox("Horario", time_slots)
            payment = c2.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
            
            if st.form_submit_button("AGENDAR AHORA"):
                if name and phone:
                    res_id = str(uuid.uuid4())[:6].upper()
                    new_apt = {
                        "id": res_id, "client": name, "phone": phone,
                        "date": str(date), "time": time, "service": selected_service,
                        "payment": payment, "status": "PENDIENTE"
                    }
                    st.session_state.data['appointments'].append(new_apt)
                    save_data(st.session_state.data)
                    st.session_state.last_res = new_apt
                    st.session_state.view = 'success'
                    st.rerun()
                else:
                    st.error("Por favor completa tu nombre y teléfono.")

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; background:#000; color:#fff; padding:60px; border:2px solid #D4AF37;'>
        <h1 style='color:#D4AF37 !important; font-size:3rem;'>¡RESERVA RECIBIDA!</h1>
        <p style='letter-spacing:3px;'>CÓDIGO DE SEGUIMIENTO: {res['id']}</p>
        <hr style='border-color:#333; width:50%; margin: 20px auto;'>
        <h3>{res['service']}</h3>
        <p>{res['date']} a las {res['time']} hs</p>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br><h2 style='text-align:center;'>DATOS DE PAGO</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='text-align:center; border:1px solid #EEE; padding:20px;'>", unsafe_allow_html=True)
            st.subheader("Banco Familiar")
            st.code("Cuenta: 815643114")
            qr_f = st.session_state.data['settings'].get('qr_familiar')
            if qr_f: st.image(base64.b64decode(qr_f), width=280)
            else: st.info("QR no disponible. Usa el número de cuenta.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div style='text-align:center; border:1px solid #EEE; padding:20px;'>", unsafe_allow_html=True)
            st.subheader("Ueno Bank / Pix")