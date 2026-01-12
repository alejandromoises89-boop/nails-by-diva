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

if 'products' not in st.session_state: st.session_state.products = []
if 'appointments' not in st.session_state: st.session_state.appointments = []
if 'expenses' not in st.session_state: st.session_state.expenses = []
if 'blocked_dates' not in st.session_state: st.session_state.blocked_dates = []
if 'view' not in st.session_state: st.session_state.view = 'booking'

BUSINESS_PHONE = "595992698406" 
ADMIN_PIN = "2026" 

# --- 3. DISEÑO Y ESTILOS CSS ---
st.markdown("""
<style>
    .stImage > img { border-radius: 20px; object-fit: cover; width: 100% !important; height: 180px !important; }
    
    /* Estilo del Ticket */
    .ticket-container {
        background-color: #fff;
        padding: 30px;
        border-radius: 10px;
        border: 2px dashed #d4af37;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-family: 'Courier New', Courier, monospace;
        max-width: 500px;
        margin: auto;
        color: #333;
    }
    .ticket-header { text-align: center; border-bottom: 1px solid #eee; margin-bottom: 20px; padding-bottom: 10px; }
    .ticket-row { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px dotted #ccc; }
    
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 20px; border-radius: 50px; text-align: center; text-decoration: none; display: block; font-weight: bold; font-size: 1.1rem; box-shadow: 0 4px 10px rgba(37,211,102,0.4); }
    .whatsapp-disabled { background-color: #cccccc; color: #666666 !important; padding: 20px; border-radius: 50px; text-align: center; display: block; font-weight: bold; cursor: not-allowed; }
    .admin-label { font-size: 0.5rem; color: #EEEEEE; text-align: center; margin-top: 80px; }
    [data-testid="stHeader"], footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE ---
def booking_interface():
    st.markdown('<h1 style="text-align:center; color:#333;">NAILS BY DIVA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#D4AF37; letter-spacing:5px; font-weight:bold;">ATELIER</p>', unsafe_allow_html=True)
    
    # Galería Visual
    catalog = st.session_state.services + st.session_state.products
    cols = st.columns(4)
    for idx, item in enumerate(catalog):
        with cols[idx % 4]:
            st.image(item["img"])
            st.caption(f"**{item['title']}** - ₲{item['price']:,}")

    st.divider()

    # Formulario de Reserva
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        with st.form("reserva_form"):
            st.subheader("📝 Datos de tu Cita")
            nombre = st.text_input("Nombre y Apellido")
            whatsapp = st.text_input("WhatsApp")
            
            # Servicio a elegir debajo del teléfono
            serv_titles = [s['title'] for s in catalog]
            servicio_elegido = st.selectbox("Selecciona el Servicio/Producto", serv_titles)
            
            fecha_sel = st.date_input("Fecha Deseada", min_value=datetime.date.today())
            
            # Lógica de Horarios
            fecha_str = str(fecha_sel)
            if fecha_str in st.session_state.blocked_dates:
                st.error("⚠️ Fecha no disponible.")
                libres = []
            else:
                ocupados = [a['time'] for a in st.session_state.appointments if a['date'] == fecha_str]
                libres = [h for h in HORARIOS_DISPONIBLES if h not in ocupados]
            
            horario_sel = st.selectbox("Horario", libres if libres else ["Sin disponibilidad"])
            metodo_pago = st.radio("Método de Pago", ["Efectivo", "Tarjeta / Pix", "Transferencia"], horizontal=True)
            
            if st.form_submit_button("GENERAR TICKET"):
                if nombre and whatsapp and horario_sel != "Sin disponibilidad":
                    sel_item = next(item for item in catalog if item["title"] == servicio_elegido)
                    st.session_state.temp_res = {
                        "id": str(uuid.uuid4())[:6].upper(),
                        "client": nombre, "phone": whatsapp,
                        "service": sel_item['title'], "price": sel_item['price'],
                        "date": fecha_str, "time": horario_sel, "payment": metodo_pago, "status": "Pendiente"
                    }
                    st.session_state.view = 'confirm'; st.rerun()
                else:
                    st.warning("Por favor completa todos los datos.")

def confirmation_view():
    res = st.session_state.temp_res
    
    # --- DISEÑO TICKET ---
    st.markdown(f"""
    <div class="ticket-container">
        <div class="ticket-header">
            <h3>NAILS BY DIVA</h3>
            <p>Atelier de Belleza</p>
            <p>Ticket ID: #{res['id']}</p>
        </div>
        <div class="ticket-row"><span>Cliente:</span> <span>{res['client']}</span></div>
        <div class="ticket-row"><span>WhatsApp:</span> <span>{res['phone']}</span></div>
        <div class="ticket-row"><span>Servicio:</span> <span>{res['service']}</span></div>
        <div class="ticket-row"><span>Fecha:</span> <span>{res['date']}</span></div>
        <div class="ticket-row"><span>Hora:</span> <span>{res['time']}</span></div>
        <div class="ticket-row"><span>Método:</span> <span>{res['payment']}</span></div>
        <div style="font-size: 1.2rem; font-weight: bold; text-align: center; margin-top: 20px; border-top: 2px solid #333; padding-top: 10px;">
            TOTAL: ₲{res['price']:,}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    comprobante_ok = True
    if res['payment'] != "Efectivo":
        st.warning("📸 Adjunta una captura del comprobante (Pix/Tarjeta) para confirmar")
        archivo = st.file_uploader("Subir imagen", type=['jpg', 'png', 'jpeg'])
        if not archivo: comprobante_ok = False
    
    msg_wa = (
        f"💅 *TICKET DE RESERVA*\n"
        f"🆔 ID: #{res['id']}\n"
        f"👤 Cliente: {res['client']}\n"
        f"✨ Servicio: {res['service']}\n"
        f"📅 Fecha: {res['date']}\n"
        f"⏰ Hora: {res['time']}\n"
        f"💳 Pago: {res['payment']}\n"
        f"💰 Total: ₲{res['price']:,}"
    )
    url_wa = f"https://wa.me/{BUSINESS_PHONE}?text={urllib.parse.quote(msg_wa)}"

    if comprobante_ok:
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">CONFIRMAR POR WHATSAPP</a>', unsafe_allow_html=True)
        if st.button("Finalizar y Guardar"):
            st.session_state.appointments.append(res); st.session_state.view = 'booking'; st.rerun()
    else:
        st.markdown('<div class="whatsapp-disabled">❌ ADJUNTA EL COMPROBANTE</div>', unsafe_allow_html=True)

# --- 5. PANEL ADMIN ---
def admin_panel():
    st.markdown('<div class="admin-label">admin</div>', unsafe_allow_html=True)
    with st.expander(" "):
        if st.text_input("PIN", type="password", key="adm_key") == ADMIN_PIN:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Caja", "⚙️ Procesos", "💅 Catálogo", "💸 Egresos", "🚫 Bloqueos"])
            
            apts = st.session_state.appointments
            df = pd.DataFrame(apts) if apts else pd.DataFrame()

            with tab1: # ESTADISTICAS
                c1, c2, c3 = st.columns(3)
                pend = len(df[df['status'] == 'Pendiente']) if not df.empty else 0
                proc = len(df[df['status'] == 'En Proceso']) if not df.empty else 0
                fina = len(df[df['status'] == 'Finalizado']) if not df.empty else 0
                ing = sum(a['price'] for a in apts if a['status'] == 'Finalizado')
                egr = sum(e['amount'] for e in st.session_state.expenses)
                
                c1.metric("⏳ Pendientes", pend)
                c2.metric("🔄 En Proceso", proc)
                c3.metric("✅ Finalizados", fina)
                st.metric("💰 Ingresos Netos", f"₲{ing-egr:,}", delta=f"Bruto: ₲{ing:,} | Gastos: ₲{egr:,}")

            with tab2: # GESTIÓN DE CITAS
                for i, a in enumerate(apts):
                    col1, col2, col3 = st.columns([2,1,1])
                    col1.write(f"**{a['client']}** ({a['date']} {a['time']}) - {a['status']}")
                    if a['status'] == 'Pendiente' and col2.button("Atender", key=f"p_{i}"):
                        st.session_state.appointments[i]['status'] = 'En Proceso'; st.rerun()
                    if a['status'] == 'En Proceso' and col2.button("Cobrar", key=f"f_{i}"):
                        st.session_state.appointments[i]['status'] = 'Finalizado'; st.rerun()
                    if col3.button("Borrar", key=f"d_{i}"):
                        st.session_state.appointments.pop(i); st.rerun()

            with tab3: # CATALOGO
                st.subheader("Nuevo Servicio/Producto")
                with st.form("new_i"):
                    tipo = st.radio("Tipo", ["Servicio", "Producto"], horizontal=True)
                    nom = st.text_input("Nombre")
                    pre = st.number_input("Precio", step=5000)
                    img = st.text_input("URL Imagen")
                    if st.form_submit_button("Guardar"):
                        item = {"id": str(uuid.uuid4())[:4], "title": nom, "price": pre, "img": img}
                        if tipo == "Servicio": st.session_state.services.append(item)
                        else: st.session_state.products.append(item)
                        st.rerun()
                for i, s in enumerate(st.session_state.services):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"💅 {s['title']} - ₲{s['price']:,}")
                    if c2.button("Eliminar", key=f"del_s_{i}"):
                        st.session_state.services.pop(i); st.rerun()

            with tab4: # EGRESOS
                with st.form("gastos"):
                    dt = st.text_input("Detalle")
                    mt = st.number_input("Monto", step=1000)
                    if st.form_submit_button("Cargar Gasto"):
                        st.session_state.expenses.append({"desc": dt, "amount": mt}); st.rerun()

            with tab5: # BLOQUEOS
                fb = st.date_input("Día a cerrar")
                if st.button("Bloquear 🔒"):
                    st.session_state.blocked_dates.append(str(fb)); st.rerun()
                for d in st.session_state.blocked_dates:
                    if st.button(f"Desbloquear {d}"):
                        st.session_state.blocked_dates.remove(d); st.rerun()

# --- FLUJO ---
if st.session_state.view == 'booking': booking_interface()
else: confirmation_view()
admin_panel()