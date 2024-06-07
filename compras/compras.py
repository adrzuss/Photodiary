from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from api.comunes import getTipoDoc
from db.db import get_db;
from datetime import date

compras_bp = Blueprint('compras_bp', __name__, template_folder='templates/compras', static_url_path='static/compras')

@compras_bp.route('/abmProveedores')
def abmProveedores():
    error, tiposDoc = getTipoDoc
    if error != None:
        flash("Error obteniendo tipos de documentos", "error")    
    print(tiposDoc)
    return render_template('abm-proveedores.html', tiposDoc=tiposDoc)

@compras_bp.route('/abmOrdCompras')
def abmOrdCompras():
    return render_template('abm-ordcompras.html')


@compras_bp.route('/ordenCompras')
def ordenCompras():
    if ('user' in session):
        return render_template('orden-compras.html')
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

@compras_bp.route('/get_proveedor/<idProveedor>')
def get_proveedor(idProveedor):
    con, cur = get_db()
    cur.execute("select P.NOMBRE, P.NFANTASIA FROM proveedor P WHERE P.PROVEE = ?", (idProveedor,))
    result = cur.fetchone()
    #con.commit()
    if result:
        return jsonify({'nombreProveedor': result[0], 'nFantasia': result[1]})
    else:
        return jsonify({'error': 'Artículo no encontrado'})

@compras_bp.route('/guardar_ordencompras', methods=['POST'])
def guardar_ordencompras():
    try:
        data = request.json
        idProveedor = data.get('cliente_id')
        items = data.get('items')
        
        # Aquí puedes procesar y guardar los datos en la base de datos
        
        # Por ejemplo, puedes imprimir los datos recibidos para verificar que se están recibiendo correctamente
        
        # Aquí debes retornar una respuesta JSON indicando el resultado del proceso
        # Por ejemplo, puedes retornar un objeto JSON con un mensaje de éxito
        flash("Orden de compras grabada")      
        return jsonify({'success': True, 'message': 'Orden de compras grabada con éxito'})
        #return redirect(url_for('compras_bp.abmOrdCompras'))
    except Exception as e:
        flash("Error grabando orden de compras", "error")     
        return jsonify({'success': False, 'message': 'Error al guardar la orden de compras'}) 
        
    #return redirect(url_for('compras_bp.abmOrdCompras'))
    #return jsonify({'mensaje': 'Factura guardada con éxito'})
        
@compras_bp.route('/get_articulos_ordcompras', methods=['GET'])
def getArticulosOrdcompras():  
    if request.method == 'GET':
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
    con, cur = get_db()
    cur.execute("select first 50 A.CODIGO, A.NOMBRE, P.PREC1, sum(I.CANT) TOTVENDIDO "
                "from articulos A "
                "join precios P "
                "  on P.CODIGO = A.CODIGO and P.IDPRECIO = 0 "
                "join factufc I "
                "  on I.CODIGO = A.CODIGO "
                "join factulb F "
                "  on F.IDLIBRO = I.IDLIBRO "
                "where "
                "F.FECHA between ? and ? "
                "group by A.CODIGO, A.NOMBRE, P.PREC1", (fecha_desde, fecha_hasta))
    result = cur.fetchall()
    data = []
    registros = 0
    for row in result:
        registros += 1
        row_dict = cur.to_dict(row)
        data.append(row_dict)
    con.commit()
    if data:
        #response = jsonify(data)
        #response.headers.add('Content-Type', 'application/json')
        #return response 
        return render_template('orden-compras.html', datosArt=data)
        #jsonify({'nombreProveedor': result[0], 'nFantasia': result[1]})
    else:
        return jsonify({'error': 'No hay datos'})      
    
@compras_bp.route('/obtener_stocks/<codigo>', methods=['GET'])
def obtenerStocks(codigo):
    error = None
    con, cur = get_db()
    cur.execute("select S.NOMBRE, ST.ENTRADA, ST.VENTA, ST.MOVREM, ST.VENTA, ST.RESERVA "
                "from stock ST "
                "join SUCURSAL S "
                "  on S.SUCURSAL = ST.DEPOSITO "
                "where "
                "  ST.CODIGO = ? and "
                "  S.INHA = 0", (codigo,))
    result = cur.fetchall()
    data = []
    registros = 0
    for row in result:
        registros += 1
        row_dict = cur.to_dict(row)
        data.append(row_dict)
    con.commit()
    if data:
        response = jsonify(data)
        response.headers.add('Content-Type', 'application/json')
        return response #jsonify({'nombreProveedor': result[0], 'nFantasia': result[1]})
    else:
        return jsonify({'error': 'No hay datos'})      
    
@compras_bp.route('/grabar_orden_compras', methods=['POST'])
def grabar_orden_compras():
    if request.method == 'POST':
        articulos = request.json
    print(articulos)
    articulos = []
    #return render_template('orden-compras.html', datosArt=articulos)
    flash('Orden de compras grabada')
    return jsonify({'message': 'Datos recibidos correctamente'})
