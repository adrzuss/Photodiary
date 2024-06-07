from db.db import get_db
from datetime import date
from api.comunes import formatear_moneda
from dateutil.relativedelta import relativedelta

def get_flujo_fondos(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select MONTO, DETALLE, TIPO from FLUJO_DE_FONDOS (?, ?) order by TIPO", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['MONTO'] == None:
            row_dict['MONTO'] = formatear_moneda(0.0)  
        else:    
            row_dict['MONTO'] = formatear_moneda(row_dict['MONTO'])
        data.append(row_dict)
    con.commit()    
    return data, error    


def get_totales_flujo_fondos(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select ENTRADAS, SALIDAS, DIF, DIF_PRC from FLUJO_DE_FONDOS_TOTALES (?, ?)", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
      row_dict = cur.to_dict(row)
      row_dict['ENTRADAS'] = formatear_moneda(row_dict['ENTRADAS'])
      row_dict['SALIDAS'] = formatear_moneda(row_dict['SALIDAS'])
      row_dict['DIF'] = formatear_moneda(row_dict['DIF'])
      row_dict['DIF_PRC'] = 100 - row_dict["DIF_PRC"]
      data.append(row_dict)
    con.commit()    
    return data, error    


def get_flujo_fondos_diaop(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select MONTO, DETALLE, TIPO, ACREDITA_DEBITA from FLUJO_DE_FONDOS_DIA(?, ?) order by TIPO", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['MONTO'] == None:
            row_dict['MONTO'] = formatear_moneda(0.0)  
        else:    
            row_dict['MONTO'] = formatear_moneda(row_dict['MONTO'])
        data.append(row_dict)
    con.commit()    
    return data, error    

def get_flujo_tarjetas(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select TIPO_ENTIDAD, sum(TOTALOP) as TOTALOP, CUOTAS from FLUJO_TARJETAS(?, ?) group by TIPO_ENTIDAD, CUOTAS order by 3 desc", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['TOTALOP'] == None:
            row_dict['TOTALOP'] = formatear_moneda(0.0)  
        else:    
            row_dict['TOTALOP'] = formatear_moneda(row_dict['TOTALOP'])
        data.append(row_dict)
    con.commit()    
    return data, error    

def get_flujo_tarjetas_acred(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select TIPO_ENTIDAD, sum(TOTALOP) as TOTALOP, CUOTAS from FLUJO_TARJETAS_DIA_ACRED(?, ?) group by TIPO_ENTIDAD, CUOTAS order by 3 desc", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['TOTALOP'] == None:
            row_dict['TOTALOP'] = formatear_moneda(0.0)  
        else:    
            row_dict['TOTALOP'] = formatear_moneda(row_dict['TOTALOP'])
        data.append(row_dict)
    con.commit()    
    return data, error    


def get_flujo_tarjetas_detalle(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select ENTIDAD, TIPO_ENTIDAD, TOTALOP, CUOTAS from FLUJO_TARJETAS(?, ?) order by IDTARJETA", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['TOTALOP'] == None:
            row_dict['TOTALOP'] = formatear_moneda(0.0)  
        else:    
            row_dict['TOTALOP'] = formatear_moneda(row_dict['TOTALOP'])
        data.append(row_dict)
    con.commit()    
    return data, error    

def get_cobros_sucs(desde, hasta):
    error = None
    con, cur = get_db()
    cur.execute("select ID_SUCURSAL, NOMBRE, NOM_CORTO from sucursales where BAJA <> 'S' and ID_SUCURSAL < 999 order by ID_SUCURSAL")
    rows = cur.fetchall()
    sucs = []
    for row in rows:
      sucs.append(cur.to_dict(row))  
    
    cadena = ''
    for row in rows:
        row_dict = cur.to_dict(row)
        idSucStr = str(row_dict['ID_SUCURSAL'])
        cadena = cadena + "SUM(CASE WHEN s.id_sucursal = " + idSucStr + " THEN PFV.MONTO ELSE 0 END) AS " + row_dict['NOM_CORTO'] + ","
    con.commit;
    cur.execute("SELECT "
                "pc.id, "
                "pc.nombre, "
                + cadena +
                "SUM(PFV.MONTO) AS TOTAL_GRAL "
                "FROM "
                "pagos_cobros PC  "
                "inner join pagos_fv PFV on PC.id = PFV.IDPAGO "
                "inner join facven FV on PFV.idfactura = FV.IDFACTURA and PFV.SUCURSAL = FV.SUCURSAL "
                "inner join sucursales s on fv.SUCURSAL = s.ID_SUCURSAL "
                "where "
                "fv.fechaf between ? and ? and "
                "fv.tipofactura in (1,2,3,5,6,7,8) "
                "GROUP BY pc.id, pc.nombre order by pc.nombre", (desde, hasta))
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        if row_dict['TOTAL_GRAL'] != None:
            row_dict['TOTAL_GRAL'] = formatear_moneda(row_dict['TOTAL_GRAL'])
        else:
            row_dict['TOTAL_GRAL'] = formatear_moneda('0.0')    
        for suc in sucs:
            if row_dict[suc['NOM_CORTO']] != None:
                row_dict[suc['NOM_CORTO']] = formatear_moneda(row_dict[suc['NOM_CORTO']])
            else:
                row_dict[suc['NOM_CORTO']] = formatear_moneda('0.0')
        data.append(row_dict)
    con.commit()    
    return sucs, data, error
