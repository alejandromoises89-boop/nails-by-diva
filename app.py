import streamlit as st
import pandas as pd
import json
import os
import uuid
import datetime
import base64
from PIL import Image
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Nails by Diva | Premium Booking",
    page_icon="💅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS PERSONALIZADOS (LUJO DARK) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;700&family=Monsieur+La+Doulaise&family=Montserrat:wght@300;400;600&display=swap');

    /* Colores base */
    :root {
        --bg-color: #0b0b0b;
        --card-bg: #1a1a1a;
        --gold: #D4AF37;
        --text: #e0e0e0;
    }

    /* Fondo general */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text);
        font-family: 'Montserrat', sans-serif;
    }

    /* Títulos */
    h1, h2, h3 {
        font-family: 'Bodoni Moda', serif;
        color: var(--gold) !important;
    }
    
    .logo-script {
        font-family: 'Monsieur La Doulaise', cursive;
        color: white;
        font-size: 3rem;
        margin-top: -20px;
        transform: rotate(-2deg);
        text-align: center;
        opacity: 0.9;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #000000 !important;
        border: 1px solid #333 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 5px var(--gold);
    }

    /* Botones */
    .stButton button {
        background: linear-gradient(45deg, #AA8C2C, #D4AF37);
        color: #0b0b0b;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0.5rem 1rem;
        width: 100%;
        transition: transform 0.1s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        color: #000;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
    }

    /* Cards */
    .service-card {
        background-color: var(--card-bg);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        transition: border-color 0.3s;
    }
    .service-card:hover {
        border-color: var(--gold);
    }

    /* Admin metrics */
    div[data-testid="metric-container"] {
        background-color: var(--card-bg);
        border: 1px solid #333;
        padding: 10px;
        border-radius: 10px;
    }
    div[data-testid="metric-container"] label {
        color: #888;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: var(--gold) !important;
    }
    
    /* Remove default header */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES Y DATOS ---
ADMIN_PIN = "2024"
BUSINESS_PHONE = "595992698406"
STORAGE_FILE = "data_nails_app.json"

SERVICES = {
    "💅 Capping Gel": {"price": 120000, "desc": "Recubrimiento de gel para mayor resistencia.", "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&q=80&w=800"},
    "✨ Mantenimiento": {"price": 80000, "desc": "Relleno y corrección del servicio anterior.", "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?auto=format&fit=crop&q=80&w=800"},
    "🎨 Semipermanente": {"price": 70000, "desc": "Esmaltado de larga duración con curado UV.", "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?auto=format&fit=crop&q=80&w=800"},
    "💎 Soft Gel": {"price": 150000, "desc": "Extensión completa con tips de gel.", "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&q=80&w=800"}
}

TIME_SLOTS = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in (0, 30)]
PAYMENT_METHODS = ["Efectivo", "Transferencia", "Pix"]

BANKING_DETAILS = {
    "FAMILIAR": {"bank": "Banco Familiar", "account": "815643114", "label": "Nro. Cuenta"},
    "UENO": {"bank": "Ueno Bank", "alias": "4437206", "label": "Alias / C.I."}
}

MOTIVATIONAL_QUOTES = [
    "Tu belleza comienza en el momento en que decides ser tú misma.",
    "Las uñas son el punto final de una frase llamada estilo.",
    "No dejes que nadie apague tu brillo, ¡especialmente el de tus uñas!",
    "Hoy es un día perfecto para brillar."
]

# --- GESTIÓN DE DATOS (PERSISTENCIA) ---
def load_data():
    if not os.path.exists(STORAGE_FILE):
        return {
            "appointments": [], 
            "expenses": [], 
            "reviews": [], 
            "settings": {"paymentQr": None, "paymentQrSecondary": None}
        }
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Inicializar estado
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'view' not in st.session_state:
    st.session_state.view = 'booking' # booking, admin, confirmation
if 'last_appointment' not in st.session_state:
    st.session_state.last_appointment = None

# --- FUNCIONES UTILITARIAS ---
def generate_id():
    return str(uuid.uuid4())[:6].upper()

