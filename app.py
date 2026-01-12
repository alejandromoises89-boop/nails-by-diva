import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

# --- 2. BASE DE DATOS FIJA (Para evitar errores de almacenamiento) ---
# Edita esta lista para cambiar tus servicios/precios permanentemente
SERVICES = [
    {"title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
    {"title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
    {"title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
    {"title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
]

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# Almacenamiento temporal para reservas (en memoria de la sesión)
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'expenses' not in st.session_state: st.session_state.expenses = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- 3. ESTILOS RESPONSIVOS (Android, iOS, PC, Mac) ---
st.markdown("""
<style>
    /* Estilo para que las imágenes se adapten a cualquier pantalla */
    .stImage > img { 
        border-radius: 15px; 
        object-fit: cover; 
        width: 100% !important; 
        height: 180px !important; 
    }
    .whatsapp-btn {
        background-color: #25D366; color: white !important; padding: 18px 25px;
        border-radius: 50px; text-align: center; text-decoration: none;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 1.1rem; margin: 20px auto; max-width: 100%;
        box-shadow: 0 4px 15px rgba(37,211,102,0.3);
    }
    .admin-label { font-size: 0.5rem; color: #EEEEEE; text-align: center; margin-top: 80px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
    
    /* Ajuste de columnas para celulares */
    @media (max-width: 600px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center; font-family:serif;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; letter-spacing:5px; color:#D4AF37;">ATELIER</p>', unsafe_allow_html=True)
    
    # Galería de Servicios
    cols = st.columns(4)
    for idx, s in enumerate(SERVICES):
        with cols[idx % 4]:
            st.image(s["img"])
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"s_{idx}", use_container_width=True):
                st.session_state.pre_selected = s
                st.toast(f"Seleccionaste {s['title']}")

    st.divider()
    
    # Formulario de Reserva
    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.form("reserva_form"):
            nombre = st.text_input("Nombre y Apellido")
            whatsapp = st.text_input("Tu número de WhatsApp")
            fecha = st.date_input("Fecha de la Cita", min_value=datetime.date.today())
            horario = st.selectbox("Horario", ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30", "18:00"])
            pago = st.radio("Método de Pago", ["Efectivo", "Transferencia / Pix"], horizontal=True)
            
            if st.form_submit_button("REVISAR CITA"):
                if nombre and whatsapp and 'pre_selected' in st.session_state:
                    res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": nombre, "phone": whatsapp,
                        "service": st.session_state.pre_selected['title'],
                        "price": st.session_state.pre_selected['price'],
                        "date": str(fecha), "time": horario,
                        "payment": pago, "status": "Por Procesar"
                    }
                    st.session_state.temp_res = res
                    st.session_state.view = 'confirm'; st.rerun()
                else:
                    st.error("Por favor selecciona un servicio y completa tus datos.")

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown(f"<h3 style='text-align:center;'>Reserva #{res['id']}</h3>", unsafe_allow_html=True)
    
    pago_ok = True
    if res['payment'] == "Transferencia / Pix":
        pago_ok = False
        st.warning(f"Total: ₲{res['price']:,} | Banco Familiar: 815643114 | Ueno: 4437206")
        file = st.file_uploader("Sube la foto del comprobante", type=['jpg', 'png', 'jpeg'])
        if file: pago_ok = True

    msg = f"💅 *NUEVA CITA - NAILS BY DIVA*\n\nID: #{res['id']}\nServicio: {res['service']}\nFecha: {res['date']}\nHora: {res['time']}\nCliente: {res['client']}\nPago: {res['payment']}"
    url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"

    if pago_ok:
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">ENVIAR A WHATSAPP</a>', unsafe_allow_html=True)
        if st.button("Confirmar y Volver"):
            st.session_state.appointments.append(res)
            st.session_state.view = 'booking'; st.rerun()
    else:
        st.error("Adjunta el comprobante para habilitar el botón.")

# --- 5. PANEL ADMIN ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            apts = st.session_state.appointments
            
            # --- MÉTRICAS ---
            ing = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
            pcobrar = sum(a['price'] for a in apts if a['status'] != 'Finalizado')
            
            c1, c2 = st.columns(2)
            c1.metric("Cobrado ✅", f"₲{ing:,}")
            c2.metric("Por Cobrar ⏳", f"₲{pcobrar:,}")

            # --- PROCESOS ---
            st.subheader("Gestión de Reservas")
            t1, t2, t3 = st.tabs(["Nuevas / Por Procesar", "Finalizadas", "Eliminar"])
            
            with t1:
                for i, a in enumerate(apts):
                    if a['status'] != 'Finalizado':
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"📌 {a['date']} {a['time']} - {a['client']} ({a['service']})")
                        if col2.button("Finalizar ✅", key=f"f_{i}"):
                            st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
            
            with t2:
                st.dataframe(pd.DataFrame([a for a in apts if a['status'] == 'Finalizado']))

            with t3:
                for i, a in enumerate(apts):
                    col1, col2 = st.columns([4, 1])
                    col1.write(f"🗑️ {a['date']} - {a['client']}")
                    if col2.button("Borrar", key=f"del_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()
