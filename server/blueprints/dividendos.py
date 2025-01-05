from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required 
from database import get_db_connection

dividendos_bp = Blueprint('dividendos_bp', __name__)

@dividendos_bp.route('/dividendos/<int:id_accion>', methods=['GET'])
@login_required
def historial_dividendos(id_accion):
    sort_by = request.args.get('sort_by', 'FechaCierre')  
    order = request.args.get('order', 'asc')  

    valid_columns = ['ID_Dividendo', 'Nombre', 'FechaCierre', 'FechaPago', 'ValorPorAccion', 'Moneda', 'ValorTotal', 'Rentabilidad']
    if sort_by not in valid_columns:
        sort_by = 'FechaCierre'  
    if order not in ['asc', 'desc']:
        order = 'asc'

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT ID_Dividendo, Nombre, FechaCierre, FechaPago, ValorPorAccion, Moneda, ValorTotal, Rentabilidad
        FROM Dividendos
        WHERE ID_Accion = %s
        ORDER BY {sort_by} {order}
    """
    cursor.execute(query, (id_accion,))
    dividendos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'acciones/dividendos/dividendos.html',
        dividendos=dividendos,
        id_accion=id_accion,
        sort_by=sort_by,
        order=order,
    )

from decimal import Decimal

@dividendos_bp.route('/add_dividendo', methods=['POST'])
@login_required
def add_dividendo():
    nombre = request.form['nombre']
    fecha_cierre = request.form['fecha_cierre']
    fecha_pago = request.form['fecha_pago']
    valor_por_accion = Decimal(request.form['valor_por_accion'])  
    moneda = request.form['moneda']
    id_accion = request.form['id_accion']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT Cantidad FROM Accion WHERE ID_Accion = %s", (id_accion,))
    cantidad_acciones = cursor.fetchone()
    if not cantidad_acciones:
        cantidad_acciones = Decimal(0)
    else:
        cantidad_acciones = Decimal(cantidad_acciones[0])

    valor_total = valor_por_accion * cantidad_acciones

    cursor.execute("""
        SELECT SUM(Cantidad * PrecioUnitario + COALESCE(Comision, 0)) / SUM(Cantidad)
        FROM Facturas
        WHERE Tipo = 'Compra' AND NombreActivo = (
            SELECT Nombre FROM Accion WHERE ID_Accion = %s
        )
    """, (id_accion,))
    precio_promedio = cursor.fetchone()[0]

    if precio_promedio:
        precio_promedio = Decimal(precio_promedio)
        rentabilidad = (valor_por_accion / precio_promedio) * 100
    else:
        rentabilidad = Decimal(0)  

    cursor.execute("""
        INSERT INTO Dividendos (ID_Accion, Nombre, FechaCierre, FechaPago, ValorPorAccion, Moneda, ValorTotal, Rentabilidad)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (id_accion, nombre, fecha_cierre, fecha_pago, float(valor_por_accion), moneda, float(valor_total), float(rentabilidad)))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Dividendo agregado exitosamente.", "success")
    return redirect(url_for('acciones/dividendos/historial_dividendos', id_accion=id_accion))

@dividendos_bp.route('/dividendos/add/<int:id_accion>', methods=['GET'])
@login_required
def formulario_add_dividendo(id_accion):
    """
    Muestra el formulario para agregar un dividendo asociado a una acción específica.
    """
    return render_template('acciones/dividendos/add_dividendo.html', id_accion=id_accion)

@dividendos_bp.route('/delete_dividendo/<int:id_dividendo>', methods=['POST'])
@login_required
def delete_dividendo(id_dividendo):
    id_accion = request.form.get('id_accion') 

    if not id_accion:
        flash("No se proporcionó un ID de acción válido.", "error")
        return redirect(url_for('acciones'))  

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Dividendos WHERE ID_Dividendo = %s", (id_dividendo,))
        conn.commit()

        flash("Dividendo eliminado exitosamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el dividendo: {e}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('acciones/dividendos/historial_dividendos', id_accion=id_accion))

@dividendos_bp.route('/edit_dividendo/<int:id_dividendo>', methods=['GET', 'POST'])
@login_required
def edit_dividendo(id_dividendo):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            print("POST recibido")  
            nombre = request.form['nombre']
            fecha_cierre = request.form['fecha_cierre']
            fecha_pago = request.form['fecha_pago']
            valor_por_accion = float(request.form['valor_por_accion'])
            moneda = request.form['moneda']
            id_accion = request.form.get('id_accion')

            if not id_accion:
                flash("Error: No se pudo identificar la acción asociada.", "error")
                return redirect(url_for('acciones'))

            print(f"Datos procesados: nombre={nombre}, fecha_cierre={fecha_cierre}, fecha_pago={fecha_pago}, valor_por_accion={valor_por_accion}, moneda={moneda}, id_accion={id_accion}")  

            cursor.execute(
                "SELECT Cantidad FROM Accion WHERE ID_Accion = %s",
                (id_accion,)
            )
            cantidad_acciones = cursor.fetchone()
            cantidad_acciones = float(cantidad_acciones[0]) if cantidad_acciones else 0.0  
            valor_total = valor_por_accion * cantidad_acciones  

            print(f"Cantidad acciones: {cantidad_acciones}, Valor total calculado: {valor_total}") 

            cursor.execute("""
                UPDATE Dividendos
                SET Nombre = %s, FechaCierre = %s, FechaPago = %s, ValorPorAccion = %s, Moneda = %s, ValorTotal = %s
                WHERE ID_Dividendo = %s
            """, (nombre, fecha_cierre, fecha_pago, valor_por_accion, moneda, valor_total, id_dividendo))
            print(f"Dividendo actualizado: {cursor.rowcount} filas afectadas.") 

            conn.commit()
            print(f"Redirigiendo a historial_dividendos con id_accion: {id_accion}") 
            flash("Dividendo actualizado exitosamente.", "success")
            return redirect(url_for('historial_dividendos', id_accion=id_accion))

        cursor.execute(
            "SELECT Nombre, FechaCierre, FechaPago, ValorPorAccion, Moneda FROM Dividendos WHERE ID_Dividendo = %s",
            (id_dividendo,)
        )
        dividendo = cursor.fetchone()
        cursor.execute("SELECT ID_Accion FROM Dividendos WHERE ID_Dividendo = %s", (id_dividendo,))
        id_accion = cursor.fetchone()[0]

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error capturado: {e}")  
        flash(f"Error al procesar la solicitud: {e}", "error")
        return redirect(url_for('acciones'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('acciones/dividendos/edit_dividendo.html', dividendo=dividendo, id_dividendo=id_dividendo, id_accion=id_accion)