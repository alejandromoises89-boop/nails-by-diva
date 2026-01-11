import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nails by Diva | Nail Atelier",
    page_icon="💅",
    layout="wide"
)

# --- 2. GESTIÓN DE DATOS ---
DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "expenses": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"appointments": [], "expenses": [], "settings": {}}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    .header-container { text-align: center; padding: 25px 0; }
    .header-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; letter-spacing: 3px; margin: 0; text-transform: uppercase; font-weight: bold; }
    .header-subtitle { font-size: 0.75rem; letter-spacing: 12px; color: #D4AF37; text-transform: uppercase; margin-top: -5px; }
    .mini-card { text-align: center; padding: 12px; background: white; border-radius: 12px; border: 1px solid #EDEDED; transition: 0.3s; }
    .mini-card:hover { border-color: #D4AF37; }
    .service-price { font-family: 'Playfair Display', serif; font-style: italic; color: #D4AF37; font-size: 1.15rem; margin-top: 5px; }
    .bank-card { background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #D4AF37; margin-bottom: 10px; font-size: 0.9rem; box-shadow: 2px 2px 10px rgba(0,0,0,0.02); }
    div.stButton > button { background-color: transparent !important; color: #333 !important; border: 1px solid #ddd !important; border-radius: 20px !important; font-size: 0.75rem !important; width: 100% !important; text-transform: uppercase; letter-spacing: 1px; }
    div.stButton > button:hover { border-color: #D4AF37 !important; color: #D4AF37 !important; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 5. COMPONENTES ---

def header():
    st.markdown('<div class="header-container"><h1 class="header-title">NAILS BY DIVA</h1><p class="header-subtitle">Atelier</p></div>', unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service["img"], use_container_width=True)
            st.markdown(f'<div class="mini-card"><div style="font-size:0.8rem; font-weight:600; text-transform:uppercase;">{service["title"]}</div><div class="service-price">₲{service["price"]:,}</div></div>', unsafe_allow_html=True)
            if st.button("Elegir", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Seleccionaste {service['title']}")

def booking_section():
    st.markdown("<h3 style='text-align:center; font-size:0.9rem; letter-spacing:4px; margin: 35px 0 25px 0; text-transform:uppercase;'>Agendar Cita</h3>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre y Apellido")
            phone = st.text_input("WhatsApp de contacto")
            date = st.date_input("Fecha preferida", min_value=datetime.date.today())
            
            service_list = [s['title'] for s in SERVICES.values()]
            idx_p = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            selected_service = st.selectbox("Tipo de Servicio", service_list, index=idx_p)
            
            price = next(s['price'] for s in SERVICES.values() if s['title'] == selected_service)
            payment = st.selectbox("Método de Pago", ["Efectivo", "Transferencia / Pix"])
            
            if st.form_submit_button("Confirmar Reserva"):
                if name and phone:
                    res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": name,
                        "service": selected_service,
                        "price": price,
                        "date": str(date),
                        "payment": payment
                    }
                    st.session_state.last_res = res
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; padding:35px; background:white; border-radius:15px; border:1px solid #D4AF37;'>
        <h2 style='font-family:serif; color:#D4AF37;'>¡SOLICITUD RECIBIDA!</h2>
        <p>Gracias por confiar en <b>Nails by Diva</b>.</p>
        <p style='color:gray; font-size:0.8rem;'>Referencia: {res['id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] == "Transferencia / Pix":
        st.markdown("<h4 style='margin-top:25px; text-align:center; font-size:1rem;'>DETALLES DE PAGO</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="bank-card"><b>BANCO FAMILIAR</b><br>Cta: 815643114<br>Nails by Diva</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="bank-card"><b>UENO BANK / PIX</b><br>Alias: <b>4437206</b><br>Nails by Diva</div>', unsafe_allow_html=True)

    # Generación de mensaje de WhatsApp (Oculto hasta enviar)
    msg_body = (
        f"✨ *NUEVA CITA - NAILS BY DIVA*\n\n"
        f"📍 *Cliente:* {res['client']}\n"
        f"💅 *Servicio:* {res['service']}\n"
        f"🗓 *Fecha:* {res['date']}\n"
        f"💰 *Total:* ₲ {res['price']:,}\n"
        f"💳 *Método:* {res['payment']}\n"
        f"🆔 *ID:* {res['id']}"
    )
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg_body)}"
    
    st.markdown(f"""
        <a href="{url}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366; color:white; padding:18px; border-radius:35px; text-align:center; font-weight:bold; font-size:1rem; margin-top:25px; box-shadow: 0 4px 15px rgba(37,211,102,0.2);">
                🚀 ENVIAR COMPROBANTE POR WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)

    if st.button("Regresar al Inicio"):
        st.session_state.view = 'booking'
        st.rerun()

# --- 6. FLUJO PRINCIPAL ---
header()
if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()