def format_currency(amount):
    return f"₲ {amount:,.0f}".replace(",", ".")

def image_to_base64(uploaded_file):
    """Convierte archivo subido a base64 para guardarlo en JSON"""
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.getvalue()
    base64_str = base64.b64encode(bytes_data).decode()
    return f"data:image/png;base64,{base64_str}"

def generate_whatsapp_link(apt, is_reminder=False):
    if is_reminder:
        text = f"Hola {apt['clientName']}! Te recordamos tu cita de {apt['service']} para hoy a las {apt['time']}hs. ✨ Te esperamos!"
        phone = apt['phone']
    else:
        text = f"👋 Hola Diva! Hice una reserva.\n\n🆔 *Reserva Nro:* #{apt['id']}\n👤 *Cliente:* {apt['clientName']}\n💅 *Servicio:* {apt['service']}\n📅 *Fecha:* {apt['date']}\n⏰ *Hora:* {apt['time']} hs\n💰 *Pago:* {apt['paymentMethod']}\n\n📎 *Adjunto el comprobante de pago aquí abajo* 👇"
        phone = BUSINESS_PHONE
    return f"https://api.whatsapp.com/send?phone={phone}&text={text.replace(' ', '%20').replace(chr(10), '%0A')}"

def generate_calendar_link(apt):
    title = f"💅 Cita Nails: {apt['service']}"
    details = f"Reserva #{apt['id']} en Nails by Diva."
    start_dt = f"{apt['date'].replace('-', '')}T{apt['time'].replace(':', '')}00"
    # Simple aproximación de fin +2 horas
    h, m = map(int, apt['time'].split(':'))
    end_dt = f"{apt['date'].replace('-', '')}T{min(h+2, 23):02d}{m:02d}00"
    return f"https://www.google.com/calendar/render?action=TEMPLATE&text={title.replace(' ', '+')}&dates={start_dt}/{end_dt}&details={details.replace(' ', '+')}"

# --- VISTAS ---

def render_header():
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; border-bottom: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 2rem;'>
            <h1 style='letter-spacing: 0.2em; font-size: 3rem; margin-bottom: 0;'>NAILS</h1>
            <div class='logo-script'>by Diva</div>
        </div>
    """, unsafe_allow_html=True)

def view_booking():
    render_header()
    
    # --- CATALOGO ---
    st.markdown("<h3 style='text-align: center; margin-bottom: 1rem;'>Menú de Servicios</h3>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, (name, details) in enumerate(SERVICES.items()):
        col = cols[i % 2]
        with col:
            st.markdown(f"""
            <div class='service-card'>
                <img src="{details['img']}" style="width:100%; border-radius:10px; height: 150px; object-fit: cover;">
                <h4 style="color: #D4AF37; margin: 10px 0 5px;">{name}</h4>
                <p style="font-size: 0.8rem; color: #aaa;">{details['desc']}</p>
                <div style="font-family: monospace; font-weight: bold; color: white;">{format_currency(details['price'])}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- FORMULARIO DE RESERVA ---
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Reserva tu Turno</h3>", unsafe_allow_html=True)
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre Completo")
            date = st.date_input("Fecha", min_value=datetime.date.today())
            service = st.selectbox("Servicio", list(SERVICES.keys()))
        with col2:
            phone = st.text_input("WhatsApp (ej: 0981...)")
            time = st.selectbox("Hora", TIME_SLOTS)
            payment = st.selectbox("Método de Pago", PAYMENT_METHODS)
        
        submitted = st.form_submit_button("CONFIRMAR RESERVA")
        
        if submitted:
            if not name or not phone:
                st.error("Por favor completa tu nombre y teléfono.")
            else:
                new_apt = {
                    "id": generate_id(),
                    "clientName": name,
                    "date": str(date),
                    "time": time,
                    "service": service,
                    "paymentMethod": payment,
                    "phone": phone,
                    "status": "PENDIENTE",
                    "createdAt": str(datetime.datetime.now()),
                    "amount": SERVICES[service]['price'],
                    "paymentProof": None,
                    "thankYouSent": False
                }
                st.session_state.data['appointments'].append(new_apt)
                save_data(st.session_state.data)
                st.session_state.last_appointment = new_apt
                st.session_state.view = 'confirmation'
                st.rerun()

    # --- FOOTER / ADMIN LINK ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([4,1])
    with col_r:
        if st.button("🔐 Admin"):
            st.session_state.view = 'admin_login'
            st.rerun()

