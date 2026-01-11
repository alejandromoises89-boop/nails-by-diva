import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import base64
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Nails by Diva | Exclusive Salon",
    page_icon="💅",
    layout="centered"
)

# --- SISTEMA DE DISEÑO (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@300;400;600&display=swap');

    :root {
        --gold: #D4AF37;
        --dark-bg: #0E0E0E;
        --glass: rgba(255, 255, 255, 0.03);
    }

    .stApp { background-color: var(--dark-bg); color: #E0E0E0; font-family: 'Montserrat', sans-serif; }

    /* Header & Logos */
    .main-header { text-align: center; padding: 2rem 0; }
    .logo-text { font-family: 'Playfair Display', serif; font-size: 3.5rem; letter-spacing: 5px; color: white; margin: 0; }
    .logo-subtext { font-family: 'Playfair Display', serif; font-style: italic; color: var(--gold); font-size: 1.5rem; margin-top: -15px; }

    /* Cards de Servicios */
    .service-container {
        background: var(--glass);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px;
        padding: 20px;
        transition: all 0.3s ease;
        text-align: center;
        margin-bottom: 20px;
    }
    .service-container:hover { border-color: var(--gold); background: rgba(212, 175, 55, 0.05); }
    
    .price-tag { 
        background: var(--gold); color: black; padding: 4px 12px; 
        border-radius: 50px; font-weight: bold; font-size: 0.9rem;
        display: inline-block; margin-top: 10px;
    }

    /* Botones Premium */
    .stButton button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
        color: black !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3rem;
        letter-spacing: 1px;
        transition: 0.4s !important;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(212, 175, 55, 0.3); }

    /* Inputs Estilizados */
    .stTextInput input, .stSelectbox div, .stDateInput input {
        border-radius: 10px !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
    }

    /* Hide redundant UI */
    #MainMenu, header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- LOGICA DE NEGOCIO ---
STORAGE_FILE = "diva_data_v2.json"
BUSINESS_PHONE = "595992698406"

SERVICES = {
    "💅 Capping Gel": {"price": 120000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400"},
    "✨ Mantenimiento": {"price": 80000, "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?w=400"},
    "🎨 Semipermanente": {"price": 70000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400"},
    "💎 Soft Gel": {"price": 150000, "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?w=400"}
}

def load_db():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f: return json.load(f)
    return {"apts": [], "settings": {}}

def save_db(data):
    with open(STORAGE_FILE, "w") as f: json.dump(data, f, indent=4)

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- UTILITARIOS ---
def img_to_b64(file):
    if not file: return None
    return f"data:image/png;base64,{base64.b64encode(file.getvalue()).decode()}"

def format_gs(val): return f"₲ {val:,.0f}".replace(",", ".")

def get_whatsapp_link(apt):
    # Mensaje ultra detallado para la dueña
    msg = (
        f"👑 *NUEVA CITA CONFIRMADA*\n"
        f"--------------------------\n"
        f"🆔 *ID:* `{apt['id']}`\n"
        f"👤 *Cliente:* {apt['client']}\n"
        f"📱 *Cel:* {apt['phone']}\n"
        f"💅 *Servicio:* {apt['service']}\n"
        f"📅 *Fecha:* {apt['date']}\n"
        f"⏰ *Hora:* {apt['time']} hs\n"
        f"💰 *Total:* {format_gs(apt['amount'])}\n"
        f"💳 *Método:* {apt['payment']}\n"
        f"--------------------------\n"
        f"✨ _Por favor, verifique el comprobante adjunto._"
    )
    return f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"

# --- VISTAS ---
def render_header():
    st.markdown("""
        <div class="main-header">
            <h1 class="logo-text">NAILS</h1>
            <div class="logo-subtext">by Diva</div>
        </div>
    """, unsafe_allow_html=True)

def view_booking():
    render_header()
    
    # Grid de Servicios
    cols = st.columns(2)
    for i, (name, info) in enumerate(SERVICES.items()):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="service-container">
                    <img src="{info['img']}" style="width:100%; border-radius:12px; height:120px; object-fit:cover;">
                    <div style="margin-top:10px; font-weight:600;">{name}</div>
                    <div class="price-tag">{format_gs(info['price'])}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><h3 style='text-align:center;'>Agendar Turno</h3>", unsafe_allow_html=True)
    
    with st.form("reserva"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Nombre y Apellido")
        phone = c2.text_input("WhatsApp")
        date = c1.date_input("Fecha", min_value=datetime.date.today())
        time = c2.selectbox("Hora disponible", [f"{h:02d}:00" for h in range(8, 20)] + [f"{h:02d}:30" for h in range(8, 20)])
        service = c1.selectbox("Elegir Servicio", list(SERVICES.keys()))
        pay = c2.selectbox("Forma de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("RESERVAR AHORA"):
            if name and phone:
                apt = {
                    "id": str(uuid.uuid4())[:6].upper(),
                    "client": name, "phone": phone, "date": str(date),
                    "time": time, "service": service, "payment": pay,
                    "amount": SERVICES[service]['price'], "proof": None
                }
                st.session_state.current_apt = apt
                st.session_state.view = 'confirm'
                st.rerun()
            else:
                st.warning("Completa tus datos, Diva.")

def view_confirmation():
    render_header()
    apt = st.session_state.current_apt
    
    st.markdown(f"""
        <div style="background:rgba(212,175,55,0.1); padding:25px; border-radius:20px; border-left: 5px solid var(--gold); margin-bottom:20px;">
            <h2 style="margin:0; color:white !important;">¡Casi listo, {apt['client']}!</h2>
            <p style="color:var(--gold);">Tu reserva <b>#{apt['id']}</b> ha sido generada.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("Servicio", apt['service'])
    col2.metric("Total a pagar", format_gs(apt['amount']))
    
    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("### 🏦 Datos para el Pago")
        t1, t2 = st.tabs(["Familiar", "Ueno / Pix"])
        t1.code("Cta: 815643114\nTitular: Diva Nails", language="text")
        t2.code("Alias: 4437206\nBanco: Ueno", language="text")
        
        proof = st.file_uploader("Sube una foto del comprobante", type=['jpg', 'png'])
        if proof:
            apt['proof'] = img_to_b64(proof)
            st.success("Comprobante cargado.")

    st.markdown("---")
    if st.button("🚀 ENVIAR CONFIRMACIÓN POR WHATSAPP"):
        # Guardar en DB solo al confirmar
        st.session_state.db['apts'].append(apt)
        save_db(st.session_state.db)
        
        link = get_whatsapp_link(apt)
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
        st.info("Abriendo WhatsApp...")

# --- MAIN ---
def main():
    if st.session_state.view == 'booking':
        view_booking()
    elif st.session_state.view == 'confirm':
        view_confirmation()
        if st.button("⬅️ Volver"):
            st.session_state.view = 'booking'
            st.rerun()

if __name__ == "__main__":
    main()