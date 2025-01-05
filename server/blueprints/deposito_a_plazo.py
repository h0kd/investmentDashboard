from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from database import get_db_connection
from werkzeug.utils import secure_filename
from helpers.utils import allowed_file
from datetime import datetime
from flask import current_app
import os

deposito_a_plazo_bp = Blueprint('deposito_a_plazo', __name__)

@deposito_a_plazo_bp.route('/deposito_a_plazo', methods=['GET'])
@login_required
def deposito_a_plazo():
    sort_by = request.args.get('sort_by', 'ID_Deposito')  
    order = request.args.get('order', 'asc')  

    valid_columns = [
        'ID_Deposito', 'Empresa', 'Banco', 'FechaEmision', 'FechaVencimiento', 'Moneda',
        'MontoInicial', 'MontoFinal', 'TipoDeposito', 'CapitalRenovacion', 'PlazoRenovacion'
    ]
    if sort_by not in valid_columns:
        sort_by = 'ID_Deposito' 

    if order not in ['asc', 'desc']:
        order = 'asc'

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT 
            d.ID_Deposito,
            ec.Nombre AS Empresa,
            b.Nombre AS Banco,
            d.FechaEmision,
            d.FechaVencimiento,
            d.Moneda,
            d.MontoInicial,
            d.MontoFinal,
            d.TipoDeposito,
            d.CapitalRenovacion,
            d.PlazoRenovacion,
            d.Comprobante
        FROM DepositoAPlazo d
        JOIN EntidadComercial ec ON d.ID_EntidadComercial = ec.ID_Entidad
        JOIN Entidad b ON d.ID_Banco = b.ID_Entidad
        ORDER BY {sort_by} {order}
    """
    cursor.execute(query)
    depositos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('depositos/deposito_a_plazo.html', depositos=depositos, sort_by=sort_by, order=order)

@deposito_a_plazo_bp.route('/add_deposito', methods=['GET', 'POST'])
@login_required
def add_deposito():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            id_deposito = request.form['numero_deposito']
            tipo = request.form['tipo']
            monto = float(request.form['monto'])
            fecha_emision = request.form['fecha_emision']
            tasa_interes = float(request.form['tasa_interes'])
            fecha_vencimiento = request.form['fecha_vencimiento']
            moneda = request.form.get('moneda', 'CLP')
            interes_ganado = float(request.form.get('interes_ganado', 0))
            id_banco = request.form['nombre_banco']
            id_beneficiario = request.form['id_beneficiario']

            if tipo == "Renovable":
                capital_renovacion = float(request.form.get('capital_renovacion', 0))
                fecha_emision_renovacion = request.form.get('fecha_emision_renovacion')
                tasa_interes_renovacion = float(request.form.get('tasa_interes_renovacion', 0))
                plazo_renovacion = int(request.form.get('plazo_renovacion', 0))
                tasa_periodo = float(request.form.get('tasa_periodo', 0))
                fecha_vencimiento_renovacion = request.form.get('fecha_vencimiento_renovacion')
                total_pagar_renovacion = float(request.form.get('total_pagar_renovacion', 0))
                reajuste_ganado = float(request.form.get('reajuste_ganado', 0))
            else:
                capital_renovacion = None
                fecha_emision_renovacion = None
                tasa_interes_renovacion = None
                plazo_renovacion = None
                tasa_periodo = None
                fecha_vencimiento_renovacion = None
                total_pagar_renovacion = None
                reajuste_ganado = None

            comprobante = None
            if 'comprobante' in request.files and request.files['comprobante'].filename != '':
                file = request.files['comprobante']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    relative_path = os.path.join('static', 'uploads', filename)
                    comprobante_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    os.makedirs(os.path.dirname(comprobante_path), exist_ok=True)
                    file.save(comprobante_path)
                    comprobante = relative_path

            cursor.execute("""
                INSERT INTO DepositoAPlazo (
                    ID_Deposito, ID_Banco, ID_EntidadComercial, FechaEmision, FechaVencimiento, Moneda, MontoInicial, TipoDeposito, 
                    InteresGanado, TasaInteres, CapitalRenovacion, FechaEmisionRenovacion, TasaInteresRenovacion, 
                    PlazoRenovacion, TasaPeriodo, FechaVencimientoRenovacion, TotalPagarRenovacion, ReajusteGanado, Comprobante
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                id_deposito, id_banco, id_beneficiario, fecha_emision, fecha_vencimiento, moneda, monto, tipo,
                interes_ganado, tasa_interes, 
                capital_renovacion, fecha_emision_renovacion, tasa_interes_renovacion,
                plazo_renovacion, tasa_periodo, fecha_vencimiento_renovacion, total_pagar_renovacion, reajuste_ganado, 
                comprobante
            ))

            conn.commit()
            flash("Depósito guardado exitosamente.", "success")

        except Exception as e:
            conn.rollback()
            flash(f"Error al guardar el depósito: {e}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('deposito_a_plazo.deposito_a_plazo'))

    try:
        cursor.execute("SELECT ID_Entidad, Nombre FROM Entidad WHERE TipoEntidad = 'Banco'")
        bancos = cursor.fetchall()
    except Exception as e:
        bancos = []
        flash(f"Error al cargar bancos: {e}", "error")

    cursor.close()
    conn.close()

    return render_template('depositos/add_deposito.html', bancos=bancos)

@deposito_a_plazo_bp.route('/edit_deposito/<int:id_deposito>', methods=['GET', 'POST'])
@login_required
def edit_deposito(id_deposito):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            original_id_deposito = request.form.get('original_id_deposito')
            new_id_deposito = request.form.get('id_deposito')
            id_banco = request.form.get('nombre_banco')
            id_beneficiario = request.form.get('id_beneficiario')
            tipo_beneficiario = request.form.get('tipo_beneficiario')
            moneda = request.form.get('moneda', '').strip()
            monto = float(request.form.get('monto', '0').strip() or 0)
            fecha_emision = request.form.get('fecha_emision')
            tasa_interes = float(request.form.get('tasa_interes', '0').strip() or 0)
            fecha_vencimiento = request.form.get('fecha_vencimiento')
            interes_ganado = float(request.form.get('interes_ganado', '0').strip() or 0)
            reajuste_ganado = float(request.form.get('reajuste_ganado', '0').strip() or 0)

            tipo = request.form.get('tipo')
            if tipo == "Renovable":
                capital_renovacion = float(request.form.get('capital_renovacion', '0').strip() or 0)
                fecha_emision_renovacion = request.form.get('fecha_emision_renovacion')
                tasa_interes_renovacion = float(request.form.get('tasa_interes_renovacion', '0').strip() or 0)
                plazo_renovacion = int(request.form.get('plazo_renovacion', '0').strip() or 0)
                tasa_periodo = float(request.form.get('tasa_periodo', '0').strip() or 0)
                fecha_vencimiento_renovacion = request.form.get('fecha_vencimiento_renovacion')
                total_pagar_renovacion = float(request.form.get('total_pagar_renovacion', '0').strip() or 0)
            else:
                capital_renovacion = None
                fecha_emision_renovacion = None
                tasa_interes_renovacion = None
                plazo_renovacion = None
                tasa_periodo = None
                fecha_vencimiento_renovacion = None
                total_pagar_renovacion = None

            comprobante = None
            if 'comprobante' in request.files:
                file = request.files['comprobante']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    comprobante = os.path.join('static/uploads', filename)
                    file.save(comprobante)
                else:
                    cursor.execute("SELECT Comprobante FROM DepositoAPlazo WHERE ID_Deposito = %s", (id_deposito,))
                    comprobante = cursor.fetchone()[0]

            print("Datos preparados para el UPDATE:")
            print("ID original:", original_id_deposito)
            print("Nuevo ID:", new_id_deposito)
            print({
                "id_banco": id_banco,
                "id_beneficiario": id_beneficiario,
                "fecha_emision": fecha_emision,
                "fecha_vencimiento": fecha_vencimiento,
                "moneda": moneda,
                "monto": monto,
                "tipo": tipo,
                "interes_ganado": interes_ganado,
                "tasa_interes": tasa_interes,
                "reajuste_ganado": reajuste_ganado,
                "capital_renovacion": capital_renovacion,
                "fecha_emision_renovacion": fecha_emision_renovacion,
                "tasa_interes_renovacion": tasa_interes_renovacion,
                "plazo_renovacion": plazo_renovacion,
                "tasa_periodo": tasa_periodo,
                "fecha_vencimiento_renovacion": fecha_vencimiento_renovacion,
                "total_pagar_renovacion": total_pagar_renovacion,
                "comprobante": comprobante,
                "id_deposito": id_deposito
            })

            cursor.execute("""
                UPDATE DepositoAPlazo
                SET ID_Deposito = %s, ID_Banco = %s, ID_EntidadComercial = %s, FechaEmision = %s, FechaVencimiento = %s,
                    Moneda = %s, MontoInicial = %s, TipoDeposito = %s, InteresGanado = %s, TasaInteres = %s,
                    ReajusteGanado = %s, CapitalRenovacion = %s, FechaEmisionRenovacion = %s, TasaInteresRenovacion = %s,
                    PlazoRenovacion = %s, TasaPeriodo = %s, FechaVencimientoRenovacion = %s, TotalPagarRenovacion = %s,
                    Comprobante = COALESCE(%s, Comprobante)
                WHERE ID_Deposito = %s
            """, (
                new_id_deposito, id_banco, id_beneficiario, fecha_emision, fecha_vencimiento, moneda, monto, tipo,
                interes_ganado, tasa_interes, reajuste_ganado, capital_renovacion, fecha_emision_renovacion,
                tasa_interes_renovacion, plazo_renovacion, tasa_periodo, fecha_vencimiento_renovacion,
                total_pagar_renovacion, comprobante, original_id_deposito
            ))
            print("Filas afectadas por el UPDATE:", cursor.rowcount)
            if cursor.rowcount == 0:
                flash("No se realizaron cambios.", "info")
            else:
                conn.commit()
                flash("Depósito actualizado exitosamente.", "success")
        except Exception as e:
            print("Error al realizar el UPDATE:", str(e))
            conn.rollback()
            flash(f"Error al actualizar el depósito: {e}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('deposito_a_plazo.deposito_a_plazo'))

    try:
        cursor.execute("""
            SELECT 
                d.ID_Deposito, d.ID_Banco, d.ID_EntidadComercial, d.FechaEmision, d.FechaVencimiento, 
                d.Moneda, d.MontoInicial, d.TipoDeposito, d.InteresGanado, d.TasaInteres, d.ReajusteGanado, 
                d.CapitalRenovacion, d.FechaEmisionRenovacion, d.TasaInteresRenovacion, d.PlazoRenovacion, 
                d.TasaPeriodo, d.FechaVencimientoRenovacion, d.TotalPagarRenovacion, d.Comprobante
            FROM DepositoAPlazo d
            WHERE d.ID_Deposito = %s
        """, (id_deposito,))
        deposito = cursor.fetchone()

        cursor.execute("SELECT ID_Entidad, Nombre FROM Entidad WHERE TipoEntidad = 'Banco'")
        bancos = cursor.fetchall()

        cursor.execute("SELECT ID_Entidad, Nombre FROM EntidadComercial WHERE TipoEntidad IN ('Empresa', 'Cliente')")
        beneficiarios = cursor.fetchall()
    except Exception as e:
        flash(f"Error al cargar datos: {e}", "error")
        deposito = None
        bancos = []
        beneficiarios = []
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'depositos/edit_deposito.html',
        deposito=deposito,
        bancos=bancos,
        beneficiarios=beneficiarios
    )

@deposito_a_plazo_bp.route('/delete_deposito/<int:id_deposito>', methods=['POST'])
@login_required
def delete_deposito(id_deposito):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM DepositoAPlazo WHERE ID_Deposito = %s", (id_deposito,))
        conn.commit()
        flash('Depósito eliminado exitosamente.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar el depósito: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('deposito_a_plazo.deposito_a_plazo'))

@deposito_a_plazo_bp.route('/beneficiarios_por_tipo/<tipo>', methods=['GET'])
@login_required
def beneficiarios_por_tipo(tipo):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if tipo == 'empresa':
            cursor.execute("SELECT ID_Entidad, Nombre, Rut FROM EntidadComercial WHERE TipoEntidad = 'Empresa'")
        elif tipo == 'cliente':
            cursor.execute("SELECT ID_Entidad, Nombre, Rut FROM EntidadComercial WHERE TipoEntidad = 'Cliente'")
        else:
            return jsonify([]), 400  

        beneficiarios = [{'id': row[0], 'nombre': row[1], 'rut': row[2]} for row in cursor.fetchall()]
        print(f"Beneficiarios ({tipo}): {beneficiarios}") 
        return jsonify(beneficiarios)

    except Exception as e:
        print(f"Error al obtener beneficiarios: {e}")
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()

@deposito_a_plazo_bp.route('/agregar_beneficiario', methods=['POST'])
@login_required
def agregar_beneficiario():
    try:
        data = request.json
        rut = data['rut']
        nombre = data['nombre']
        tipo_beneficiario = data['tipo_beneficiario']

        conn = get_db_connection()
        cursor = conn.cursor()

        if tipo_beneficiario in ["Empresa", "Cliente"]:
            cursor.execute("""
                INSERT INTO EntidadComercial (Rut, Nombre, TipoEntidad) 
                VALUES (%s, %s, %s) RETURNING ID_Entidad
            """, (rut, nombre, tipo_beneficiario))
        else:
            return jsonify({"success": False, "error": "Tipo de beneficiario inválido"}), 400

        beneficiario_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({"success": True, "id": beneficiario_id})
    except Exception as e:
        print(f"Error al agregar beneficiario: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@deposito_a_plazo_bp.route('/agregar_banco', methods=['POST'])
@login_required
def agregar_banco():
    try:
        data = request.json
        rut = data['rut']
        nombre = data['nombre']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Entidad (Rut, Nombre, TipoEntidad) 
            VALUES (%s, %s, 'Banco') RETURNING ID_Entidad
        """, (rut, nombre))
        banco_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({"success": True, "id": banco_id})
    except Exception as e:
        print(f"Error al agregar banco: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

