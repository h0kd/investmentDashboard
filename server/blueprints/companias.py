from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required 
from database import get_db_connection

companias_bp = Blueprint('companias_bp', __name__)

@companias_bp.route('/companias', methods=['GET'])
@login_required
def listar_companias():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ID_Entidad, Rut, Nombre, FonoMovil, Email
            FROM Entidad
            WHERE TipoEntidad = 'Compania'
            ORDER BY Nombre ASC
            """)
        companias = cursor.fetchall()

    except Exception as e:
        flash(f"Error al obtener los datos de los companias: {e}", "error")
        companias = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/companias/companias.html', companias=companias)

@companias_bp.route('/companias/add', methods=['GET', 'POST'])
@login_required
def add_compania():
    if request.method == 'POST':
        rut = request.form['rut']
        nombre = request.form['nombre'].upper()
        email = request.form.get('email')  
        fono_fijo = request.form.get('fono_fijo')  
        fono_movil = request.form.get('fono_movil')  

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Entidad (Rut, Nombre, Email, FonoFijo, FonoMovil, TipoEntidad)
                VALUES (%s, %s, %s, %s, %s, 'Compania')
            """, (rut, nombre, email, fono_fijo, fono_movil))
            conn.commit()

            flash("Compania agregado exitosamente.", "success")
            return redirect(url_for('companias_bp.listar_companias'))
        except Exception as e:
            conn.rollback()
            flash(f"Error al agregar el compania: {e}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('configuracion/companias/add_companias.html')

@companias_bp.route('/delete_compania/<int:id_compania>', methods=['POST'])
@login_required
def delete_compania(id_compania):
    print(f"Entrando a delete_compania con ID: {id_compania}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Entidad WHERE ID_Entidad = %s AND TipoEntidad = 'Compania'", (id_compania,))
        compania = cursor.fetchone()
        if not compania:
            flash("El compania no existe o no es del tipo 'Compania'.", "error")
            return redirect(url_for('companias_bp.listar_companias'))

        cursor.execute("DELETE FROM Entidad WHERE ID_Entidad = %s AND TipoEntidad = 'Compania'", (id_compania,))
        conn.commit()

        print(f"Compania eliminado: {id_compania}")
        flash("Compania eliminado exitosamente.", "success")
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar: {e}")
        flash(f"Error al eliminar el compania: {e}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('companias_bp.listar_companias'))

@companias_bp.route('/companias/edit/<int:id_compania>', methods=['GET', 'POST'])
@login_required
def edit_compania(id_compania):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            rut = request.form['rut']
            nombre = request.form['nombre']
            email = request.form.get('email')  
            fono_fijo = request.form.get('fono_fijo')  
            fono_movil = request.form.get('fono_movil')  

            cursor.execute("""
                UPDATE Entidad
                SET Rut = %s, Nombre = %s, Email = %s, FonoFijo = %s, FonoMovil = %s
                WHERE ID_Entidad = %s AND TipoEntidad = 'Compania'
            """, (rut, nombre, email, fono_fijo, fono_movil, id_compania))
            conn.commit()

            flash("Compania actualizado exitosamente.", "success")
            return redirect(url_for('companias_bp.listar_companias'))

        cursor.execute("""
            SELECT Rut, Nombre, Email, FonoFijo, FonoMovil
            FROM Entidad
            WHERE ID_Entidad = %s AND TipoEntidad = 'Compania'
        """, (id_compania,))
        compania = cursor.fetchone()

        if not compania:
            flash("Compania no encontrado.", "error")
            return redirect(url_for('companias_bp.listar_companias'))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error al procesar la solicitud: {e}", "error")
        return redirect(url_for('companias_bp.listar_companias'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/companias/edit_companias.html', compania=compania, id_compania=id_compania)