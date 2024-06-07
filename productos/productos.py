from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from api.api_productos import getProductos, get_datos_producto, actualizarProducto, agregarProducto, getGrupos, get_datos_grupo,\
                              actualizarGrupo, agregarGrupo, getMarcas, get_datos_marca, actualizarMarca, agregarMarca, get_datos_producto_codigo
from api.api_productos import getProductoByDetalle, getProductoById, getProductosByCodigo
from db.db import get_db;
from datetime import date

productos_bp = Blueprint('productos_bp', __name__, template_folder='templates/productos')


@productos_bp.route('/abmProductos', methods=['GET', 'POST'])
@productos_bp.route('/abmProductos/<idProducto>', methods=['GET', 'POST'])
def abmProductos(idProducto = None):
    if 'user' in session:
        producto = []
        grupos = []
        marcas = []
        grupos, error = getGrupos()
        marcas, error = getMarcas()
        if request.method == 'GET':
            #idProducto = request.args.get('idProducto')
            if idProducto != None:
                producto, error = get_datos_producto(idProducto)
            if idProducto == '-1':
                producto = []    
        elif request.method == 'POST':
            idProducto = request.form['idProducto']
            codigo = request.form['codigo']
            grupo = request.form['grupo']
            marca = request.form['marca']
            detalle = request.form['detalle']
            costo = request.form['costo']
            precio = request.form['precio']
            if request.form.get('enDolares') != None:
                enDolares = 'S'
            else:
                enDolares = 'N'    
            precioDolar = request.form['precioDolar']
            if request.form.get('esServicio') != None:
                esServico = 'S'
            else:
                esServico = 'N'    
            if idProducto == '':
                producto, error = agregarProducto(codigo, grupo, marca, detalle, costo, precio, enDolares, precioDolar, esServico)    
            else:
                producto, error = actualizarProducto(idProducto, codigo, grupo, marca, detalle, costo, precio, enDolares, precioDolar, esServico)
            if error is None:
                flash('Datos de producto grabado')  
            else:
                flash('Error grabando producto', 'error')    
        productos, error = getProductos()        
        return render_template('abm-productos.html', productos=productos, producto=producto, grupos=grupos, marcas=marcas)
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))    


@productos_bp.route('/getProducto/<idProducto>', methods=['GET', 'POST'])
def getCliente(idProducto):
    producto, error = getProductoById(idProducto)
    if error == None:
        datos = jsonify({'producto': producto})
        return datos
    else:
        return jsonify({'error': 'No hay datos'})


@productos_bp.route('/get_producto/<codigo>')
def get_producto(codigo):
    error = None
    producto, error = get_datos_producto(codigo)
    if producto:
        return jsonify({'descripcion': producto[4], 'precio': float(producto[6])})
    else:
        return jsonify({'error': 'Artículo no encontrado'})

@productos_bp.route('/get_producto_codigo/<codigo>')
def get_producto_codigo(codigo):
    error = None
    producto, error = get_datos_producto_codigo(codigo)
    if producto:
        return jsonify({'id': producto[0], 'codigo': producto[1], 'descripcion': producto[4], 'precio': float(producto[6])})
    else:
        return jsonify({'error': 'Artículo no encontrado'})

@productos_bp.route('/buscarProductos/<buscarPor>/<valorBusqueda>', methods=['GET', 'POST'])
def buscarProductos(buscarPor, valorBusqueda):
    if buscarPor == 'idProducto':
        producto, error = getProductoById(valorBusqueda)
    elif buscarPor == 'codigo':
        producto, error = getProductosByCodigo(valorBusqueda)        
    elif buscarPor == 'detalle':
        producto, error = getProductoByDetalle(valorBusqueda)
    if error == None:
        if producto == {}:
            flash('No hay datos de productos para el valor ingresado')
            return jsonify({'producto': producto})
        else:    
            return jsonify({'producto': producto})
    else:
        return 'No hay datos'

@productos_bp.route('/calcular_total', methods=['POST'])
def calcular_total():
    data = request.get_json()
    items = data['items']

    total_factura = 0

    for item in items:
        codigo = item['codigo']
        cantidad = item['cantidad']

        # Llamada a la función para obtener datos del artículo desde la base de datos
        producto_data = get_datos_producto(codigo)
        if producto_data:
            descripcion = producto_data['descripcion']
            precio = producto_data['precio']

            total_item = cantidad * precio
            total_factura += total_item
        else:
            return jsonify({'error': 'Artículo no encontrado'})

    return jsonify({'total_factura': total_factura})

@productos_bp.route('/datosproducto', methods=['GET'])
def datosproducto():
    idproducto = request.args.get('idproducto')
    datos, stocks, ventas, error = get_datos_producto(idproducto)
    return render_template('datos-producto.html', datosArt=datos, stkSucursales=stocks, ventas=ventas)

@productos_bp.route('/consultaProductos', methods=['GET'])
def consultaProductos():
    codigo = request.args.get('query')
    productos, error = getProductosByCodigo(codigo)
    return productos


@productos_bp.route('/abmGrupos', methods=['GET', 'POST'])
@productos_bp.route('/abmGrupos/<idGrupo>', methods=['GET', 'POST'])
def abmGrupos(idGrupo = None):
    error = None
    datosGrupo = []
    if request.method == 'GET':
        #idGrupo = request.args.get('idGrupo')
        if idGrupo != None:
            datosGrupo, error = get_datos_grupo(idGrupo)
        if idGrupo == '-1':
            datosGrupo = []    
    elif request.method == 'POST':
        idGrupo = request.form['idGrupo']
        grupo = request.form['grupo']
        if idGrupo != '':
            datosGrupo, error = actualizarGrupo(idGrupo, grupo)
        else:    
            datosGrupo, error = agregarGrupo(grupo)
        if error is None:
            flash('Datos de grupo grabado')  
        else:
            flash('Error grabando grupos', 'error')          
    grupos, error = getGrupos()        
    return render_template('abm-grupos.html', grupos=grupos, datosGrupo=datosGrupo)

@productos_bp.route('/abmMarcas', methods=['GET', 'POST'])
@productos_bp.route('/abmMarcas/<idMarca>', methods=['GET', 'POST'])
def abmMarcas(idMarca = None):
    error = None
    datosMarca = []
    if request.method == 'GET':
        #idGrupo = request.args.get('idGrupo')
        if idMarca != None:
            datosMarca, error = get_datos_marca(idMarca)
        if idMarca == '-1':
            datosMarca = []    
    elif request.method == 'POST':
        idMarca = request.form['idMarca']
        marca = request.form['marca']
        if idMarca != '':
            datosMarca, error = actualizarMarca(idMarca, marca)
        else:    
            datosMarca, error = agregarMarca(marca)
        if error is None:
            flash('Datos de marca grabado')  
        else:
            flash('Error grabando grupos', 'error')          
    marcas, error = getMarcas()        
    return render_template('abm-marcas.html', marcas=marcas, datosMarca=datosMarca)