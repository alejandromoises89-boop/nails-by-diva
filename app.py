import streamlit as st
import pandas as pd
import datetime
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

# Horarios estándar del atelier
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
if 'blocked_dates' not in st.session_state: st.session_state.blocked_dates = [] # Fechas bloqueadas
if 'expenses' not in st.session_state: st.session_state.expenses = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. DISEÑO RESPONSIVO ---
st.markdown("""
<style>
    .stImage > img { border-radius: 20px; object-fit: cover; width: 100% !important; height: 180px !important; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 18px; border-radius: 50px; text-align: center; text-decoration: none; display: block; font-weight: bold; }
    .admin-label { font-size: 0.5rem; color: #F8F8F8; text-align: center; margin-top: 80px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE CON BLOQUEO ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    
    # Galería de servicios
    cols = st.columns(4)
    for idx, s in enumerate(st.session_state.services):
        with cols[idx % 4]:
            st.image(s["img"])
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"s_{idx}", use_container_width=True):
                st.session_state.selected_item = s
                st.toast(f"Elegido: {s['title']}")

    st.divider()
    
    with st.form("reserva_segura"):
        st.subheader("Datos de la Reserva")
        nombre = st.text_input("Nombre y Apellido")
        whatsapp = st.text_input("WhatsApp")
        
        # Selección de fecha
        fecha_sel = st.date_input("Selecciona la Fecha", min_value=datetime.date.today())
        fecha_str = str(fecha_sel)
        
        # Verificar si la fecha está bloqueada totalmente
        if fecha_str in st.session_state.blocked_dates:
            st.error("⚠️ Esta fecha no está disponible (Cerrado o Completo).")
            horarios_libres = []
        else:
            # Filtrar horarios ya ocupados en esa fecha
            ocupados = [a['time'] for a in st.session_state.appointments if a['date'] == fecha_str]
            horarios_libres = [h for h in HORARIOS_DISPONIBLES if h not in ocupados]
        
        horario_sel = st.selectbox("Horarios Disponibles", horarios_libres if horarios_libres else ["Sin turnos"])
        
        if st.form_submit_button("RESERVAR"):
            if nombre and whatsapp and 'selected_item' in st.session_state and horario_sel != "Sin turnos":
                st.session_state.temp_res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": nombre, "phone": whatsapp,
                    "service": st.session_state.selected_item['title'],
                    "price": st.session_state.selected_item['price'],
                    "date": fecha_str, "time": horario_sel, "status": "Pendiente"
                }
                st.session_state.view = 'confirm'; st.rerun()
            else:
                st.error("Por favor, completa todos los campos y elige un servicio.")

def confirmation_view():
    res = st.session_state.temp_res
    st.info(f"Reserva para {res['client']} el {res['date']} a las {res['time']}")
    url = f"https://wa.me/{BUSINESS_PHONE}?text=Reserva {res['id']}: {res['service']} para el {res['date']} a las {res['time']}"
    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">CONFIRMAR EN WHATSAPP</a>', unsafe_allow_html=True)
    if st.button("Finalizar Registro"):
        st.session_state.appointments.append(res); st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMIN CON BLOQUEO DE FECHAS ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password", key="admin_pin") == ADMIN_PIN:
            t1, t2, t3, t4 = st.tabs(["📊 Caja", "🚫 Bloquear Fechas", "⚙️ Procesos", "💅 Catálogo"])
            
            with t1: # CAJA
                apts = st.session_state.appointments
                ingresos = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
                pendientes = sum(a['price'] for a in apts if a['status'] != 'Finalizado')
                st.metric("Ingresos (Cobrado)", f"₲{ingresos:,}")
                st.metric("Por Cobrar", f"₲{pendientes:,}")

            with t2: # BLOQUEO DE FECHAS
                st.subheader("Bloquear un día entero")
                f_block = st.date_input("Selecciona fecha para cerrar")
                if st.button("Bloquear Fecha 🔒"):
                    if str(f_block) not in st.session_state.blocked_dates:
                        st.session_state.blocked_dates.append(str(f_block))
                        st.success(f"Día {f_block} bloqueado.")
                    st.rerun()
                
                st.write("**Fechas Bloqueadas actualmente:**")
                for fb in st.session_state.blocked_dates:
                    c1, c2 = st.columns([3,1])
                    c1.write(fb)
                    if c2.button("Desbloquear", key=f"unl_{fb}"):
                        st.session_state.blocked_dates.remove(fb); st.rerun()

            with t3: # PROCESOS Y BORRAR RESERVAS
                for i, a in enumerate(st.session_state.appointments):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"{a['date']} {a['time']} | {a['client']}")
                    if col2.button("Finalizar ✅", key=f"f_{i}"):
                        st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
                    if col3.button("Borrar 🗑️", key=f"dr_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

            with t4: # CATALOGO
                # (Aquí va el código anterior de agregar/borrar servicios y cambiar precios)
                st.info("Aquí puedes gestionar tus servicios como en la versión anterior.")

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()