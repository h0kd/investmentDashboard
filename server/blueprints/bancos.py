from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required 
from database import get_db_connection

bancos_bp = Blueprint('bancos_bp', __name__)

@bancos_bp.route('/bancos', methods=['GET'])
@login_required
def listar_bancos():
    try:
 
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ID_Entidad, Rut, Nombre, FonoMovil, Email
            FROM Entidad
            WHERE TipoEntidad = 'Banco'
            ORDER BY Nombre ASC
            """)
        bancos = cursor.fetchall()

    except Exception as e:
        flash(f"Error al obtener los datos de los bancos: {e}", "error")
        bancos = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/bancos/bancos.html', bancos=bancos)

@bancos_bp.route('/delete_banco/<int:id_banco>', methods=['POST'])
@login_required
def delete_banco(id_banco):
    print(f"Entrando a delete_banco con ID: {id_banco}")
    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Entidad WHERE ID_Entidad = %s AND TipoEntidad = 'Banco'", (id_banco,))
        banco = cursor.fetchone()
        if not banco:
            flash("El banco no existe o no es del tipo 'Banco'.", "error")
            return redirect(url_for('listar_bancos'))

        cursor.execute("DELETE FROM Entidad WHERE ID_Entidad = %s AND TipoEntidad = 'Banco'", (id_banco,))
        conn.commit()

        print(f"Banco eliminado: {id_banco}")
        flash("Banco eliminado exitosamente.", "success")

    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar: {e}")
        flash(f"Error al eliminar el banco: {e}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('bancos_bp.listar_bancos'))

@bancos_bp.route('/bancos/add', methods=['GET', 'POST'])
@login_required
def add_banco():
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
                VALUES (%s, %s, %s, %s, %s, 'Banco')
            """, (rut, nombre, email, fono_fijo, fono_movil))
            conn.commit()

            flash("Banco agregado exitosamente.", "success")
            return redirect(url_for('bancos_bp.listar_bancos'))
        except Exception as e:
            conn.rollback()
            flash(f"Error al agregar el banco: {e}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('configuracion/bancos/add_bancos.html')

@bancos_bp.route('/bancos/edit/<int:id_banco>', methods=['GET', 'POST'])
@login_required
def edit_banco(id_banco):
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
                WHERE ID_Entidad = %s AND TipoEntidad = 'Banco'
            """, (rut, nombre, email, fono_fijo, fono_movil, id_banco))
            conn.commit()

            flash("Banco actualizado exitosamente.", "success")
            return redirect(url_for('bancos_bp.listar_bancos'))

        cursor.execute("""
            SELECT Rut, Nombre, Email, FonoFijo, FonoMovil
            FROM Entidad
            WHERE ID_Entidad = %s AND TipoEntidad = 'Banco'
        """, (id_banco,))
        banco = cursor.fetchone()

        if not banco:
            flash("Banco no encontrado.", "error")
            return redirect(url_for('bancos_bp.listar_bancos'))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error al procesar la solicitud: {e}", "error")
        return redirect(url_for('bancos_bp.listar_bancos'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/bancos/edit_banco.html', banco=banco, id_banco=id_banco)