import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

TIME_SLOTS = ["08:00", "09:30", "11:00", "13:00", "14:30", "16:00", "17:30"]

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
    .whatsapp-btn {
        background-color: #25D366; color: white !important; padding: 18px 25px;
        border-radius: 50px; text-align: center; text-decoration: none;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 1.1rem; margin: 25px auto; max-width: 380px;
    }
    .admin-label { font-size: 0.5rem; color: #E0E0E0; text-align: center; margin-top: 100px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. FLUJO CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, (key, s) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(s["img"], use_container_width=True)
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"btn_{key}"):
                st.session_state.pre_selected = s['title']

    st.divider()
    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        with st.form("main_booking"):
            n = st.text_input("Nombre y Apellido")
            p = st.text_input("WhatsApp")
            d = st.date_input("Fecha", min_value=datetime.date.today())
            blocked = [a['time'] for a in st.session_state.data['appointments'] if a['date'] == str(d)]
            avail = [s for s in TIME_SLOTS if s not in blocked]
            t = st.selectbox("Horario Disponible", avail if avail else ["Sin turnos"])
            s_list = [s['title'] for s in SERVICES.values()]
            serv = st.selectbox("Servicio", s_list)
            pay = st.radio("Método de Pago", ["Efectivo", "Transferencia / Pix"], horizontal=True)
            if st.form_submit_button("REVISAR"):
                if n and p and t != "Sin turnos":
                    st.session_state.temp_res = {"id": str(uuid.uuid4())[:6].upper(), "client": n, "phone": p, "service": serv, "price": next(s['price'] for s in SERVICES.values() if s['title'] == serv), "date": str(d), "time": t, "payment": pay, "status": "Por Procesar"}
                    st.session_state.view = 'confirm'; st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    pago_ok = True
    if res['payment'] == "Transferencia / Pix":
        pago_ok = False
        st.info(f"Familiar: 815643114 | Ueno: 4437206")
        file = st.file_uploader("ADJUNTAR COMPROBANTE", type=['jpg', 'png', 'jpeg'])
        if file: pago_ok = True

    msg = f"💅 *RESERVA NAILS BY DIVA*\n*ID:* #{res['id']}\n*Cliente:* {res['client']}\n*Servicio:* {res['service']}\n*Fecha:* {res['date']} {res['time']}"
    url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"

    if pago_ok:
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">ENVIAR COMPROBANTE Y AGENDAR</a>', unsafe_allow_html=True)
        if st.button("Finalizar"):
            st.session_state.data['appointments'].append(res); save_data(st.session_state.data)
            st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMIN ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            apts = st.session_state.data['appointments']
            exps = st.session_state.data['expenses']
            
            # --- MÉTRICAS ---
            ing = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
            gst = sum(e['amount'] for e in exps)
            pcobrar = sum(a['price'] for a in apts if a['status'] in ['Pendiente', 'Por Procesar'])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos (Caja)", f"₲{ing:,}")
            c2.metric("Egresos (Gastos)", f"₲{gst:,}")
            c3.metric("Monto Por Cobrar", f"₲{pcobrar:,}")

            # --- ESTADÍSTICA DE LÍNEA ---
            if apts:
                df = pd.DataFrame(apts)
                df['date'] = pd.to_datetime(df['date'])
                df_fin = df[df['status'] == 'Finalizado']
                if not df_fin.empty:
                    st.subheader("📊 Histórico de Ingresos")
                    fig = px.line(df_fin.groupby('date')['price'].sum().reset_index(), x='date', y='price', markers=True)
                    st.plotly_chart(fig, use_container_width=True)

            # --- PROCESOS ---
            st.subheader("📦 Procesos")
            t1, t2, t3, t4 = st.tabs(["Por Procesar", "Pendientes", "Finalizados", "Gasto"])
            
            with t1: # Por procesar
                for i, a in enumerate(apts):
                    if a['status'] == 'Por Procesar':
                        st.write(f"🆕 {a['date']} {a['time']} - {a['client']}")
                        if st.button(f"Confirmar Cita #{a['id']}", key=f"c_{i}"):
                            st.session_state.data['appointments'][i]['status'] = 'Pendiente'
                            save_data(st.session_state.data); st.rerun()
            
            with t2: # Pendientes
                for i, a in enumerate(apts):
                    if a['status'] == 'Pendiente':
                        st.write(f"📌 {a['date']} {a['time']} - {a['client']}")
                        if st.button(f"Finalizar Trabajo #{a['id']}", key=f"f_{i}"):
                            st.session_state.data['appointments'][i]['status'] = 'Finalizado'
                            save_data(st.session_state.data); st.rerun()
            
            with t3: # Finalizados
                if apts: st.dataframe(pd.DataFrame([a for a in apts if a['status'] == 'Finalizado']))

            with t4: # Gasto
                with st.form("g"):
                    conc = st.text_input("Gasto")
                    mont = st.number_input("Monto", step=1000)
                    if st.form_submit_button("Guardar"):
                        st.session_state.data['expenses'].append({"desc": conc, "amount": mont})
                        save_data(st.session_state.data); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()