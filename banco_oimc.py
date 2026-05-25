import streamlit as st
import json
import os

# Configuración visual de la página web
st.set_page_config(page_title="Banco Central O.I.M.C.", page_icon="🏛️", layout="centered")

# Nombre del archivo donde se guardará absolutamente todo
DB_FILE = "banco_oimc_db.json"

# Base de datos oficial inicial con los nombres y PINES reales que me diste
DB_INICIAL = {
    "2313": {"nombre": "Juan", "saldo": 10, "sc": 70, "historial": []},
    "2021": {"nombre": "Asier", "saldo": 10, "sc": 70, "historial": []},
    "1365": {"nombre": "Jesús", "saldo": 10, "sc": 70, "historial": []},
    "1460": {"nombre": "Yolanda", "saldo": 10, "sc": 70, "historial": []},
    "2013": {"nombre": "Mikel", "saldo": 10, "sc": 70, "historial": []},
    "9837": {"nombre": "Gaizka", "saldo": 10, "sc": 70, "historial": []},
    "7467": {"nombre": "Iñaki", "saldo": 10, "sc": 70, "historial": []},
    "7562": {"nombre": "Erika", "saldo": 0, "sc": 70, "historial": []},
    "9786": {"nombre": "Nahia", "saldo": 0, "sc": 70, "historial": []},
    "1053": {"nombre": "Amets", "saldo": 0, "sc": 70, "historial": []},
    "2325": {"nombre": "BANCO-OIMC", "saldo": 1000, "sc": 100, "historial": []}
}

# Funciones para leer y escribir en el archivo JSON (Garantiza el guardado permanente)
def cargar_base_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DB_INICIAL

