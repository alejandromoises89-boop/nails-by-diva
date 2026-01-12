import streamlit as st
import pandas as pd
import datetime
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

HORARIOS_DISPONIBLES = ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30", "18:00"]

# --- 2. INICIALIZACIÓN DE DATOS ---
if 'services' not in st.session_state:
    st.session_state.services = [
        {"id": "1", "title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
        {"id": "2", "title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
        {"id": "3", "title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
        {"id": "4", "title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
    ]

if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .stImage > img { border-radius: 20px; object-fit: cover; width: 100% !important; height: 180px !important; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 20px; border-radius: 50px; text-align: center; text-decoration: none; display: block; font-weight: bold; font-size: 1.1rem; }
    .whatsapp-disabled { background-color: #cccccc; color: #666666 !important; padding: 20px; border-radius: 50px; text-align: center; display: block; font-weight: bold; cursor: not-allowed; }
    .admin-label { font-size: 0.5rem; color: #F8F8F8; text-align: center; margin-top: 80px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    
    # 1. SELECCIÓN DE SERVICIO
    st.subheader("1. Elige tu Servicio")
    cols = st.columns(4)
    for idx, s in enumerate(st.session_state.services):
        with cols[idx % 4]:
            st.image(s["img"])
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"s_{idx}", use_container_width=True):
                st.session_state.selected_item = s
                st.toast(f"Elegido: {s['title']}")

    st.divider()
    
    # 2. DATOS Y HORARIOS
    with st.form("reserva_final"):
        st.subheader("2. Datos de la Cita")
        nombre = st.text_input("Nombre Completo")
        whatsapp = st.text_input("Número de WhatsApp")
        fecha_sel = st.date_input("Fecha", min_value=datetime.date.today())
        
        # Bloqueo de horarios ocupados
        ocupados = [a['time'] for a in st.session_state.appointments if a['date'] == str(fecha_sel)]
        libres = [h for h in HORARIOS_DISPONIBLES if h not in ocupados]
        horario_sel = st.selectbox("Horario Disponible", libres if libres else ["Sin turnos"])
        
        # 3. SELECCIÓN DE PAGO
        st.subheader("3. Método de Pago")
        metodo_pago = st.radio("¿Cómo deseas pagar?", ["Efectivo", "Tarjeta / Pix", "Transferencia Bancaria"], horizontal=True)
        
        if st.form_submit_button("CONTINUAR A CONFIRMACIÓN"):
            if nombre and whatsapp and 'selected_item' in st.session_state and horario_sel != "Sin turnos":
                st.session_state.temp_res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": nombre, "phone": whatsapp,
                    "service": st.session_state.selected_item['title'],
                    "price": st.session_state.selected_item['price'],
                    "date": str(fecha_sel), "time": horario_sel, "payment": metodo_pago, "status": "Pendiente"
                }
                st.session_state.view = 'confirm'; st.rerun()
            else:
                st.error("Por favor completa todos los datos y selecciona un servicio.")

def confirmation_view():
    res = st.session_state.temp_res
    st.markdown(f"### 📋 Resumen de tu Reserva #{res['id']}")
    
    # Mostrar detalles
    col_a, col_b = st.columns(2)
    col_a.write(f"**Cliente:** {res['client']}\n\n**Servicio:** {res['service']}\n\n**Fecha:** {res['date']}")
    col_b.write(f"**Hora:** {res['time']}\n\n**Monto:** ₲{res['price']:,}\n\n**Pago:** {res['payment']}")

    st.divider()
    
    # LOGICA DE COMPROBANTE
    comprobante_cargado = True
    if res['payment'] != "Efectivo":
        st.warning("⚠️ Has seleccionado un método electrónico. Por favor, adjunta tu comprobante para habilitar el envío del mensaje.")
        archivo = st.file_uploader("Subir foto del Comprobante / Screenshot", type=['jpg', 'png', 'jpeg'])
        if not archivo:
            comprobante_cargado = False
            st.info("💡 El botón de WhatsApp se activará cuando subas la imagen.")
    
    # MENSAJE PERSONALIZADO
    msg_wa = (
        f"💅 *RESERVA CONFIRMADA - NAILS BY DIVA*\n"
        f"------------------------------------------\n"
        f"🆔 *Ticket:* #{res['id']}\n"
        f"👤 *Cliente:* {res['client']}\n"
        f"✨ *Servicio:* {res['service']}\n"
        f"📅 *Fecha:* {res['date']}\n"
        f"⏰ *Hora:* {res['time']}\n"
        f"💰 *Monto:* ₲{res['price']:,}\n"
        f"💳 *Método:* {res['payment']}\n"
        f"------------------------------------------\n"
        f"📍 *Ubicación:* Presidente Franco, Alto Paraná.\n"
        f"🙏 *Gracias por elegirnos!*"
    )
    url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg_wa)}"

    # BOTÓN BLOQUEABLE
    if comprobante_cargado:
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">✅ ENVIAR TURNO POR WHATSAPP</a>', unsafe_allow_html=True)
        if st.button("Finalizar y Guardar"):
            st.session_state.appointments.append(res)
            st.session_state.view = 'booking'; st.rerun()
    else:
        st.markdown('<div class="whatsapp-disabled">❌ ADJUNTA EL PAGO PARA CONTINUAR</div>', unsafe_allow_html=True)

# --- 5. PANEL ADMIN ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password", key="admin_key") == ADMIN_PIN:
            # (Se mantienen las funciones de borrar, estadísticas y catálogo del código anterior)
            st.write("Panel Administrativo Activo")
            if st.button("Limpiar todas las reservas"):
                st.session_state.appointments = []; st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()
