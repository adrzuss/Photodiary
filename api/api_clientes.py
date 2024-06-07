from flask import jsonify, session, url_for
from db.db import get_db
from api.api_ventas import insertarFacturaVta, insertarPagos
from api.comunes import CustomError
import datetime
from datetime import date, timedelta

def darAltaCliente(nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones):
    try:
        baja = datetime.datetime(1900, 1, 1)
        idUsuario = session["user_id"]
        error = None
        con, cur = get_db()
        cur.execute('insert into clientes (idusuario, nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones, baja) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                                          (idUsuario, nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idCliente = cur.fetchone()[0]
        return idCliente, error
    except Exception as e:
        error = e
        print(f'Error insertando cliente: {e}')
        return jsonify({'error': str(e)}), 500

def actualizarCliente(idCliente, nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones):
    try:
        error = None
        con, cur = get_db()
        cur.execute('update clientes set nombre = ?, apellido = ?, celular = ?, documento = ?, domicilio = ?, provincia = ?, contacto = ?, observaciones = ? where id = ?',
                    (nombre, apellido, celular, documento, domicilio, provincia, contacto, observaciones, idCliente))
        con.commit()
        return idCliente, error
    except Exception as e:
        error = e
        print(f'Error actualizando cliente: {e}')
        return jsonify({'error': str(e)}), 500
    
def getClientes():
    try:
        error = None
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("select id, apellido, nombre, celular from clientes where idusuario = ?", (idUsuario, ))
        clientes = cur.fetchall()
        con.commit()
        return clientes, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def getLastClienteById():
    try:
        error = None
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("select max(id) from clientes where idusuario = ?", (idUsuario, ))
        cliente = cur.fetchone()
        con.commit()
        return cliente[0], error
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def getClienteById(idCliente):
    try:
        error = None
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("select id, apellido, nombre, celular, documento, domicilio, provincia, contacto, observaciones, DATE_FORMAT(alta, '%d-%m-%Y'), DATE_FORMAT(baja, '%d-%m-%Y') from clientes where id = ? and idusuario = ?", (idCliente, idUsuario))
        cliente = cur.fetchone()
        cli = []
        con.commit()
        for dato in cliente:
            if dato == 'null':
                cli.append('')     
            else:
                cli.append(dato)
        return cli, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def getClienteByDocumento(valorBusqueda):
    try:
        error = None
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("select id, apellido, nombre, celular, documento from clientes where documento LIKE ? and idusuario = ? order by id", (valorBusqueda + '%', idUsuario))
        row = cur.fetchall()
        con.commit()
        if row == None:
            row = {}
        return row, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def getClienteByPhone(valorBusqueda):
    try:
        error = None
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("select id, apellido, nombre, celular, documento from clientes where celular LIKE ? and idusuario = ? order by id", (valorBusqueda + '%', idUsuario))
        rows = cur.fetchall()
        con.commit()
        if rows == None:
            rows = {}
        return rows, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def getClienteByName(valorBusqueda):
    print(valorBusqueda)
    pass

def getTipoEventos():
    try:
        error = None
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("select id, tipo_evento from tipo_eventos where idusuario = ? order by id", (idUsuario, ))
        rows = cur.fetchall()
        con.commit()
        if rows == None:
            rows = {}
        return rows, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def darAltaCita(idCliente, diaCita, horaCita, tipoEvento, diaEvento, lugarEvento, observaciones):
    try:
        error = None
        baja = datetime.datetime(1900, 1, 1)
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute("insert into citas (idcliente, idusuario, dia, hora, idtipo_evento, dia_evento, lugar_evento, observaciones, baja) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", (idCliente, idUsuario, diaCita, horaCita, tipoEvento, diaEvento, lugarEvento, observaciones, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idCita = cur.fetchone()[0]
        return idCita, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def getCitasActivas(idCliente):
    try:
        error = None
        idUsuario = session['user_id']
        con, cur = get_db()
        cur.execute("select count(*) from citas where idusuario = ? and idcliente = ? and dia >= 'today'", (idUsuario, idCliente, ))
        row = cur.fetchone()
        con.commit()
        cantCita = row[0]
        return cantCita, error
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500
    
def getListadoCitas(desde, hasta):
    try:
        error = None
        idUsuario = session['user_id']
        con, cur = get_db()
        cur.execute("select c.id, c.dia, c.hora, cl.apellido, cl.nombre, cl.celular, te.tipo_evento "
                    "from citas c "
                    "join clientes cl"
                    "  on c.idcliente = cl.id "
                    "join tipo_eventos te "
                    "  on c.idtipo_evento = te.id "
                    "where "
                    "  c.idusuario = ? and c.dia between ? and ?", (idUsuario, desde, hasta))
        rows = cur.fetchall()
        con.commit()
        return rows, error
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500
    
def citasDesdeHasta(desde, hasta):
    try:
        error = None
        idUsuario = session['user_id']
        con, cur = get_db()
        cur.execute("select count(*) from citas where idusuario = ? and dia between ? and ?", (idUsuario, desde, hasta))
        row = cur.fetchone()
        con.commit()
        cantCita = row[0]
        return cantCita, error
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

def getEventosActivos(idCliente):
    try:
        error = None
        idUsuario = session['user_id']
        con, cur = get_db()
        cur.execute("select count(*) from eventos where idusuario = ? and idcliente = ? and fecha >= 'today'", (idUsuario, idCliente, ))
        row = cur.fetchone()
        con.commit()
        cantEventos = row[0]
        return cantEventos, error
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

def getListadoEventos(desde, hasta):
    try:
        error = None
        con, cur = get_db()
        cur.execute("select e.id, e.fecha, e.hora, e.nombre_evento, e.lugar_evento, cl.apellido, cl.nombre, cl.celular, te.tipo_evento "
                    "from eventos e "
                    "join clientes cl"
                    "  on cl.id = e.idcliente "
                    "join tipo_eventos te "
                    "  on te.id = e.tipo_evento "
                    "where "
                    "  e.fecha between ? and ?", (desde, hasta))
        rows = cur.fetchall()
        con.commit()
        return rows, error
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

def get_datos_evento(idEvento):
    error = None
    evento = []
    idUser = session['user_id']
    con, cur = get_db()
    cur.execute("select id, tipo_evento, color, alta, baja "
                "from tipo_eventos "
                "where "
                "  id = ? and idusuario = ?", (idEvento, idUser))
    evento = cur.fetchone()
    con.commit()
    return evento, error

def getEventos():
    error = None
    tipoEventos = []
    idUser = session["user_id"]
    con, cur = get_db()
    cur.execute("select id, tipo_evento, alta, baja "
                "from tipo_eventos "
                "where "
                "  idusuario = ?", (idUser, ))
    tipoEventos = cur.fetchall()
    con.commit()
    return tipoEventos, error

def getControlProductos():
    error = None
    idUser = session["user_id"]
    con, cur = get_db()
    cur.execute('select control_productos from usuarios where id = ?', (idUser,))
    controlProductos = cur.fetchone()
    con.commit()
    return controlProductos, error

def actualizarEvento(idEvento, tipoEvento, colorEvento):
    try:
        error = None
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("update tipo_eventos set tipo_evento = ?, color = ? where id = ? and idusuario =?", (tipoEvento, colorEvento, idEvento, idUser))
        con.commit()
        cur.execute("select id, tipo_evento from tipo_eventos where id = ? and idusuario = ?", (idEvento, idUser))
        datosEvento = cur.fetchone()
        return datosEvento, error
    except Exception as e:
        datosEvento = []
        print(f'Error grabado tipo de evento: {e}')
        return jsonify({'error': str(e)}), 500

def agregarEvento(tipoEvento, colorEvento):
    try:
        error = None
        baja = datetime.datetime(1900, 1, 1)
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("insert into tipo_eventos (tipo_evento, color, idusuario, baja) value (?,?,?,?)", (tipoEvento, colorEvento, idUser, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idEvento = cur.fetchone()
        cur.execute("select id, tipo_evento from tipo_eventos where id = ? and idusuario = ?", (idEvento, idUser))
        datosEvento = cur.fetchone()
        return datosEvento, error
    except Exception as e:
        datosEvento = []
        print(f'Error grabado tipo de evento: {e}')
        return jsonify({'error': str(e)}), 500


def eventosDesdeHasta(desde, hasta):
    try:
        error = None
        idUsuario = session['user_id']
        con, cur = get_db()
        cur.execute("select count(*) from eventos where fecha between ? and ? and idusuario = ?", (desde, hasta, idUsuario))
        row = cur.fetchone()
        con.commit()
        cantEventos = row[0]
        return cantEventos, error
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

def getEventoById(idEvento):
    try:
        error = None
        con, cur = get_db()
        cur.execute("select id, tipo_evento, idcliente, nombre_evento, lugar_evento, fecha, hora, observaciones, DATE_FORMAT(alta, '%d-%m-%Y'), DATE_FORMAT(baja, '%d-%m-%Y') from eventos where id = ?", (idEvento, ))
        evento = cur.fetchone()
        ev = []
        con.commit()
        for dato in evento:
            if dato == 'null':
                ev.append('')     
            else:
                ev.append(dato)
        return ev, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def getContratoById(idContrato):
    try:
        error = None
        con, cur = get_db()
        cur.execute("select id, idcliente, titulo_evento, nombre_contrato, dni_contrato, domicilio_contrato, dia, idtipo_evento, dia_evento, "
                    "hora_evento, lugar_evento, dia_civil, hora_civil, lugar_civil, dia_ceremonia, hora_ceremonia, lugar_ceremonia, DATE_FORMAT(alta, '%d-%m-%Y'), DATE_FORMAT(baja, '%d-%m-%Y') from contratos where id = ?", (idContrato, ))
        contrato = cur.fetchone()
        cont = []
        con.commit()
        for dato in contrato:
            if dato == 'null':
                cont.append('')     
            else:
                cont.append(dato)
        return cont, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def grabarEvento(cliente, evento, items, datosDelPago):
    error = None
    idUsuario = session['user_id']
    idCliente = evento[2]
    try:
        con, cur = get_db()
        cur.execute('update clientes set celular = ?, documento = ?, domicilio = ?, contacto = ? where id = ? and idusuario = ?', 
                    (cliente[3], cliente[4], cliente[5], cliente[7], cliente[0], idUsuario))
        if evento[0] > 0:
            idEvento = evento[0]
            cur.execute('update eventos set tipo_evento = ?, idcliente = ?, nombre_evento = ?, lugar_evento = ?, fecha = ?, hora = ?, observaciones = ? where id = ? and idusuario = ?', 
                        (evento[1], evento[2], evento[3], evento[4], evento[5], evento[6], evento[7], evento[0], idUsuario))
            con.commit()
        else:
            baja = datetime.datetime(1900, 1, 1)
            cur.execute('insert into eventos (idusuario, tipo_evento, idcliente, nombre_evento, lugar_evento, fecha, hora, observaciones, baja) values (?,?,?,?,?,?,?,?,?)',
                        (idUsuario, evento[1], evento[2], evento[3], evento[4], evento[5], evento[6], evento[7], baja))    
            con.commit()
            cur.execute('select LAST_INSERT_ID()')
            idEvento = cur.fetchone()[0]
            con.commit()
            error = insertarFacturaVta(evento[2], items)
            if error != None:
                raise CustomError(error)
            error = insertarPagos(idEvento, evento[2], datosDelPago)
        #return jsonify({'evento': idEvento}), 200
        return idEvento, error
    except Exception as e:
        print(e)
        error = 'Error grabando evento: ' + str(e)
        return jsonify({'error': str(e)}), 500

def cuotaInicial(idEvento):
    try:
        con, cur = get_db()
        idUser = session['user_id']
        cur.execute('select id from ctacte_cli where idevento = ? and idusuario = ? and cuota = 0', (idEvento, idUser))
        aux = cur.fetchone()
        con.commit()
        if aux[0] > 0:
            hayCuota = True
            idcc = aux[0]
        else:
            hayCuota = False
            idcc = -1    
        return hayCuota, idcc
    except Exception as e:
        return False, -2
    
def getProximosEventos():
    error = None
    try:
        desde = date.today() 
        idUser = session['user_id']
        con, cur = get_db()
        cur.execute('select e.id, e.nombre_evento, e.lugar_evento, e.fecha, c.apellido, c.nombre, te.tipo_evento '
                    'from eventos e '
                    'join clientes c on c.id = e.idcliente '
                    'join tipo_eventos te on te.id = e.tipo_evento '
                    'where '
                    'e.idusuario = ? and e.fecha >= ?', (idUser, desde))   
        proximosEventos = cur.fetchall()
        con.commit()
        return proximosEventos, error
    except Exception as e:
        print(e)
        error = 'Error obteniendo proximos eventos: ' + str(e)
        return jsonify({'error': str(e)}), 500
    
def getProximasCuotas():
    error = None
    try:
        desde = date.today() 
        hasta = desde + timedelta(days=30)
        idUser = session['user_id']
        con, cur = get_db()
        cur.execute('select cc.id, cc.cuota, cc.vto_cuota, cc.importe, e.nombre_evento, c.apellido, c.nombre '
                    'from ctacte_cli cc '
                    'join eventos e on e.id = cc.idevento '
                    'join clientes c on c.id = cc.idcliente '
                    'where '
                    'cc.idusuario = ? and cc.vto_cuota between ? and ?', (idUser, desde, hasta))   
        proximasCuotas = cur.fetchall()
        con.commit()
        return proximasCuotas, error
    except Exception as e:
        print(e)
        error = 'Error obteniendo proximas cuotas: ' + str(e)
        return jsonify({'error': str(e)}), 500
 
def getCuotasVencidas():
    error = None
    try:
        desde = date.today() 
        idUser = session['user_id']
        con, cur = get_db()
        cur.execute('select cc.id, cc.cuota, cc.vto_cuota, cc.importe, e.nombre_evento, c.apellido, c.nombre '
                    'from ctacte_cli cc '
                    'join eventos e on e.id = cc.idevento '
                    'join clientes c on c.id = cc.idcliente '
                    'where '
                    'cc.idusuario = ? and cc.vto_cuota < ?', (idUser, desde))   
        proximasCuotas = cur.fetchall()
        con.commit()
        return proximasCuotas, error
    except Exception as e:
        print(e)
        error = 'Error obteniendo cuotas vencidas: ' + str(e)
        return jsonify({'error': str(e)}), 500   
    
def getProximasCitas():
    error = None
    try:
        desde = date.today() 
        hasta = desde + timedelta(days=30)
        idUser = session['user_id']
        con, cur = get_db()
        cur.execute('select ct.id, ct.dia, ct.hora, ct.lugar_evento, c.apellido, c.nombre '
                    'from citas ct '
                    'join clientes c on c.id = ct.idcliente '
                    'where '
                    'ct.idusuario = ? and ct.dia between ? and ?', (idUser, desde, hasta))   
        proximasCitas = cur.fetchall()
        con.commit()
        return proximasCitas, error
    except Exception as e:
        print(e)
        error = 'Error obteniendo proximas citas: ' + str(e)
        return jsonify({'error': str(e)}), 500
