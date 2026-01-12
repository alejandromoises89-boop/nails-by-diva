import streamlit as st
import pandas as pd
import datetime
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

# --- 2. INICIALIZACIÓN DE DATOS (Memoria de Sesión para evitar errores de disco) ---
if 'services' not in st.session_state:
    st.session_state.services = [
        {"id": "1", "title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
        {"id": "2", "title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
        {"id": "3", "title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
        {"id": "4", "title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
    ]

if 'products' not in st.session_state: st.session_state.products = []
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. DISEÑO RESPONSIVO ---
st.markdown("""
<style>
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
    }
    .admin-label { font-size: 0.5rem; color: #F0F0F0; text-align: center; margin-top: 100px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#D4AF37; letter-spacing:5px;">ATELIER</p>', unsafe_allow_html=True)
    
    # Mostrar Servicios y Productos
    catalog = st.session_state.services + st.session_state.products
    if catalog:
        cols = st.columns(4)
        for idx, item in enumerate(catalog):
            with cols[idx % 4]:
                st.image(item["img"])
                if st.button(f"{item['title']}\n₲{item['price']:,}", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.selected_item = item
                    st.toast(f"Seleccionado: {item['title']}")

    st.divider()
    with st.form("reserva_form"):
        n = st.text_input("Nombre y Apellido")
        p = st.text_input("WhatsApp")
        f = st.date_input("Fecha", min_value=datetime.date.today())
        h = st.selectbox("Horario", ["08:00", "10:00", "13:00", "15:00", "17:00"])
        if st.form_submit_button("RESERVAR AHORA"):
            if n and p and 'selected_item' in st.session_state:
                st.session_state.temp_res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": n, "phone": p,
                    "service": st.session_state.selected_item['title'],
                    "price": st.session_state.selected_item['price'],
                    "date": str(f), "time": h, "status": "Por Procesar"
                }
                st.session_state.view = 'confirm'; st.rerun()
            else:
                st.error("Selecciona un servicio arriba.")

def confirmation_view():
    res = st.session_state.temp_res
    st.subheader(f"Confirmar Turno: {res['service']}")
    msg = f"💅 *NUEVA CITA*\n*ID:* #{res['id']}\n*Servicio:* {res['service']}\n*Fecha:* {res['date']}\n*Hora:* {res['time']}\n*Cliente:* {res['client']}"
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">ENVIAR AGENDAMIENTO</a>', unsafe_allow_html=True)
    if st.button("Finalizar"):
        st.session_state.appointments.append(res)
        st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMIN ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            t1, t2, t3 = st.tabs(["📊 Estadísticas", "💅 Catálogo", "📅 Reservas"])
            
            with t1: # Estadísticas
                apts = st.session_state.appointments
                ing = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
                st.metric("Total Cobrado", f"₲{ing:,}")
                if apts: st.line_chart(pd.DataFrame(apts).groupby('date')['price'].sum())

            with t2: # Gestión de Catálogo (Agregar, Cambiar Precio y BORRAR)
                st.subheader("Nuevo Item")
                with st.form("add"):
                    tipo = st.radio("Tipo", ["Servicio", "Producto"], horizontal=True)
                    nom = st.text_input("Nombre")
                    pre = st.number_input("Precio", step=5000)
                    img = st.text_input("URL Imagen")
                    if st.form_submit_button("Guardar"):
                        item = {"id": str(uuid.uuid4())[:4], "title": nom, "price": pre, "img": img}
                        if tipo == "Servicio": st.session_state.services.append(item)
                        else: st.session_state.products.append(item)
                        st.rerun()
                
                st.divider()
                st.subheader("Lista de Catálogo")
                
                # Gestión de Servicios
                st.write("**Servicios:**")
                for i, s in enumerate(st.session_state.services):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    new_p = col1.number_input(f"Precio {s['title']}", value=s['price'], key=f"ps_{i}")
                    st.session_state.services[i]['price'] = new_p
                    if col2.button("Actualizar", key=f"up_s_{i}"):
                        st.success("Precio actualizado"); st.rerun()
                    if col3.button("🗑️ Borrar", key=f"del_s_{i}"):
                        st.session_state.services.pop(i); st.rerun()

                # Gestión de Productos
                st.write("**Productos:**")
                for i, p in enumerate(st.session_state.products):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    new_p = col1.number_input(f"Precio {p['title']}", value=p['price'], key=f"pp_{i}")
                    st.session_state.products[i]['price'] = new_p
                    if col2.button("Actualizar", key=f"up_p_{i}"):
                        st.success("Precio actualizado"); st.rerun()
                    if col3.button("🗑️ Borrar", key=f"del_p_{i}"):
                        st.session_state.products.pop(i); st.rerun()

            with t3: # Gestión de Reservas
                for i, a in enumerate(st.session_state.appointments):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"{a['date']} | {a['client']} ({a['status']})")
                    if col2.button("✅ Cobrar", key=f"fin_{i}"):
                        st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
                    if col3.button("🗑️ Eliminar", key=f"del_res_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()