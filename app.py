import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import base64
import urllib.parse

# --- CONFIGURACIÓN PREMIUM ---
st.set_page_config(
    page_title="Diva | Exclusive Nail Studio",
    page_icon="✨",
    layout="centered"
)

# --- PALETA DE COLORES "QUIET LUXURY" ---
# Ivory: #F9F7F2 | Moka: #8E7D71 | Champagne: #E5D1B8 | Deep Brown: #3D3531
COLORS = {
    "bg": "#F9F7F2",
    "card": "#FFFFFF",
    "accent": "#8E7D71",
    "text": "#3D3531",
    "soft": "#E5D1B8"
}

# --- DISEÑO DE INTERFAZ (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Inter:wght@300;400;600&display=swap');

    .stApp {{ background-color: {COLORS['bg']}; color: {COLORS['text']}; font-family: 'Inter', sans-serif; }}
    
    /* Header Estilo Boutique */
    .header-container {{ text-align: center; padding: 40px 0; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 4rem; letter-spacing: 8px; margin: 0; font-weight: 500; text-transform: uppercase; color: {COLORS['text']}; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.5rem; color: {COLORS['accent']}; margin-top: -15px; letter-spacing: 3px; }}

    /* Tarjetas de Servicio Minimalistas */
    .service-card {{
        background: {COLORS['card']};
        border-radius: 0px; /* Estilo editorial cuadrado */
        padding: 0px;
        margin-bottom: 25px;
        border: 1px solid #EEE;
        transition: all 0.4s ease;
    }}
    .service-card:hover {{ border-color: {COLORS['accent']}; transform: translateY(-5px); }}
    .service-info {{ padding: 20px; text-align: center; }}
    .price-badge {{ 
        font-family: 'Inter', sans-serif; font-weight: 300; font-size: 0.9rem;
        letter-spacing: 2px; color: {COLORS['accent']}; border-top: 1px solid #EEE;
        margin-top: 10px; padding-top: 10px;
    }}

    /* Formulario y Botones */
    .stButton button {{
        background-color: {COLORS['text']} !important;
        color: {COLORS['bg']} !important;
        border-radius: 0px !important; /* Estilo Premium Editorial */
        border: none !important;
        height: 50px;
        width: 100%;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    .stButton button:hover {{ background-color: {COLORS['accent']} !important; }}
    
    /* Inputs */
    .stTextInput input, .stSelectbox div, .stDateInput input {{
        border-radius: 0px !important;
        border: 1px solid #DDD !important;
        background-color: white !important;
    }}

    /* Eliminar UI Streamlit */
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
STORAGE_FILE = "diva_luxury_db.json"
BUSINESS_PHONE = "595992698406"

SERVICES = {
    "Capping Gel": {"price": 120000, "img": "https://i.ibb.co/3yxmB8s/nails1.jpg", "desc": "Refuerzo natural para tus uñas."},
    "Mantenimiento": {"price": 80000, "img": "https://i.ibb.co/6YhYyX0/nails2.jpg", "desc": "Renueva tu estilo Diva."},
    "Semipermanente": {"price": 70000, "img": "https://i.ibb.co/xS8K1yK/nails3.jpg", "desc": "Color impecable por semanas."},
    "Soft Gel": {"price": 150000, "img": "https://i.ibb.co/vYm0hNq/nails4.jpg", "desc": "Extensiones de lujo y ligereza."}
}

# --- LÓGICA ---
def load_db():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f: return json.load(f)
    return {"appointments": []}

def save_db(data):
    with open(STORAGE_FILE, "w") as f: json.dump(data, f, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'view' not in st.session_state: st.session_state.view = 'booking'

def format_gs(val): return f"₲ {val:,.0f}".replace(",", ".")

def send_whatsapp(apt):
    # Formato de mensaje ejecutivo para la empresa
    msg = (
        f"✨ *NUEVA RESERVA EXCLUSIVA - DIVA STUDIO*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📎 *ID DE SERVICIO:* #{apt['id']}\n"
        f"👤 *CLIENTE:* {apt['client'].upper()}\n"
        f"💅 *SERVICIO:* {apt['service']}\n"
        f"📅 *FECHA:* {apt['date']}\n"
        f"⏰ *HORA:* {apt['time']} hs\n"
        f"💰 *TOTAL:* {format_gs(apt['amount'])}\n"
        f"💳 *PAGO:* {apt['payment']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📱 *WHATSAPP:* {apt['phone']}\n\n"
        f"_(El comprobante se adjunta a continuación)_"
    )
    return f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"

# --- VISTAS ---
def view_booking():
    st.markdown(f"""
        <div class="header-container">
            <h1 class="logo-main">Diva</h1>
            <div class="logo-sub">Exclusive Studio</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Grid de Servicios Estilo Catálogo de Moda
    cols = st.columns(2)
    for i, (name, info) in enumerate(SERVICES.items()):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="service-card">
                    <div class="service-info">
                        <small style="letter-spacing:3px; color:{COLORS['accent']};">Diva Nails</small>
                        <h3 style="margin:10px 0; font-family:'Cormorant Garamond';">{name}</h3>
                        <p style="font-size:0.8rem; color:gray;">{info['desc']}</p>
                        <div class="price-badge">{format_gs(info['price'])}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid #DDD; margin: 40px 0;'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; font-family:Cormorant Garamond;'>Agendar Experiencia</h3>", unsafe_allow_html=True)
    
    with st.form("booking_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Nombre Completo")
        phone = c2.text_input("Celular (ej. 0981...)")
        
        date = c1.date_input("Día de su cita", min_value=datetime.date.today())
        time = c2.selectbox("Hora", [f"{h:02d}:00" for h in range(8, 20)] + [f"{h:02d}:30" for h in range(8, 20)])
        
        service = c1.selectbox("Servicio Deseado", list(SERVICES.keys()))
        pay = c2.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("RESERVAR TURNO"):
            if name and phone:
                apt_id = str(uuid.uuid4())[:6].upper()
                st.session_state.current_apt = {
                    "id": apt_id, "client": name, "phone": phone,
                    "date": str(date), "time": time, "service": service,
                    "payment": pay, "amount": SERVICES[service]['price']
                }
                st.session_state.view = 'confirmation'
                st.rerun()
            else:
                st.error("Por favor, complete sus datos de contacto.")

def view_confirmation():
    apt = st.session_state.current_apt
    st.markdown("<div style='padding:50px 0;'>", unsafe_allow_html=True)
    st.success(f"Reserva #{apt['id']} lista para confirmación")
    
    st.markdown(f"""
        <div style="background:white; padding:30px; border:1px solid #EEE;">
            <h4 style="font-family:Cormorant Garamond; border-bottom:1px solid #EEE; padding-bottom:10px;">Detalle de su cita</h4>
            <p><b>Servicio:</b> {apt['service']}</p>
            <p><b>Fecha y Hora:</b> {apt['date']} - {apt['time']} hs</p>
            <p><b>Total:</b> {format_gs(apt['amount'])}</p>
            <p><b>Forma de Pago:</b> {apt['payment']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("⚠️ Su cita será confirmada al enviar el comprobante.")
        with st.expander("Ver Datos de Cuenta Bancaria"):
            st.write("**Banco Familiar** | Cta: 815643114")
            st.write("**Ueno Bank** | Alias: 4437206")
        
        proof = st.file_uploader("Subir foto del comprobante", type=['jpg', 'png', 'jpeg'])
        if proof:
            st.session_state.current_apt['proof_b64'] = "Imagen cargada" # En una app real aquí va el b64
            st.success("Comprobante adjuntado con éxito.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("CONFIRMAR Y ENVIAR WHATSAPP"):
        st.session_state.db['appointments'].append(st.session_state.current_apt)
        save_db(st.session_state.db)
        
        wa_link = send_whatsapp(apt)
        st.markdown(f'<a href="{wa_link}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; font-weight:bold;">ABRIR WHATSAPP EMPRESARIAL</div></a>', unsafe_allow_html=True)
        st.balloons()
    
    if st.button("Volver atrás"):
        st.session_state.view = 'booking'
        st.rerun()

# --- NAVEGACIÓN ---
if st.session_state.view == 'booking':
    view_booking()
elif st.session_state.view == 'confirmation':
    view_confirmation()