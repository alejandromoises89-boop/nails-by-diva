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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; }
    .header-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; text-align: center; text-transform: uppercase; margin-bottom: 0; }
    .ticket-box { background: white; padding: 25px; border-radius: 10px; border: 1px dashed #ccc; margin: 20px 0; }
    .bank-info { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #D4AF37; margin: 10px 0; font-size: 0.9rem; }
    .stButton > button { border-radius: 25px !important; text-transform: uppercase; font-weight: bold; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE CLIENTE ---
def booking_interface():
    st.markdown('<div style="padding:20px 0;"><h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:8px; color:#D4AF37; font-size:0.7rem;">ESTÉTICA & DISEÑO</p></div>', unsafe_allow_html=True)
    
    # Catálogo
    cols = st.columns(4)
    for idx, (key, s) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(s["img"], use_container_width=True)
            st.markdown(f'<div style="text-align:center; font-size:0.75rem;"><b>{s["title"]}</b><br><span style="color:#D4AF37;">₲{s["price"]:,}</span></div>', unsafe_allow_html=True)
            if st.button("Seleccionar", key=f"sel_{key}"):
                st.session_state.pre_selected = s['title']
                st.toast(f"Elegiste {s['title']}")

    st.divider()

    # Formulario
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        with st.form("main_form"):
            n = st.text_input("Tu Nombre")
            p = st.text_input("WhatsApp")
            d = st.date_input("Fecha", min_value=datetime.date.today())
            
            s_list = [s['title'] for s in SERVICES.values()]
            idx = s_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            serv_escogido = st.selectbox("Servicio", s_list, index=idx)
            metodo = st.radio("Método de Pago", ["Efectivo", "Transferencia / Pix"], horizontal=True)
            
            if st.form_submit_button("CONTINUAR"):
                if n and p:
                    st.session_state.temp_res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": n, "phone": p, "service": serv_escogido,
                        "price": next(s['price'] for s in SERVICES.values() if s['title'] == serv_escogido),
                        "date": str(d), "payment": metodo, "status": "Pendiente"
                    }
                    st.session_state.view = 'confirm'
                    st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown("<h4 style='text-align:center;'>CONFIRMA TU PEDIDO</h4>", unsafe_allow_html=True)
    
    # Mostrar datos del banco SI es transferencia
    if res['payment'] == "Transferencia / Pix":
        st.markdown(f"""
        <div class="bank-info">
            <b>🏦 DATOS DE PAGO:</b><br>
            • Banco Familiar: 815643114<br>
            • Ueno Alias: <b>4437206</b><br>
            • Titular: Nails by Diva
        </div>
        """, unsafe_allow_html=True)
        
        comp = st.file_uploader("SUBIR COMPROBANTE AQUÍ (Requerido)", type=['jpg', 'png', 'pdf'])
        pago_listo = True if comp else False
    else:
        st.info("📍 Pago al finalizar el servicio en efectivo.")
        pago_listo = True

    # Botón de WhatsApp Estilo PedidosYa
    if pago_listo:
        # Formato de mensaje estilo Ticket
        msg_ticket = (
            f"🛍️ *ORDEN DE SERVICIO - NAILS BY DIVA*\n"
            f"------------------------------------------\n"
            f"🆔 *Pedido:* #{res['id']}\n"
            f"👤 *Cliente:* {res['client']}\n"
            f"💅 *Servicio:* {res['service']}\n"
            f"📅 *Fecha:* {res['date']}\n"
            f"------------------------------------------\n"
            f"💰 *TOTAL A PAGAR:* ₲ {res['price']:,}\n"
            f"💳 *PAGO:* {res['payment']}\n"
            f"------------------------------------------\n"
            f"✅ *¡Comprobante adjuntado!*" if res['payment'] != "Efectivo" else "💵 *Pago en el local*"
        )
        url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg_ticket)}"
        
        if st.button("✅ FINALIZAR Y ENVIAR WHATSAPP", type="primary"):
            st.session_state.data['appointments'].append(res)
            save_data(st.session_state.data)
            st.markdown(f'<meta http-equiv="refresh" content="0;URL={url}">', unsafe_allow_html=True)
    else:
        st.button("🚫 SUBE EL COMPROBANTE PARA FINALIZAR", disabled=True)

    if st.button("⬅ Volver"):
        st.session_state.view = 'booking'
        st.rerun()

# --- 5. PANEL ADMIN ---
def admin_footer():
    st.markdown('<br><br><br><div style="text-align:center; opacity:0.1;">.</div>', unsafe_allow_html=True)
    with st.expander("Admin"):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            apts = st.session_state.data['appointments']
            st.write(pd.DataFrame(apts))
            if st.button("Limpiar todo (CUIDADO)"):
                st.session_state.data['appointments'] = []
                save_data(st.session_state.data); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking':
    booking_interface()
else:
    confirmation_view()

admin_footer()