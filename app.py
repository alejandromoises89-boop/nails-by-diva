import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
import uuid
from PIL import Image
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Diva | Nail Atelier",
    page_icon="💅",
    layout="wide"
)

# Archivo de base de datos
DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406"

# --- LÓGICA DE DATOS ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"appointments": [], "settings": {"qr_familiar": None, "qr_ueno": None}}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'view' not in st.session_state:
    st.session_state.view = 'booking'

# --- DATOS DE SERVICIOS ---
SERVICES = {
    "CAPPING": {
        "title": "💅 Capping Gel",
        "price": 120000,
        "desc": "Fortalecimiento sobre tu uña natural.",
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800&q=80"
    },
    "MAINTENANCE": {
        "title": "✨ Mantenimiento",
        "price": 80000,
        "desc": "Relleno y perfeccionamiento técnico.",
        "img": "https://i.ibb.co/bjf3G85q/images-1.jpg" # Link actualizado
    },
    "SEMIPERMANENT": {
        "title": "🎨 Semipermanente",
        "price": 70000,
        "desc": "Color duradero con brillo extremo.",
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?w=800&q=80"
    },
    "SOFT_GEL": {
        "title": "💎 Soft Gel",
        "price": 150000,
        "desc": "Extensiones premium con tips de gel.",
        "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg" # Link actualizado
    }
}

# --- MEJORA EN LA FUNCIÓN DE VISUALIZACIÓN ---
def show_catalog():
    cols = st.columns(len(SERVICES))
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            # Usamos st.image en lugar de HTML puro para mayor compatibilidad con URLs externas
            st.image(service["img"], use_container_width=True)
            
            st.markdown(f"""
            <div class="service-card" style="border-top: 3px solid #D4AF37;">
                <h4>{service['title']}</h4>
                <p>{service['desc']}</p>
                <h3 style="color:#D4AF37 !important;">₲ {service['price']:,}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"SELECCIONAR", key=f"btn_{key}"):
                st.session_state.pre_selected = service['title']
                st.toast(f"Seleccionaste {service['title']}")
def booking_section():
    st.markdown("<br><br><h2 style='text-align:center; letter-spacing:3px;'>RESERVAR CITA</h2>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        with st.form("booking_form"):
            name = st.text_input("Nombre y Apellido")
            phone = st.text_input("WhatsApp (ej: 0981...)")
            c1, c2 = st.columns(2)
            date = c1.date_input("Fecha", min_value=datetime.date.today())
            service_list = [s['title'] for s in SERVICES.values()]
            default_idx = 0
            if 'pre_selected' in st.session_state:
                if st.session_state.pre_selected in service_list:
                    default_idx = service_list.index(st.session_state.pre_selected)
            selected_service = c2.selectbox("Servicio", service_list, index=default_idx)
            time_slots = [f"{h:02d}:{m}" for h in range(8, 20) for m in ["00", "30"]]
            time = c1.selectbox("Horario", time_slots)
            payment = c2.selectbox("Forma de Pago", ["Efectivo", "Transferencia", "Pix"])
            
            if st.form_submit_button("CONFIRMAR MI EXPERIENCIA"):
                if name and phone:
                    res_id = str(uuid.uuid4())[:6].upper()
                    new_apt = {
                        "id": res_id, "client": name, "phone": phone,
                        "date": str(date), "time": time, "service": selected_service,
                        "payment": payment, "status": "PENDIENTE"
                    }
                    st.session_state.data['appointments'].append(new_apt)
                    save_data(st.session_state.data)
                    st.session_state.last_res = new_apt
                    st.session_state.view = 'success'
                    st.rerun()
                else:
                    st.warning("Por favor completa tu nombre y teléfono.")

def success_view():
    res = st.session_state.last_res
    st.markdown(f"""
    <div style='text-align:center; background:#000; color:#fff; padding:40px; border:2px solid #D4AF37;'>
        <h1 style='color:#D4AF37 !important;'>¡RESERVA SOLICITADA!</h1>
        <p>ID: {res['id']}</p>
        <h2 style='color:white !important;'>{res['service']}</h2>
        <p>{res['date']} — {res['time']} hs</p>
    </div>
    """, unsafe_allow_html=True)
    
    if res['payment'] in ["Transferencia", "Pix"]:
        st.markdown("<h2 style='text-align:center; margin-top:20px;'>MÉTODOS DE PAGO</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("BANCO FAMILIAR")
            st.code("Cta: 815643114")
            qr_f = st.session_state.data['settings'].get('qr_familiar')
            if qr_f: st.image(f"data:image/png;base64,{qr_f}", use_container_width=True)
            else: st.info("QR pendiente de carga")
        with col2:
            st.subheader("UENO / PIX")
            st.code("Alias: 4437206")
            qr_u = st.session_state.data['settings'].get('qr_ueno')
            if qr_u: st.image(f"data:image/png;base64,{qr_u}", use_container_width=True)
            else: st.info("QR pendiente de carga")

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.view = 'booking'
        st.rerun()

# --- PANEL DE ADMINISTRACIÓN ---
def admin_panel():
    st.sidebar.title("🔐 Administración")
    if st.sidebar.checkbox("Acceder al Panel"):
        st.divider()
        st.header("Gestión de QRs de Pago")
        
        c1, c2 = st.columns(2)
        with c1:
            up_f = st.file_uploader("Subir QR Familiar", type=['png', 'jpg', 'jpeg'])
            if up_f and st.button("Guardar QR Familiar"):
                b64 = base64.b64encode(up_f.getvalue()).decode()
                st.session_state.data['settings']['qr_familiar'] = b64
                save_data(st.session_state.data)
                st.success("QR Familiar Guardado")
        
        with c2:
            up_u = st.file_uploader("Subir QR Ueno", type=['png', 'jpg', 'jpeg'])
            if up_u and st.button("Guardar QR Ueno"):
                b64 = base64.b64encode(up_u.getvalue()).decode()
                st.session_state.data['settings']['qr_ueno'] = b64
                save_data(st.session_state.data)
                st.success("QR Ueno Guardado")

        st.divider()
        st.header("Citas Recibidas")
        if st.session_state.data['appointments']:
            df = pd.DataFrame(st.session_state.data['appointments'])
            st.dataframe(df)
            if st.button("Limpiar historial"):
                st.session_state.data['appointments'] = []
                save_data(st.session_state.data)
                st.rerun()

# --- EJECUCIÓN PRINCIPAL ---
admin_panel()
header()

if st.session_state.view == 'booking':
    show_catalog()
    booking_section()
else:
    success_view()