import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595973574457" # Número de Nails Diva
ADMIN_PIN = "2026" 

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "expenses": []}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"appointments": [], "expenses": []}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- 2. SERVICIOS ---
SERVICES = {
    "CAPPING": {"title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
    "MAINTENANCE": {"title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
    "SEMIPERMANENT": {"title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
    "SOFT_GEL": {"title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
}

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .header-title { font-family: serif; font-size: 2.5rem; text-align: center; color: #333; }
    .bank-card { background: #fff; padding: 15px; border-radius: 10px; border-left: 5px solid #D4AF37; margin-bottom: 15px; border: 1px solid #eee; }
    .stButton > button { width: 100%; border-radius: 30px !important; font-weight: bold; height: 3.5em; background-color: #25D366 !important; color: white !important; border: none; }
    .stButton > button:disabled { background-color: #ccc !important; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE CLIENTE ---
def booking_interface():
    st.markdown('<h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:8px; color:#D4AF37; font-size:0.8rem; margin-top:-10px;">ATELIER</p>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for idx, (key, s) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(s["img"], use_container_width=True)
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"s_{key}"):
                st.session_state.pre_selected = s['title']
                st.toast(f"Elegido: {s['title']}")

    st.divider()

    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        with st.form("form_booking"):
            name = st.text_input("Nombre y Apellido")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            
            s_titles = [s['title'] for s in SERVICES.values()]
            def_idx = s_titles.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            serv = st.selectbox("Servicio", s_titles, index=def_idx)
            pay = st.radio("Método de Pago", ["Efectivo", "Transferencia / Pix"], horizontal=True)
            
            if st.form_submit_button("CONTINUAR"):
                if name and phone:
                    st.session_state.temp_res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": name, "phone": phone, "service": serv,
                        "price": next(s['price'] for s in SERVICES.values() if s['title'] == serv),
                        "date": str(date), "payment": pay, "status": "Pendiente"
                    }
                    st.session_state.view = 'confirm'
                    st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown("<h3 style='text-align:center;'>FINALIZAR Y ENVIAR</h3>", unsafe_allow_html=True)
    
    pago_listo = True
    if res['payment'] == "Transferencia / Pix":
        pago_listo = False
        st.markdown(f"""
        <div class="bank-card">
            <b>🏦 DATOS PARA TRANSFERENCIA:</b><br>
            • Banco Familiar: 815643114<br>
            • Ueno / Pix Alias: <b>4437206</b><br>
            • Monto: ₲ {res['price']:,}
        </div>
        """, unsafe_allow_html=True)
        
        archivo = st.file_uploader("SUBIR COMPROBANTE (REQUERIDO)", type=['jpg', 'png', 'jpeg'])
        if archivo:
            st.success("✅ Comprobante cargado.")
            pago_listo = True

    # Mensaje Ticket
    msg = (
        f"🛍️ *TICKET DE RESERVA - NAILS BY DIVA*\n"
        f"----------------------------------\n"
        f"🆔 *ID:* #{res['id']}\n"
        f"👤 *Cliente:* {res['client']}\n"
        f"💅 *Servicio:* {res['service']}\n"
        f"📅 *Fecha:* {res['date']}\n"
        f"💰 *Monto:* ₲ {res['price']:,}\n"
        f"💳 *Pago:* {res['payment']}\n"
        f"----------------------------------\n"
        f"✅ *¡Enviando Comprobante!*"
    )
    url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"

    if pago_listo:
        if st.button("🚀 ENVIAR AL WHATSAPP"):
            # 1. Guardar datos
            st.session_state.data['appointments'].append(res)
            save_data(st.session_state.data)
            
            # 2. Redirección automática forzada con JavaScript
            js = f"window.open('{url_wa}', '_self')"
            st.markdown(f'<img src="x" onerror="{js}">', unsafe_allow_html=True)
            st.write(f"Si no redirige, [haz clic aquí]({url_wa})")
    else:
        st.button("🚫 CARGAR COMPROBANTE PRIMERO", disabled=True)

    if st.button("« Volver"):
        st.session_state.view = 'booking'
        st.rerun()

# --- 5. PANEL ADMIN ---
def admin_footer():
    st.markdown('<div style="margin-top:150px; opacity:0;">.</div>', unsafe_allow_html=True)
    with st.expander("Admin"):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            st.write(pd.DataFrame(st.session_state.data['appointments']))

# --- FLUJO ---
if st.session_state.view == 'booking':
    booking_interface()
else:
    confirmation_view()

admin_footer()
