import streamlit as st
import numpy as np
import time
import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️", layout="wide")

# ==============================================================================
# 📧 CONFIGURACIÓN DE TU CORREO Y CUENTA LÍDER
# ==============================================================================
ADMIN_USER = "BANCO_OIMC"
ADMIN_PASS = "2325"
ADMIN_EMAIL = "oimcjuan2325@gmail.com"
GMAIL_EMISOR = "oimcjuan2325@gmail.com"  
PASSWORD_EMISOR = "ouagwqwvjetehcwu"  # Contraseña de aplicación de Google

DB_FILE = "banco_oimc_db_v2.json" # Usamos una versión limpia para evitar conflictos previos

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def obtener_fecha_actual():
    now = datetime.now()
    mes = MESES[now.month]
    return f"{now.day} de {mes} de {now.year}"

# --- FUNCIONES DE BASE DE DATOS Y CORREO ---
def cargar_base_datos():
    db_inicial = {
        ADMIN_USER: {
            "nombre": "BANCO_OIMC",
            "gmail": ADMIN_EMAIL,
            "password": ADMIN_PASS,
            "estado": "AUTORIZADO",
            "fecha_autorizacion": "22 de julio de 2026",
            "bloqueo_hasta": None,
            "saldo": 1160,
            "sc": 100,
            "historial": []
        }
    }
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                
                # Asegurar siempre que el administrador (BANCO_OIMC) esté perfecto y actualizado
                datos[ADMIN_USER] = {
                    "nombre": "BANCO_OIMC",
                    "gmail": ADMIN_EMAIL,
                    "password": ADMIN_PASS,
                    "estado": "AUTORIZADO",
                    "fecha_autorizacion": datos.get(ADMIN_USER, {}).get("fecha_autorizacion", "22 de julio de 2026"),
                    "bloqueo_hasta": None,
                    "saldo": datos.get(ADMIN_USER, {}).get("saldo", 1160),
                    "sc": datos.get(ADMIN_USER, {}).get("sc", 100),
                    "historial": datos.get(ADMIN_USER, {}).get("historial", [])
                }
                return datos
        except:
            return db_inicial
    else:
        guardar_base_datos(db_inicial)
        return db_inicial

def guardar_base_datos(datos):
    if ADMIN_USER in datos:
        datos[ADMIN_USER]["gmail"] = ADMIN_EMAIL
        datos[ADMIN_USER]["password"] = ADMIN_PASS
        datos[ADMIN_USER]["estado"] = "AUTORIZADO"
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def enviar_email(destino, asunto, cuerpo):
    msg = MIMEText(cuerpo, 'plain', 'utf-8')
    msg['Subject'] = Header(asunto, 'utf-8')
    msg['From'] = GMAIL_EMISOR
    msg['To'] = destino

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(GMAIL_EMISOR, PASSWORD_EMISOR)
        server.sendmail(GMAIL_EMISOR, [destino], msg.as_string())
        server.quit()
        return True
    except Exception:
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
            server.login(GMAIL_EMISOR, PASSWORD_EMISOR)
            server.sendmail(GMAIL_EMISOR, [destino], msg.as_string())
            server.quit()
            return True
        except Exception:
            return False

def enviar_notificacion_admin(gmail_solicitante, usuario_solicitante):
    asunto = f"🚨 BANCO OIMC: Nueva solicitud de registro de {usuario_solicitante}"
    cuerpo = f"""Se ha registrado una nueva solicitud en el Banco Central O.I.M.C.:

- Usuario: {usuario_solicitante}
- Gmail: {gmail_solicitante}

Inicia sesión en la web con tu cuenta de Administrador para AUTORIZAR o NO AUTORIZAR el acceso."""
    enviar_email(ADMIN_EMAIL, asunto, cuerpo)

