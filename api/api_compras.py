from db.db import get_db
from datetime import date
from api.comunes import formatear_moneda
from dateutil.relativedelta import relativedelta

def get_rem_proveedores():
    error = None
    con, cur = get_db()
    cur.execute("select F.NROFACTURA, F.FECHAF, P.NOMBRE "
                "from faccom F " 
                "join proveedores P "
                "  on P.IDPROVEEDOR = F.PROVEEDOR "
                "where "
                "  FECHAINGRESO = 'today' and "
                "  TIPOFACTURA = 15")
    rows = cur.fetchall()
    data = []
    for row in rows:
        data.append(cur.to_dict(row))
    con.commit()    
    return data, error    

def get_ops():
    error = None
    con, cur = get_db()
    cur.execute("select PP.NROCOMPROBANTE, PP.TOTAL, P.NOMBRE "
                "from PAGOSPROV PP "
                "join proveedores P "
                "  on P.IDPROVEEDOR = PP.IDPROVEEDOR "
                "where "
                "  FECHA = 'today'")
    rows = cur.fetchall()
    data = []
    for row in rows:
        row_dict = cur.to_dict(row)
        row_dict['TOTAL'] = formatear_moneda(row_dict['TOTAL'])
        data.append(row_dict)
    con.commit()    
    return data, error    

