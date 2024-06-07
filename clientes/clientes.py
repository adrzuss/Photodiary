from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from db.db import get_db;
from datetime import date
from api.comunes import getProvincias
from api.api_clientes import darAltaCliente, actualizarCliente, getClienteById, getClienteByDocumento, getClienteByPhone, getClienteByName,\
                             getTipoEventos, getLastClienteById, darAltaCita, getCitasActivas, getListadoCitas, getClientes, getContratoById, getEventoById 
from api.api_clientes import grabarEvento, getEventosActivos, getListadoEventos, get_datos_evento, actualizarEvento, agregarEvento, getEventos, getControlProductos, cuotaInicial
from api.api_ventas import getPagosPendientesCliente

clientes_bp = Blueprint('clientes_bp', __name__, template_folder='templates/clientes')

@clientes_bp.route('/abmClientes/<id>', methods=['GET', 'POST'])
@clientes_bp.route('/abmClientes', methods=['GET', 'POST'])
def abmClientes(id=None):
    if ('user in session'):
        cuotasPendientes = []
        provincias, error = getProvincias()
        if request.method == 'GET':
            if id == None:
                idCliente = request.args.get('idcliente')
            else:
                idCliente = id    
            if not idCliente:
                idCliente, error = getLastClienteById()  
        elif request.method == 'POST':
            idCliente = request.form['idcliente']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            celular = request.form['celular']
            documento = request.form['documento']
            domicilio = request.form['domicilio']
            provincia = request.form['provincia']
            contacto = request.form['contacto']
            observaciones = request.form['observaciones']
            idCliente, error = grabarCliente(idCliente, nombre, apellido, celular, provincia, documento, domicilio, contacto, observaciones)
            flash("Datos del cliente grabados")
        if idCliente != '-1':  
            print(f'El cliente: {idCliente}')  
            cliente, error = getClienteById(idCliente)  
            citasActivas, error = getCitasActivas(idCliente)
            eventosActivos, error = getEventosActivos(idCliente)
            cuotasPendientes, error = getPagosPendientesCliente(idCliente)
        else:
            cliente = []
            citasActivas = []  
            eventosActivos = []    
            cuotasPendientes = []
        print(f'----El cliente: {idCliente}')    
        hoy = date.today()
        return render_template('abm-clientes.html', cliente = cliente, provincias=provincias, citasActivas = citasActivas, eventosActivos=eventosActivos, hoy=hoy, cuotasPendientes=cuotasPendientes)
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

@clientes_bp.route('/getCliente/<idCliente>', methods=['GET', 'POST'])
def getCliente(idCliente):
    cliente, error = getClienteById(idCliente)
    if error == None:
        datos = jsonify({'cliente': cliente})
        return datos
    else:
        return jsonify({'error': 'No hay datos'})

@clientes_bp.route('/buscarCliente/<buscarPor>/<valorBusqueda>', methods=['GET', 'POST'])
def buscarCliente(buscarPor, valorBusqueda):
    if buscarPor == 'documento':
        cliente, error = getClienteByDocumento(valorBusqueda)
    elif buscarPor == 'telefono':
        cliente, error = getClienteByPhone(valorBusqueda)        
    elif buscarPor == 'nombre':
        cliente, error = getClienteByName(valorBusqueda)
    if error == None:
        if cliente == {}:
            flash('No hay datos de cliente para el valor ingresado')
            return jsonify({'cliente': cliente})
        else:    
            return jsonify({'cliente': cliente})
    else:
        return 'No hay datos'

@clientes_bp.route('/grabarCliente/<idCliente>/<nombre>/<apellido>/<celular>/<provincia>/<documento>/<domicilio>/<contacto>/<observaciones>', methods=['POST'])
def grabarCliente(idCliente, nombre, apellido, celular, provincia=None, documento=None, domicilio=None, contacto=None, observaciones=None):
    #estos parámetros no son requeridos, por eso no se pasan y se leen de la siguiente manera
    error = None
    print('empezando a grabar')
    if idCliente == "":
        print('Grabando cliente nuevo')
        idCliente, error = darAltaCliente(nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones.strip())
        print(f'Listo, nuevo: {idCliente}')
    else:
        print('Actualizando cliente')
        idCliente, error = actualizarCliente(idCliente, nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones.strip())
        print(f'Listo, actualizado: {idCliente}')
    if error is None:
        #return jsonify({'idcliente': idCliente}), 200
        return idCliente, error
    else:
        print(f'Error: {error}')
        flash(f'Error: {error}', 'error')
        return jsonify({'error': error}), 500

