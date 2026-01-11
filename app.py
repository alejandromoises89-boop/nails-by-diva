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

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    .header-title { font-family: serif; font-size: 2.5rem; text-align: center; color: #333; }
    .stButton > button { width: 100%; border-radius: 30px !important; font-weight: bold; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 class="header-title">NAILS BY DIVA</h1><p style="text-align:center; letter-spacing:8px; color:#D4AF37; font-size:0.8rem;">ATELIER</p>', unsafe_allow_html=True)
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
            if st.form_submit_button("REVISAR"):
                if name and phone:
                    st.session_state.temp_res = {"id": str(uuid.uuid4())[:6].upper(), "client": name, "phone": phone, "service": serv, "price": next(s['price'] for s in SERVICES.values() if s['title'] == serv), "date": str(date), "payment": pay, "status": "Pendiente"}
                    st.session_state.view = 'confirm'; st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown("<h3 style='text-align:center;'>CONFIRMACIÓN</h3>", unsafe_allow_html=True)
    
    pago_listo = True
    if res['payment'] == "Transferencia / Pix":
        pago_listo = False
        st.warning(f"🏦 Banco Familiar: 815643114 | Ueno Alias: 4437206 | Total: ₲ {res['price']:,}")
        archivo = st.file_uploader("SUBIR COMPROBANTE", type=['jpg', 'png', 'jpeg'])
        if archivo: pago_listo = True

    if pago_listo:
        msg = f"💅 *RESERVA NAILS BY DIVA*\nID: #{res['id']}\nCliente: {res['client']}\nServicio: {res['service']}\nFecha: {res['date']}\nTotal: ₲ {res['price']:,}"
        url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
        if st.button("🚀 ENVIAR AL WHATSAPP"):
            st.session_state.data['appointments'].append(res); save_data(st.session_state.data)
            st.markdown(f'<meta http-equiv="refresh" content="0;URL={url_wa}">', unsafe_allow_html=True)
    else:
        st.button("🚫 CARGAR COMPROBANTE", disabled=True)

# --- 5. PANEL ADMIN CON ESTADÍSTICAS ---
def admin_footer():
    st.markdown('<div style="margin-top:100px; opacity:0.1;">.</div>', unsafe_allow_html=True)
    with st.expander("🛠️ Admin Panel"):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            apts = st.session_state.data['appointments']
            exps = st.session_state.data['expenses']
            
            # Métricas
            in_r = sum(a['price'] for a in apts if a.get('status') == 'Concluido')
            gst = sum(e['amount'] for e in exps)
            st.metric("GANANCIA LIMPIA (NETO)", f"₲ {in_r-gst:,}")

            # GRÁFICA DE RENTABILIDAD
            if apts:
                st.subheader("📊 Ingresos por Servicio")
                df = pd.DataFrame(apts)
                # Filtrar solo concluidos para la gráfica de dinero real
                df_concluido = df[df['status'] == 'Concluido']
                if not df_concluido.empty:
                    stats = df_concluido.groupby('service')['price'].sum()
                    st.bar_chart(stats)
                    
                else:
                    st.info("Aún no hay servicios 'Concluidos' para mostrar estadísticas.")

            st.divider()
            t1, t2 = st.tabs(["Citas", "Gastos"])
            with t1:
                for i, a in enumerate(apts):
                    if a.get('status') == 'Pendiente':
                        if st.button(f"Concluir {a['client']} (₲{a['price']:,})", key=f"c_{i}"):
                            st.session_state.data['appointments'][i]['status'] = 'Concluido'
                            save_data(st.session_state.data); st.rerun()
            with t2:
                with st.form("egreso"):
                    desc = st.text_input("Gasto")
                    monto = st.number_input("₲", step=1000)
                    if st.form_submit_button("Guardar"):
                        st.session_state.data['expenses'].append({"desc": desc, "amount": monto})
                        save_data(st.session_state.data); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_footer()