def enviar_notificacion_edicion_admin(usuario_antiguo, nuevo_usuario, nuevo_gmail, nueva_pass):
    asunto = f"✏️ BANCO OIMC: Modificación de datos de cuenta ({usuario_antiguo})"
    cuerpo = f"""El usuario '{usuario_antiguo}' ha actualizado los datos de su cuenta bancaria.

Nuevos datos registrados en el sistema:
- Nuevo Usuario: {nuevo_usuario}
- Nuevo Gmail: {nuevo_gmail}
- Nueva Contraseña: {nueva_pass}

Puedes consultarlos desde el panel de administrador."""
    enviar_email(ADMIN_EMAIL, asunto, cuerpo)

def enviar_confirmacion_usuario(gmail_destino, usuario, password, estado):
    if estado == "AUTORIZADO":
        asunto = "✅ Cuenta Bancaria Autorizada - Banco O.I.M.C."
        cuerpo = f"""Felicitaciones, su cuenta bancaria ha sido autorizada. Ya puede iniciar sesión en la web del banco.

----------------------------------------
📌 SUS DATOS DE ACCESO:
• Nombre de usuario: {usuario}
• Contraseña: {password}
----------------------------------------

Ya puede acceder y utilizar las funciones del banco."""
    else:
        asunto = "❌ Estado de Solicitud de Cuenta Bancaria"
        cuerpo = f"""Lo sentimos mucho, pero su cuenta ({usuario}) no ha sido autorizada por el Administrador del Banco. 

Por favor, inténtelo de nuevo más tarde o contacte con el Administrador."""
    enviar_email(gmail_destino, asunto, cuerpo)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .warning-banner {
        background-color: #3d0000;
        color: #ff4d4d;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #ff0000;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    .notice-box {
        background-color: #0e2a38;
        color: #a3e5ff;
        padding: 25px;
        border-radius: 10px;
        border: 2px solid #00aaff;
        font-size: 18px;
        text-align: center;
        margin-top: 20px;
    }
    .permanent-warning {
        background-color: #4a0000;
        color: #ffb3b3;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ff3333;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADOS DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = None
if 'modo_pantalla' not in st.session_state: st.session_state.modo_pantalla = "login"

db_usuarios = cargar_base_datos()

# =========================================================
# 1. GESTIÓN DE ACCESO (LOGIN, REGISTRO, CIERRE, EDICIÓN)
# =========================================================
if not st.session_state.autenticado:

    if st.session_state.modo_pantalla == "registro_completado":
        st.markdown("""
        <div class="notice-box">
            <h2>📩 Solicitud enviada con éxito</h2>
            <p>Tiene que esperar hasta que el Administrador le autorice la cuenta.</p>
            <p>Cuando sea autorizada o rechazada, se le mandará un correo de notificación. Esté atento a su Gmail.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("⬅️ Volver al Inicio de Sesión"):
            st.session_state.modo_pantalla = "login"
            st.rerun()

    elif st.session_state.modo_pantalla == "registro":
        st.title("🏛️ Banco Central O.I.M.C.")
        st.subheader("Crear cuenta bancaria nueva")
        
        reg_gmail = st.text_input("Introduce tu Gmail:", key="reg_gmail")
        reg_user = st.text_input("Nombre de usuario:", key="reg_user")
        reg_pass = st.text_input("Contraseña:", type="password", key="reg_pass")
        
        st.write("")
        col_reg1, col_reg2 = st.columns([1, 2])
        with col_reg1:
            if st.button("Crear cuenta", key="btn_reg"):
                if not reg_gmail or not reg_user or not reg_pass:
                    st.warning("Por favor, rellene todos los campos.")
                elif "@" not in reg_gmail:
                    st.error("El formato del correo electrónico no es válido.")
                elif reg_user == ADMIN_USER or reg_user in db_usuarios:
                    st.error("Ese nombre de usuario ya está ocupado. Elija otro.")
                else:
                    db_usuarios[reg_user] = {
                        "nombre": reg_user,
                        "gmail": reg_gmail,
                        "password": reg_pass,
                        "estado": "PENDIENTE",
                        "fecha_autorizacion": "",
                        "bloqueo_hasta": None,
                        "saldo": 100,
                        "sc": 100,
                        "historial": ["Cuenta creada. Saldo inicial de bienvenida: +100 Oincalias."]
                    }
                    guardar_base_datos(db_usuarios)
                    enviar_notificacion_admin(reg_gmail, reg_user)
                    st.session_state.modo_pantalla = "registro_completado"
                    st.rerun()
        with col_reg2:
            if st.button("Cancelar y volver"):
                st.session_state.modo_pantalla = "login"
                st.rerun()

    elif st.session_state.modo_pantalla == "cierre_permanente":
        st.title("🏛️ Banco Central O.I.M.C.")
        st.subheader("Cerrar cuenta permanentemente")
        
        st.markdown("""
        <div class="permanent-warning">
            ⚠️ ADVERTENCIA: Al cerrar tu cuenta, esta quedará bloqueada durante 5 días (120 horas) antes de poder volver a utilizarse.
        </div>
        """, unsafe_allow_html=True)
        
        perm_gmail = st.text_input("Introduce tu Gmail:", key="perm_gmail")
        perm_user = st.text_input("Introduce tu Nombre de usuario:", key="perm_user")
        perm_pass = st.text_input("Introduce tu Contraseña:", type="password", key="perm_pass")
        
        st.write("")
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            if st.button("Cerrar cuenta definitivamente", key="btn_ejecutar_cierre"):
                if not perm_gmail or not perm_user or not perm_pass:
                    st.warning("Por favor, rellene todos los campos.")
                elif perm_user == ADMIN_USER:
                    st.error("La cuenta administradora principal no puede cerrarse permanentemente.")
                elif perm_user in db_usuarios:
                    usr_data = db_usuarios[perm_user]
                    if usr_data["gmail"] == perm_gmail and usr_data["password"] == perm_pass:
                        tiempo_bloqueo = datetime.now() + timedelta(hours=120)
                        db_usuarios[perm_user]["bloqueo_hasta"] = tiempo_bloqueo.isoformat()
                        guardar_base_datos(db_usuarios)
                        st.success("Cuenta cerrada definitivamente. Ha sido bloqueada temporalmente por 5 días.")
                        time.sleep(2)
                        st.session_state.modo_pantalla = "login"
                        st.rerun()
                    else:
                        st.error("Los datos introducidos (Gmail, usuario o contraseña) no coinciden.")
                else:
                    st.error("El usuario especificado no existe en el sistema.")
        with col_p2:
            if st.button("Cancelar y volver"):
                st.session_state.modo_pantalla = "login"
                st.rerun()

    elif st.session_state.modo_pantalla == "editar_cuenta":
        st.title("🏛️ Banco Central O.I.M.C.")
        st.subheader("Editar datos de tu cuenta")
        
        if 'edit_verificado' not in st.session_state:
            st.session_state.edit_verificado = False
            st.session_state.edit_user_target = ""

        if not st.session_state.edit_verificado:
            st.write("Por favor, introduzca los datos actuales de su cuenta para verificar su identidad:")
            v_user = st.text_input("Usuario actual:", key="v_user")
            v_gmail = st.text_input("Gmail actual:", key="v_gmail")
            v_pass = st.text_input("Contraseña actual:", type="password", key="v_pass")

            col_e1, col_e2 = st.columns([1, 2])
            with col_e1:
                if st.button("Verificar identidad"):
                    if v_user == ADMIN_USER:
                        st.error("La cuenta de Administrador principal no se edita desde aquí.")
                    elif v_user in db_usuarios:
                        data_u = db_usuarios[v_user]
                        if data_u["gmail"] == v_gmail and data_u["password"] == v_pass:
                            st.session_state.edit_verificado = True
                            st.session_state.edit_user_target = v_user
                            st.success("¡Identidad verificada con éxito! Ya puede modificar sus datos.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Los datos introducidos no coinciden con nuestros registros.")
                    else:
                        st.error("El usuario especificado no existe.")
            with col_e2:
                if st.button("Cancelar"):
                    st.session_state.edit_verificado = False
                    st.session_state.modo_pantalla = "login"
                    st.rerun()
        else:
            usr_antiguo = st.session_state.edit_user_target
            datos_actuales = db_usuarios[usr_antiguo]

            st.info(f"Modificando cuenta de: **{usr_antiguo}**")
            nuevo_user = st.text_input("Nuevo nombre de usuario:", value=usr_antiguo, key="nuevo_user")
            nuevo_gmail = st.text_input("Nuevo Gmail:", value=datos_actuales["gmail"], key="nuevo_gmail")
            nueva_pass = st.text_input("Nueva contraseña:", value=datos_actuales["password"], type="password", key="nueva_pass")

            col_n1, col_n2 = st.columns([1, 2])
            with col_n1:
                if st.button("Guardar cambios"):
                    if not nuevo_user or not nuevo_gmail or not nueva_pass:
                        st.warning("Por favor, rellene todos los campos.")
                    elif "@" not in nuevo_gmail:
                        st.error("El formato del correo electrónico no es válido.")
                    elif nuevo_user != usr_antiguo and (nuevo_user == ADMIN_USER or nuevo_user in db_usuarios):
                        st.error("Ese nombre de usuario ya está ocupado.")
                    else:
                        if nuevo_user != usr_antiguo:
                            db_usuarios[nuevo_user] = db_usuarios.pop(usr_antiguo)
                        
                        db_usuarios[nuevo_user]["nombre"] = nuevo_user
                        db_usuarios[nuevo_user]["gmail"] = nuevo_gmail
                        db_usuarios[nuevo_user]["password"] = nueva_pass
                        db_usuarios[nuevo_user]["historial"].append("Datos de inicio de sesión actualizados por el usuario.")

                        guardar_base_datos(db_usuarios)
                        enviar_notificacion_edicion_admin(usr_antiguo, nuevo_user, nuevo_gmail, nueva_pass)

                        st.session_state.edit_verificado = False
                        st.session_state.modo_pantalla = "login"
                        st.success("¡Datos actualizados correctamente y notificación enviada al Administrador!")
                        time.sleep(2)
                        st.rerun()
            with col_n2:
                if st.button("Cancelar y volver"):
                    st.session_state.edit_verificado = False
                    st.session_state.modo_pantalla = "login"
                    st.rerun()

    else:
        st.title("🏛️ Banco Central O.I.M.C.")
        st.subheader("Iniciar sesión")
        
        u_login = st.text_input("Nombre / Usuario:")
        p_login = st.text_input("Contraseña / PIN:", type="password")
        
        st.write("")
        if st.button("Iniciar sesión"):
            if u_login == ADMIN_USER and p_login == ADMIN_PASS:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = ADMIN_USER
                st.success("Acceso concedido como Administrador del Banco.")
                time.sleep(1)
                st.rerun()
            elif u_login in db_usuarios:
                usr_data = db_usuarios[u_login]
                
                bloqueo_hasta_str = usr_data.get("bloqueo_hasta")
                if bloqueo_hasta_str:
                    tiempo_limite = datetime.fromisoformat(bloqueo_hasta_str)
                    if datetime.now() < tiempo_limite:
                        tiempo_restante = tiempo_limite - datetime.now()
                        horas_restantes = int(tiempo_restante.total_seconds() // 3600)
                        minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
                        st.error(f"⚠️ Cuenta bloqueada por cierre definitivo. Debe esperar {horas_restantes} horas y {minutos_restantes} minutos.")
                        st.stop()
                    else:
                        usr_data["bloqueo_hasta"] = None
                        guardar_base_datos(db_usuarios)

                if usr_data["password"] == p_login:
                    if usr_data["estado"] == "AUTORIZADO":
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = u_login
                        st.success(f"Sesión iniciada correctamente como {u_login}")
                        time.sleep(1)
                        st.rerun()
                    elif usr_data["estado"] == "RECHAZADO":
                        st.error("Lo sentimos mucho, pero su cuenta ha sido rechazada por el Administrador.")
                    else:
                        st.info("Su cuenta está pendiente de revisión por el Administrador. Vuelva a intentarlo más tarde.")
                else:
                    st.warning("Contraseña incorrecta.")
            else:
                st.error("El usuario no existe en el sistema. Por favor, cree una cuenta.")

        st.divider()
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn1:
            if st.button("🔗 Crear una cuenta nueva", type="secondary"):
                st.session_state.modo_pantalla = "registro"
                st.rerun()
        with col_btn2:
            if st.button("🔒 Cerrar cuenta permanentemente", type="secondary"):
                st.session_state.modo_pantalla = "cierre_permanente"
                st.rerun()
        with col_btn3:
            if st.button("✏️ Editar tu cuenta", type="secondary"):
                st.session_state.modo_pantalla = "editar_cuenta"
                st.rerun()

# =========================================================
# 2. PANTALLA PRINCIPAL DEL BANCO (LOGUEADO)
# =========================================================
else:
    usuario_actual_id = st.session_state.usuario_actual
    mis_datos = db_usuarios[usuario_actual_id]
    es_admin = (usuario_actual_id == ADMIN_USER)

    st.title("Sistema Bancario Central O.I.M.C.")
    st.header(f"Bienvenido, {mis_datos.get('nombre', usuario_actual_id)}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Tu Saldo Disponible", value=f"{mis_datos['saldo']} Oincalias")
    with col2:
        st.metric(label="Social Credit (S.C.)", value=f"{mis_datos['sc']} Ptos")
        
    st.markdown("---")

    if es_admin:
        with st.expander("👑 PANEL DE ADMINISTRADOR Y GESTIÓN DE CUENTAS", expanded=True):
            tab_pend, tab_aut, tab_no_aut, tab_eco = st.tabs([
                "⏳ Cuentas Pendientes", 
                "✅ Cuentas Autorizadas", 
                "❌ Cuentas Rechazadas",
                "🏛️ Gestión Económica y Social"
            ])
            
            with tab_pend:
                pendientes = {u: d for u, d in db_usuarios.items() if d.get("estado") == "PENDIENTE" and u != ADMIN_USER}
                if not pendientes:
                    st.info("No hay ninguna cuenta en proceso de autorización.")
                else:
                    for usr, data in pendientes.items():
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.write(f"👤 **Usuario:** `{usr}`\n\n 📧 **Gmail:** `{data['gmail']}`\n\n 🔑 **Contraseña:** `{data['password']}`")
                        with c2:
                            if st.button(f"✅ Autorizar", key=f"aut_{usr}"):
                                fecha_hoy = obtener_fecha_actual()
                                db_usuarios[usr]["estado"] = "AUTORIZADO"
                                db_usuarios[usr]["fecha_autorizacion"] = fecha_hoy
                                guardar_base_datos(db_usuarios)
                                enviar_confirmacion_usuario(data["gmail"], usr, data["password"], "AUTORIZADO")
                                st.success(f"{usr} autorizado el {fecha_hoy} y notificado.")
                                time.sleep(1)
                                st.rerun()
                        with c3:
                            if st.button(f"❌ No Autorizar", key=f"no_aut_{usr}"):
                                db_usuarios[usr]["estado"] = "RECHAZADO"
                                guardar_base_datos(db_usuarios)
                                enviar_confirmacion_usuario(data["gmail"], usr, data["password"], "RECHAZADO")
                                st.error(f"{usr} rechazado y notificado.")
                                time.sleep(1)
                                st.rerun()
                        st.divider()

            with tab_aut:
                autorizadas = {u: d for u, d in db_usuarios.items() if d.get("estado") == "AUTORIZADO"}
                if not autorizadas:
                    st.info("No hay cuentas autorizadas.")
                else:
                    for usr, data in autorizadas.items():
                        c1, c2 = st.columns([3, 1])
                        fecha_str = data.get("fecha_autorizacion", "Fecha no registrada")
                        with c1:
                            if usr == ADMIN_USER:
                                st.write(f"👑 **Administrador Principal:** `{usr}` — `{data['gmail']}`")
                            else:
                                st.write(f"👤 **Usuario:** `{usr}` | 📧 `{data['gmail']}` | 🔑 `{data['password']}`\n\n📅 Autorizado el: `{fecha_str}`")
                        with c2:
                            if usr != ADMIN_USER:
                                if st.button(f"🚫 Desautorizar", key=f"desaut_{usr}"):
                                    db_usuarios[usr]["estado"] = "RECHAZADO"
                                    guardar_base_datos(db_usuarios)
                                    st.warning(f"Se ha desautorizado la cuenta {usr}.")
                                    time.sleep(1)
                                    st.rerun()
                        st.divider()

            with tab_no_aut:
                no_autorizadas = {u: d for u, d in db_usuarios.items() if d.get("estado") == "RECHAZADO" and u != ADMIN_USER}
                if not no_autorizadas:
                    st.info("No hay cuentas rechazadas.")
                else:
                    for usr, data in no_autorizadas.items():
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.write(f"👤 **Usuario:** `{usr}` | 📧 `{data['gmail']}` | 🔑 `{data['password']}`")
                        with c2:
                            if st.button(f"✅ Autorizar", key=f"re_aut_{usr}"):
                                fecha_hoy = obtener_fecha_actual()
                                db_usuarios[usr]["estado"] = "AUTORIZADO"
                                db_usuarios[usr]["fecha_autorizacion"] = fecha_hoy
                                guardar_base_datos(db_usuarios)
                                enviar_confirmacion_usuario(data["gmail"], usr, data["password"], "AUTORIZADO")
                                st.success(f"{usr} ha sido autorizada el {fecha_hoy}.")
                                time.sleep(1)
                                st.rerun()
                        st.divider()

            with tab_eco:
                st.subheader("🛠️ Panel de Gestión Económica y Social")
                usuarios_ciudadanos = [u["nombre"] for u in db_usuarios.values() if u["nombre"] != ADMIN_USER and u.get("estado") == "AUTORIZADO"]
                
                if not usuarios_ciudadanos:
                    st.info("No hay ciudadanos con cuentas autorizadas disponibles para gestionar.")
                else:
                    ciudadano_elegido = st.selectbox("Selecciona un ciudadano para gestionar:", usuarios_ciudadanos)
                    id_ciudadano = [p for p, u in db_usuarios.items() if u["nombre"] == ciudadano_elegido][0]
                    datos_ciudadano = db_usuarios[id_ciudadano]
                    
                    tab_sueldos, tab_impuestos, tab_sc, tab_historiales = st.tabs([
                        "💰 Pago de Sueldos", "🏛️ Cobro de Impuestos", "📊 Social Credit", "🔍 Historiales Globales"
                    ])
                    
                    with tab_sueldos:
                        cantidad_sueldo = st.number_input("Cantidad de oincalias a pagar de sueldo:", min_value=1, step=1, key="admin_pay")
                        if st.button("Pagar Sueldo"):
                            if db_usuarios[ADMIN_USER]["saldo"] >= cantidad_sueldo:
                                db_usuarios[ADMIN_USER]["saldo"] -= cantidad_sueldo
                                db_usuarios[id_ciudadano]["saldo"] += cantidad_sueldo
                                db_usuarios[id_ciudadano]["historial"].append(f"Cobro de sueldo: +{cantidad_sueldo} Oincalias.")
                                db_usuarios[ADMIN_USER]["historial"].append(f"Sueldo pagado a {ciudadano_elegido}: -{cantidad_sueldo} Oincalias.")
                                guardar_base_datos(db_usuarios)
                                st.success(f"Sueldo pagado correctamente. Se han descontado {cantidad_sueldo} a {ADMIN_USER}.")
                                st.rerun()
                            else:
                                st.error(f"Fallo fiscal: La cuenta central {ADMIN_USER} no tiene dinero suficiente.")
                                
                    with tab_impuestos:
                        cantidad_impuesto = st.number_input("Cantidad de oincalias a cobrar de impuesto:", min_value=1, step=1, key="admin_tax")
                        if st.button("Cobrar Impuesto"):
                            if datos_ciudadano["saldo"] >= cantidad_impuesto:
                                db_usuarios[id_ciudadano]["saldo"] -= cantidad_impuesto
                                db_usuarios[ADMIN_USER]["saldo"] += cantidad_impuesto
                                db_usuarios[id_ciudadano]["historial"].append(f"Impuesto pagado: -{cantidad_impuesto} Oincalias.")
                                db_usuarios[ADMIN_USER]["historial"].append(f"Impuesto recaudado de {ciudadano_elegido}: +{cantidad_impuesto} Oincalias.")
                                guardar_base_datos(db_usuarios)
                                st.success(f"Impuesto cobrado con éxito. Se han sumado {cantidad_impuesto} a {ADMIN_USER}.")
                                st.rerun()
                            else:
                                st.error(f"El ciudadano {ciudadano_elegido} no tiene suficiente saldo para abonar este impuesto.")
                                
                    with tab_sc:
                        sc_actual = datos_ciudadano["sc"]
                        nuevo_sc = st.slider("Ajustar nivel de Social Credit (S.C.):", min_value=0, max_value=1000, value=int(sc_actual))
                        if st.button("Guardar Social Credit"):
                            db_usuarios[id_ciudadano]["sc"] = nuevo_sc
                            guardar_base_datos(db_usuarios)
                            st.success(f"Social Credit de {ciudadano_elegido} actualizado a {nuevo_sc} puntos.")
                            st.rerun()
                            
                    with tab_historiales:
                        st.write(f"Historial de transacciones de: **{ciudadano_elegido}**")
                        if datos_ciudadano["historial"]:
                            for transaccion in reversed(datos_ciudadano["historial"]):
                                st.text(f"• {transaccion}")
                        else:
                            st.info("Este ciudadano no tiene movimientos registrados.")

        st.markdown("---")

    st.subheader("📱 Enviar transferencia instantánea (Bizum)")
    destinatarios_disponibles = [u["nombre"] for u in db_usuarios.values() if u["nombre"] != mis_datos.get("nombre", usuario_actual_id) and u.get("estado") == "AUTORIZADO"]
    
    if not destinatarios_disponibles:
        st.info("No hay otros usuarios autorizados disponibles para hacer Bizum.")
    else:
        usuario_receptor = st.selectbox("Elige al usuario al que le quieras mandar el bizum:", destinatarios_disponibles)
        cantidad_bizum = st.number_input("Cantidad de oincalias a enviar:", min_value=1, step=1)
        mensaje_bizum = st.text_input("Mensaje en el bizum:", placeholder="Escribe un concepto...")
        
        if st.button("Enviar Bizum 🚀"):
            if mis_datos["saldo"] >= cantidad_bizum:
                id_receptor = [p for p, u in db_usuarios.items() if u["nombre"] == usuario_receptor][0]
                mis_datos["saldo"] -= cantidad_bizum
                db_usuarios[id_receptor]["saldo"] += cantidad_bizum
                
                nombre_emisor = mis_datos.get("nombre", usuario_actual_id)
                msg_emisor = f"Bizum enviado a {usuario_receptor}: -{cantidad_bizum} Oincalias. Mensaje: \"{mensaje_bizum}\""
                msg_receptor = f"Bizum recibido de {nombre_emisor}: +{cantidad_bizum} Oincalias. Mensaje: \"{mensaje_bizum}\""
                
                mis_datos["historial"].append(msg_emisor)
                db_usuarios[id_receptor]["historial"].append(msg_receptor)
                
                guardar_base_datos(db_usuarios)
                st.success("¡Bizum realizado correctamente!")
                st.rerun()
            else:
                st.error("No posees suficientes oincalias para realizar este Bizum.")
                
    st.markdown("---")

    st.subheader("🗂️ Historial de tu cuenta bancaria")
    if mis_datos["historial"]:
        for transaccion in reversed(mis_datos["historial"]):
            st.text(f"• {transaccion}")
    else:
        st.info("Tu cuenta no registra movimientos todavía.")

    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.rerun()