@clientes_bp.route('/listadoClientes', methods=['GET'])
def listadoClientes():
    if ('user' in session):
        error = None
        clientes, error = getClientes()
        print(clientes)
        if error is None:
            return render_template('listado-clientes.html', clientes=clientes)    
        else:
            flash('Error obteniendo listado de clientes')
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))        
        
# Citas-----------------------------------

@clientes_bp.route('/abmCitas/<idcliente>', methods=['GET'])
def abmCitas(idcliente):
    if ('user' in session):
        error = None
        if (request.method == 'GET')and(idcliente != None):
            cliente, error = getClienteById(idcliente)
            tipoEventos, error = getTipoEventos()
            return render_template('abm-citas.html', idcliente=cliente[0], apellido = cliente[1], nombre = cliente[2], tipoEventos = tipoEventos)
        else:
            flash('No hay datos para el cliente', 'error')    
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))        

@clientes_bp.route('/grabarCita', methods=['POST'])    
def grabarCita():
    if request.method == 'POST':
        idCliente = request.form['idcliente']
        diaCita = request.form['dia']
        horaCita = request.form['hora']
        tipoEvento = request.form['tipoEvento']
        diaEvento = request.form['diaEvento']
        lugarEvento = request.form['lugarEvento']
        observaciones = request.form['observaciones']
        idCita, error = darAltaCita(idCliente, diaCita, horaCita, tipoEvento, diaEvento, lugarEvento, observaciones)
        if error is None:
            flash(f'Cita grabada {idCita} - {diaCita}')
        else:
            flash(f'Error grabando cita: {error}', 'error')
        return redirect(url_for('clientes_bp.abmClientes', id=idCliente))    

@clientes_bp.route('/listadoCitas', methods=['GET'])
def listadoCitas():
    if ('user' in session):
        if request.method == 'GET':
            desde = request.args.get('desde')
            hasta = request.args.get('hasta')
            if desde == None:
                desde = date.today()
            if hasta == None:
                hasta = date.today()
            citas, error = getListadoCitas(desde, hasta)
            return render_template('listado-citas.html', desde=desde, hasta=hasta, citas=citas)
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

# Fin Citas-----------------------------------
# Tipo de eventos-----------------------------------
@clientes_bp.route('/abmTipoEventos', methods=['GET', 'POST'])
@clientes_bp.route('/abmTipoEventos/<idTipoEvento>', methods=['GET', 'POST'])
def abmTipoEventos(idTipoEvento = None):
    error = None
    datosEvento = []
    if request.method == 'GET':
        #idGrupo = request.args.get('idGrupo')
        if idTipoEvento != None:
            datosEvento, error = get_datos_evento(idTipoEvento)
        if idTipoEvento == '-1':
            datosEvento = []    
    elif request.method == 'POST':
        idTipoEvento = request.form['idTipoEvento']
        tipoEvento = request.form['tipoEvento']
        colorEvento = request.form['colorEvento']
        print(f'El color es: {colorEvento}')
        if idTipoEvento != '':
            datosEvento, error = actualizarEvento(idTipoEvento, tipoEvento, colorEvento)
        else:    
            datosEvento, error = agregarEvento(tipoEvento, colorEvento)
        if error is None:
            flash('Datos del tipo de evento grabado')  
        else:
            flash('Error grabando tipo de evento', 'error')          
    tipoEventos, error = getEventos()        
    return render_template('abm-tipoeventos.html', tipoEventos=tipoEventos, datosEvento=datosEvento)

@clientes_bp.route('/listadoEventos', methods=['GET'])
def listadoEventos():
    if ('user' in session):
        if request.method == 'GET':
            desde = request.args.get('desde')
            hasta = request.args.get('hasta')
            if desde == None:
                desde = date.today()
            if hasta == None:
                hasta = date.today()
            eventos, error = getListadoEventos(desde, hasta)
            if error is None:
                return render_template('listado-eventos.html', desde=desde, hasta=hasta, eventos=eventos)
            else:
                flash('Error obteniendo listado de eventos', 'error')
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

@clientes_bp.route('/getEvento/<idEvento>', methods=['GET', 'POST'])
def getEvento(idEvento):
    evento, error = getEventoById(idEvento)
    if error == None:
        datos = jsonify({'evento': evento})
        return datos
    else:
        return jsonify({'error': 'No hay datos'})

# Fin Tipo de eventos-----------------------------------

