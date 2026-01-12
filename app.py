import streamlit as st
import pandas as pd
import datetime
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

# --- 2. BASE DE DATOS ESTATICA (Cambia precios aquí para que no den error) ---
if 'services' not in st.session_state:
    st.session_state.services = [
        {"id": 1, "title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
        {"id": 2, "title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
        {"id": 3, "title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
        {"id": 4, "title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
    ]

if 'products' not in st.session_state: st.session_state.products = []
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'expenses' not in st.session_state: st.session_state.expenses = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. DISEÑO RESPONSIVO (CORRECCIÓN PARA TABLETS/MÓVILES) ---
st.markdown("""
<style>
    /* Ajuste para que las imágenes no se estiren y se vean bien en iPad/iPhone */
    .stImage > img { 
        border-radius: 20px; 
        object-fit: cover; 
        width: 100% !important; 
        height: 200px !important; 
    }
    .whatsapp-btn {
        background-color: #25D366; color: white !important; padding: 20px;
        border-radius: 50px; text-align: center; text-decoration: none;
        display: block; font-weight: bold; font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    /* Admin casi invisible al final */
    .admin-label { font-size: 0.5rem; color: #F0F0F0; text-align: center; margin-top: 100px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#D4AF37; letter-spacing:5px;">ATELIER</p>', unsafe_allow_html=True)
    
    # Grid de Servicios Dinámicos
    services = st.session_state.services
    cols = st.columns(len(services) if len(services) < 5 else 4)
    for idx, s in enumerate(services):
        with cols[idx % 4]:
            st.image(s["img"])
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"serv_{idx}", use_container_width=True):
                st.session_state.selected_service = s
                st.toast(f"Seleccionado: {s['title']}")

    st.divider()
    
    with st.form("reserva_tablet"):
        n = st.text_input("Nombre y Apellido")
        p = st.text_input("WhatsApp")
        f = st.date_input("Fecha", min_value=datetime.date.today())
        h = st.selectbox("Horario", ["08:00", "10:00", "13:00", "15:00", "17:00"])
        promo = st.text_input("Código de Promoción (Opcional)")
        
        if st.form_submit_button("RESERVAR AHORA"):
            if n and p and 'selected_service' in st.session_state:
                st.session_state.temp_res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": n, "phone": p,
                    "service": st.session_state.selected_service['title'],
                    "price": st.session_state.selected_service['price'],
                    "date": str(f), "time": h, "status": "Por Procesar"
                }
                st.session_state.view = 'confirm'; st.rerun()
            else:
                st.error("Selecciona un servicio arriba primero.")

def confirmation_view():
    res = st.session_state.temp_res
    st.subheader(f"Confirmar Turno: {res['service']}")
    
    # Lógica de mensaje personalizado para WhatsApp
    msg = f"💅 *NUEVA CITA*\n*ID:* #{res['id']}\n*Servicio:* {res['service']}\n*Fecha:* {res['date']}\n*Hora:* {res['time']}\n*Cliente:* {res['client']}"
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
    
    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">ENVIAR AGENDAMIENTO</a>', unsafe_allow_html=True)
    
    if st.button("Finalizar y Salir"):
        st.session_state.appointments.append(res)
        st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMIN COMPLETO ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        pin = st.text_input("PIN de Acceso", type="password")
        if pin == ADMIN_PIN:
            t1, t2, t3, t4 = st.tabs(["📊 Estadísticas", "💅 Catálogo", "📅 Reservas", "🏷️ Promos"])
            
            with t1: # ESTADISTICAS
                apts = st.session_state.appointments
                ing = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
                pend = sum(a['price'] for a in apts if a['status'] != 'Finalizado')
                st.metric("INGRESOS REALES (Finalizados)", f"₲{ing:,}")
                st.metric("POR COBRAR (Pendientes)", f"₲{pend:,}")
                if apts: st.line_chart(pd.DataFrame(apts).groupby('date')['price'].sum())

            with t2: # AGREGAR Y CAMBIAR PRECIOS
                st.subheader("Agregar Servicio o Producto")
                with st.form("add_item"):
                    tipo = st.radio("Tipo", ["Servicio", "Producto"], horizontal=True)
                    nom = st.text_input("Nombre")
                    pre = st.number_input("Precio", step=5000)
                    img = st.text_input("URL Imagen (https://...)")
                    if st.form_submit_button("Guardar"):
                        nuevo = {"id": len(st.session_state.services)+1, "title": nom, "price": pre, "img": img}
                        if tipo == "Servicio": st.session_state.services.append(nuevo)
                        else: st.session_state.products.append(nuevo)
                        st.rerun()
                
                st.divider()
                st.subheader("Cambiar Precios")
                for i, s in enumerate(st.session_state.services):
                    new_p = st.number_input(f"Editar {s['title']}", value=s['price'], key=f"p_{i}")
                    st.session_state.services[i]['price'] = new_p

            with t3: # BORRAR Y GESTIONAR
                st.subheader("Gestión de Procesos")
                for i, a in enumerate(st.session_state.appointments):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"{a['date']} | {a['client']} ({a['status']})")
                    if col2.button("Finalizar ✅", key=f"fin_{i}"):
                        st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
                    if col3.button("Borrar 🗑️", key=f"del_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

            with t4: # PROMOS
                st.subheader("Agregar Promoción")
                cod = st.text_input("Código (ej: DIVA10)")
                desc = st.slider("Descuento %", 0, 100, 10)
                if st.button("Activar Promo"):
                    st.success(f"Promo {cod} activada")

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()
