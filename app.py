import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diva | Nail Atelier Premium", page_icon="💅", layout="centered")

# --- PALETA DE COLORES REFINADA ---
COLORS = {
    "bg": "#FDFCFB",
    "text": "#2A2624",
    "accent": "#9E897F", # Taupe editorial
    "gold": "#D4AF37",
    "white": "#FFFFFF",
    "soft_bg": "#F4F1EE"
}

# --- ESTILOS CSS (CORRECCIÓN DE IMÁGENES Y DISEÑO) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;1,400&family=Montserrat:wght@200;400;600&display=swap');

    .stApp {{ background-color: {COLORS['bg']}; font-family: 'Montserrat', sans-serif; }}
    
    /* Header Editorial */
    .header-box {{ text-align: center; padding: 40px 0; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 4rem; letter-spacing: 12px; margin: 0; text-transform: uppercase; font-weight: 300; color: {COLORS['text']}; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.4rem; color: {COLORS['accent']}; margin-top: -10px; letter-spacing: 5px; }}

    /* Contenedor de Imagen Horizontal (Ajuste Perfecto) */
    .img-container {{
        width: 100%;
        height: 250px;
        border-radius: 2px;
        background-position: center;
        background-size: cover; /* Esto elimina los espacios en blanco */
        background-repeat: no-repeat;
        display: flex;
        align-items: flex-end;
        position: relative;
        margin-bottom: 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }}
    
    .img-overlay {{
        position: absolute;
        width: 100%;
        height: 100%;
        background: linear-gradient(0deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 50%);
        border-radius: 2px;
    }}
    
    .img-text {{
        position: relative;
        z-index: 2;
        padding: 20px;
        color: white;
        width: 100%;
    }}

    /* Botones Premium */
    .stButton button {{
        background-color: {COLORS['text']} !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        height: 45px;
        letter-spacing: 2px;
        text-transform: uppercase;
        width: 100%;
        transition: 0.4s;
        font-size: 0.8rem;
    }}
    .stButton button:hover {{ background-color: {COLORS['accent']} !important; transform: translateY(-2px); }}

    /* Inputs Estilizados */
    .stTextInput input, .stSelectbox div, .stDateInput input {{
        border-radius: 0px !important;
        border: 1px solid #E0E0E0 !important;
        background-color: white !important;
    }}

    /* Estilo de la Sección de Pago */
    .payment-card {{
        background: {COLORS['white']};
        padding: 25px;
        border: 1px solid #EEE;
        border-left: 4px solid {COLORS['accent']};
        margin: 20px 0;
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE SERVICIOS (URLS ESTABLES) ---
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

BUSINESS_PHONE = "595992698406"

def format_gs(val): return f"₲ {val:,.0f}".replace(",", ".")

# --- ESTADO DE SESIÓN ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_service' not in st.session_state: st.session_state.selected_service = "Capping Gel"

# --- VISTAS ---
def view_main():
    # Header
    st.markdown(f"""
        <div class="header-box">
            <h1 class="logo-main">Diva</h1>
            <div class="logo-sub">Nail Atelier</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; letter-spacing:3px; font-size:0.8rem; color:gray; margin-bottom:40px;'>CATÁLOGO DE SERVICIOS</p>", unsafe_allow_html=True)

    # Catálogo de Servicios con imágenes ajustadas
    for name, info in SERVICES.items():
        st.markdown(f"""
            <div class="img-container" style="background-image: url('{info['img']}');">
                <div class="img-overlay"></div>
                <div class="img-text">
                    <small style="letter-spacing:2px; color:#E0E0E0;">{info['desc']}</small>
                    <h3 style="font-family:'Cormorant Garamond'; font-size:2rem; margin:0; font-weight:300;">{name}</h3>
                    <div style="font-weight:600; letter-spacing:1px; color:{COLORS['gold']}">{format_gs(info['price'])}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"SELECCIONAR {name.upper()}", key=f"sel_{name}"):
            st.session_state.selected_service = name
            st.toast(f"Elegiste {name}")

    st.markdown("<div style='margin:50px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-family:Cormorant Garamond; font-size:2.5rem;'>Reserva de Turno</h2>", unsafe_allow_html=True)
    
    # Formulario
    with st.form("booking_form"):
        c1, c2 = st.columns(2)
        name_in = c1.text_input("Nombre Completo")
        phone_in = c2.text_input("WhatsApp")
        
        date_in = c1.date_input("Fecha", min_value=datetime.date.today())
        time_in = c2.selectbox("Hora", [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in ("00", "30")])
        
        service_in = c1.selectbox("Servicio", list(SERVICES.keys()), 
                                  index=list(SERVICES.keys()).index(st.session_state.selected_service))
        pay_in = c2.selectbox("Forma de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("RESERVAR AHORA"):
            if name_in and phone_in:
                st.session_state.current_apt = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": name_in, "phone": phone_in,
                    "date": str(date_in), "time": time_in, "service": service_in,
                    "payment": pay_in, "amount": SERVICES[service_in]['price']
                }
                st.session_state.view = 'confirm'
                st.rerun()
            else:
                st.error("Diva, completa tu nombre y teléfono.")

def view_confirm():
    apt = st.session_state.current_apt
    
    st.markdown("<div class='header-box'><h1 class='logo-main'>Diva</h1></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; font-family:Cormorant Garamond;'>Confirmar Servicio</h3>", unsafe_allow_html=True)
    
    # Detalle de la Reserva
    st.markdown(f"""
        <div class="payment-card">
            <p style="margin:0; font-size:0.8rem; color:gray;">CLIENTE: {apt['client'].upper()}</p>
            <h2 style="font-family:Cormorant Garamond; margin:10px 0;">{apt['service']}</h2>
            <p><b>Día:</b> {apt['date']}  |  <b>Hora:</b> {apt['time']} hs</p>
            <h3 style="color:{COLORS['accent']}">{format_gs(apt['amount'])}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Sección de Pago Mejorada
    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("#### 💳 Detalles para el Pago")
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"""
                <div style="background:#F4F1EE; padding:15px; border:1px solid #DDD;">
                    <small>BANCO FAMILIAR</small><br>
                    <b>Cuenta:</b> 815643114<br>
                    <small>DIVA NAILS STUDIO</small>
                </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""
                <div style="background:#F4F1EE; padding:15px; border:1px solid #DDD;">
                    <small>UENO BANK / PIX</small><br>
                    <b>Alias:</b> 4437206<br>
                    <small>MARINA BAEZ</small>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.file_uploader("Subir foto del comprobante (opcional aquí)", type=['jpg','png','jpeg'])

    # Acción Final
    if st.button("FINALIZAR Y ENVIAR WHATSAPP"):
        msg = (
            f"👑 *NUEVA CITA: DIVA NAILS*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖 *ID:* #{apt['id']}\n"
            f"👤 *CLIENTE:* {apt['client'].upper()}\n"
            f"💅 *SERVICIO:* {apt['service']}\n"
            f"📅 *FECHA:* {apt['date']}\n"
            f"⏰ *HORA:* {apt['time']} hs\n"
            f"💰 *VALOR:* {format_gs(apt['amount'])}\n"
            f"💳 *PAGO:* {apt['payment']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 *WHATSAPP:* {apt['phone']}\n\n"
            f"✨ _Por favor, confirme la recepción de este mensaje._"
        )
        link = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
        st.success("Redirigiendo a WhatsApp...")

    if st.button("Volver atrás"):
        st.session_state.view = 'main'
        st.rerun()

# --- NAVEGACIÓN ---
if st.session_state.view == 'main':
    view_main()
else:
    view_confirm()
