import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Diva | Nail Atelier", page_icon="💅", layout="centered")

# --- 2. GENERACIÓN DE HORARIOS (Sintaxis simplificada para evitar errores) ---
HORARIOS_DISPONIBLES = []
for h in range(8, 20):
    HORARIOS_DISPONIBLES.append(str(h).zfill(2) + ":00")
    HORARIOS_DISPONIBLES.append(str(h).zfill(2) + ":30")

# --- 3. CATÁLOGO ---
SERVICES = {
    "Capping Gel": {
        "price": 120000, 
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=1000&q=80", 
        "desc": "Protección para tus uñas naturales."
    },
    "Mantenimiento": {
        "price": 80000, 
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=1000&q=80", 
        "desc": "Retoque profesional de crecimiento."
    },
    "Semipermanente": {
        "price": 70000, 
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?w=1000&q=80", 
        "desc": "Color impecable y brillo duradero."
    },
    "Soft Gel": {
        "price": 150000, 
        "img": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?w=1000&q=80", 
        "desc": "Extensiones de alta gama ultra ligeras."
    }
}

SERVICE_NAMES = list(SERVICES.keys())
BUSINESS_PHONE = "595992698406"

# --- 4. DISEÑO CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;600&family=Montserrat:wght@200;400&display=swap');

    .stApp {{ background-color: #FDFCFB; color: #2A2624; font-family: 'Montserrat', sans-serif; }}
    
    .header-box {{ text-align: center; padding: 30px 0; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 3.5rem; letter-spacing: 10px; text-transform: uppercase; font-weight: 300; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.2rem; color: #9E897F; margin-top: -10px; }}

    .img-container {{
        width: 100%; height: 240px;
        background-position: center;
        background-size: cover;
        display: flex; align-items: flex-end; position: relative;
        margin-bottom: 10px;
        border: 1px solid #EAEAEA;
    }}
    
    .img-overlay {{
        position: absolute; width: 100%; height: 100%;
        background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 60%);
    }}
    
    .img-text {{ position: relative; z-index: 2; padding: 20px; color: white; }}

    .stButton button {{
        background-color: #2A2624 !important;
        color: white !important;
        border-radius: 0px !important;
        height: 45px; letter-spacing: 2px;
        text-transform: uppercase; width: 100%; font-size: 0.8rem;
    }}
    
    .bank-box {{
        background: white; padding: 15px;
        border: 1px solid #EEE; border-top: 3px solid #9E897F;
        text-align: center; margin-bottom: 5px;
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE ESTADO ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_service' not in st.session_state: st.session_state.selected_service = SERVICE_NAMES[0]

def format_gs(val): return "₲ " + "{:,.0f}".format(val).replace(",", ".")

# --- 6. VISTAS ---
def view_main():
    st.markdown('<div class="header-box"><h1 class="logo-main">Diva</h1><div class="logo-sub">Nail Atelier</div></div>', unsafe_allow_html=True)
    
    for name, info in SERVICES.items():
        st.markdown(f'''
            <div class="img-container" style="background-image: url('{info['img']}');">
                <div class="img-overlay"></div>
                <div class="img-text">
                    <small>{info['desc']}</small>
                    <h3 style="margin:0; font-family:'Cormorant Garamond'; font-size:1.8rem;">{name}</h3>
                    <div style="color:#C5A059; font-weight:600;">{format_gs(info['price'])}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button(f"ELEGIR {name.upper()}", key="btn_" + name):
            st.session_state.selected_service = name
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    with st.form("booking_form"):
        st.markdown("<h3 style='text-align:center; font-family:Cormorant Garamond;'>Reservar Turno</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        name_in = c1.text_input("Nombre")
        phone_in = c2.text_input("WhatsApp")
        date_in = c1.date_input("Fecha", min_value=datetime.date.today())
        time_in = c2.selectbox("Hora", options=HORARIOS_DISPONIBLES)
        
        default_idx = SERVICE_NAMES.index(st.session_state.selected_service)
        service_in = c1.selectbox("Servicio", options=SERVICE_NAMES, index=default_idx)
        pay_in = c2.selectbox("Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("SIGUIENTE"):
            if name_in and phone_in:
                st.session_state.current_apt = {
                    "id": str(uuid.uuid4())[:6].upper(),
                    "client": name_in, "phone": phone_in,
                    "date": str(date_in), "time": time_in,
                    "service": service_in, "payment": pay_in,
                    "amount": SERVICES[service_in]['price']
                }
                st.session_state.view = 'confirm'
                st.rerun()
            else:
                st.error("Completa tus datos")

def view_confirm():
    apt = st.session_state.current_apt
    st.markdown('<div class="header-box"><h1 class="logo-main">Diva</h1></div>', unsafe_allow_html=True)
    
    st.markdown(f'''
        <div style="background:white; padding:25px; border:1px solid #EEE; text-align:center;">
            <p style="color:#9E897F; font-size:0.8rem;">RESUMEN</p>
            <h2 style="font-family:Cormorant Garamond; margin:5px 0;">{apt['service']}</h2>
            <p>{apt['date']} | {apt['time']} hs</p>
            <h3>{format_gs(apt['amount'])}</h3>
        </div>
    ''', unsafe_allow_html=True)

    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown('<div class="bank-box"><small>FAMILIAR</small><br><b>815643114</b></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="bank-box"><small>UENO/PIX</small><br><b>Alias: 4437206</b></div>', unsafe_allow_html=True)
        st.file_uploader("Subir comprobante")

    if st.button("CONFIRMAR EN WHATSAPP"):
        msg = f"👑 *RESERVA: DIVA*\n\n" \
              f"👤 *CLIENTE:* {apt['client'].upper()}\n" \
              f"💅 *SERVICIO:* {apt['service']}\n" \
              f"📅 *FECHA:* {apt['date']}\n" \
              f"⏰ *HORA:* {apt['time']} hs\n" \
              f"💰 *VALOR:* {format_gs(apt['amount'])}\n" \
              f"💳 *PAGO:* {apt['payment']}"
        
        link = "https://wa.me/" + BUSINESS_PHONE + "?text=" + urllib.parse.quote(msg)
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)

    if st.button("Volver"):
        st.session_state.view = 'main'
        st.rerun()

# --- 7. EJECUCIÓN ---
if st.session_state.view == 'main':
    view_main()
else:
    view_confirm()