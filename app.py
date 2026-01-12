import streamlit as st
import pandas as pd
import datetime
import json
import os
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

DB_FILE = "nails_db.json"
BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "1234" 

def load_data():
    if not os.path.exists(DB_FILE):
        return {"appointments": [], "expenses": [], "services": [
            {"id": "S1", "title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
            {"id": "S2", "title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
            {"id": "S3", "title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
            {"id": "S4", "title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
        ], "products": []}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"appointments": [], "expenses": [], "services": [], "products": []}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'view' not in st.session_state: st.session_state.view = 'booking'

# --- 2. ESTILOS RESPONSIVOS (PARA TODO DISPOSITIVO) ---
st.markdown("""
<style>
    /* Ajuste para móviles y tablets */
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    .stImage > img { 
        border-radius: 15px; 
        object-fit: cover; 
        width: 100% !important; 
        height: 200px !important; 
    }
    .whatsapp-btn {
        background-color: #25D366; color: white !important; padding: 15px;
        border-radius: 50px; text-align: center; text-decoration: none;
        display: block; font-weight: bold; margin: 10px auto;
    }
    .admin-label { font-size: 0.6rem; color: #E0E0E0; text-align: center; margin-top: 50px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    
    # Mostrar servicios dinámicos
    services = st.session_state.data.get('services', [])
    cols = st.columns(len(services) if services else 1)
    for idx, s in enumerate(services):
        with cols[idx % 4 if len(services) > 4 else idx]:
            st.image(s["img"])
            if st.button(f"{s['title']}\n₲{s['price']:,}", key=f"s_{idx}"):
                st.session_state.pre_selected = s
                st.toast(f"Elegido: {s['title']}")

    st.divider()
    with st.form("reserva"):
        n = st.text_input("Nombre")
        p = st.text_input("WhatsApp")
        d = st.date_input("Fecha", min_value=datetime.date.today())
        promo = st.text_input("Código de Descuento (Opcional)")
        if st.form_submit_button("RESERVAR"):
            if n and p and 'pre_selected' in st.session_state:
                res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": n, "phone": p,
                    "service": st.session_state.pre_selected['title'],
                    "price": st.session_state.pre_selected['price'],
                    "date": str(d), "status": "Pendiente"
                }
                st.session_state.temp_res = res
                st.session_state.view = 'confirm'; st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    st.subheader(f"Confirmar {res['service']}")
    msg = f"💅 *NUEVA CITA*\nCliente: {res['client']}\nServicio: {res['service']}\nFecha: {res['date']}"
    url = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg)}"
    
    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">ENVIAR A WHATSAPP</a>', unsafe_allow_html=True)
    if st.button("Finalizar"):
        st.session_state.data['appointments'].append(res); save_data(st.session_state.data)
        st.session_state.view = 'booking'; st.rerun()

# --- 4. PANEL ADMIN COMPLETO ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            tab1, tab2, tab3 = st.tabs(["📊 Caja y Reservas", "💅 Catálogo/Precios", "🧹 Limpieza"])
            
            with tab1: # CAJA
                apts = st.session_state.data['appointments']
                df = pd.DataFrame(apts) if apts else pd.DataFrame()
                if not df.empty:
                    st.metric("Total Cobrado", f"₲{sum(a['price'] for a in apts if a['status'] == 'Finalizado'):,}")
                    st.write("Citas Pendientes")
                    for i, a in enumerate(apts):
                        if a['status'] == 'Pendiente':
                            col1, col2 = st.columns([3, 1])
                            col1.write(f"{a['client']} - {a['service']}")
                            if col2.button("Cobrar ✅", key=f"cob_{i}"):
                                st.session_state.data['appointments'][i]['status'] = 'Finalizado'
                                save_data(st.session_state.data); st.rerun()

            with tab2: # GESTIÓN DE PRODUCTOS Y SERVICIOS
                st.subheader("Agregar Servicio o Producto")
                with st.form("nuevo_item"):
                    tipo = st.selectbox("Tipo", ["Servicio", "Producto"])
                    nombre = st.text_input("Nombre")
                    precio = st.number_input("Precio", min_value=0, step=5000)
                    img_url = st.text_input("URL de Imagen")
                    if st.form_submit_button("Guardar en Catálogo"):
                        nuevo = {"id": str(uuid.uuid4())[:4], "title": nombre, "price": precio, "img": img_url}
                        key = 'services' if tipo == "Servicio" else 'products'
                        st.session_state.data[key].append(nuevo)
                        save_data(st.session_state.data); st.success("Guardado!"); st.rerun()
                
                st.subheader("Cambiar Precios Actuales")
                for i, s in enumerate(st.session_state.data['services']):
                    new_p = st.number_input(f"Precio: {s['title']}", value=s['price'], key=f"price_{i}")
                    if new_p != s['price']:
                        st.session_state.data['services'][i]['price'] = new_p
                        if st.button(f"Actualizar {s['title']}"):
                            save_data(st.session_state.data); st.rerun()

            with tab3: # BORRAR RESERVAS
                st.subheader("Eliminar Citas")
                if apts:
                    for i, a in enumerate(apts):
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"{a['date']} - {a['client']}")
                        if col2.button("🗑️", key=f"del_{i}"):
                            st.session_state.data['appointments'].pop(i)
                            save_data(st.session_state.data); st.rerun()
                else: st.info("No hay reservas para borrar.")

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()