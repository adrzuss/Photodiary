from flask import session, jsonify
from db.db import get_db
from datetime import date
from api.comunes import formatear_moneda
import datetime
from dateutil.relativedelta import relativedelta

def get_datos_cuenta(idCuenta):
    error = None
    try:
        idUser = session['user_id']
        con, cur = get_db()
        cur.execute('select id, nombre, nro_cuenta, cbu_cvu, alias, alta, baja from cuentas_bancarias where id = ? and idusuario = ?', (idCuenta, idUser))
        datoCuenta = cur.fetchone()
        con.commit()
        return datoCuenta, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

def getCuentas():
    error = None
    try:
        idUser = session['user_id']
        con, cur = get_db()
        cur.execute('select id, nombre from cuentas_bancarias where idusuario = ?', (idUser,))
        cuentas = cur.fetchall()
        con.commit()
        return cuentas, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

def actualizarCuenta(idCuenta, cuenta, nroCuenta, cbu ,alias):
    try:
        error = None
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("update cuentas_bancarias set nombre = ?, nro_cuenta = ?, cbu_cvu = ?, alias = ? where id = ? and idusuario =?", (cuenta, nroCuenta, cbu ,alias, idCuenta, idUser))
        con.commit()
        cur.execute("select id, nombre from cuentas_bancarias where id = ? and idusuario = ?", (idCuenta, idUser))
        datosGrupo = cur.fetchone()
        return datosGrupo, error
    except Exception as e:
        datosGrupo = []
        print(f'Error grabado cuenta: {e}')
        return jsonify({'error': str(e)}), 500

def agregarCuenta(cuenta, nroCuenta, cbu ,alias):
    try:
        error = None
        baja = datetime.datetime(1900, 1, 1)
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("insert into cuentas_bancarias (nombre, nro_cuenta, cbu_cvu, alias, idusuario, baja) value (?,?,?,?,?,?)", (cuenta, nroCuenta, cbu ,alias, idUser, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idCuenta = cur.fetchone()
        cur.execute("select id, nombre from cuentas_bancarias where id = ? and idusuario = ?", (idCuenta, idUser))
        datosCuenta = cur.fetchone()
        return datosCuenta, error
    except Exception as e:
        datosCuenta = []
        print(f'Error grabado grupo: {e}')
        return jsonify({'error': str(e)}), 500
    
def getMovimientosCuenta(cuenta, desde, hasta):
    try:
        error = None
        idUsuario = session["user_id"]
        print(cuenta, desde, hasta)
        con, cur = get_db()
        cur.execute("select mb.id, mb.fecha, CONCAT('$', FORMAT(coalesce(mb.debito, 0.0), 2)) debito, CONCAT('$', FORMAT(coalesce(mb.credito, 0.0), 2)) credito, tmb.tipo_movimiento, mb.detalle "
                    "from mov_bancarios mb "
                    "join tipos_movbancos tmb on tmb.id = mb.idtipo_movimiento "
                    "where "
                    "mb.idusuario = ? and "
                    "mb.idcuenta_bancaria = ? and "
                    "mb.fecha between ? and ?", (idUsuario, cuenta, desde, hasta))
        movimientos = cur.fetchall()
        con.commit()
        return movimientos, error
    except Exception as e:
        movimientos = []
        print(f'Error grabado grupo: {e}')
        return jsonify({'error': str(e)}), 500
            