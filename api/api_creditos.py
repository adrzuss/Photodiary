from flask import flash, redirect, url_for
from db.db import get_db
from datetime import date
from dateutil.relativedelta import relativedelta
from api.comunes import formatear_moneda

def get_cant_cred_sucursales(desde, hasta):
    error = None
    try:
        con, cur = get_db()
        cur.execute("select CANT_OP_CRE, SUCURSAL from GET_OPERACIONES_CRE_SUC(?, ?)", (desde, hasta))
        rows = cur.fetchall()
        data = []
        for row in rows:
            data.append(cur.to_dict(row))
        con.commit()
        return data, error    
    except Exception as e:
        data = []
        flash(f"Error de conección a la base de datos:{e}", "error")
        return data, error
    
def get_cant_clientes_cred(desde, hasta):
    error = None
    try:
        con, cur = get_db()
        cur.execute("select CANT_CRED_CLIENTES_NUEVOS, CANT_CRED from GET_CANT_CLI_OPER_CRE(?, ?)", (desde, hasta))
        rows = cur.fetchall()
        data = []
        for row in rows:
            data.append(cur.to_dict(row))
        con.commit()
        return data, error    
    except Exception as e:
        rows = []
        flash(f"Error de conección a la base de datos:{e}", "error")
        return rows, error
    
def get_cobranzas_cred(desde, hasta):
    error = None
    try:
        con, cur = get_db()
        cur.execute("select TOT_VENCIMIENTOS, CANT_VENCIMIENTOS, TOT_EN_TERMINO, CANT_EN_TERMINO, TOT_FUERA_TERMINO, CANT_FUERA_TERMINO, TOT_ANTERIORES, CANT_ANTERIORES "
                    "from GET_DETALLE_CUOTAS_PERIODO(?, ?)", (desde, hasta))
        data = []
        rows = cur.fetchall()
        data = cur.to_dict(rows[0])
        data['TOT_VENCIMIENTOS'] = formatear_moneda(data['TOT_VENCIMIENTOS'])
        data['TOT_EN_TERMINO'] = formatear_moneda(data['TOT_EN_TERMINO'])
        data['TOT_FUERA_TERMINO'] = formatear_moneda(data['TOT_FUERA_TERMINO'])
        data['TOT_ANTERIORES'] = formatear_moneda(data['TOT_ANTERIORES'])
        con.commit()
        return data, error    
    except Exception as e:
        data = []
        flash(f"Error obteniendo datos de cobranza:{e}", "error")
        return data, error

def get_cobranzas_sucs(desde, hasta):
    error = None
    try:
        con, cur = get_db()
        cur.execute("select SUCURSAL, NOM_SUC, TOT_VENCIMIENTOS, CANT_VENCIMIENTOS, TOT_EN_TERMINO, CANT_EN_TERMINO from GET_DETALLE_CUOTAS_SUCS(?, ?)", (desde, hasta))
        rows = cur.fetchall()
        data = []
        for row in rows:
            row_dict = cur.to_dict(row)
            if row_dict['TOT_VENCIMIENTOS'] == None:
                row_dict['TOT_VENCIMIENTOS'] = 0.0
            else:
                row_dict['TOT_VENCIMIENTOS'] = row_dict['TOT_VENCIMIENTOS']
            data.append(row_dict)
        con.commit()
        return data, error    
    except Exception as e:
        rows = []
        flash(f"Error de conección a la base de datos:{e}", "error")
        return rows, error
