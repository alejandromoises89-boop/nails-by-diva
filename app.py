import streamlit as st
import pandas as pd
import datetime
import uuid
import urllib.parse
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva Admin", page_icon="💅", layout="wide")

# --- 2. INICIALIZACIÓN DE DATOS ---
if 'services' not in st.session_state:
    st.session_state.services = [
        {"id": "1", "title": "Capping Gel", "price": 120000, "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80"},
        {"id": "2", "title": "Mantenimiento", "price": 80000, "img": "https://i.ibb.co/bjf3G85q/images-1.jpg"},
        {"id": "3", "title": "Semipermanente", "price": 70000, "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&q=80"},
        {"id": "4", "title": "Soft Gel", "price": 150000, "img": "https://i.ibb.co/d07rD7xL/77c227-9403abc92b0d4b00a7c9fe128fe5a386-mv2-1.jpg"}
    ]

if 'products' not in st.session_state: st.session_state.products = []
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'expenses' not in st.session_state: st.session_state.expenses = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. DISEÑO ---
st.markdown("""
<style>
    .stImage > img { border-radius: 20px; object-fit: cover; width: 100% !important; height: 200px !important; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 20px; border-radius: 50px; text-align: center; text-decoration: none; display: block; font-weight: bold; }
    .admin-label { font-size: 0.5rem; color: #F0F0F0; text-align: center; margin-top: 100px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    catalog = st.session_state.services + st.session_state.products
    cols = st.columns(4)
    for idx, item in enumerate(catalog):
        with cols[idx % 4]:
            st.image(item["img"])
            if st.button(f"{item['title']}\n₲{item['price']:,}", key=f"c_{idx}", use_container_width=True):
                st.session_state.selected_item = item
                st.toast(f"Seleccionado: {item['title']}")
    
    st.divider()
    with st.form("reserva"):
        n = st.text_input("Nombre")
        p = st.text_input("WhatsApp")
        f = st.date_input("Fecha", min_value=datetime.date.today())
        if st.form_submit_button("RESERVAR"):
            if n and p and 'selected_item' in st.session_state:
                st.session_state.temp_res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": n, "phone": p,
                    "service": st.session_state.selected_item['title'],
                    "price": st.session_state.selected_item['price'],
                    "date": str(f), "status": "Pendiente"
                }
                st.session_state.view = 'confirm'; st.rerun()

def confirmation_view():
    res = st.session_state.temp_res
    url = f"https://wa.me/{BUSINESS_PHONE}?text=Reserva {res['id']} de {res['client']}"
    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">ENVIAR WHATSAPP</a>', unsafe_allow_html=True)
    if st.button("Finalizar"):
        st.session_state.appointments.append(res); st.session_state.view = 'booking'; st.rerun()

# --- 5. PANEL ADMIN CORREGIDO ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password") == ADMIN_PIN:
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Estadísticas", "⚙️ Procesos", "💅 Catálogo", "💸 Egresos"])
            
            apts = st.session_state.appointments
            df = pd.DataFrame(apts) if apts else pd.DataFrame()

            with tab1: # ESTADISTICAS PROFESIONALES
                c1, c2, c3 = st.columns(3)
                c4, c5 = st.columns(2)
                
                # Conteos por estado
                pendientes = len(df[df['status'] == 'Pendiente']) if not df.empty else 0
                en_proceso = len(df[df['status'] == 'En Proceso']) if not df.empty else 0
                finalizados = len(df[df['status'] == 'Finalizado']) if not df.empty else 0
                
                # Dinero
                ingresos = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
                egresos = sum(e['amount'] for e in st.session_state.expenses)
                
                c1.metric("⏳ Pendientes", pendientes)
                c2.metric("🔄 En Proceso", en_proceso)
                c3.metric("✅ Finalizados", finalizados)
                c4.metric("💰 Ingresos Totales", f"₲{ingresos:,}", delta=f"Neto: ₲{ingresos-egresos:,}")
                c5.metric("📉 Egresos", f"₲{egresos:,}")
                
                if not df.empty:
                    st.subheader("Gráfico de Ingresos")
                    df_fin = df[df['status'] == 'Finalizado']
                    if not df_fin.empty:
                        st.line_chart(df_fin.groupby('date')['price'].sum())

            with tab2: # PROCESOS: PENDIENTES -> EN PROCESO -> FINALIZADOS
                st.subheader("Gestión de Citas")
                for i, a in enumerate(apts):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    col1.write(f"**{a['client']}** - {a['service']} ({a['status']})")
                    
                    if a['status'] == 'Pendiente':
                        if col2.button("Empezar ➡️", key=f"proc_{i}"):
                            st.session_state.appointments[i]['status'] = 'En Proceso'; st.rerun()
                    
                    if a['status'] == 'En Proceso':
                        if col2.button("Finalizar ✅", key=f"fin_{i}"):
                            st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
                    
                    if col4.button("Borrar 🗑️", key=f"del_res_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

            with tab3: # CATALOGO (BORRAR SERVICIOS/PRODUCTOS)
                st.subheader("Agregar Item")
                with st.form("add"):
                    t = st.radio("Tipo", ["Servicio", "Producto"], horizontal=True)
                    n = st.text_input("Nombre")
                    p = st.number_input("Precio", step=5000)
                    img = st.text_input("URL Imagen")
                    if st.form_submit_button("Guardar"):
                        item = {"id": str(uuid.uuid4())[:4], "title": n, "price": p, "img": img}
                        if t == "Servicio": st.session_state.services.append(item)
                        else: st.session_state.products.append(item)
                        st.rerun()
                
                st.divider()
                st.write("**Eliminar Items del Catálogo:**")
                all_items = st.session_state.services + st.session_state.products
                for i, item in enumerate(st.session_state.services):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"💅 {item['title']} - ₲{item['price']:,}")
                    if c2.button("Borrar", key=f"ds_{i}"):
                        st.session_state.services.pop(i); st.rerun()

            with tab4: # EGRESOS
                st.subheader("Registrar Gasto")
                with st.form("gasto"):
                    det = st.text_input("Detalle del gasto")
                    amt = st.number_input("Monto", step=1000)
                    if st.form_submit_button("Registrar Egresos"):
                        st.session_state.expenses.append({"desc": det, "amount": amt})
                        st.rerun()
                for e in st.session_state.expenses:
                    st.write(f"🔴 -₲{e['amount']:,} : {e['desc']}")

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()
