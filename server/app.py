from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    login_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# Importa tus funciones y modelos
from database import get_db_connection
from models.models import User

# Blueprints (asumiendo que dentro de cada uno devolviste JSON en vez de render_template)
from blueprints.acciones import acciones_bp
from blueprints.fondos_mutuos import fondos_mutuos_bp
from blueprints.facturas import facturas_bp
from blueprints.deposito_a_plazo import deposito_a_plazo_bp
from blueprints.boletas_garantia import boletas_garantia_bp
from blueprints.polizas import polizas_bp
from blueprints.bancos import bancos_bp
from blueprints.empresas import empresas_bp
from blueprints.corredores import corredores_bp
from blueprints.companias import companias_bp
from blueprints.clientes import clientes_bp
from blueprints.parametros import parametros_bp
from blueprints.dividendos import dividendos_bp

#lol
# Cargar variables de entorno
load_dotenv()

# Configuración de Flask
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'una_clave_de_sesion'
CORS(app, supports_credentials=True)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'  # Si ya no usas rutas HTML, opcional quitar

# Registrar los Blueprints (cada uno debería exponer rutas tipo /api/...)
app.register_blueprint(acciones_bp)
app.register_blueprint(fondos_mutuos_bp)
app.register_blueprint(facturas_bp)
app.register_blueprint(deposito_a_plazo_bp)
app.register_blueprint(boletas_garantia_bp)
app.register_blueprint(polizas_bp)
app.register_blueprint(bancos_bp)
app.register_blueprint(empresas_bp)
app.register_blueprint(corredores_bp)
app.register_blueprint(companias_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(parametros_bp)
app.register_blueprint(dividendos_bp)

# Manejo de archivos (por si lo necesitas)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

###############################################################################
#                                FLASK-LOGIN                                  #
###############################################################################

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login requiere esta función para 'cargar' el usuario
    desde su ID, que guarda en la sesión.
    """
    return User.get(user_id)  # Ajusta a cómo recuperas el usuario en tu modelo


###############################################################################
#                                 RUTAS API                                   #
###############################################################################

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    Endpoint para manejar login (recibe JSON con username y password).
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Faltan datos"}), 400

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, NombreUsuario, Contraseña FROM Usuarios WHERE NombreUsuario = %s", (username,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_data:
        user_id, db_username, db_password = user_data
        if check_password_hash(db_password, password):
            user = User(id=user_id, username=db_username)
            login_user(user)  # Crea la sesión en el servidor
            return jsonify({"success": True, "message": "Inicio de sesión exitoso"})
        else:
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401
    else:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """
    Cierra la sesión del usuario en Flask-Login.
    """
    logout_user()
    return jsonify({"success": True, "message": "Cierre de sesión exitoso"})


@app.route('/api/summary', methods=['GET'])
@login_required
def api_summary():
    """
    Ejemplo de endpoint que devuelve datos en JSON para una vista 'Dashboard' en React.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Empresas registradas
        cursor.execute("SELECT COUNT(*) FROM EntidadComercial WHERE TipoEntidad = 'Empresa';")
        total_empresas = cursor.fetchone()[0]

        # Total acciones
        cursor.execute("SELECT SUM(Cantidad) FROM Facturas;")
        total_acciones = cursor.fetchone()[0] or 0

        # Valor total invertido
        cursor.execute("SELECT SUM(Valor) FROM Facturas;")
        valor_total_invertido = cursor.fetchone()[0] or 0

        # Total dividendos
        cursor.execute("SELECT SUM(valortotal) FROM Dividendos;")
        total_dividendos = cursor.fetchone()[0] or 0

    except Exception as e:
        print(f"Error al obtener métricas: {e}")
        return jsonify({
            "success": False,
            "error": f"Error al obtener métricas: {str(e)}"
        }), 500
    finally:
        cursor.close()
        conn.close()

    data = {
        "success": True,
        "total_empresas": total_empresas,
        "total_acciones": total_acciones,
        "valor_total_invertido": valor_total_invertido,
        "total_dividendos": total_dividendos
    }
    return jsonify(data)


@app.route('/api/change_password', methods=['POST'])
@login_required
def api_change_password():
    """
    Endpoint para cambiar la contraseña. 
    Se asume que el front envía un JSON con:
      {
        "current_password": "...",
        "new_password": "...",
        "confirm_password": "..."
      }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Faltan datos"}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    # Verificar que coincida la confirmación
    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtenemos la contraseña actual en la BD
        cursor.execute("SELECT Contraseña FROM Usuarios WHERE ID = %s", (current_user.id,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        stored_hash = resultado[0]
        # Verificar la contraseña actual
        if not check_password_hash(stored_hash, current_password):
            return jsonify({"success": False, "message": "La contraseña actual es incorrecta"}), 401

        # Actualizar la nueva contraseña en la BD
        nuevo_hash = generate_password_hash(new_password)
        cursor.execute("UPDATE Usuarios SET Contraseña = %s WHERE ID = %s", (nuevo_hash, current_user.id))
        conn.commit()

        return jsonify({"success": True, "message": "Contraseña cambiada con éxito"})
    except Exception as e:
        print(f"Error al cambiar la contraseña: {e}")
        return jsonify({"success": False, "message": "Hubo un error al cambiar la contraseña"}), 500
    finally:
        cursor.close()
        conn.close()


###############################################################################
#                        OPCIONAL: SERVIR REACT BUILD                         #
###############################################################################
#
# Si deseas servir el build de React desde Flask (un solo servidor),
# descomenta y ajusta las siguientes líneas una vez tengas /client/build.

# import os
# from flask import send_from_directory

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve(path):
#     """
#     Sirve los archivos estáticos compilados de React
#     (requiere que hayas hecho 'npm run build' o 'yarn build' en /client).
#     """
#     if path != "" and os.path.exists(os.path.join('..', 'client', 'build', path)):
#         return send_from_directory(os.path.join('..', 'client', 'build'), path)
#     else:
#         return send_from_directory(os.path.join('..', 'client', 'build'), 'index.html')


###############################################################################
#                            ERROR HANDLERS                                   #
###############################################################################

@app.errorhandler(404)
def not_found(e):
    """
    Ejemplo de manejo de error 404:
    si NO estás sirviendo React desde Flask, 
    simplemente devolvemos JSON de "no encontrado".
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal Server Error"}), 500


###############################################################################
#                          INICIAR LA APLICACIÓN                              #
###############################################################################

if __name__ == '__main__':
    app.run(debug=True)
