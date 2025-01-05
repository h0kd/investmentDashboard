from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required 
from database import get_db_connection

empresas_bp = Blueprint('empresas_bp', __name__)


@empresas_bp.route('/empresas', methods=['GET'])
@login_required
def listar_empresas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ID_Entidad, Rut, Nombre, FonoMovil, Email
            FROM EntidadComercial
            WHERE TipoEntidad = 'Empresa'
            ORDER BY Nombre ASC
            """)
        empresas = cursor.fetchall()

    except Exception as e:
        flash(f"Error al obtener los datos de las empresas: {e}", "error")
        empresas = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/empresas/empresas.html', empresas=empresas)

@empresas_bp.route('/empresas/add', methods=['GET', 'POST'])
@login_required
def add_empresa():
    if request.method == 'POST':
        rut = request.form['rut']
        nombre = request.form['nombre'].upper()
        fono_fijo = request.form['fono_fijo']
        fono_movil = request.form['fono_movil']
        email = request.form['email']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO EntidadComercial (Rut, Nombre, FonoFijo, FonoMovil, Email, TipoEntidad)
                VALUES (%s, %s, %s, %s, %s, 'Empresa')
            """, (rut, nombre, fono_fijo, fono_movil, email))
            conn.commit()

            flash("Empresa agregada exitosamente.", "success")
            return redirect(url_for('empresas_bp.listar_empresas'))
        except Exception as e:
            conn.rollback()
            flash(f"Error al agregar la empresa: {e}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('configuracion/empresas/add_empresas.html')

@empresas_bp.route('/delete_empresa/<int:id_empresa>', methods=['POST'])
@login_required
def delete_empresa(id_empresa):
    print(f"Entrando a delete_empresa con ID: {id_empresa}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM EntidadComercial WHERE ID_Entidad = %s AND TipoEntidad = 'Empresa'", (id_empresa,))
        empresa = cursor.fetchone()
        if not empresa:
            flash("La empresa no existe o no es del tipo 'Banco'.", "error")
            return redirect(url_for('listar_empresas'))

        cursor.execute("DELETE FROM EntidadComercial WHERE ID_Entidad = %s AND TipoEntidad = 'Empresa'", (id_empresa,))
        conn.commit()

        print(f"Empresa eliminada: {id_empresa}")
        flash("Empresa eliminada exitosamente.", "success")
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar: {e}")
        flash(f"Error al eliminar la empresa: {e}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('empresas_bp.listar_empresas'))

@empresas_bp.route('/empresas/edit/<int:id_empresa>', methods=['GET', 'POST'])
@login_required
def edit_empresa(id_empresa):
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
                UPDATE EntidadComercial
                SET Rut = %s, Nombre = %s, Email = %s, FonoFijo = %s, FonoMovil = %s
                WHERE ID_Entidad = %s AND TipoEntidad = 'Empresa'
            """, (rut, nombre, email, fono_fijo, fono_movil, id_empresa))
            conn.commit()

            flash("Empresa actualizado exitosamente.", "success")
            return redirect(url_for('empresas_bp.listar_empresas'))

        cursor.execute("""
            SELECT Rut, Nombre, Email, FonoFijo, FonoMovil
            FROM EntidadComercial
            WHERE ID_Entidad = %s AND TipoEntidad = 'Empresa'
        """, (id_empresa,))
        empresa = cursor.fetchone()

        if not empresa:
            flash("Empresa no encontrada.", "error")
            return redirect(url_for('empresas_bp.listar_empresas'))

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"Error al procesar la solicitud: {e}", "error")
        return redirect(url_for('empresas_bp.listar_empresas'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('configuracion/empresas/edit_empresa.html', empresa=empresa, id_empresa=id_empresa)