import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Diva | Nail Atelier", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "expenses": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
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

# --- 3. ESTILOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    .stApp { background-color: #FAFAFA; color: #333; font-family: 'Inter', sans-serif; }
    .header-container { text-align: center; padding: 20px 0; }
    .header-title { font-family: 'Playfair Display', serif; font-size: 3rem; letter-spacing: 8px; margin: 0; }
    .header-subtitle { font-size: 0.7rem; letter-spacing: 10px; color: #D4AF37; text-transform: uppercase; }
    .mini-card { text-align: center; padding: 10px; background: white; border-radius: 12px; border: 1px solid #F0F0F0; }
    .service-price { font-family: 'Playfair Display', serif; font-style: italic; color: #D4AF37; font-size: 1.1rem; }
    .metric-box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border-bottom: 3px solid #D4AF37; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. PANEL ADMINISTRATIVO (NUEVO) ---
def admin_dashboard():
    with st.sidebar:
        st.markdown("### 🔒 Diva Admin")
        show_admin = st.checkbox("Abrir Panel de Control")
    
    if show_admin:
        st.divider()
        st.title("Panel de Gestión Financiera")
        
        # Métricas principales
        apts = st.session_state.data.get('appointments', [])
        exps = st.session_state.data.get('expenses', [])
        
        ingreso_total = sum(a['price'] for a in apts)
        gastos_totales = sum(e['amount'] for e in exps)
        # Suponiendo que 'pendiente' son los que no son 'Efectivo' o no confirmados
        pendientes = sum(a['price'] for a in apts if a.get('status') == 'Pendiente')
        
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-box"><h6>Ingreso Bruto</h6><h3>₲ {ingreso_total:,}</h3></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-box"><h6>Pendiente Cobro</h6><h3>₲ {pendientes:,}</h3></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-box"><h6>Gastos</h6><h3>₲ {gastos_totales:,}</h3></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-box"><h6>Balance Neto</h6><h3>₲ {ingreso_total - gastos_totales:,}</h3></div>', unsafe_allow_html=True)

        # Sección Gastos y QRs
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Registrar Gasto")
            with st.form("expense_form"):
                desc = st.text_input("Concepto (ej: Alquiler, Esmaltes)")
                amt = st.number_input("Monto ₲", min_value=0, step=5000)
                if st.form_submit_button("Guardar Gasto"):
                    st.session_state.data['expenses'].append({"desc": desc, "amount": amt, "date": str(datetime.date.today())})
                    save_data(st.session_state.data)
                    st.rerun()

        with col_b:
            st.subheader("Actualizar QRs")
            qr_f = st.file_uploader("Subir QR Familiar", type=['png', 'jpg'])
            if qr_f:
                st.session_state.data['settings']['qr_familiar'] = base64.b64encode(qr_f.read()).decode()
                save_data(st.session_state.data)
                st.success("QR Familiar actualizado")

        st.subheader("Listado de Citas")
        if apts:
            df = pd.DataFrame(apts)
            st.table(df[['id', 'client', 'service', 'price', 'payment']])
        
        if st.button("Cerrar Panel"): st.rerun()
        st.divider()

# --- 5. FUNCIONES DE CLIENTE ---
def header():
    st.markdown('<div class="header-container"><h1 class="header-title">DIVA</h1><p class="header-subtitle">Nail Atelier</p></div>', unsafe_allow_html=True)

def show_catalog():
    cols = st.columns(4)
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service["img"], use_container_width=True)
            st.markdown(f'<div class="mini-card"><div class="service-title">{service["title"]}</div><div class="service-price">₲{service["price"]:,}</div></div>', unsafe_allow_html=True)
            if st.button("SELECCIONAR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Elegiste {service['title']}")

def booking_section():
    st.markdown("<h3 style='text-align:center; font-size:1rem; letter-spacing:3px; margin: 40px 0 20px 0;'>RESERVAR CITA</h3>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            phone = st.text_input("WhatsApp")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            service_list = [s['title'] for s in SERVICES.values()]
            idx_p = service_list.index(st.session_state.pre_selected) if 'pre_selected' in st.session_state else 0
            selected_service = st.selectbox("Servicio", service_list, index=idx_p)
            price = next(s['price'] for s in SERVICES.values() if s['title'] == selected_service)
            payment = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Pix"])
            
            if st.form_submit_button("CONFIRMAR"):
                if name and phone:
                    # Marcamos como pendiente si no es efectivo
                    status = "Pendiente" if payment != "Efectivo" else "Cobrado"
                    res = {"id": str(uuid.uuid4())[:6].upper(), "client": name, "phone": phone, "service": selected_service, "price": price, "date": str(date), "payment": payment, "status": status}
                    st.session_state.data['appointments'].append(res)
                    save_data(st.session_state.data)
                    st.session_state.last_res = res
                    st.session_state.view = 'success'
                    st.rerun()

def success_view():
    res = st.session_state.last_res
    st.markdown(f"<div style='text-align:center; padding:30px; background:white; border-radius:15px; border:1px solid #D4AF37;'><h2>¡REGISTRADO!</h2><p>{res['service']} - ₲ {res['price']:,}</p></div>", unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.subheader("Datos de Pago")
        c1, c2 = st.columns(2)
        with c1:
            st.info("Banco Familiar: 815643114")
            qr = st.session_state.data['settings'].get('qr_familiar')
            if qr: st.image(f"data:image/png;base64,{qr}")
        with c2:
            st.info("Ueno / Pix: 4437206")

    msg = f"Reserva Diva: {res['service']} - {res['client']} - ID: {res['id']}"
    st.markdown(f'<a href="https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}" target="_blank"><div style="background:#25D366; color:white; padding:15px; border-radius:30px; text-align:center; font-weight:bold;">ENVIAR COMPROBANTE</div></a>', unsafe_allow_html=True)
    if st.button("VOLVER"):
        st.session_state.view = 'booking'
        st.rerun()

# --- 6. FLUJO ---
admin_dashboard()
header()
if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()