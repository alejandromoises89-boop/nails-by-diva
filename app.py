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
BUSINESS_PHONE = "595992698406" 
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

# --- 3. ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .header-title { font-family: serif; font-size: 2.5rem; text-align: center; color: #333; }
    
    /* Botón WhatsApp Estilo Corporativo */
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 15px 30px;
        border-radius: 50px;
        text-align: center;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.1rem;
        margin: 20px auto;
        max-width: 350px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .whatsapp-icon { width: 25px; margin-right: 10px; }
    
    /* Admin Minimalista al fondo */
    .admin-footer { 
        font-size: 0.5rem; 
        color: #E0E0E0; 
        text-align: center; 
        margin-top: 150px;
    }
    
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 class="header-title">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; letter-spacing:8px; color:#D4AF37; font-size:0.8rem; margin-top:-10px;">ATELIER</p>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for idx, (key, s) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(s["img"], use_container_width=True)
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"s_{key}"):
                st.session_state.pre_selected = s['title']
                st.toast(f"Elegiste {s['title']}")

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
            if st.form_submit_button("REVISAR DATOS"):
                if name and phone:
                    st.session_state.temp_res = {"id": str(uuid.uuid4())[:6].upper(), "client": name, "phone": phone, "service": serv, "price": next(s['price'] for s in SERVICES.values() if s['title'] == serv), "date": str(date), "payment": pay, "status": "Pendiente"}
                    st.session_state.view = 'confirm'; st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown("<h3 style='text-align:center;'>FINALIZAR</h3>", unsafe_allow_html=True)
    
    pago_listo = True
    if res['payment'] == "Transferencia / Pix":
        pago_listo = False
        st.info(f"🏦 Banco Familiar: 815643114 | Ueno Alias: 4437206")
        archivo = st.file_uploader("SUBIR COMPROBANTE AQUÍ", type=['jpg', 'png', 'jpeg'])
        if archivo: pago_listo = True

    if pago_listo:
        msg = f"💅 *TICKET NAILS BY DIVA*\n*Servicio:* {res['service']}\n*ID:* #{res['id']}\n*Total:* ₲{res['price']:,}\n*Pago:* {res['payment']}"
        url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
        
        # BOTÓN WHATSAPP CORPORATIVO
        st.markdown(f"""
            <a href="{url_wa}" target="_blank" class="whatsapp-btn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-icon">
                ENVIAR COMPROBANTE POR WHATSAPP
            </a>
        """, unsafe_allow_html=True)
        
        if st.button("Finalizar y Volver"):
            st.session_state.data['appointments'].append(res); save_data(st.session_state.data)
            st.session_state.view = 'booking'; st.rerun()
    else:
        st.error("Adjunta el comprobante para habilitar el envío.")

# --- 5. PANEL ADMIN (SOLO "admin") ---
def admin_footer():
    st.markdown('<div class="admin-footer">.</div>', unsafe_allow_html=True)
    with st.expander("admin"):
        pin = st.text_input("PIN", type="password")
        if pin == ADMIN_PIN:
            apts = st.session_state.data['appointments']
            df = pd.DataFrame(apts)
            st.metric("INGRESOS REALES", f"₲ {sum(a['price'] for a in apts if a.get('status') == 'Concluido'):,}")
            if not df.empty:
                st.bar_chart(df[df['status'] == 'Concluido'].groupby('service')['price'].sum())
                st.dataframe(df)

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_footer()
