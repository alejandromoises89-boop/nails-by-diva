import streamlit as st
import pandas as pd
import datetime
import uuid
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails by Diva", page_icon="💅", layout="wide")

HORARIOS_DISPONIBLES = ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30", "18:00"]

# --- 2. INICIALIZACIÓN DE DATOS (En memoria de sesión para evitar errores) ---
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
if 'blocked_dates' not in st.session_state: st.session_state.blocked_dates = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. ESTILOS ---
st.markdown("""
<style>
    .stImage > img { border-radius: 20px; object-fit: cover; width: 100% !important; height: 180px !important; }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 20px; border-radius: 50px; text-align: center; text-decoration: none; display: block; font-weight: bold; font-size: 1.1rem; }
    .whatsapp-disabled { background-color: #cccccc; color: #666666 !important; padding: 20px; border-radius: 50px; text-align: center; display: block; font-weight: bold; cursor: not-allowed; }
    .admin-label { font-size: 0.5rem; color: #EEEEEE; text-align: center; margin-top: 80px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#D4AF37; letter-spacing:5px;">ATELIER</p>', unsafe_allow_html=True)
    
    # Grid de Catálogo
    catalog = st.session_state.services + st.session_state.products
    cols = st.columns(4)
    for idx, item in enumerate(catalog):
        with cols[idx % 4]:
            st.image(item["img"])
            if st.button(f"{item['title']}\n₲{item['price']:,}", key=f"c_{idx}", use_container_width=True):
                st.session_state.selected_item = item
                st.toast(f"Elegido: {item['title']}")

    st.divider()
    with st.form("reserva_final"):
        st.subheader("Datos de la Cita")
        nombre = st.text_input("Nombre Completo")
        whatsapp = st.text_input("Número de WhatsApp")
        fecha_sel = st.date_input("Fecha", min_value=datetime.date.today())
        
        # Bloqueo de Fechas y Horarios
        fecha_str = str(fecha_sel)
        if fecha_str in st.session_state.blocked_dates:
            st.error("⚠️ Esta fecha está bloqueada por el Atelier.")
            libres = []
        else:
            ocupados = [a['time'] for a in st.session_state.appointments if a['date'] == fecha_str]
            libres = [h for h in HORARIOS_DISPONIBLES if h not in ocupados]
        
        horario_sel = st.selectbox("Horario Disponible", libres if libres else ["Sin turnos"])
        metodo_pago = st.radio("Método de Pago", ["Efectivo", "Tarjeta / Pix", "Transferencia"], horizontal=True)
        
        if st.form_submit_button("REVISAR RESERVA"):
            if nombre and whatsapp and 'selected_item' in st.session_state and horario_sel != "Sin turnos":
                st.session_state.temp_res = {
                    "id": str(uuid.uuid4())[:6].upper(), "client": nombre, "phone": whatsapp,
                    "service": st.session_state.selected_item['title'], "price": st.session_state.selected_item['price'],
                    "date": fecha_str, "time": horario_sel, "payment": metodo_pago, "status": "Pendiente"
                }
                st.session_state.view = 'confirm'; st.rerun()
            else:
                st.error("Completa tus datos y selecciona un servicio.")

def confirmation_view():
    res = st.session_state.temp_res
    st.subheader(f"Resumen Ticket #{res['id']}")
    st.write(f"**{res['service']}** | {res['date']} a las {res['time']} | Total: ₲{res['price']:,}")
    
    st.divider()
    comprobante_ok = True
    if res['payment'] != "Efectivo":
        st.warning("Adjunta comprobante para habilitar WhatsApp")
        archivo = st.file_uploader("Subir Comprobante", type=['jpg', 'png', 'jpeg'])
        if not archivo: comprobante_ok = False
    
    msg_wa = f"💅 *TICKET NAILS BY DIVA*\n🆔 ID: #{res['id']}\n👤 Cliente: {res['client']}\n✨ Servicio: {res['service']}\n📅 Fecha: {res['date']}\n⏰ Hora: {res['time']}\n💳 Pago: {res['payment']}"
    url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg_wa)}"

    if comprobante_ok:
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">ENVIAR A WHATSAPP</a>', unsafe_allow_html=True)
        if st.button("Finalizar y Guardar"):
            st.session_state.appointments.append(res); st.session_state.view = 'booking'; st.rerun()
    else:
        st.markdown('<div class="whatsapp-disabled">❌ ADJUNTA PAGO PARA CONTINUAR</div>', unsafe_allow_html=True)

# --- 5. PANEL ADMIN COMPLETO ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password", key="adm_auth") == ADMIN_PIN:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Estadísticas", "⚙️ Procesos", "💅 Catálogo", "💸 Egresos", "🚫 Bloqueos"])
            
            apts = st.session_state.appointments
            df = pd.DataFrame(apts) if apts else pd.DataFrame()

            with tab1: # ESTADISTICAS
                c1, c2, c3 = st.columns(3)
                c4, c5 = st.columns(2)
                
                pend = len(df[df['status'] == 'Pendiente']) if not df.empty else 0
                proc = len(df[df['status'] == 'En Proceso']) if not df.empty else 0
                fina = len(df[df['status'] == 'Finalizado']) if not df.empty else 0
                ing = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
                egr = sum(e['amount'] for e in st.session_state.expenses)
                
                c1.metric("⏳ Pendientes", pend)
                c2.metric("🔄 En Proceso", proc)
                c3.metric("✅ Finalizados", fina)
                c4.metric("💰 Ingresos (Cobrado)", f"₲{ing:,}")
                c5.metric("📉 Egresos (Gastos)", f"₲{egr:,}", delta=f"Neto: ₲{ing-egr:,}")
                
                if not df.empty:
                    st.line_chart(df[df['status']=='Finalizado'].groupby('date')['price'].sum())

            with tab2: # PROCESOS Y BORRAR RESERVAS
                st.subheader("Gestión de Reservas")
                for i, a in enumerate(apts):
                    col1, col2, col3, col4 = st.columns([2,1,1,1])
                    col1.write(f"**{a['client']}** ({a['date']} {a['time']})")
                    if a['status'] == 'Pendiente' and col2.button("Empezar ➡️", key=f"start_{i}"):
                        st.session_state.appointments[i]['status'] = 'En Proceso'; st.rerun()
                    if a['status'] == 'En Proceso' and col2.button("Finalizar ✅", key=f"done_{i}"):
                        st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
                    if col4.button("Borrar 🗑️", key=f"del_r_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

            with tab3: # CATALOGO: AGREGAR, CAMBIAR PRECIO Y BORRAR
                st.subheader("Nuevo Item")
                with st.form("new_item"):
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
                st.write("**Administrar Catálogo Actual:**")
                for i, s in enumerate(st.session_state.services):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    new_p = c1.number_input(f"Precio {s['title']}", value=s['price'], key=f"ps_{i}")
                    st.session_state.services[i]['price'] = new_p
                    if c3.button("🗑️", key=f"ds_{i}"):
                        st.session_state.services.pop(i); st.rerun()

            with tab4: # EGRESOS
                with st.form("egr"):
                    det = st.text_input("Concepto del Gasto")
                    mon = st.number_input("Monto ₲", step=1000)
                    if st.form_submit_button("Registrar Gasto"):
                        st.session_state.expenses.append({"desc": det, "amount": mon}); st.rerun()
                for e in st.session_state.expenses: st.write(f"🔴 -₲{e['amount']:,} : {e['desc']}")

            with tab5: # BLOQUEO DE FECHAS
                f_bl = st.date_input("Día a cerrar")
                if st.button("Bloquear Día 🔒"):
                    if str(f_bl) not in st.session_state.blocked_dates:
                        st.session_state.blocked_dates.append(str(f_bl)); st.rerun()
                for d in st.session_state.blocked_dates:
                    if st.button(f"Desbloquear {d}"):
                        st.session_state.blocked_dates.remove(d); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()