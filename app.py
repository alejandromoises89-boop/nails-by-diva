import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "expenses": [], "settings": {}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"appointments": [], "expenses": [], "settings": {}}

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
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    .header-container { text-align: center; padding: 20px 0; }
    .header-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; letter-spacing: 3px; margin: 0; text-transform: uppercase; }
    .metric-card { background: #fff; padding: 15px; border-radius: 10px; border-top: 3px solid #D4AF37; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .mini-card { text-align: center; padding: 10px; background: white; border-radius: 12px; border: 1px solid #F0F0F0; }
    [data-testid="stHeader"], footer { visibility: hidden; }
    .admin-box { background: #fdfdfd; padding: 40px; border-top: 1px solid #ddd; margin-top: 100px; }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNCIONES DE CLIENTE ---
def header():
    st.markdown('<div class="header-container"><h1 class="header-title">NAILS BY DIVA</h1><p style="letter-spacing:10px; color:#D4AF37; font-size:0.8rem;">ATELIER</p></div>', unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service["img"], use_container_width=True)
            st.markdown(f'<div class="mini-card"><div style="font-size:0.8rem; font-weight:600;">{service["title"]}</div><div style="color:#D4AF37; font-weight:bold;">₲{service["price"]:,}</div></div>', unsafe_allow_html=True)
            if st.button("SELECCIONAR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Elegiste {service['title']}")

def booking_section():
    st.markdown("<h3 style='text-align:center; font-size:0.9rem; letter-spacing:3px; margin-top:30px;'>AGENDAR CITA</h3>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            service_list = [s['title'] for s in SERVICES.values()]
            idx_p = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            selected_service = st.selectbox("Servicio", service_list, index=idx_p)
            payment = st.selectbox("Pago", ["Efectivo", "Transferencia / Pix"])
            if st.form_submit_button("CONFIRMAR"):
                if name and phone:
                    res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": name, "phone": phone, "service": selected_service,
                        "price": next(s['price'] for s in SERVICES.values() if s['title'] == selected_service),
                        "date": str(date), "payment": payment, "status": "Pendiente"
                    }
                    st.session_state.data['appointments'].append(res)
                    save_data(st.session_state.data)
                    st.session_state.last_res = res
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"<div style='text-align:center; padding:30px; background:white; border-radius:15px; border:1px solid #D4AF37;'><h2>¡RESERVA REGISTRADA!</h2><p>Ref: <b>{res['id']}</b></p></div>", unsafe_allow_html=True)
    if res['payment'] == "Transferencia / Pix":
        st.info("B. Familiar: 815643114 | Ueno Alias: 4437206")
    msg = f"✨ *NAILS BY DIVA*\n*ID:* {res['id']}\n*Servicio:* {res['service']}"
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{url}" target="_blank"><div style="background:#25D366; color:white; padding:15px; border-radius:30px; text-align:center; font-weight:bold;">🚀 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
    if st.button("VOLVER AL INICIO"): st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMINISTRATIVO (AL FINAL) ---
def bottom_admin_panel():
    st.markdown('<div class="admin-box"></div>', unsafe_allow_html=True)
    with st.expander("🛠️ ACCESO ADMINISTRATIVO (NAILS BY DIVA)"):
        st.header("📊 Resumen del Negocio")
        
        apts = st.session_state.data.get('appointments', [])
        exps = st.session_state.data.get('expenses', [])
        
        # Cálculos de ingresos
        ingreso_real = sum(a['price'] for a in apts if a.get('status') == 'Concluido')
        ingreso_pend = sum(a['price'] for a in apts if a.get('status') == 'Pendiente')
        gastos = sum(e['amount'] for e in exps)
        neto = ingreso_real - gastos
        
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><small>INGRESOS REALES</small><h3>₲ {ingreso_real:,}</h3></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><small>POR COBRAR</small><h3 style="color:orange;">₲ {ingreso_pend:,}</h3></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><small>GASTOS</small><h3 style="color:red;">₲ {gastos:,}</h3></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><small>BALACE NETO</small><h3 style="color:green;">₲ {neto:,}</h3></div>', unsafe_allow_html=True)

        

        st.divider()
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.subheader("💸 Nuevo Gasto")
            with st.form("gasto_form"):
                d = st.text_input("Concepto")
                v = st.number_input("Monto ₲", step=1000)
                if st.form_submit_button("Guardar Gasto"):
                    st.session_state.data['expenses'].append({"desc": d, "amount": v, "date": str(datetime.date.today())})
                    save_data(st.session_state.data)
                    st.success("Gasto guardado")
                    st.rerun()

        with c_right:
            st.subheader("📅 Gestión de Citas")
            if apts:
                for i, a in enumerate(apts):
                    status_text = "✅" if a.get('status') == 'Concluido' else "⌛"
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(f"{status_text} **{a['client']}** - {a['service']}")
                    if a.get('status') == 'Pendiente':
                        if col_b.button("Concluir", key=f"btn_{i}"):
                            st.session_state.data['appointments'][i]['status'] = 'Concluido'
                            save_data(st.session_state.data)
                            st.rerun()
            else:
                st.write("No hay datos.")

# --- 6. FLUJO PRINCIPAL ---
header()

if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()

# Aquí el panel administrativo siempre queda al final de todo
bottom_admin_panel()