def guardar_base_datos(datos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Inicializar los datos en la memoria de la web
if "db" not in st.session_state:
    st.session_state.db = cargar_base_datos()

if "usuario_conectado" not in st.session_state:
    st.session_state.usuario_conectado = None

# =========================================================
# 1. PANTALLA DE INICIO DE SESIÓN (LOGIN)
# =========================================================
if st.session_state.usuario_conectado is None:
    st.title("Tu Cuenta de Banco de la O.I.M.C.")
    st.subheader("Iniciar sesión")
    
    input_user = st.text_input("Nombre / Usuario:")
    input_pin = st.text_input("PIN:", type="password", max_chars=4)
    
    if st.button("Iniciar sesión"):
        # Verificamos si el PIN existe en el censo
        if input_pin in st.session_state.db:
            datos_cuenta = st.session_state.db[input_pin]
            # Validamos que el nombre introducido sea exactamente igual (sin importar mayúsculas)
            if datos_cuenta["nombre"].lower() == input_user.strip().lower():
                st.session_state.usuario_conectado = input_pin
                st.success(f"Sesión iniciada como {datos_cuenta['nombre']}")
                st.rerun()
            else:
                st.error("El nombre de usuario no coincide con el PIN introducido.")
        else:
            st.error("PIN incorrecto. No coincide con ningún usuario del sistema.")

# =========================================================
# 2. PANTALLA PRINCIPAL DEL BANCO (LOGUEADO)
# =========================================================
else:
    pin_actual = st.session_state.usuario_conectado
    mis_datos = st.session_state.db[pin_actual]
    es_admin = (mis_datos["nombre"] == "BANCO-OIMC")

    st.title("Sistema Bancario Central O.I.M.C.")
    st.header(f"Bienvenido, {mis_datos['nombre']}")
    
    # Se muestran únicamente los indicadores de Saldo y Social Credit
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Tu Saldo Disponible", value=f"{mis_datos['saldo']} Oincalias")
    with col2:
        st.metric(label="Social Credit (S.C.)", value=f"{mis_datos['sc']} Ptos")
        
    st.markdown("---")

    # -----------------------------------------------------
    # PANEL EXCLUSIVO PARA CUENTA ADMIN ("BANCO-OIMC")
    # -----------------------------------------------------
    if es_admin:
        st.subheader("🛠️ Panel de Gestión Económica y Social (Administrador)")
        
        # Filtramos la lista para poder elegir a cualquier usuario excepto a sí mismo
        usuarios_ciudadanos = [u["nombre"] for u in st.session_state.db.values() if u["nombre"] != "BANCO-OIMC"]
        ciudadano_elegido = st.selectbox("Selecciona un ciudadano para gestionar:", usuarios_ciudadanos)
        
        # Buscamos el PIN del ciudadano seleccionado
        pin_ciudadano = [p for p, u in st.session_state.db.items() if u["nombre"] == ciudadano_elegido][0]
        datos_ciudadano = st.session_state.db[pin_ciudadano]
        
        # Pestañas para organizar las acciones de administrador
        tab_sueldos, tab_impuestos, tab_sc, tab_historiales = st.tabs([
            "💰 Pago de Sueldos", "🏛️ Cobro de Impuestos", "📊 Social Credit", "🔍 Historiales Globales"
        ])
        
        # Acción: Pago de Sueldos (Descuenta de Admin y suma al usuario)
        with tab_sueldos:
            cantidad_sueldo = st.number_input("Cantidad de oincalias a pagar de sueldo:", min_value=1, step=1, key="admin_pay")
            if st.button("Pagar Sueldo"):
                if st.session_state.db["2325"]["saldo"] >= cantidad_sueldo:
                    st.session_state.db["2325"]["saldo"] -= cantidad_sueldo
                    st.session_state.db[pin_ciudadano]["saldo"] += cantidad_sueldo
                    
                    # Registro de la operación en ambos historiales
                    st.session_state.db[pin_ciudadano]["historial"].append(f"Cobro de sueldo: +{cantidad_sueldo} Oincalias.")
                    st.session_state.db["2325"]["historial"].append(f"Sueldo pagado a {ciudadano_elegido}: -{cantidad_sueldo} Oincalias.")
                    
                    guardar_base_datos(st.session_state.db)
                    st.success(f"Sueldo pagado correctamente. Se han descontado {cantidad_sueldo} a BANCO-OIMC.")
                    st.rerun()
                else:
                    st.error("Fallo fiscal: La cuenta central BANCO-OIMC no tiene dinero suficiente.")
                    
        # Acción: Cobro de Impuestos (Resta al usuario y suma a Admin)
        with tab_impuestos:
            cantidad_impuesto = st.number_input("Cantidad de oincalias a cobrar de impuesto:", min_value=1, step=1, key="admin_tax")
            if st.button("Cobrar Impuesto"):
                if datos_ciudadano["saldo"] >= cantidad_impuesto:
                    st.session_state.db[pin_ciudadano]["saldo"] -= cantidad_impuesto
                    st.session_state.db["2325"]["saldo"] += cantidad_impuesto
                    
                    # Registro de la operación en ambos historiales
                    st.session_state.db[pin_ciudadano]["historial"].append(f"Impuesto pagado: -{cantidad_impuesto} Oincalias.")
                    st.session_state.db["2325"]["historial"].append(f"Impuesto recaudado de {ciudadano_elegido}: +{cantidad_impuesto} Oincalias.")
                    
                    guardar_base_datos(st.session_state.db)
                    st.success(f"Impuesto cobrado con éxito. Se han sumado {cantidad_impuesto} a BANCO-OIMC.")
                    st.rerun()
                else:
                    st.error(f"El ciudadano {ciudadano_elegido} no tiene suficiente saldo para abonar este impuesto.")
                    
        # Acción: Cambio de Social Credit con barrita deslizable
        with tab_sc:
            sc_actual = datos_ciudadano["sc"]
            nuevo_sc = st.slider("Ajustar nivel de Social Credit (S.C.):", min_value=0, max_value=1000, value=int(sc_actual))
            if st.button("Guardar Social Credit"):
                st.session_state.db[pin_ciudadano]["sc"] = nuevo_sc
                guardar_base_datos(st.session_state.db)
                st.success(f"Social Credit de {ciudadano_elegido} actualizado a {nuevo_sc} puntos.")
                st.rerun()
                
        # Acción: Ver historial de todos (Elegir usuario y ver su historial)
        with tab_historiales:
            st.write(f"Historial de transacciones de: **{ciudadano_elegido}**")
            if datos_ciudadano["historial"]:
                for transaccion in reversed(datos_ciudadano["historial"]):
                    st.text(f"• {transaccion}")
            else:
                st.info("Este ciudadano no tiene movimientos registrados.")

        st.markdown("---")

    # -----------------------------------------------------
    # SECCIÓN DE ENVIAR BIZUM (USER Y ADMIN)
    # -----------------------------------------------------
    st.subheader("📱 Enviar transferencia instantánea (Bizum)")
    
    # Lista de destinatarios excluyendo al propio usuario que envía
    destinatarios_disponibles = [u["nombre"] for u in st.session_state.db.values() if u["nombre"] != mis_datos["nombre"]]
    usuario_receptor = st.selectbox("Elige al usuario que le quieras mandar el bizum:", destinatarios_disponibles)
    
    cantidad_bizum = st.number_input("Cantidad de oincalias a enviar:", min_value=1, step=1)
    mensaje_bizum = st.text_input("Mensaje en el bizum:", placeholder="Escribe un concepto...")
    
    if st.button("Enviar Bizum 🚀"):
        if mis_datos["saldo"] >= cantidad_bizum:
            # Encontrar el PIN del destinatario
            pin_receptor = [p for p, u in st.session_state.db.items() if u["nombre"] == usuario_receptor][0]
            
            # Restamos al emisor y sumamos al receptor de inmediato
            st.session_state.db[pin_actual]["saldo"] -= cantidad_bizum
            st.session_state.db[pin_receptor]["saldo"] += cantidad_bizum
            
            # Anotamos los mensajes en los historiales correspondientes
            msg_emisor = f"Bizum enviado a {usuario_receptor}: -{cantidad_bizum} Oincalias. Mensaje: \"{mensaje_bizum}\""
            msg_receptor = f"Bizum recibido de {mis_datos['nombre']}: +{cantidad_bizum} Oincalias. Mensaje: \"{mensaje_bizum}\""
            
            st.session_state.db[pin_actual]["historial"].append(msg_emisor)
            st.session_state.db[pin_receptor]["historial"].append(msg_receptor)
            
            # Guardamos los cambios de manera persistente en el JSON
            guardar_base_datos(st.session_state.db)
            st.success("¡Bizum realizado correctamente!")
            st.rerun()
        else:
            st.error("No posees suficientes oincalias para realizar este Bizum.")
            
    st.markdown("---")

    # -----------------------------------------------------
    # SECCIÓN HISTORIAL PERSONAL (USER Y ADMIN)
    # -----------------------------------------------------
    st.subheader("🗂️ Historial de tu cuenta bancaria")
    if mis_datos["historial"]:
        for transaccion in reversed(mis_datos["historial"]):
            st.text(f"• {transaccion}")
    else:
        st.info("Tu cuenta no registra movimientos todavía.")

    # Botón de desconexión segura
    if st.button("Cerrar Sesión"):
        st.session_state.usuario_conectado = None
        st.rerun()
