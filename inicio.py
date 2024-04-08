import streamlit as st
import boto3
import pandas as pd

from config import cargar_configuracion
from ingresaRevisionFosa import main as revisionFosa
from visualizaRevisionFosa import visualizar_revisiones_en_fosa as visualizaRevisionFosa
from ingresaUsuarios import ingresa_usuario
from visualizaUsuarios import main as visualiza_usuarios

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para obtener usuarios desde el archivo CSV en S3
def buscar_usuarios(nombre_usuario_input):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'usuarios.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        usuarios_df = pd.read_csv(response['Body'])

        # Filtrar por nombre de usuario
        usuarios_df = usuarios_df[usuarios_df['nombreApellido'].str.contains(nombre_usuario_input, case=False)]

        return usuarios_df

    except Exception as e:
        st.error(f"Error al buscar usuarios: {e}")
        return pd.DataFrame()

# Definir las variables para el estado de inicio de sesión
logged_in = st.session_state.get("logged_in", False)
user_nombre_apellido = st.session_state.get("user_nombre_apellido", "")
user_rol = st.session_state.get("user_rol", "")

# Función para verificar las credenciales y obtener el rol del usuario
def login(username, password):
    try:
        usuarios_df = buscar_usuarios(username.strip())

        if not usuarios_df.empty:
            stored_password = usuarios_df.iloc[0]['contraseña']
            if password == stored_password:
                st.session_state.logged_in = True
                st.session_state.user_rol = usuarios_df.iloc[0]['rol']
                st.session_state.user_nombre_apellido = username
                st.session_state.id_usuario = usuarios_df.iloc[0]['idUsuario']
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas. Inténtalo de nuevo")
        else:
            st.error("Usuario no encontrado")

    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")

# Función para cerrar sesión
def logout():
    st.session_state.logged_in = False
    st.session_state.user_rol = ""
    st.session_state.user_nombre_apellido = ""  # Limpiar el nombre y apellido al cerrar sesión
    st.success("Sesión cerrada exitosamente")

def main():
    st.title(":red[Pagina de Ejemplo]")
    st.title(":blue[T.A. Ciudad de Alderetes - T.A. El Tigre 🚌]")
    st.header("Sistema para Revisiones de Fosa")

    if logged_in:
        st.sidebar.title("Menú")

        st.subheader(f"Bienvenido, {user_nombre_apellido}!")

        if user_rol == "admin":
            selected_option = st.sidebar.selectbox("Seleccione una opción:", ["Nueva Revision en Fosa", "Visualizar Revisiones en Fosa","Nuevo Usuario", "Visualiza Usuarios"])
            if selected_option == "Nuevo Usuario":
                ingresa_usuario()
            if selected_option == "Visualiza Usuarios":
                visualiza_usuarios()
            if selected_option == "Nueva Revision en Fosa":
                revisionFosa()
            if selected_option == "Visualizar Revisiones en Fosa":
                visualizaRevisionFosa()

            if selected_option == "Inicio":
                texto_inicio()

        else:
            selected_option = st.sidebar.selectbox("Seleccione una opción:", ["Nueva Revision en Fosa", "Visualizar Revisiones en Fosa"])
            if selected_option == "Nueva Revision en Fosa":
                revisionFosa()
            if selected_option == "Visualizar Revisiones en Fosa":
                visualizaRevisionFosa()
            if selected_option == "Inicio":
                texto_inicio()

        st.write(f"Usuario: {user_nombre_apellido}")

    else:
        st.sidebar.title("Inicio de Sesión")

        with st.form(key="login_form"):
            st.subheader("Nombre de Usuario: digidatasalta")
            st.subheader("Contraseña: digidatasalta")
            username = st.text_input("Nombre de Usuario:")
            password = st.text_input("Contraseña:", type="password")

            login_submitted = st.form_submit_button("Iniciar Sesión")

            if login_submitted and username and password:
                login(username, password)

    if logged_in:
        st.sidebar.button("Cerrar Sesión", on_click=logout)

def texto_inicio():
    st.write(f"Bienvenido, {user_nombre_apellido}! - Sistema para Revisiones de Fosa")
    st.write(f"Bienvenido, {user_nombre_apellido}! - T.A. Ciudad de Alderetes y T.A. El Tigre")
    st.header("""Instrucciones \n * **Menú de la Izquierda**: En la interfaz de la aplicación, observarás un menú en el lado izquierdo de la pantalla. \n * **Despliegue del Menú**: Localiza el icono ">"que indica el despliegue del menú. \n * **Selección de Función**: Haz clic en el despliegue del menú y selecciona la opción correspondiente a la función que deseas utilizar. \n * **Interfaz de Función**: Una vez que hayas seleccionado la función, la interfaz cambiará para mostrar los campos o una tabla con la informacion requerida. \n * **Completar una Función**: Rellena los campos o visualiza la informacion que desees. \n * **Cerrar Sesión**: Cuando sea necesario busca el boton para cerrar sesión.
    """)
    st.header("Funciones")
    st.subheader("""Ingresar Nueva Revisión en Fosa\n * Ingrese el número de coche en el campo proporcionado.\n * Haga clic en el botón 'Comenzar Revisión' para iniciar la revisión.\n * Complete la inspección de cada posición y punto de inspección.\n * Haga clic en el botón 'Guardar Revisión' al finalizar la inspección.\n * La información se guardará automáticamente en el archivo 'revisiones.csv'.""")
    st.subheader("""Visualizar Revisiones en Fosa\n * Selecciona el estado deseado en el menú desplegable 'Filtrar por Estado'.\n * Se mostrarán las revisiones filtradas según el estado seleccionado.\n * Si deseas ver detalles de una revisión específica, ingresa el 'idRevision' en el campo correspondiente y presiona Enter.\n * La sección 'Detalles de Revisiones en Fosa' mostrará información detallada sobre la revisión seleccionada.\n * Para editar el estado de una revisión, ingresa el 'idRevision' en el campo 'Ingrese idRevision para editar'.\n * Selecciona el nuevo estado en el menú desplegable 'Nuevo Estado'.\n * Presiona el botón 'Editar Estado' para aplicar los cambios (disponible solo para usuarios administradores antes de las 24:00).\n * La sección 'Detalle de Posiciones' proporciona información detallada sobre cada posición inspeccionada.\n * Utiliza el menú desplegable 'Filtrar por Estado' para mostrar solo los puntos con un estado específico.\n * La información se actualiza dinámicamente según las selecciones realizadas.""")

    if user_rol == "admin":
        st.subheader("""Crear Usuario\n * Ingrese los datos del usuario, incluyendo nombre y apellido, email, contraseña, verificación de contraseña, fecha de nacimiento, DNI, domicilio y rol (empleado o admin).\n * Presione 'Registrar Usuario' para guardar la información.""")
        st.subheader("""Visualizar Usuarios\n * Visualice la información de los usuarios, salvo la contraseña.\n * Edite la información del usuario ingresando el ID correspondiente y modifique los campos necesarios.\n * Presione 'Guardar cambios' para confirmar las modificaciones.""")

if __name__ == "__main__":
    main()