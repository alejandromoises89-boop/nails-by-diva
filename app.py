import streamlit as st
import pandas as pd
import uuid
import datetime
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Diva | Nail Atelier", page_icon="💅", layout="centered")

# --- 2. HORARIOS (Escritos manualmente para evitar errores de servidor) ---
HORARIOS_DISPONIBLES = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", 
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", 
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", 
    "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"
]

# --- 3. SERVICIOS ---
SERVICES = {
    "Capping Gel": {
        "price": 120000, 
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=1000&q=80", 
        "desc": "Protección para tus uñas naturales."
    },
    "Mantenimiento": {
        "price": 80000, 
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=1000&q=80", 
        "desc": "Renovación profesional de tu set."
    },
    "Semipermanente": {
        "price": 70000, 
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?w=1000&q=80", 
        "desc": "Esmaltado de larga duración y brillo intenso."
    },
    "Soft Gel": {
        "price": 150000, 
        "img": "https://images.unsplash.com/photo-1604902396830-aca29e19b067?w=1000&q=80", 
        "desc": "Extensiones premium ultra ligeras."
    }
}

SERVICE_NAMES = list(SERVICES.keys())
BUSINESS_PHONE = "595992698406"

# --- 4. ESTILOS CSS REFINADOS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;600&family=Montserrat:wght@300;400&display=swap');

    .stApp {{ background-color: #FDFCFB; color: #2A2624; font-family: 'Montserrat', sans-serif; }}
    
    .header-box {{ text-align: center; padding: 40px 0; }}
    .logo-main {{ font-family: 'Cormorant Garamond', serif; font-size: 3.8rem; letter-spacing: 12px; text-transform: uppercase; font-weight: 300; color: #1A1A1A; }}
    .logo-sub {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.3rem; color: #9E897F; margin-top: -12px; }}

    /* IMAGEN HORIZONTAL SIN ESPACIOS EN BLANCO */
    .img-banner {{
        width: 100%; height: 260px;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        display: flex; align-items: flex-end; position: relative;
        margin-bottom: 12px;
        border: 1px solid #EEE;
    }}
    
    .overlay {{
        position: absolute; width: 100%; height: 100%;
        background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 60%);
    }}
    
    .text-content {{ position: relative; z-index: 2; padding: 25px; color: white; width: 100%; }}

    /* BOTONES */
    .stButton button {{
        background-color: #2A2624 !important;
        color: white !important;
        border-radius: 0px !important;
        height: 50px; letter-spacing: 3px;
        text-transform: uppercase; width: 100%; font-size: 0.8rem;
        border: none !important;
    }}
    .stButton button:hover {{ background-color: #9E897F !important; }}

    .payment-info {{
        background: white; padding: 20px;
        border: 1px solid #EEE; border-top: 4px solid #9E897F;
        text-align: center; margin-top: 15px;
    }}

    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. ESTADO ---
if 'view' not in st.session_state: st.session_state.view = 'main'
if 'selected_service' not in st.session_state: st.session_state.selected_service = SERVICE_NAMES[0]

def format_gs(val):
    return "₲ " + "{:,.0f}".format(val).replace(",", ".")

# --- 6. VISTA PRINCIPAL ---
def view_main():
    st.markdown('<div class="header-box"><h1 class="logo-main">Diva</h1><div class="logo-sub">Nail Atelier</div></div>', unsafe_allow_html=True)
    
    # Renderizar servicios
    for name, info in SERVICES.items():
        st.markdown(f'''
            <div class="img-banner" style="background-image: url('{info['img']}');">
                <div class="overlay"></div>
                <div class="text-content">
                    <small style="letter-spacing:2px; opacity:0.9;">{info['desc']}</small>
                    <h3 style="margin:0; font-family:'Cormorant Garamond'; font-size:2rem; font-weight:300;">{name}</h3>
                    <div style="color:#C5A059; font-weight:600;">{format_gs(info['price'])}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button(f"ELEGIR {name.upper()}", key="btn_" + name):
            st.session_state.selected_service = name
            st.rerun()

    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    
    # Formulario
    with st.form("booking_form"):
        st.markdown("<h3 style='text-align:center; font-family:Cormorant Garamond; font-size:2.2rem;'>Reserva de Turno</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        name_in = c1.text_input("Nombre Completo")
        phone_in = c2.text_input("WhatsApp")
        
        date_in = c1.date_input("Fecha", min_value=datetime.date.today())
        time_in = c2.selectbox("Horario sugerido", options=HORARIOS_DISPONIBLES)
        
        # Sincronización
        current_idx = SERVICE_NAMES.index(st.session_state.selected_service)
        service_in = c1.selectbox("Servicio", options=SERVICE_NAMES, index=current_idx)
        
        pay_in = c2.selectbox("Método de Pago", ["Transferencia", "Pix", "Efectivo"])
        
        if st.form_submit_button("RESERVAR AHORA"):
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
                st.warning("Por favor, completa tu nombre y contacto.")

# --- 7. CONFIRMACIÓN ---
def view_confirm():
    apt = st.session_state.current_apt
    st.markdown('<div class="header-box"><h1 class="logo-main">Diva</h1></div>', unsafe_allow_html=True)
    
    st.markdown(f'''
        <div style="background:white; padding:35px; border:1px solid #EEE; text-align:center;">
            <p style="color:#9E897F; font-size:0.8rem; letter-spacing:2px;">DETALLES DE LA CITA</p>
            <h2 style="font-family:Cormorant Garamond; font-size:2.8rem; margin:10px 0;">{apt['service']}</h2>
            <p>{apt['date']} — {apt['time']} hs</p>
            <h3>{format_gs(apt['amount'])}</h3>
        </div>
    ''', unsafe_allow_html=True)

    if apt['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown('<div class="payment-info"><small>FAMILIAR</small><br><b>815643114</b></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="payment-info"><small>UENO / PIX</small><br><b>Alias: 4437206</b></div>', unsafe_allow_html=True)

    if st.button("CONFIRMAR POR WHATSAPP"):
        msg = f"👑 *NUEVA CITA: DIVA ATELIER*\n\n" \
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

# --- 8. EJECUCIÓN ---
if st.session_state.view == 'main':
    view_main()
else:
    view_confirm()