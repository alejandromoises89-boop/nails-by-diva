import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import base64
import urllib.parse

# --- CONFIGURACIÓN DE LUJO ---
st.set_page_config(
    page_title="Nails by Diva | Atelier Premium",
    page_icon="💅",
    layout="centered"
)

# --- PALETA "CHAMPAGNE & SLATE" ---
COLORS = {
    "bg": "#F4F1EE",      # Lino claro
    "card": "#FFFFFF",    # Blanco puro
    "accent": "#9A8478",  # Taupe / Moka
    "text": "#2C2C2C",    # Gris carbón
    "highlight": "#E0C3B1" # Champagne Rosé
}

# --- ESTILOS CSS REFINADOS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;1,500&family=Montserrat:wght@300;400;500&display=swap');

    .stApp {{ background-color: {COLORS['bg']}; color: {COLORS['text']}; font-family: 'Montserrat', sans-serif; }}
    
    /* Header Boutique */
    .header-box {{ text-align: center; padding: 50px 0 30px 0; border-bottom: 0.5px solid {COLORS['accent']}; margin-bottom: 40px; }}
    .logo-main {{ font-family: 'Playfair Display', serif; font-size: 3.8rem; letter-spacing: 10px; margin: 0; text-transform: uppercase; font-weight: 500; }}
    .logo-sub {{ font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.4rem; color: {COLORS['accent']}; margin-top: -10px; }}

    /* Tarjetas de Catálogo */
    .service-card {{
        background: {COLORS['card']};
        margin-bottom: 30px;
        border: 1px solid #EAEAEA;
        overflow: hidden;
        transition: transform 0.3s ease;
    }}
    .service-card:hover {{ transform: translateY(-5px); border-color: {COLORS['accent']}; }}
    
    .service-img {{
        width: 100%;
        height: 220px;
        object-fit: cover;
    }}
    
    .service-content {{ padding: 20px; text-align: center; }}
    .service-title {{ font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 8px; color: {COLORS['text']}; }}
    .service-desc {{ font-size: 0.85rem; color: #666; line-height: 1.4; margin-bottom: 15px; min-height: 40px; }}
    .price-tag {{ 
        font-weight: 500; letter-spacing: 2px; color: {COLORS['accent']}; 
        border-top: 1px solid #F5F5F5; padding-top: 15px; font-size: 1.1rem;
    }}

    /* Botón Editorial */
    .stButton button {{
        background-color: {COLORS['text']} !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        height: 55px;
        font-weight: 500;
        letter-spacing: 3px;
        text-transform: uppercase;
        width: 100%;
        margin-top: 20px;
    }}
    .stButton button:hover {{ background-color: {COLORS['accent']} !important; }}

    /* Estilo de Formulario */
    .stTextInput input, .stSelectbox div, .stDateInput input {{
        border-radius: 0px !important;
        border: 0.5px solid #CCC !important;
        padding: 12px !important;
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DE SERVICIOS (CON IMÁGENES ESTÉTICAS) ---
# Usamos imágenes que evocan limpieza, detalle y lujo
SERVICES = {
    "Capping Gel": {
        "price": 120000, 
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?q=80&w=800&auto=format&fit=crop", 
        "desc": "Protección y fuerza para tus uñas naturales con un acabado impecable."
    },
    "Mantenimiento": {
        "price": 80000, 
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?q=80&w=800&auto=format&fit=crop", 
        "desc": "El cuidado necesario para mantener la perfección de tu set original."
    },
    "Semipermanente": {
        "price": 70000, 
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?q=80&w=800&auto=format&fit=crop", 
        "desc": "Color vibrante y brillo espejo de larga duración para toda ocasión."
    },
    "Soft Gel": {
        "price": 150000, 
        "img": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?q=80&w=800&auto=format&fit=crop", 
        "desc": "Extensiones premium ultra ligeras que lucen y se sienten como naturales."
    }
}

BUSINESS_PHONE = "595992698406"

# --- FUNCIONES ---
def format_gs(val): return f"₲ {val:,.0f}".replace(",", ".")

def generate_wa_msg(apt):
    msg = (
        f"✨ *SOLICITUD DE CITA - DIVA ATELIER*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔖 *RESERVA:* #{apt['id']}\n"
        f"👤 *CLIENTE:* {apt['client'].upper()}\n"
        f"💅 *SERVICIO:* {apt['service']}\n"
        f"📅 *FECHA:* {apt['date']}\n"
        f"⏰ *HORA:* {apt['time']} hs\n"
        f"💰 *TOTAL:* {format_gs(apt['amount'])}\n"
        f"💳 *PAGO:* {apt['payment']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📱 *WHATSAPP:* {apt['phone']}\n\n"
        f"_(Adjunto el comprobante a continuación)_"
    )
    return f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"

# --- VISTA PRINCIPAL ---
if 'view' not in st.session_state: st.session_state.view = 'catalog'

def view_catalog():
    st.markdown(f"""
        <div class="header-box">
            <h1 class="logo-main">Diva</h1>
            <div class="logo-sub">Nail Atelier</div>
        </div>
    """, unsafe_allow_html=True)

    # Renderizado del Catálogo Visual
    cols = st.columns(2)
    for i, (name, info) in enumerate(SERVICES.items()):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="service-card">
                    <img src="{info['img']}" class="service-img">
                    <div class="service-content">
                        <div class="service-title">{name}</div>
                        <div class="service-desc">{info['desc']}</div>
                        <div class="price-tag">{format_gs(info['price'])}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; font-family:Playfair Display;'>Agendar su Visita</h3>", unsafe_allow_html=True)
    
    with st.form("booking_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Nombre y Apellido")
        phone = c2.text_input("WhatsApp")
        
        date = c1.date_input("Fecha", min_value=datetime.date.today())
        time = c2.selectbox("Horario", [f"{h:02d}:00" for h in range(8, 20)] + [f"{h:02d}:30" for h in range(8, 20)])
        
        service = c1.selectbox("Servicio", list(SERVICES.keys()))
        pay = c2.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("Siguiente"):
            if name and phone:
                st.session_state.current_apt = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": name, "phone": phone,
                    "date": str(date), "time": time, "service": service,
                    "payment": pay, "amount": SERVICES[service]['price']
                }
                st.session_state.view = 'confirm'
                st.rerun()
            else:
                st.warning("Por favor complete sus datos.")

def view_confirm():
    apt = st.session_state.current_apt
    st.markdown(f"<h2 style='text-align:center; font-family:Playfair Display;'>Confirmación</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background:white; padding:40px; border:1px solid #DDD; text-align:center;">
            <p style="letter-spacing:2px; color:{COLORS['accent']};">DETALLES DE RESERVA</p>
            <h3 style="font-family:Playfair Display;">{apt['service']}</h3>
            <p>{apt['date']} — {apt['time']} hs</p>
            <p style="font-size:1.3rem;"><b>Total: {format_gs(apt['amount'])}</b></p>
        </div>
    """, unsafe_allow_html=True)

    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📌 Envíe el comprobante para validar su turno.")
        with st.expander("Ver Datos de Pago"):
            st.write("**Banco Familiar:** Cta 815643114")
            st.write("**Ueno Bank:** Alias 4437206")
        
        proof = st.file_uploader("Adjuntar Comprobante", type=['jpg', 'png', 'jpeg'])

    if st.button("FINALIZAR Y ENVIAR WHATSAPP"):
        link = generate_wa_msg(apt)
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={link}">', unsafe_allow_html=True)
        st.success("Redirigiendo a WhatsApp...")

    if st.button("Corregir datos"):
        st.session_state.view = 'catalog'
        st.rerun()

# --- NAVEGACIÓN ---
if st.session_state.view == 'catalog':
    view_catalog()
else:
    view_confirm()
