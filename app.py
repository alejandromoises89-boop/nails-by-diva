import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Diva | Nail Atelier",
    page_icon="💅",
    layout="wide"
)

# Archivo de base de datos
DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

# --- DATOS DE SERVICIOS CON TUS IMÁGENES ---
# Nota: He usado las URLs directas de las imágenes de ejemplo que proporcionaste
SERVICES = {
    "CAPPING": {
        "title": "💅 Capping Gel",
        "price": 120000,
        "desc": "Fortalecimiento sobre tu uña natural.",
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800&q=80"
    },
    "MAINTENANCE": {
        "title": "✨ Mantenimiento",
        "price": 80000,
        "desc": "Relleno y perfeccionamiento técnico.",
        "img": "https://i.ibb.co/bjf3G85q/images-1.jpg" # Imagen de lima/manicura
    },
    "SEMIPERMANENT": {
        "title": "🎨 Semipermanente",
        "price": 70000,
        "desc": "Color duradero con brillo extremo.",
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?w=800&q=80"
    },
    "SOFT_GEL": {
        "title": "💎 Soft Gel",
        "price": 150000,
        "desc": "Extensiones premium con tips de gel.",
        "img": "https://ibb.co/5W26L2wn" # Imagen de tips transparentes
    }
}

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@700&family=Montserrat:wght@300;400;600&display=swap');
    
    .stApp { background-color: #FFFFFF; color: #1a1a1a; font-family: 'Montserrat', sans-serif; }
    
    /* Títulos Estilo Boutique */
    h1, h2, h3 { font-family: 'Bodoni Moda', serif !important; color: #000000 !important; text-transform: uppercase; }

    /* Tarjetas de Servicio en Negro */
    .service-card {
        background-color: #000000;
        padding: 20px;
        text-align: center;
        border: 1px solid #111;
        margin-bottom: 10px;
    }
    .service-card h4 { color: #D4AF37 !important; margin-bottom: 5px; font-weight: 600; }
    .service-card p { color: #888 !important; font-size: 0.8rem; height: 40px; }
    
    /* Botón de Reserva Dorado */
    div.stButton > button {
        background-color: #D4AF37 !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        font-weight: 600;
        letter-spacing: 2px;
        width: 100%;
        padding: 12px;
        transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #B8962E !important; color: white !important; }

    /* Estilo del Formulario */
    [data-testid="stForm"] { border: 1px solid #000 !important; padding: 30px !important; border-radius: 0px; }

    #MainMenu, header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- INTERFAZ DE USUARIO ---

def header():
    st.markdown("<div style='text-align:center; padding: 40px 0;'><h1 style='font-size:4rem; margin:0; letter-spacing:5px;'>DIVA</h1><p style='letter-spacing:10px; color:#D4AF37; margin-top:-10px;'>NAIL ATELIER</p></div>", unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(len(SERVICES))
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            # Imagen con formato horizontal/cuadrado consistente
            st.markdown(f'<img src="{service["img"]}" style="width:100%; height:280px; object-fit:cover; border-bottom: 3px solid #D4AF37;">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="service-card">
                <h4>{service['title']}</h4>
                <p>{service['desc']}</p>
                <h3 style="color:#D4AF37 !important; margin:10px 0;">₲ {service['price']:,}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón que activa el scroll
            if st.button(f"SELECCIONAR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                # Script de scroll instantáneo
                st.markdown('<script>window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});</script>', unsafe_allow_html=True)

def booking_section():
    st.markdown("<br><br><br><h2 style='text-align:center; letter-spacing:3px;'>RESERVAR CITA</h2>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre y Apellido")
            phone = st.text_input("WhatsApp de contacto")
            
            c1, c2 = st.columns(2)
            date = c1.date_input("Fecha preferida", min_value=datetime.date.today())
            
            service_list = [s['title'] for s in SERVICES.values()]
            default_idx = 0
            if 'pre_selected' in st.session_state:
                if st.session_state.pre_selected in service_list:
                    default_idx = service_list.index(st.session_state.pre_selected)
            
            selected_service = c2.selectbox("Servicio confirmado", service_list, index=default_idx)
            
            # Horarios
            time_slots = [f"{h:02d}:{m}" for h in range(8, 20) for m in ["00", "30"]]
            time = c1.selectbox("Horario sugerido", time_slots)
            payment = c2.selectbox("Preferencia de Pago", ["Transferencia", "Pix", "Efectivo"])
            
            if st.form_submit_button("CONFIRMAR MI EXPERIENCIA"):
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
                    st.warning("Diva, necesitamos tu nombre y WhatsApp para agendar.")

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; background:#000; color:#fff; padding:60px; border:2px solid #D4AF37;'>
        <h1 style='color:#D4AF37 !important;'>¡RESERVA SOLICITADA!</h1>
        <p style='letter-spacing:2px;'>ID DE SEGUIMIENTO: {res['id']}</p>
        <hr style='border-color:#333; width:30%; margin: 20px auto;'>
        <h2 style='color:white !important;'>{res['service']}</h2>
        <p style='font-size:1.2rem;'>{res['date']} — {res['time']} hs</p>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br><h2 style='text-align:center;'>MÉTODOS DE PAGO</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='text-align:center; border:1px solid #EEE; padding:25px;'>", unsafe_allow_html=True)
            st.subheader("BANCO FAMILIAR")
            st.code("Cuenta: 815643114")
            qr_f = st.session_state.data['settings'].get('qr_familiar')
            if qr_f: st.image(base64.b64decode(qr_f), width=300)
            else: st.caption("Sube tu QR desde el panel admin")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div style='text-align:center; border:1px solid #EEE; padding:25px;'>", unsafe_allow_html=True)
            st.subheader("UENO BANK / PIX")
            st.code("Alias: 4437206")
            qr_u = st.session_state.data['settings'].get('qr_ueno')
            if qr_u: st.image(base64.b64decode(qr_u), width=300)
            else: st.caption("Sube tu QR desde el panel admin")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL MENÚ"):
        st.session_state.view = 'booking'
        st.rerun()

# --- NAVEGACIÓN ---
header()
if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()