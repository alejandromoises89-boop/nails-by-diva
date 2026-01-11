import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diva | Nail Atelier Premium", page_icon="💅", layout="centered")

# --- PALETA DE COLORES "QUIET LUXURY" ---
COLORS = {
    "bg": "#FDFCFB",        # Crema muy claro
    "text": "#2A2624",      # Carbón suave
    "accent": "#9E897F",    # Taupe / Moka
    "gold": "#C5A059",      # Dorado mate
    "white": "#FFFFFF",
    "border": "#EAEAEA"
}

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;1,400&family=Montserrat:wght@200;400;600&display=swap');

    .stApp {{ background-color: {COLORS['bg']}; font-family: 'Montserrat', sans-serif; }}
    
    .header-box {{ text-align: center; padding: 40px 0; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 4rem; letter-spacing: 12px; margin: 0; text-transform: uppercase; font-weight: 300; color: {COLORS['text']}; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.4rem; color: {COLORS['accent']}; margin-top: -15px; letter-spacing: 5px; }}

    /* IMAGEN HORIZONTAL PERFECTA */
    .img-container {{
        width: 100%;
        height: 250px;
        background-position: center;
        background-size: cover; /* Cubre todo sin espacios blancos */
        background-repeat: no-repeat;
        display: flex;
        align-items: flex-end;
        position: relative;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid {COLORS['border']};
    }}
    
    .img-overlay {{
        position: absolute;
        width: 100%;
        height: 100%;
        background: linear-gradient(0deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 50%);
    }}
    
    .img-text {{ position: relative; z-index: 2; padding: 25px; color: white; width: 100%; }}

    /* BOTONES */
    .stButton button {{
        background-color: {COLORS['text']} !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        height: 45px;
        letter-spacing: 2px;
        text-transform: uppercase;
        width: 100%;
        font-size: 0.75rem;
        transition: 0.3s ease;
    }}
    .stButton button:hover {{ background-color: {COLORS['accent']} !important; }}

    /* PAGO CARDS */
    .bank-card {{
        background: white;
        padding: 20px;
        border: 1px solid #EEE;
        border-top: 3px solid {COLORS['accent']};
        text-align: center;
        margin-bottom: 10px;
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE SERVICIOS ---
SERVICES = {
    "Capping Gel": {
        "price": 120000, 
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=1200&q=80", 
        "desc": "Refuerzo para uñas naturales."
    },
    "Mantenimiento": {
        "price": 80000, 
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=1200&q=80", 
        "desc": "Renovación técnica de tu set."
    },
    "Semipermanente": {
        "price": 70000, 
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?w=1200&q=80", # Imagen estética rosada
        "desc": "Brillo extremo y color duradero."
    },
    "Soft Gel": {
        "price": 150000, 
        "img": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?w=1200&q=80", 
        "desc": "Extensiones premium ultra ligeras."
    }
}

BUSINESS_PHONE = "595992698406"

def format_gs(val): return f"₲ {val:,.0f}".replace(",", ".")

# --- NAVEGACIÓN ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_service' not in st.session_state: st.session_state.selected_service = "Capping Gel"

def view_main():
    st.markdown(f'<div class="header-box"><h1 class="logo-main">Diva</h1><div class="logo-sub">Nail Atelier</div></div>', unsafe_allow_html=True)
    
    # Catálogo Visual
    for name, info in SERVICES.items():
        st.markdown(f"""
            <div class="img-container" style="background-image: url('{info['img']}');">
                <div class="img-overlay"></div>
                <div class="img-text">
                    <small style="letter-spacing:2px; opacity:0.8;">{info['desc']}</small>
                    <h3 style="font-family:'Cormorant Garamond'; font-size:2.2rem; margin:0; font-weight:300;">{name}</h3>
                    <div style="font-weight:600; letter-spacing:1px; color:{COLORS['gold']}">{format_gs(info['price'])}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"ELEGIR {name.upper()}", key=f"btn_{name}"):
            st.session_state.selected_service = name
            st.toast(f"Seleccionado: {name}")

    st.markdown("<div style='margin:50px 0;'></div>", unsafe_allow_html=True)
    
    # Formulario
    with st.form("booking_form"):
        st.markdown("<h3 style='text-align:center; font-family:Cormorant Garamond; font-size:2rem;'>Detalles de Reserva</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        name_in = c1.text_input("Nombre Completo")
        phone_in = c2.text_input("WhatsApp")
        
        date_in = c1.date_input("Fecha", min_value=datetime.date.today())
        
        # Horarios (Arreglo del error de selectbox)
        time_options = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in ("00", "30")]
        time_in = c2.selectbox("Hora disponible", options=time_options)
        
        # Servicio (Selección automática)
        svc_options = list(SERVICES.keys())
        svc_in = c1.selectbox("Servicio", options=svc_options, index=svc_options.index(st.session_state.selected_service))
        
        pay_in = c2.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("AGENDAR AHORA"):
            if name_in and phone_in:
                st.session_state.current_apt = {
                    "id": str(uuid.uuid4())[:6].upper(),
                    "client": name_in, "phone": phone_in,
                    "date": str(date_in), "time": time_in,
                    "service": svc_in, "payment": pay_in,
                    "amount": SERVICES[svc_in]['price']
                }
                st.session_state.view = 'confirm'
                st.rerun()
            else:
                st.error("Diva, por favor completa tu nombre y contacto.")

def view_confirm():
    apt = st.session_state.current_apt
    st.markdown("<div class='header-box'><h1 class='logo-main'>Diva</h1></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background:white; padding:30px; border:1px solid #EEE; text-align:center; margin-bottom:20px;">
            <p style="letter-spacing:2px; color:{COLORS['accent']};">RESUMEN DE CITA</p>
            <h2 style="font-family:Cormorant Garamond; font-size:2.5rem; margin:10px 0;">{apt['service']}</h2>
            <p>{apt['date']} — {apt['time']} hs</p>
            <h3 style="color:{COLORS['text']}">{format_gs(apt['amount'])}</h3>
        </div>
    """, unsafe_allow_html=True)

    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("#### 💳 Datos para el pago")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="bank-card"><small>FAMILIAR</small><br><b>815643114</b></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="bank-card"><small>UENO / PIX</small><br><b>Alias: 4437206</b></div>', unsafe_allow_html=True)
        st.file_uploader("Subir comprobante")

    if st.button("CONFIRMAR Y ENVIAR WHATSAPP"):
        msg = (
            f"👑 *RESERVA: DIVA ATELIER*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *CLIENTE:* {apt['client'].upper()}\n"
            f"💅 *SERVICIO:* {apt['service']}\n"
            f"📅 *FECHA:* {apt['date']}\n"
            f"⏰ *HORA:* {apt['time']} hs\n"
            f"💰 *VALOR:* {format_gs(apt['amount'])}\n"
            f"💳 *PAGO:* {apt['payment']}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        link = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)

    if st.button("Corregir datos"):
        st.session_state.view = 'main'
        st.rerun()

# Lógica Principal
if st.session_state.view == 'main':
    view_main()
else:
    view_confirm()