def view_confirmation():
    apt = st.session_state.last_appointment
    if not apt:
        st.session_state.view = 'booking'
        st.rerun()

    st.success(f"¡Reserva Recibida! #{apt['id']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Cliente:** {apt['clientName']}")
        st.markdown(f"**Fecha:** {apt['date']} a las {apt['time']}")
    with col2:
        st.markdown(f"**Servicio:** {apt['service']}")
        st.markdown(f"**Total:** {format_currency(apt['amount'])}")

    st.markdown("---")
    
    # Datos Bancarios si es transferencia
    if apt['paymentMethod'] in ["Transferencia", "Pix"]:
        st.info("ℹ️ Realiza el pago para confirmar tu cita.")
        
        tab1, tab2 = st.tabs(["Banco Familiar", "Ueno Bank"])
        
        with tab1:
            st.markdown(f"**Cuenta:** {BANKING_DETAILS['FAMILIAR']['account']}")
            qr_primary = st.session_state.data['settings'].get('paymentQr')
            if qr_primary:
                st.image(qr_primary, width=200)
        
        with tab2:
            st.markdown(f"**Alias:** {BANKING_DETAILS['UENO']['alias']}")
            qr_secondary = st.session_state.data['settings'].get('paymentQrSecondary')
            if qr_secondary:
                st.image(qr_secondary, width=200)

        # Upload Proof
        uploaded_proof = st.file_uploader("Subir Comprobante", type=['png', 'jpg', 'jpeg'])
        if uploaded_proof:
            # Buscar el appointment en la lista y actualizarlo
            for a in st.session_state.data['appointments']:
                if a['id'] == apt['id']:
                    a['paymentProof'] = image_to_base64(uploaded_proof)
                    apt['paymentProof'] = a['paymentProof'] # update local var
                    save_data(st.session_state.data)
                    st.success("Comprobante subido correctamente.")
                    break
    
    st.markdown("---")
    
    # Botones de Acción
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Inicio"):
            st.session_state.view = 'booking'
            st.session_state.last_appointment = None
            st.rerun()
    with c2:
        st.markdown(f'''<a href="{generate_calendar_link(apt)}" target="_blank" style="text-decoration: none;">
            <button style="width:100%; padding: 0.5rem; background: #333; color: white; border-radius: 5px; border:none;">📅 Agendar</button>
            </a>''', unsafe_allow_html=True)
    with c3:
        can_send = True
        if apt['paymentMethod'] in ["Transferencia", "Pix"] and not apt['paymentProof']:
            can_send = False
        
        if can_send:
            st.markdown(f'''<a href="{generate_whatsapp_link(apt)}" target="_blank" style="text-decoration: none;">
                <button style="width:100%; padding: 0.5rem; background: #25D366; color: white; border-radius: 5px; border:none;">💬 WhatsApp</button>
                </a>''', unsafe_allow_html=True)
        else:
            st.caption("Sube comprobante para enviar a WP")

