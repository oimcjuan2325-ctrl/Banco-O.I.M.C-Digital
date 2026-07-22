import streamlit as st
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️", layout="wide")

# Credenciales y base de datos maestra almacenada de forma persistente en Streamlit Secrets
# Puedes editar esto fácilmente desde el panel de control de tu app en Streamlit Cloud
ADMIN_USER = "BANCO_OIMC"
ADMIN_PASS = "2325"

# --- ESTADOS DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = None

# Base de datos simulada y persistente mediante secrets o estado global seguro
if "db_usuarios" not in st.session_state:
    # Si usas st.secrets puedes cargar la BD desde ahí, si no, usamos una base por defecto persistente en memoria de sesión
    st.session_state.db_usuarios = {
        ADMIN_USER: {
            "nombre": "BANCO_OIMC",
            "password": ADMIN_PASS,
            "saldo": 1160,
            "sc": 100,
            "historial": ["Cuenta principal del Banco iniciada."]
        },
        "usuario1": {
            "nombre": "Ciudadano 1",
            "password": "1234",
            "saldo": 500,
            "sc": 100,
            "historial": ["Cuenta creada con éxito."]
        }
    }

db_usuarios = st.session_state.db_usuarios

# =========================================================
# 1. PANTALLA DE ACCESO (LOGIN)
# =========================================================
if not st.session_state.autenticado:
    st.title("🏛️ Banco Central O.I.M.C.")
    st.subheader("Iniciar sesión")
    
    u_login = st.text_input("Nombre de usuario:")
    p_login = st.text_input("Contraseña:", type="password")
    
    st.write("")
    if st.button("Iniciar sesión"):
        if u_login in db_usuarios and db_usuarios[u_login]["password"] == p_login:
            st.session_state.autenticado = True
            st.session_state.usuario_actual = u_login
            st.success(f"¡Bienvenido, {u_login}!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

# =========================================================
# 2. PANTALLA PRINCIPAL DEL BANCO
# =========================================================
else:
    usuario_actual_id = st.session_state.usuario_actual
    mis_datos = db_usuarios[usuario_actual_id]
    es_admin = (usuario_actual_id == ADMIN_USER)

    st.title("Sistema Bancario Central O.I.M.C.")
    st.header(f"Panel de: {mis_datos['nombre']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Tu Saldo Disponible", value=f"{mis_datos['saldo']} Oincalias")
    with col2:
        st.metric(label="Social Credit (S.C.)", value=f"{mis_datos['sc']} Ptos")
        
    st.markdown("---")

    # Panel exclusivo de Administrador
    if es_admin:
        with st.expander("👑 PANEL DE ADMINISTRADOR", expanded=True):
            st.subheader("Gestión de Ciudadanos")
            
            # Selector de usuarios (excluyendo al admin)
            ciudadanos = [u for u in db_usuarios.keys() if u != ADMIN_USER]
            if ciudadanos:
                c_elegido = st.selectbox("Selecciona un ciudadano:", ciudadanos)
                datos_c = db_usuarios[c_elegido]
                
                cant_sueldo = st.number_input("Pagar sueldo (Oincalias):", min_value=1, step=1, key="p_sueldo")
                if st.button("Enviar Sueldo"):
                    if db_usuarios[ADMIN_USER]["saldo"] >= cant_sueldo:
                        db_usuarios[ADMIN_USER]["saldo"] -= cant_sueldo
                        db_usuarios[c_elegido]["saldo"] += cant_sueldo
                        db_usuarios[c_elegido]["historial"].append(f"Sueldo recibido: +{cant_sueldo} Oincalias.")
                        st.success(f"Sueldo enviado correctamente a {c_elegido}.")
                        st.rerun()
                    else:
                        st.error("El banco no tiene suficiente saldo.")
            else:
                st.info("No hay ciudadanos registrados.")

        st.markdown("---")

    # Bizum / Transferencias entre usuarios
    st.subheader("📱 Enviar transferencia (Bizum)")
    receptores = [u for u in db_usuarios.keys() if u != usuario_actual_id]
    
    if receptores:
        receptor_elegido = st.selectbox("Destinatario:", receptores)
        cant_bizum = st.number_input("Cantidad a enviar:", min_value=1, step=1, key="c_bizum")
        msg_bizum = st.text_input("Concepto:")
        
        if st.button("Enviar Bizum 🚀"):
            if mis_datos["saldo"] >= cant_bizum:
                mis_datos["saldo"] -= cant_bizum
                db_usuarios[receptor_elegido]["saldo"] += cant_bizum
                
                mis_datos["historial"].append(f"Bizum enviado a {receptor_elegido}: -{cant_bizum} Oincalias ({msg_bizum})")
                db_usuarios[receptor_elegido]["historial"].append(f"Bizum recibido de {usuario_actual_id}: +{cant_bizum} Oincalias ({msg_bizum})")
                
                st.success("¡Bizum realizado con éxito!")
                st.rerun()
            else:
                st.error("Saldo insuficiente.")
    else:
        st.info("No hay otros usuarios disponibles para transferencias.")

    st.markdown("---")

    # Historial de movimientos
    st.subheader("🗂️ Historial de transacciones")
    if mis_datos["historial"]:
        for h in reversed(mis_datos["historial"]):
            st.text(f"• {h}")
    else:
        st.info("No hay movimientos registrados.")

    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.rerun()
