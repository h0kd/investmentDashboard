from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required 
from database import get_db_connection
import requests

parametros_bp = Blueprint('parametros_bp', __name__)

def obtener_valor_dolar():
    access_key = "ff4a1918901e515058e82a1826a1f916"  
    try:
        url = f"https://api.exchangerate.host/live?access_key={access_key}&currencies=CLP"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print("Respuesta de la API:", data)  

            if data.get('success') and 'quotes' in data and 'USDCLP' in data['quotes']:
                return data['quotes']['USDCLP']  
            else:
                print(f"Error en la respuesta de la API: {data}")
                return None
        else:
            print(f"Error al conectar con la API. Código de estado: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al obtener el valor del dólar: {e}")
        return None

valor_dolar = obtener_valor_dolar()
if valor_dolar:
    print(f"El valor actual del dólar en CLP es: {valor_dolar}")
else:
    print("No se pudo obtener el valor del dólar.")




@parametros_bp.route('/parametros', methods=['GET', 'POST'])
@login_required
def gestionar_parametros():
    valor_dolar = obtener_valor_dolar()  
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            nombre = request.form['nombre']
            valor = float(request.form['valor'])

            cursor.execute("SELECT ID_Parametro FROM Parametros WHERE Nombre = %s", (nombre,))
            parametro = cursor.fetchone()
            if parametro:
                cursor.execute("""
                    UPDATE Parametros
                    SET Valor = %s, FechaActualizacion = NOW()
                    WHERE ID_Parametro = %s
                """, (valor, parametro[0]))
                flash(f"Parámetro '{nombre}' actualizado.", "success")
            else:
                cursor.execute("""
                    INSERT INTO Parametros (Nombre, Valor)
                    VALUES (%s, %s)
                """, (nombre, valor))
                flash(f"Parámetro '{nombre}' agregado.", "success")
            conn.commit()

        cursor.execute("SELECT ID_Parametro, Nombre, Valor, FechaActualizacion FROM Parametros")
        parametros = cursor.fetchall()

        if valor_dolar:
            cursor.execute("""
                UPDATE Parametros
                SET Valor = %s, FechaActualizacion = NOW()
                WHERE Nombre = 'Dólar'
            """, (valor_dolar,))
            conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error al gestionar parámetros: {e}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/parametros/parametros.html', parametros=parametros, valor_dolar=valor_dolar)

@parametros_bp.route('/parametros/update', methods=['POST'])
@login_required
def actualizar_parametro():
    try:
        id_parametro = request.form['id_parametro']
        nuevo_valor = float(request.form['valor'])

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Parametros
            SET Valor = %s, FechaActualizacion = NOW()
            WHERE ID_Parametro = %s
        """, (nuevo_valor, id_parametro))

        conn.commit()
        flash("Parámetro actualizado exitosamente.", "success")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error al actualizar el parámetro: {e}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('gestionar_parametros'))

@parametros_bp.route('/parametros/delete', methods=['POST'])
@login_required
def eliminar_parametro():
    try:
        id_parametro = request.form['id_parametro']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Parametros WHERE ID_Parametro = %s", (id_parametro,))
        conn.commit()

        flash("Parámetro eliminado exitosamente.", "success")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error al eliminar el parámetro: {e}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('gestionar_parametros'))