def view_admin():
    st.markdown("## Panel de Administración")
    
    if st.button("⬅️ Salir"):
        st.session_state.view = 'booking'
        st.rerun()
    
    tab_dash, tab_apts, tab_config = st.tabs(["Dashboard", "Citas", "Configuración"])

    # --- DASHBOARD ---
    with tab_dash:
        apts = st.session_state.data['appointments']
        expenses = st.session_state.data['expenses']
        
        total_income = sum(a['amount'] for a in apts if a['status'] != 'PENDIENTE')
        total_expense = sum(e['amount'] for e in expenses)
        pending_count = len([a for a in apts if a['status'] == 'PENDIENTE'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos", format_currency(total_income))
        m2.metric("Gastos", format_currency(total_expense))
        m3.metric("Pendientes", pending_count)
        
        # Agregar Gasto
        with st.expander("Registrar Gasto"):
            with st.form("add_expense"):
                desc = st.text_input("Descripción")
                amt = st.number_input("Monto", min_value=0)
                cat = st.selectbox("Categoría", ["Insumos", "Alquiler", "Otros"])
                if st.form_submit_button("Guardar Gasto"):
                    st.session_state.data['expenses'].append({
                        "id": generate_id(), "description": desc, "amount": amt, "category": cat, "date": str(datetime.date.today())
                    })
                    save_data(st.session_state.data)
                    st.rerun()
        
        # Lista de Gastos
        if expenses:
            st.markdown("### Últimos Gastos")
            df_exp = pd.DataFrame(expenses)
            st.dataframe(df_exp[['date', 'description', 'amount', 'category']], hide_index=True)

    # --- CITAS ---
    with tab_apts:
        appointments = st.session_state.data['appointments']
        # Sort by date
        appointments.sort(key=lambda x: x['date'] + x['time'])
        
        for i, apt in enumerate(appointments):
            status_color = "🔴" if apt['status'] == "PENDIENTE" else "🟢" if apt['status'] == "CONFIRMADO" else "🔵"
            
            with st.expander(f"{status_color} {apt['date']} {apt['time']} - {apt['clientName']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Servicio:** {apt['service']}")
                    st.write(f"**Tel:** {apt['phone']}")
                    st.write(f"**Pago:** {apt['paymentMethod']}")
                    if apt.get('paymentProof'):
                        st.image(apt['paymentProof'], caption="Comprobante", width=150)
                    else:
                        st.warning("Sin comprobante")
                
                with c2:
                    new_status = st.selectbox("Estado", ["PENDIENTE", "CONFIRMADO", "COMPLETADO"], index=["PENDIENTE", "CONFIRMADO", "COMPLETADO"].index(apt['status']), key=f"s_{i}")
                    if new_status != apt['status']:
                        apt['status'] = new_status
                        save_data(st.session_state.data)
                        st.rerun()
                    
                    if st.button("🗑️ Eliminar", key=f"d_{i}"):
                        st.session_state.data['appointments'].pop(i)
                        save_data(st.session_state.data)
                        st.rerun()
                    
                    st.markdown(f"[Recordar WP]({generate_whatsapp_link(apt, True)})")

    # --- CONFIGURACION ---
    with tab_config:
        st.write("### Códigos QR de Pago")
        
        st.write("Bano Familiar (Principal)")
        qr1 = st.file_uploader("Subir QR Familiar", type=['png', 'jpg'], key="u1")
        if qr1:
            st.session_state.data['settings']['paymentQr'] = image_to_base64(qr1)
            save_data(st.session_state.data)
            st.success("QR Familiar actualizado")

        st.write("Ueno Bank (Secundario)")
        qr2 = st.file_uploader("Subir QR Ueno", type=['png', 'jpg'], key="u2")
        if qr2:
            st.session_state.data['settings']['paymentQrSecondary'] = image_to_base64(qr2)
            save_data(st.session_state.data)
            st.success("QR Ueno actualizado")

def main():
    if st.session_state.view == 'booking':
        view_booking()
    elif st.session_state.view == 'confirmation':
        view_confirmation()
    elif st.session_state.view == 'admin_login':
        render_header()
        st.markdown("<h3 style='text-align: center;'>Acceso Admin</h3>", unsafe_allow_html=True)
        pin = st.text_input("PIN de Acceso", type="password")
        if st.button("Entrar"):
            if pin == ADMIN_PIN:
                st.session_state.view = 'admin_panel'
                st.rerun()
            else:
                st.error("PIN Incorrecto")
        if st.button("Volver"):
            st.session_state.view = 'booking'
            st.rerun()
    elif st.session_state.view == 'admin_panel':
        view_admin()

if __name__ == "__main__":
    main()