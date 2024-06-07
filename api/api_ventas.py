from flask import flash, session, send_file, after_this_request, make_response
from db.db import get_db
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from api.comunes import formatear_moneda

def insertarFacturaVta(idCliente, items):
    error = None
    try:
        idUser = session['user_id']
        baja = datetime(1900, 1, 1)
        hoy = date.today()
        total = 0
        for item in items:
            total = total + (item['cantidad'] * item['precio'])
        con, cur = get_db()
        cur.execute('insert into fac_ventas (idusuario, fecha, idcliente, total, baja) values (?, ?, ?, ?, ?)', (idUser, hoy, idCliente, total, baja))    
        con.commit()
        cur.execute('select LAST_INSERT_ID()')
        idFactura = cur.fetchone()
        for index, item in enumerate(items):
            cur.execute('insert into items_ventas (id, iditem, idarticulo, cantidad, precio) values (?, ?, ?, ?, ?)', (idFactura[0], index+1, item['idProducto'], item['cantidad'], item['precio']))
        con.commit()    
        return error
    except Exception as e:
        flash('Error grabando la factura', 'error')  
        print(f'Error: {e}')      
        error = e
        return error

def insertarPagos(idEvento, idCliente, datosDelPago):
    #{'pagoEfectivo': pagoEfectivo, 'cuotas': cuotas, 'impCuota': impCuota, 'vtoPrimerCuota': vtoPrimerCuota}
    error = None
    try:
        con, cur = get_db()
        idUsuario = session["user_id"]
        efectivo = float(datosDelPago['pagoEfectivo'])
        if (efectivo > 0):
            importe = datosDelPago['pagoEfectivo']
            hoy = date.today()
            baja = datetime(1900, 1, 1)
            cur.execute('insert into ctacte_cli (idusuario, idcliente, idevento, cuota, vto_cuota, estado, importe, baja) values (?, ?, ?, ?, ?, ?, ?, ?)', (idUsuario, idCliente, idEvento, 0, hoy, 1, importe, baja))
        cuotas = int(datosDelPago['cuotas'])
        vtoCuota = datetime.strptime(datosDelPago['vtoPrimerCuota'], "%Y-%m-%d")
        for index in range(cuotas):
            importe = datosDelPago['impCuota']
            baja = datetime(1900, 1, 1)
            cur.execute('insert into ctacte_cli (idusuario, idcliente, idevento, cuota, vto_cuota, estado, importe, baja) values (?, ?, ?, ?, ?, ?, ?, ?)', (idUsuario, idCliente, idEvento, index+1, vtoCuota, 1, importe, baja))
            vtoCuota = vtoCuota + relativedelta(months = 1)
        con.commit()    
        return error    
    except Exception as e:        
        flash('Error grabando pagos', 'error')  
        print(f'Error: {e}')      
        error = e
        return error

def getFacturasVta(desde, hasta):
    error = None
    try:
        idUsuario = session["user_id"]
        db, cur = get_db()
        cur.execute("select f.id, f.fecha, CONCAT('$', FORMAT(f.total, 2)), c.apellido, c.nombre "
                    "from fac_ventas f "
                    "join clientes c on f.idcliente = c.id "
                    "where "
                    "  f.fecha between ? and ? and c.idusuario = ?", (desde, hasta, idUsuario))
        ventas = cur.fetchall()
        db.commit()
        return error, ventas
    except Exception as e:
        flash('Error obteniendo datos de facturas', 'error')  
        print(f'Error: {e}')      
        error = e
        return error        

def getPagosPendientesCliente(idCliente):
    error = None
    try:
        print(f'El cliente: {idCliente}')
        idUsuario = session["user_id"]
        db, cur = get_db()
        cur.execute("select cc.id, cc.cuota, cc.vto_cuota, CONCAT('$', FORMAT(cc.importe, 2)), e.nombre_evento, (cc.vto_cuota < CURDATE()) vencida "
                    "from ctacte_cli cc "
                    "join eventos e on e.id = cc.idevento "
                    "where "
                    "  cc.idcliente = ? and cc.idusuario = ? and "
                    "  cc.estado = 1", (idCliente, idUsuario))
        pendientes = cur.fetchall()
        db.commit()
        return pendientes, error
    except Exception as e:
        flash('Error obteniendo pagos pendientes', 'error')  
        print(f'Error: {e}')      
        error = e
        return error        

    
