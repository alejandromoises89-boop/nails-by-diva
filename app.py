import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails | by Diva", page_icon="💅", layout="centered")

# --- 2. GENERACIÓN DE HORARIOS (Sintaxis ultra-compatible) ---
HORARIOS_DISPONIBLES = []
for h in range(8, 20):
    hora_formateada = str(h).zfill(2)
    HORARIOS_DISPONIBLES.append(hora_formateada + ":00")
    HORARIOS_DISPONIBLES.append(hora_formateada + ":30")

# --- 3. CATÁLOGO DE SERVICIOS ---
SERVICES = {
    "Capping Gel": {
        "price": 120000, 
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=1000&q=80", 
        "desc": "Refuerzo estructural para tus uñas naturales."
    },
    "Mantenimiento": {
        "price": 80000, 
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=1000&q=80", 
        "desc": "Renovación estética y técnica del servicio."
    },
    "Semipermanente": {
        "price": 70000, 
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?w=1000&q=80", 
        "desc": "Color vibrante y brillo espejo de larga duración."
    },
    "Soft Gel": {
        "price": 150000, 
        "img": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?w=1000&q=80", 
        "desc": "Extensiones premium de máxima ligereza."
    }
}

SERVICE_NAMES = list(SERVICES.keys())
BUSINESS_PHONE = "595992698406"

# --- 4. DISEÑO REFINADO (Champagne & Slate) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;600&family=Montserrat:wght@300;400&display=swap');

    .stApp {{ background-color: #FDFCFB; color: #2A2624; font-family: 'Montserrat', sans-serif; }}
    
    .header-box {{ text-align: center; padding: 40px 0; border-bottom: 1px solid #EEE; margin-bottom: 30px; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 3.8rem; letter-spacing: 12px; text-transform: uppercase; font-weight: 300; color: #1A1A1A; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.3rem; color: #9E897F; margin-top: -12px; }}

    /* IMAGEN HORIZONTAL SIN ESPACIOS EN BLANCO */
    .img-container {{
        width: 100%; height: 260px;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        display: flex; align-items: flex-end; position: relative;
        margin-bottom: 12px;
        border: 1px solid #F0F0F0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    }}
    
    .img-overlay {{
        position: absolute; width: 100%; height: 100%;
        background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 60%);
    }}
    
    .img-text {{ position: relative; z-index: 2; padding: 25px; color: white; width: 100%; }}

    /* BOTONES ESTILO BOUTIQUE */
    .stButton button {{
        background-color: #2A2624 !important;
        color: #FDFCFB !important;
        border-radius: 0px !important;
        height: 50px; letter-spacing: 3px;
        text-transform: uppercase; width: 100%; font-size: 0.8rem;
        border: none !important; transition: 0.3s;
    }}
    .stButton button:hover {{ background-color: #9E897F !important; }}

    /* TARJETAS DE PAGO */
    .payment-box {{
        background: #FFFFFF; padding: 20px;
        border: 1px solid #EAEAEA; border-top: 4px solid #9E897F;
        text-align: center; margin-top: 15px;
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE ESTADO ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_service' not in st.session_state: st.session_state.selected_service = SERVICE_NAMES[0]

def format_gs(val):
    return "₲ " + "{:,.0f}".format(val).replace(",", ".")

# --- 6. VISTA PRINCIPAL ---
def view_main():
    st.markdown('<div class="header-box"><h1 class="logo-main">Diva</h1><div class="logo-sub">Nail Atelier</div></div>', unsafe_allow_html=True)
    
    # Catálogo de servicios
    for name, info in SERVICES.items():
        st.markdown(f'''
            <div class="img-container" style="background-image: url('{info['img']}');">
                <div class="img-overlay"></div>
                <div class="img-text">
                    <small style="letter-spacing:2px; opacity:0.9;">{info['desc']}</small>
                    <h3 style="margin:0; font-family:'Cormorant Garamond'; font-size:2rem; font-weight:300;">{name}</h3>
                    <div style="color:#C5A059; font-weight:600; letter-spacing:1px;">{format_gs(info['price'])}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button(f"SELECCIONAR {name.upper()}", key="btn_" + name):
            st.session_state.selected_service = name
            st.rerun()

    st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)
    
    # Formulario de reserva
    with st.form("booking_form"):
        st.markdown("<h3 style='text-align:center; font-family:Cormorant Garamond; font-size:2.2rem;'>Reserva de Experiencia</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        name_in = c1.text_input("Nombre y Apellido")
        phone_in = c2.text_input("WhatsApp de contacto")
        date_in = c1.date_input("Fecha de la cita", min_value=datetime.date.today())
        time_in = c2.selectbox("Horario sugerido", options=HORARIOS_DISPONIBLES)
        
        # Sincronización automática del servicio
        default_idx = SERVICE_NAMES.index(st.session_state.selected_service)
        service_in = c1.selectbox("Servicio confirmado", options=SERVICE_NAMES, index=default_idx)
        pay_in = c2.selectbox("Preferencia de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("RESERVAR TURNO"):
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
                st.error("Diva, necesitamos tu nombre y contacto.")

# --- 7. VISTA DE CONFIRMACIÓN ---
def view_confirm():
    apt = st.session_state.current_apt
    st.markdown('<div class="header-box"><h1 class="logo-main">Diva</h1></div>', unsafe_allow_html=True)
    
    st.markdown(f'''
        <div style="background:white; padding:35px; border:1px solid #EEE; text-align:center;">
            <p style="color:#9E897F; font-size:0.8rem; letter-spacing:2px;">SOLICITUD RECIBIDA</p>
            <h2 style="font-family:Cormorant Garamond; font-size:2.8rem; margin:10px 0;">{apt['service']}</h2>
            <p style="font-size:1.1rem; font-weight:300;">{apt['date']} — {apt['time']} hs</p>
            <h3 style="font-size:1.6rem;">{format_gs(apt['amount'])}</h3>
        </div>
    ''', unsafe_allow_html=True)

    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown('<div class="payment-box"><small>BANCO FAMILIAR</small><br><b>815643114</b></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="payment-box"><small>UENO / PIX</small><br><b>Alias: 4437206</b></div>', unsafe_allow_html=True)
        st.file_uploader("Adjuntar comprobante de reserva")

    if st.button("CONFIRMAR Y ENVIAR WHATSAPP"):
        msg = f"👑 *NUEVA CITA: DIVA NAILS*\n\n" \
              f"👤 *CLIENTE:* {apt['client'].upper()}\n" \
              f"💅 *SERVICIO:* {apt['service']}\n" \
              f"📅 *FECHA:* {apt['date']}\n" \
              f"⏰ *HORA:* {apt['time']} hs\n" \
              f"💰 *VALOR:* {format_gs(apt['amount'])}\n" \
              f"💳 *PAGO:* {apt['payment']}"
        
        link = "https://wa.me/" + BUSINESS_PHONE + "?text=" + urllib.parse.quote(msg)
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)

    if st.button("Corregir datos"):
        st.session_state.view = 'main'
        st.rerun()

# --- 8. EJECUCIÓN PRINCIPAL ---
if st.session_state.view == 'main':
    view_main()
else:
    view_confirm()
