from flask import session, jsonify
from db.db import get_db
import datetime
from api.comunes import formatear_moneda
from dateutil.relativedelta import relativedelta

def getProductos():
    error = None
    productos = []
    idUser = session['user_id']
    con, cur = get_db()
    cur.execute("select id, codigo, detalle "
                "from productos "
                "where "
                "  idusuario = ?", (idUser,))
    productos = cur.fetchall()
    con.commit()
    return productos, error

def get_datos_producto(idproducto):
    error = None
    producto = []
    idUser = session["user_id"]
    con, cur = get_db()
    cur.execute("select id, codigo, idgrupo, idmarca, detalle, CONCAT('$', FORMAT(costo, 2)), CONCAT('$', FORMAT(precio, 2)), en_dolares, CONCAT('$', FORMAT(precio_usd, 2)), es_servicio, alta, baja "
                "from productos "
                "where "
                "  id = ? and idusuario = ?", (idproducto, idUser))
    producto = cur.fetchone()
    """
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['PLISTA'] == None:
            row_dict['PLISTA'] = formatear_moneda(0.0)  
        else:    
            row_dict['PLISTA'] = formatear_moneda(row_dict['PLISTA'])
        data.append(row_dict)
    """
    con.commit()
    return producto, error

def get_datos_producto_codigo(codigo):
    error = None
    producto = []
    idUser = session["user_id"]
    con, cur = get_db()
    cur.execute("select id, codigo, idgrupo, idmarca, detalle, costo, precio, en_dolares, precio_usd, es_servicio, alta, baja "
                "from productos "
                "where "
                "  codigo = ? and idusuario = ?", (codigo, idUser))
    producto = cur.fetchone()
    con.commit()
    return producto, error


def actualizarProducto(idProducto, codigo, grupo, marca, detalle, costo, precio, enDolares, precioDolar, esServicio):
    try:
        error = None
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("update productos set codigo = ?, idgrupo = ?, idmarca = ?, detalle = ?, costo = ?, precio = ?, en_dolares = ?, precio_usd = ?, es_servicio = ? "
                    "where id = ? and idusuario = ?", (codigo, grupo, marca, detalle, costo, precio, enDolares, precioDolar, esServicio, idProducto, idUser))
        con.commit()
        cur.execute("select id, codigo, idgrupo, idmarca, detalle, CONCAT('$', FORMAT(costo, 2)), CONCAT('$', FORMAT(precio, 2)), en_dolares, CONCAT('$', FORMAT(precio_usd, 2)), es_servicio, alta, baja from productos where id = ? and idusuario = ?", (idProducto, idUser))
        datosProducto = cur.fetchone()
        return datosProducto, error
    except Exception as e:
        datosProducto = []
        print(f'Error grabado producto: {e}')
        return jsonify({'error': str(e)}), 500

