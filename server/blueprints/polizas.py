from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import get_db_connection
from werkzeug.utils import secure_filename
from helpers.utils import allowed_file
from flask import current_app
import os

polizas_bp = Blueprint('polizas_bp', __name__)


@polizas_bp.route('/polizas', methods=['GET'])
@login_required
def listar_polizas():
    conn = get_db_connection()
    cursor = conn.cursor()

    sort_by = request.args.get('sort_by', 'Numero')  
    order = request.args.get('order', 'asc') 

    valid_columns = ['Numero', 'TipoAsegurado', 'FechaInicio', 'FechaTermino', 'Monto']
    if sort_by not in valid_columns:
        sort_by = 'Numero'
    if order not in ['asc', 'desc']:
        order = 'asc'

    query = f"SELECT * FROM Polizas ORDER BY {sort_by} {order}"
    cursor.execute(query)
    polizas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('polizas/polizas.html', polizas=polizas, sort_by=sort_by, order=order)

@polizas_bp.route('/add_poliza', methods=['GET', 'POST'])
@login_required
def agregar_poliza():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            numero = request.form['numero']  
            tipo_asegurado = request.form['tipo_asegurado']
            fecha_inicio = request.form['fecha_inicio']
            fecha_termino = request.form['fecha_termino']
            monto = float(request.form['monto'])

            adjunto_poliza = None
            if 'adjunto_poliza' in request.files:
                file = request.files['adjunto_poliza']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    adjunto_poliza = os.path.join(current_app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
                    file.save(adjunto_poliza)

            cursor.execute("SELECT 1 FROM Polizas WHERE Numero = %s", (numero,))
            if cursor.fetchone():
                flash("El número de póliza ya existe. Por favor, ingrese otro.", "error")
                return redirect(url_for('agregar_poliza'))
            
            if fecha_inicio > fecha_termino:
                flash("La fecha de inicio no puede ser posterior a la fecha de término.", "error")
                return redirect(url_for('agregar_poliza'))

            cursor.execute("""
                INSERT INTO Polizas (Numero, TipoAsegurado, FechaInicio, FechaTermino, Monto, AdjuntoPoliza)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (numero, tipo_asegurado, fecha_inicio, fecha_termino, monto, adjunto_poliza))

            conn.commit()
            flash('Póliza agregada exitosamente.', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error al agregar la póliza: {e}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('listar_polizas'))

    return render_template('polizas/add_polizas.html')

@polizas_bp.route('/edit_poliza/<int:numero>', methods=['GET', 'POST'])
@login_required
def editar_poliza(numero):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            tipo_asegurado = request.form['tipo_asegurado']
            fecha_inicio = request.form['fecha_inicio']
            fecha_termino = request.form['fecha_termino']
            monto = float(request.form['monto'])

            adjunto_poliza = None
            if 'adjunto_poliza' in request.files:
                file = request.files['adjunto_poliza']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    adjunto_poliza = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(adjunto_poliza)

            cursor.execute("""
                UPDATE Polizas
                SET TipoAsegurado = %s, FechaInicio = %s, FechaTermino = %s, Monto = %s, AdjuntoPoliza = %s
                WHERE Numero = %s
            """, (tipo_asegurado, fecha_inicio, fecha_termino, monto, adjunto_poliza, numero))

            conn.commit()
            flash('Póliza actualizada exitosamente.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error al actualizar la póliza: {e}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('listar_polizas'))

    cursor.execute("SELECT * FROM Polizas WHERE Numero = %s", (numero,))
    poliza = cursor.fetchone()
    cursor.close()
    conn.close()

    if not poliza:
        flash('La póliza no existe.', 'error')
        return redirect(url_for('listar_polizas'))

    return render_template('polizas/edit_polizas.html', poliza=poliza)

@polizas_bp.route('/delete_poliza/<int:numero>', methods=['POST'])
@login_required
def eliminar_poliza(numero):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Polizas WHERE Numero = %s", (numero,))
        conn.commit()
        flash('Póliza eliminada exitosamente.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar la póliza: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('listar_polizas'))