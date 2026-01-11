import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import urllib.parse

# --- CONFIGURACIÓN DE ATELIER ---
st.set_page_config(page_title="Diva | Luxury Nails", page_icon="💅", layout="centered")

# --- PALETA DE COLORES "MISTY ROSE & SLATE" ---
COLORS = {
    "bg": "#F8F9FA",
    "text": "#1A1A1A",
    "accent": "#9E897F", # Café con leche suave
    "soft_rose": "#EAD7D1",
    "white": "#FFFFFF"
}

# --- ESTILOS CSS AVANZADOS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;1,400&family=Montserrat:wght@200;400;600&display=swap');

    .stApp {{ background-color: {COLORS['bg']}; font-family: 'Montserrat', sans-serif; }}
    
    /* Header Editorial */
    .header-box {{ text-align: center; padding: 60px 0; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 4.5rem; letter-spacing: 12px; margin: 0; text-transform: uppercase; font-weight: 300; color: {COLORS['text']}; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.6rem; color: {COLORS['accent']}; margin-top: -15px; letter-spacing: 5px; }}

    /* Catálogo Horizontal Estilizado */
    .service-container {{
        position: relative;
        width: 100%;
        height: 280px;
        margin-bottom: 25px;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        align-items: flex-end;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }}
    
    .service-img {{
        position: absolute;
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.8s ease;
        z-index: 1;
    }}
    
    .service-overlay {{
        position: absolute;
        width: 100%;
        height: 100%;
        background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 60%);
        z-index: 2;
    }}
    
    .service-text-box {{
        position: relative;
        z-index: 3;
        padding: 30px;
        width: 100%;
        color: white;
    }}
    
    .service-title-h {{ font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; margin: 0; font-weight: 300; }}
    .service-price-h {{ font-weight: 200; letter-spacing: 3px; font-size: 1rem; color: {COLORS['soft_rose']}; }}

    /* Botones y Formulario */
    .stButton button {{
        background-color: {COLORS['text']} !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        height: 55px;
        letter-spacing: 3px;
        text-transform: uppercase;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton button:hover {{ background-color: {COLORS['accent']} !important; }}

    /* Input Styling */
    .stTextInput input, .stSelectbox div, .stDateInput input {{
        border-radius: 0px !important;
        border: 0.5px solid #DDD !important;
        padding: 12px !important;
        background-color: white !important;
    }}

    /* Remove UI */
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE SERVICIOS (HORIZONTAL IMAGES) ---
SERVICES = {
    "Capping Gel": {
        "price": 120000, 
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?q=80&w=1200&auto=format&fit=crop", 
        "desc": "Refuerzo estructural para uñas naturales."
    },
    "Mantenimiento": {
        "price": 80000, 
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?q=80&w=1200&auto=format&fit=crop", 
        "desc": "Renovación estética y técnica del servicio."
    },
    "Semipermanente": {
        "price": 70000, 
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?q=80&w=1200&auto=format&fit=crop", 
        "desc": "Brillo de alta intensidad y color duradero."
    },
    "Soft Gel": {
        "price": 150000, 
        "img": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?q=80&w=1200&auto=format&fit=crop", 
        "desc": "Extensiones premium de máxima ligereza."
    }
}

BUSINESS_PHONE = "595992698406"

def format_gs(val): return f"₲ {val:,.0f}".replace(",", ".")

# --- VISTA PRINCIPAL ---
if 'selected_service' not in st.session_state: st.session_state.selected_service = list(SERVICES.keys())[0]
if 'view' not in st.session_state: st.session_state.view = 'main'

def render_header():
    st.markdown(f"""
        <div class="header-box">
            <h1 class="logo-main">Diva</h1>
            <div class="logo-sub">Nail Atelier</div>
        </div>
    """, unsafe_allow_html=True)

def view_main():
    render_header()
    
    # --- CATÁLOGO HORIZONTAL ---
    st.markdown("<p style='text-align:center; letter-spacing:4px; font-weight:200; color:gray;'>NUESTRO MENÚ EXCLUSIVO</p>", unsafe_allow_html=True)
    
    for name, info in SERVICES.items():
        # Renderizado de Tarjeta Horizontal
        st.markdown(f"""
            <div class="service-container">
                <img src="{info['img']}" class="service-img">
                <div class="service-overlay"></div>
                <div class="service-text-box">
                    <div class="service-price-h">{format_gs(info['price'])}</div>
                    <h3 class="service-title-h">{name}</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de reserva vinculado al nombre
        if st.button(f"ELEGIR {name.upper()}", key=f"btn_{name}"):
            st.session_state.selected_service = name
            # JS para scroll automático al formulario
            st.markdown("<script>window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});</script>", unsafe_allow_html=True)
            st.toast(f"Has seleccionado {name}")

    st.markdown("<br><hr style='border:0.1px solid #EEE'><br>", unsafe_allow_html=True)
    st.markdown("<h2 id='form_section' style='text-align:center; font-family:Cormorant Garamond; font-size:2.5rem;'>Detalles de la Cita</h2>", unsafe_allow_html=True)
    
    # --- FORMULARIO ---
    with st.form("booking_form"):
        c1, c2 = st.columns(2)
        name_input = c1.text_input("Nombre Completo")
        phone_input = c2.text_input("WhatsApp de contacto")
        
        date_input = c1.date_input("Fecha preferida", min_value=datetime.date.today())
        time_input = c2.selectbox("Horario sugerido", [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in ("00", "30")])
        
        service_input = c1.selectbox("Confirmar Servicio", list(SERVICES.keys()), 
                                     index=list(SERVICES.keys()).index(st.session_state.selected_service))
        pay_input = c2.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("Siguiente Paso"):
            if name_input and phone_input:
                st.session_state.current_apt = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": name_input, "phone": phone_input,
                    "date": str(date_input), "time": time_input, "service": service_input,
                    "payment": pay_input, "amount": SERVICES[service_input]['price']
                }
                st.session_state.view = 'confirm'
                st.rerun()
            else:
                st.warning("Diva, necesitamos tu nombre y teléfono para agendar.")

def view_confirm():
    render_header()
    apt = st.session_state.current_apt
    
    st.markdown(f"""
        <div style="background:white; padding:40px; border:1px solid #DDD; text-align:center;">
            <p style="letter-spacing:3px; color:{COLORS['accent']}; font-size:0.8rem;">CONFIRMACIÓN DE TURNO</p>
            <h2 style="font-family:Cormorant Garamond; font-size:2.5rem; margin:10px 0;">{apt['service']}</h2>
            <p style="font-size:1.1rem; font-weight:300;">{apt['date']} — {apt['time']} hs</p>
            <div style="margin:20px 0; border-top:1px solid #EEE; padding-top:20px;">
                <span style="font-size:1.5rem; font-weight:600;">{format_gs(apt['amount'])}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if apt['payment'] in ["Transferencia", "Pix"]:
        st.info("📌 Su cita será confirmada al recibir el comprobante.")
        st.write("**Banco Familiar:** Cta 815643114 | **Ueno:** Alias 4437206")
        proof = st.file_uploader("Adjuntar foto del comprobante", type=['jpg', 'png', 'jpeg'])

    if st.button("CONFIRMAR Y ENVIAR WHATSAPP"):
        msg = (
            f"👑 *NUEVA CITA: DIVA ATELIER*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔖 *ID:* #{apt['id']}\n"
            f"👤 *CLIENTE:* {apt['client'].upper()}\n"
            f"💅 *SERVICIO:* {apt['service']}\n"
            f"📅 *FECHA:* {apt['date']}\n"
            f"⏰ *HORA:* {apt['time']} hs\n"
            f"💰 *VALOR:* {format_gs(apt['amount'])}\n"
            f"💳 *PAGO:* {apt['payment']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📎 _Adjunto comprobante aquí abajo_"
        )
        link = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)

    if st.button("Volver al Catálogo"):
        st.session_state.view = 'main'
        st.rerun()

# --- LÓGICA DE NAVEGACIÓN ---
if st.session_state.view == 'main':
    view_main()
else:
    view_confirm()