def agregarProducto(codigo, grupo, marca, detalle, costo, precio, enDolares, precioDolar, esServicio):
    try:
        error = None
        baja = datetime.datetime(1900, 1, 1)
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("insert into productos (idusuario, codigo, detalle, idgrupo, idmarca, costo, precio, precio_usd, en_dolares, es_servicio, baja) value (?,?,?,?,?,?,?,?,?,?,?)", (idUser, codigo, detalle, grupo, marca, costo, precio, precioDolar, enDolares, esServicio, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idProducto = cur.fetchone()
        cur.execute("select id, codigo, idgrupo, idmarca, detalle, CONCAT('$', FORMAT(costo, 2)), CONCAT('$', FORMAT(precio, 2)), en_dolares, CONCAT('$', FORMAT(precio_usd, 2)), es_servicio, alta, baja from productos where id = ? and idusuario = ?", (idProducto, idUser))
        datosProducto = cur.fetchone()
        return datosProducto, error
    except Exception as e:
        datosProducto = []
        print(f'Error grabado producto: {e}')
        return jsonify({'error': str(e)}), 500
    
def getProductoById(valorBusqueda):
    try:
        idUsuario = session['user_id']
        error = None
        con, cur = get_db()
        cur.execute("select id, codigo, detalle from productos where id = ? and idusuario = ? order by id", (valorBusqueda, idUsuario))
        row = cur.fetchall()
        con.commit()
        if row == None:
            row = {}
        return row, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def getProductosByCodigo(valorBusqueda):
    try:
        idUsuario = session['user_id']
        error = None
        con, cur = get_db()
        cur.execute("select id, codigo, detalle from productos where codigo LIKE ? and idusuario = ? order by id", (valorBusqueda + '%', idUsuario))
        row = cur.fetchall()
        con.commit()
        if row == None:
            row = {}
        return row, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def getProductoByDetalle(valorBusqueda):
    pass

def getGrupos():
    error = None
    grupos = []
    idUser = session['user_id']
    con, cur = get_db()
    cur.execute("select id, grupo, alta, baja "
                "from grupos "
                "where "
                "  idusuario = ?", (idUser,))
    grupos = cur.fetchall()
    con.commit()
    return grupos, error

def get_datos_grupo(idGrupo):
    error = None
    grupo = []
    idUser = session['user_id']
    con, cur = get_db()
    cur.execute("select id, grupo, alta, baja "
                "from grupos "
                "where "
                "  id = ? and idusuario = ?", (idGrupo, idUser))
    grupo = cur.fetchone()
    con.commit()
    return grupo, error

def actualizarGrupo(idGrupo, grupo):
    try:
        error = None
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("update grupos set grupo = ? where id = ? and idusuario =?", (grupo, idGrupo, idUser))
        con.commit()
        cur.execute("select id, grupo from grupos where id = ? and idusuario = ?", (idGrupo, idUser))
        datosGrupo = cur.fetchone()
        return datosGrupo, error
    except Exception as e:
        datosGrupo = []
        print(f'Error grabado grupo: {e}')
        return jsonify({'error': str(e)}), 500

def agregarGrupo(grupo):
    try:
        error = None
        baja = datetime.datetime(1900, 1, 1)
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("insert into grupos (grupo, idusuario, baja) value (?,?,?)", (grupo, idUser, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idGrupo = cur.fetchone()
        cur.execute("select id, grupo from grupos where id = ? and idusuario = ?", (idGrupo, idUser))
        datosGrupo = cur.fetchone()
        return datosGrupo, error
    except Exception as e:
        datosGrupo = []
        print(f'Error grabado grupo: {e}')
        return jsonify({'error': str(e)}), 500

def getMarcas():
    error = None
    marcas = []
    idUser = session["user_id"]
    con, cur = get_db()
    cur.execute("select id, marca, alta, baja "
                "from marcas "
                "where "
                "  idusuario = ?", (idUser, ))
    marcas = cur.fetchall()
    con.commit()
    return marcas, error

def get_datos_marca(idMarca):
    error = None
    marca = []
    idUser = session["user_id"]
    con, cur = get_db()
    cur.execute("select id, marca, alta, baja "
                "from marcas "
                "where "
                "  id = ? and idusuario = ?", (idMarca, idUser))
    marca = cur.fetchone()
    con.commit()
    return marca, error

def actualizarMarca(idMarca, marca):
    try:
        error = None
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("update marcas set marca = ? where id = ? and idusuario =?", (marca, idMarca, idUser))
        con.commit()
        cur.execute("select id, marca from marcas where id = ? and idusuario = ?", (idMarca, idUser))
        datosMarca = cur.fetchone()
        return datosMarca, error
    except Exception as e:
        datosMarca = []
        print(f'Error grabado marca: {e}')
        return jsonify({'error': str(e)}), 500

def agregarMarca(marca):
    try:
        error = None
        baja = datetime.datetime(1900, 1, 1)
        idUser = session["user_id"]
        con, cur = get_db()
        cur.execute("insert into marcas (marca, idusuario, baja) value (?,?,?)", (marca, idUser, baja))
        con.commit()
        cur.execute('SELECT LAST_INSERT_ID()')
        idMarca = cur.fetchone()
        cur.execute("select id, marca from marcas where id = ? and idusuario = ?", (idMarca, idUser))
        datosGrupo = cur.fetchone()
        return datosGrupo, error
    except Exception as e:
        datosGrupo = []
        print(f'Error grabado marca: {e}')
        return jsonify({'error': str(e)}), 500