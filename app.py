import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
from io import BytesIO
from PIL import Image
import urllib.parse

# --- CONSTANTES Y CONFIGURACIÓN ---
st.set_page_config(
    page_title="Nails by Diva | Premium Booking",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Archivo de base de datos local
DB_FILE = "nails_db.json"
ADMIN_PIN = "2024"
BUSINESS_PHONE = "595992698406"

# Datos Estáticos
SERVICES = {
    "CAPPING": {
        "title": "💅 Capping Gel",
        "price": 120000,
        "desc": "Recubrimiento de gel sobre la uña natural para mayor resistencia.",
        "img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&q=80&w=800"
    },
    "MAINTENANCE": {
        "title": "✨ Mantenimiento",
        "price": 80000,
        "desc": "Relleno y corrección del servicio anterior.",
        "img": "https://images.unsplash.com/photo-1522337374993-64bd22fde451?auto=format&fit=crop&q=80&w=800"
    },
    "SEMIPERMANENT": {
        "title": "🎨 Semipermanente",
        "price": 70000,
        "desc": "Esmaltado de larga duración con curado UV/LED.",
        "img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?auto=format&fit=crop&q=80&w=800"
    },
    "SOFT_GEL": {
        "title": "💎 Soft Gel",
        "price": 150000,
        "desc": "Extensión completa con tips de gel.",
        "img": "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&q=80&w=800"
    }
}

BANKING_DETAILS = {
    "FAMILIAR": {"bank": "Banco Familiar", "account": "815643114", "label": "Nro. Cuenta"},
    "UENO": {"bank": "Ueno Bank", "alias": "4437206", "label": "Alias / C.I."}
}

TIME_SLOTS = [f"{h:02d}:{m}" for h in range(8, 20) for m in ["00", "30"]]

MOTIVATIONAL_QUOTES = [
    "Tu belleza comienza en el momento en que decides ser tú misma.",
    "Las uñas son el punto final de una frase llamada estilo.",
    "Irradia confianza y el mundo te sonreirá."
]

# --- ESTILOS CSS PERSONALIZADOS (Theme Luxury) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;700&family=Monsieur+La+Doulaise&family=Montserrat:wght@300;400;600&display=swap');
    
    /* Global Colors */
    :root {
        --gold: #D4AF37;
        --dark-bg: #0b0b0b;
        --card-bg: #1a1a1a;
    }

    .stApp {
        background-color: var(--dark-bg);
        color: #e0e0e0;
        font-family: 'Montserrat', sans-serif;
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Bodoni Moda', serif !important;
        color: var(--gold) !important;
    }
    
    .script-font {
        font-family: 'Monsieur La Doulaise', cursive;
        font-size: 3rem;
        color: white;
        opacity: 0.9;
    }

    /* Cards */
    .service-card {
        background-color: var(--card-bg);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        transition: transform 0.3s;
        margin-bottom: 20px;
    }
    .service-card:hover {
        border-color: var(--gold);
        transform: translateY(-5px);
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(to right, #AA8C2C, #D4AF37);
        color: #0b0b0b;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    div.stButton > button:hover {
        background: #E5C558;
        color: black;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #000;
        color: white;
        border: 1px solid #333;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    div[data-testid="stMetricLabel"] { color: #888; }
    div[data-testid="stMetricValue"] { color: var(--gold); }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---

def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "appointments": [],
            "expenses": [],
            "reviews": [],
            "settings": {"qr_familiar": None, "qr_ueno": None},
            "client_history": {}
        }
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_id():
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def format_currency(amount):
    return f"₲ {amount:,.0f}".replace(",", ".")

def image_to_base64(uploaded_file):
    if uploaded_file is None: return None
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode()

def generate_whatsapp_link(phone, message):
    encoded_msg = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={phone}&text={encoded_msg}"

# --- INICIALIZACIÓN DE ESTADO ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'view' not in st.session_state:
    st.session_state.view = 'booking' # booking, admin, success
if 'last_booking' not in st.session_state:
    st.session_state.last_booking = None
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- COMPONENTES UI ---

def header():
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; border-bottom: 1px solid rgba(212,175,55,0.3); margin-bottom: 2rem;">
        <h1 style="font-size: 4rem; margin-bottom: 0;">NAILS</h1>
        <div class="script-font" style="margin-top: -1rem; transform: rotate(-2deg);">by Diva</div>
    </div>
    """, unsafe_allow_html=True)

def service_catalog():
    st.markdown("<h3 style='text-align: center;'>Menú de Servicios</h3>", unsafe_allow_html=True)
    
    cols = st.columns(len(SERVICES))
    for idx, (key, service) in enumerate(SERVICES.items()):
        with cols[idx]:
            st.image(service['img'], use_container_width=True)
            st.markdown(f"""
            <div class="service-card">
                <h4 style="color:white; margin:0;">{service['title']}</h4>
                <div style="color:#D4AF37; font-weight:bold; font-size:1.2rem; margin: 10px 0;">{format_currency(service['price'])}</div>
                <p style="font-size:0.8rem; color:#aaa; height: 60px;">{service['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Reservar", key=f"btn_{key}"):
                st.session_state.pre_selected_service = service['title']
                # Hacer scroll manual en la mente del usuario, en Streamlit el rerun lleva arriba
                st.rerun()

def booking_form():
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"<div style='background: rgba(26,26,26,0.8); padding: 30px; border-radius: 20px; border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center'>Completa tu Reserva</h3>", unsafe_allow_html=True)
        
        with st.form("booking_form"):
            name = st.text_input("Nombre Completo")
            
            c_date, c_service = st.columns(2)
            date = c_date.date_input("Fecha", min_value=datetime.date.today())
            
            service_options = [s['title'] for s in SERVICES.values()]
            default_idx = 0
            if 'pre_selected_service' in st.session_state:
                try:
                    default_idx = service_options.index(st.session_state.pre_selected_service)
                except:
                    pass
            
            service_name = c_service.selectbox("Servicio", service_options, index=default_idx)
            
            # Buscar precio
            selected_price = 0
            selected_service_key = ""
            for k, v in SERVICES.items():
                if v['title'] == service_name:
                    selected_price = v['price']
                    selected_service_key = k

            st.markdown(f"<div style='background: rgba(212,175,55,0.1); padding: 10px; border-radius: 5px; text-align:right; color: #D4AF37; font-weight:bold;'>Precio: {format_currency(selected_price)}</div>", unsafe_allow_html=True)
            
            c_time, c_payment = st.columns(2)
            time = c_time.selectbox("Hora", TIME_SLOTS)
            payment = c_payment.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Pix"])
            
            phone = st.text_input("WhatsApp (ej: 0981...)")
            
            submitted = st.form_submit_button("CONFIRMAR RESERVA")
            
            if submitted:
                if not name or not phone:
                    st.error("Por favor completa nombre y teléfono.")
                else:
                    new_apt = {
                        "id": generate_id(),
                        "clientName": name,
                        "date": str(date),
                        "time": time,
                        "service": service_name,
                        "paymentMethod": payment,
                        "phone": phone,
                        "status": "PENDIENTE",
                        "amount": selected_price,
                        "paymentProof": None,
                        "createdAt": str(datetime.datetime.now()),
                        "thankYouSent": False
                    }
                    st.session_state.data['appointments'].append(new_apt)
                    save_data(st.session_state.data)
                    st.session_state.last_booking = new_apt
                    st.session_state.view = 'success'
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def confirmation_page():
    apt = st.session_state.last_booking
    is_transfer = apt['paymentMethod'] in ["Transferencia", "Pix"]
    
    st.markdown(f"""
    <div style="background: #1a1a1a; padding: 20px; border-radius: 20px; text-align: center; border: 1px solid #D4AF37;">
        <h2 style="color: #4CAF50 !important;">¡Reserva Recibida!</h2>
        <p style="font-size: 1.5rem; font-family: monospace; color: #D4AF37;">#{apt['id']}</p>
        <p>Estado: <span style="color: #FFC107;">{apt['status']}</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Resumen")
        st.info(f"""
        **Cliente:** {apt['clientName']}  
        **Fecha:** {apt['date']} a las {apt['time']} hs  
        **Servicio:** {apt['service']}  
        **Total:** {format_currency(apt['amount'])}
        """)
        
        # Botones de Acción
        msg = f"Hola Diva! Hice una reserva #{apt['id']} para {apt['service']} el {apt['date']} a las {apt['time']}."
        wa_link = generate_whatsapp_link(BUSINESS_PHONE, msg)
        
        st.markdown(f"""
        <a href="{wa_link}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:10px;">
                Enviar a WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        if st.button("Volver al Inicio"):
            st.session_state.view = 'booking'
            st.rerun()

    with col2:
        if is_transfer:
            st.markdown("### Datos de Pago")
            
            # Banco Familiar
            with st.expander("Banco Familiar (QR Principal)", expanded=True):
                st.write(f"**Cuenta:** {BANKING_DETAILS['FAMILIAR']['account']}")
                qr_fam = st.session_state.data['settings'].get('qr_familiar')
                if qr_fam:
                    st.image(base64.b64decode(qr_fam), width=200)
            
            # Ueno
            with st.expander("Ueno Bank (QR Secundario)"):
                st.write(f"**Alias:** {BANKING_DETAILS['UENO']['alias']}")
                qr_ueno = st.session_state.data['settings'].get('qr_ueno')
                if qr_ueno:
                    st.image(base64.b64decode(qr_ueno), width=200)
            
            # Subir Comprobante
            st.markdown("#### Subir Comprobante")
            uploaded_proof = st.file_uploader("Adjuntar imagen", type=['jpg', 'png', 'jpeg'])
            
            if uploaded_proof:
                proof_b64 = image_to_base64(uploaded_proof)
                # Actualizar en DB
                for a in st.session_state.data['appointments']:
                    if a['id'] == apt['id']:
                        a['paymentProof'] = proof_b64
                save_data(st.session_state.data)
                st.success("¡Comprobante subido correctamente!")

def admin_panel():
    if not st.session_state.admin_auth:
        col_c, col_in, col_c2 = st.columns([1,1,1])
        with col_in:
            st.markdown("### Acceso Admin")
            pin = st.text_input("PIN de Seguridad", type="password")
            if st.button("Ingresar"):
                if pin == ADMIN_PIN:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("PIN Incorrecto")
        return

    # --- ADMIN DASHBOARD ---
    st.markdown("## Panel de Administración")
    
    # KPIs
    apts = st.session_state.data['appointments']
    expenses = st.session_state.data['expenses']
    
    total_income = sum(a['amount'] for a in apts if a['status'] != 'PENDIENTE')
    total_expense = sum(e['amount'] for e in expenses)
    net_profit = total_income - total_expense
    pending_count = len([a for a in apts if a['status'] == 'PENDIENTE'])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ingresos", format_currency(total_income), delta_color="normal")
    k2.metric("Egresos", format_currency(total_expense), delta_color="inverse")
    k3.metric("Ganancia Neta", format_currency(net_profit))
    k4.metric("Pendientes", f"{pending_count}")

    tab1, tab2, tab3 = st.tabs(["Citas", "Gastos", "Configuración"])
    
    with tab1:
        st.subheader("Gestión de Reservas")
        if not apts:
            st.info("No hay reservas.")
        
        # Ordenar por fecha
        sorted_apts = sorted(apts, key=lambda x: (x['date'], x['time']), reverse=True)
        
        for i, apt in enumerate(sorted_apts):
            with st.container():
                # Estilo de tarjeta para admin
                bg_color = "#1a1a1a"
                border_color = "#D4AF37" if apt['status'] == 'PENDIENTE' else "#333"
                
                c_info, c_actions = st.columns([3, 1])
                with c_info:
                    st.markdown(f"""
                    <div style="background:{bg_color}; border-left: 4px solid {border_color}; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                        <span style="font-size:1.2rem; font-weight:bold; color:white;">{apt['clientName']}</span> 
                        <span style="background:#333; padding:2px 8px; border-radius:4px; font-size:0.8rem;">{apt['status']}</span><br>
                        <small style="color:#aaa;">{apt['date']} | {apt['time']} hs | {apt['service']} | {apt['paymentMethod']}</small><br>
                        <strong style="color:#D4AF37;">{format_currency(apt['amount'])}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    if apt.get('paymentProof'):
                        with st.expander("Ver Comprobante"):
                            st.image(base64.b64decode(apt['paymentProof']))

                with c_actions:
                    new_status = st.selectbox("Estado", ["PENDIENTE", "CONFIRMADO", "COMPLETADO"], index=["PENDIENTE", "CONFIRMADO", "COMPLETADO"].index(apt['status']), key=f"st_{apt['id']}")
                    if new_status != apt['status']:
                        apt['status'] = new_status
                        save_data(st.session_state.data)
                        st.rerun()
                    
                    if st.button("🗑️", key=f"del_{apt['id']}"):
                        st.session_state.data['appointments'] = [a for a in st.session_state.data['appointments'] if a['id'] != apt['id']]
                        save_data(st.session_state.data)
                        st.rerun()
                    
                    if apt['status'] == "COMPLETADO" and not apt.get('thankYouSent'):
                         quote = MOTIVATIONAL_QUOTES[0] # Simplificado para el ejemplo
                         msg = f"Hola {apt['clientName']}! Gracias por venir. '{quote}'. Déjanos una reseña!"
                         link = generate_whatsapp_link(apt['phone'], msg)
                         st.markdown(f"<a href='{link}' target='_blank'>💌 Agradecer</a>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Registrar Gasto")
        with st.form("expense_form"):
            desc = st.text_input("Descripción")
            amount = st.number_input("Monto", min_value=0, step=1000)
            cat = st.selectbox("Categoría", ["Insumos", "Alquiler", "Servicios", "Otros"])
            if st.form_submit_button("Guardar Gasto"):
                new_exp = {
                    "id": generate_id(),
                    "description": desc,
                    "amount": amount,
                    "category": cat,
                    "date": str(datetime.date.today())
                }
                st.session_state.data['expenses'].append(new_exp)
                save_data(st.session_state.data)
                st.success("Gasto guardado")
                st.rerun()
        
        st.write("---")
        st.subheader("Historial de Gastos")
        st.dataframe(pd.DataFrame(st.session_state.data['expenses']))

    with tab3:
        st.subheader("Configuración de QRs")
        
        c_qr1, c_qr2 = st.columns(2)
        with c_qr1:
            st.write("Banco Familiar")
            f_qr = st.file_uploader("Subir QR Familiar", key="up_fam")
            if f_qr:
                st.session_state.data['settings']['qr_familiar'] = image_to_base64(f_qr)
                save_data(st.session_state.data)
                st.success("QR Familiar actualizado")
            
            curr_fam = st.session_state.data['settings'].get('qr_familiar')
            if curr_fam: st.image(base64.b64decode(curr_fam), width=150)

        with c_qr2:
            st.write("Ueno Bank")
            u_qr = st.file_uploader("Subir QR Ueno", key="up_ueno")
            if u_qr:
                st.session_state.data['settings']['qr_ueno'] = image_to_base64(u_qr)
                save_data(st.session_state.data)
                st.success("QR Ueno actualizado")

            curr_ueno = st.session_state.data['settings'].get('qr_ueno')
            if curr_ueno: st.image(base64.b64decode(curr_ueno), width=150)
        
        if st.button("Cerrar Sesión Admin"):
            st.session_state.admin_auth = False
            st.rerun()

def review_section():
    st.markdown("---")
    st.markdown("<h3 style='text-align:center'>Experiencias Diva</h3>", unsafe_allow_html=True)
    
    col_list, col_form = st.columns([1,1])
    
    with col_list:
        reviews = st.session_state.data['reviews']
        if not reviews:
            st.write("Aún no hay reseñas.")
        else:
            for r in reversed(reviews[-5:]): # Mostrar últimas 5
                st.markdown(f"""
                <div style="background: #1a1a1a; padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #333;">
                    <strong>{r['clientName']}</strong> {'⭐'*r['rating']}<br>
                    <em style="color:#aaa;">"{r['comment']}"</em>
                </div>
                """, unsafe_allow_html=True)
    
    with col_form:
        with st.form("review_form"):
            r_name = st.text_input("Tu Nombre")
            r_stars = st.slider("Calificación", 1, 5, 5)
            r_comment = st.text_area("Tu Opinión")
            if st.form_submit_button("Publicar Reseña"):
                if r_name and r_comment:
                    new_rev = {
                        "id": generate_id(),
                        "clientName": r_name,
                        "rating": r_stars,
                        "comment": r_comment,
                        "date": str(datetime.date.today())
                    }
                    st.session_state.data['reviews'].append(new_rev)
                    save_data(st.session_state.data)
                    st.success("Gracias por tu opinión!")
                    st.rerun()

# --- LÓGICA PRINCIPAL ---

def main():
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navegación")
        if st.button("🏠 Inicio / Reservar"):
            st.session_state.view = 'booking'
            st.rerun()
        if st.button("🛡️ Admin Panel"):
            st.session_state.view = 'admin'
            st.rerun()

    header()

    if st.session_state.view == 'booking':
        service_catalog()
        booking_form()
        review_section()
    
    elif st.session_state.view == 'success':
        confirmation_page()
    
    elif st.session_state.view == 'admin':
        admin_panel()

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 50px; padding: 20px; border-top: 1px solid #333;">
        © 2024 Nails by Diva. All Rights Reserved.<br>
        Made for luxury experiences.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()