def getPagosPendientes(desde, hasta):
    error = None
    try:
        idUsuario = session["user_id"]
        db, cur = get_db()
        cur.execute("select cc.id, cc.idcliente, cc.cuota, cc.vto_cuota, CONCAT('$', FORMAT(cc.importe, 2)), c.apellido, c.nombre, e.nombre_evento, (cc.vto_cuota < CURDATE()) vencida "
                    "from ctacte_cli cc "
                    "join clientes c on cc.idcliente = c.id "
                    "join eventos e on e.id = cc.idevento "
                    "where "
                    "  cc.vto_cuota between ? and ? and cc.idusuario = ? and "
                    "  cc.estado = 1", (desde, hasta, idUsuario))
        pendientes = cur.fetchall()
        db.commit()
        return error, pendientes
    except Exception as e:
        flash('Error obteniendo pagos pendientes', 'error')  
        print(f'Error: {e}')      
        error = e
        return error        
    
def getPagosRealizados(desde, hasta):
    error = None
    try:
        idUsuario = session["user_id"]
        db, cur = get_db()
        cur.execute("select cc.id, cc.idcliente, cc.cuota, cc.vto_cuota, CONCAT('$', FORMAT(cc.importe, 2)), c.apellido, c.nombre, e.nombre_evento "
                    "from ctacte_cli cc "
                    "join clientes c on cc.idcliente = c.id "
                    "join eventos e on e.id = cc.idevento "
                    "where "
                    "  cc.vto_cuota between ? and ? and cc.idusuario = ? and "
                    "  cc.estado = 2", (desde, hasta, idUsuario))
        realizados = cur.fetchall()
        db.commit()
        return error, realizados
    except Exception as e:
        flash('Error obteniendo pagos realizados', 'error')  
        print(f'Error: {e}')      
        error = e
        return error        
    
def cuotasPendPeriodo(desde, hasta):
    error = None
    try:
        idUsuario = session['user_id']
        con, cur = get_db()
        cur.execute("SELECT coalesce(COUNT(*), 0) cuotas, CONCAT('$', FORMAT(coalesce(SUM(importe), 0.0), 2)) total "
                    "FROM ctacte_cli "
                    "WHERE "
                    "idusuario = ? and "
                    "vto_cuota BETWEEN ? AND ? and "
                    "estado = 1", (idUsuario, desde, hasta))
        pendientes = cur.fetchone()
        con.commit()
        return error, pendientes
    except Exception as e:
        flash('Error obteniendo pagos pendientes por periodo', 'error')  
        print(f'Error: {e}')      
        error = e
        return error        
    
def getDatosReciboPendiente(idcc):
    error = None
    try:
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("select cc.idcliente, cc.idevento, cc.cuota, cc.vto_cuota, cc.importe, "
                    "c.apellido, c.nombre, e.nombre_evento, e.lugar_evento, e.fecha "
                    "from ctacte_cli cc "
                    "join clientes c on c.id = cc.idcliente "
                    "join eventos e on e.id = cc.idevento "
                    "where "
                    "cc.id = ? and cc.idusuario = ? and cc.estado = 1", (idcc, idUser))
        datosRecibo = cur.fetchone()
        con.commit()
        return datosRecibo, error
    except Exception as e:
        flash('Error obteniendo pagos pendientes por periodo', 'error')  
        print(f'Error: {e}')      
        error = e
        return error        
    
def grabarPagoRecibo(idcc):
    error = None
    try:
        con, cur = get_db()
        cur.execute("update ctacte_cli set estado = 2 where id = ?", (idcc,))
        con.commit()
        return error
    except Exception as e:
        flash('Error grabando pago', 'error')  
        print(f'Error: {e}')      
        error = e
        return error
    
def grabarCaja(fecha, efectivo, cuentaBancaria, banco, detalle):
    error = None
    try:
        con, cur = get_db()
        baja = datetime(1900, 1, 1)
        idUsuario = session['user_id']
        print(fecha, efectivo, banco, cuentaBancaria)
        if banco > 0:
            cur.execute("insert into mov_bancarios (idusuario, idcuenta_bancaria, fecha, idtipo_movimiento, debito, credito, baja, detalle) values (?,?,?,?,?,?,?,?)",
                                                   (idUsuario, cuentaBancaria, fecha, 1, banco, 0, baja, detalle))
            con.commit()
            print('pago grabado')
    except Exception as e:
        flash('Error grabando caja', 'error')  
        print(f'Error: {e}')      
        error = e
        return error