# Eventos-----------------------------------
@clientes_bp.route('/abmEvento', methods=['GET','POST'])
def abmEvento():
    if ('user' in session):
        cliente = []
        tipoEventos, error = getTipoEventos()
        controlProductos, error = getControlProductos()
        print(f'Control de productos: {controlProductos}')
        print(f'Metodo: {request.method}')
        if request.method == 'GET':
            idCliente = request.args.get('idCliente')
            idEvento = request.args.get('idEvento')
            datosCliente = getCliente(idCliente)
            datosEvento = getEvento(idEvento)
            cliente = datosCliente.get_json()['cliente']
            if 'evento' in datosEvento.get_json():
                evento = datosEvento.get_json()['evento']
            else:
                evento = []    
            return render_template('abm-evento.html', tipoEventos=tipoEventos, controlProductos=controlProductos[0] , cliente=cliente, evento=evento)        
        if request.method == 'POST':    
            print('voy a grabar el evento')
            #datos del cliente
            idCliente = request.form['idCliente']
            apellido = request.form['apellido']
            nombre = request.form['nombre']
            celular = request.form['celular']
            documento = request.form['documento']
            contacto = request.form['contacto']
            domicilio = request.form['domicilio']
            #datos del evento
            idEvento = request.form['idEvento']
            tituloEvento = request.form['tituloEvento']
            tipoEvento = request.form['tipoEvento']
            fechaEvento = request.form['fechaEvento']
            horaEvento = request.form['horaEvento']
            lugarEvento = request.form['lugarEvento']
            observaciones = request.form['observaciones']
            #datos de productos
            idProductos = request.form.getlist('idProducto[]')
            cantidades = request.form.getlist('cantidad[]')
            precios = request.form.getlist('precio-unitario[]')
            print('los datos de los productos son')
            print(idProductos)
            print(cantidades)
            print(precios)
            #datos del pago
            pagoEfectivo = request.form['efectivo']
            cuotas = request.form['cuotas']
            impCuota = request.form['impCuotas']
            vtoPrimerCuota = request.form['vtoCuota']
            datosDelPago = {}
            datosDelPago = {'pagoEfectivo': pagoEfectivo, 'cuotas': cuotas, 'impCuota': impCuota, 'vtoPrimerCuota': vtoPrimerCuota}
            #----------------------------------
            datosCliente = getCliente(idCliente)
            cliente = datosCliente.get_json()['cliente']
            cliente[3] = celular
            cliente[4] = documento
            cliente[5] = domicilio
            cliente[7] = contacto
            datosEvento = getEvento(idEvento)
            if 'evento' in datosEvento.get_json():
                idEvento = datosEvento.get_json()['evento'][0]
                evento = []    
                evento.append(idEvento)
            else:
                evento = []    
                evento.append(0)
            evento.append(tipoEvento)
            evento.append(idCliente)
            evento.append(tituloEvento)
            evento.append(lugarEvento)
            evento.append(fechaEvento)
            evento.append(horaEvento)
            evento.append(observaciones)
            items = []
            for i in range(len(idProductos)):
                if (idProductos[i] != ''):
                    item = {
                        'idProducto': idProductos[i],
                        'cantidad': int(cantidades[i]),
                        'precio': float(precios[i])
                    }
                    items.append(item)
                
            idEvento, error = grabarEvento(cliente, evento, items, datosDelPago)  
            flash('Evento grabado - Factura creada')      
            hayCuota, idcc = cuotaInicial(idEvento)
            if hayCuota:
                return redirect(url_for('ventas_bp.reciboPago', idcc=idcc))
            else:
              return redirect(url_for('clientes_bp.abmClientes', id=idCliente))    
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))
    
# Fin Eventos-----------------------------------

# Contratos-----------------------------------
@clientes_bp.route('/getContrato/<idContrato>', methods=['GET', 'POST'])
def getContrato(idContrato):
    contrato, error = getContratoById(idContrato)
    if error == None:
        datos = jsonify({'contrato': contrato})
        return datos
    else:
        return jsonify({'error': 'No hay datos'})

   
@clientes_bp.route('/abmContrato', methods=['GET','POST'])
def abmContrato():
    if ('user' in session):
        cliente = []
        if request.method == 'GET':
            idCliente = request.args.get('idCliente')
            idContrato = request.args.get('idContrato')
            #cliente = getClienteById(idCliente)
            datosCliente = getCliente(idCliente)
            datosContrato = getContrato(idContrato)
            cliente = datosCliente.get_json()['cliente']
            if 'contrato' in datosContrato.get_json():
                contrato = datosContrato.get_json()['contrato']
            else:
                contrato = []    
        if request.method == 'POST':    
            idCliente = request.form['idCliente']
            #queHago = 'POST'
        return render_template('abm-contrato.html', cliente=cliente, contrato=contrato)    
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

@clientes_bp.route('/provincias', methods=['GET'])
def cargarProvincias():
    provincias, error = getProvincias()
    if error == None:
        return jsonify({'provincias': provincias}), 200
    else:
        return 'Error cargando provincias'