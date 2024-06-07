from flask import flash, session, jsonify
from db.db import get_db
import locale

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class CustomError(Exception): 
    def __init__(self, message): 
        super().__init__(message)

def formatear_moneda(valor):
    # Configurar la localización a la configuración regional del sistema
    locale.setlocale(locale.LC_ALL, 'es_AR')

    # Formatear el valor como moneda
    valor_formateado = locale.currency(valor, grouping=True)

    return valor_formateado

def redondear(valor, decimales):
    return round(valor, decimales)

def getProvincias():
    try:
        error = None
        con, cur = get_db()
        cur.execute("select id, provincia from provincias")
        provincias = cur.fetchall()
        con.commit()    
        #provincias = {provincia[0]: provincia[1] for provincia in row}
        if provincias == None:
            error = {'error': 'provincias no encontradas'}
            raise Exception("No hay provincias cargadas")
        return provincias, error
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def getTipoDoc():
    error = None
    try:
        con, cur = get_db()
        cur.execute("select IDTIPO, NOMBRE from TIPOS where TIPO = '0001'")
        cur.fetchall()
        rows = cur.fetchall()
        data = []
        for row in rows:
            row_dict = cur.to_dict(row)
            data.append(row_dict)
        con.commit()
    except Exception as e:
            flash(f"Error obteniendo tipos de docuemtos:{error}", "error")              
    return data, error

def getPunitorios():
    error = None
    try:
        idUsuario = session["user_id"]
        con, cur = get_db()
        cur.execute('select interes_punitorio from usuarios where id = ?', (idUsuario,))
        punitorios = cur.fetchone()
        con.commit()
        return punitorios, error
    except Exception as e:
        flash('Error obteniendo punitorios', 'error')
        return 0, error

def coord(x, y, unit=1):
    x, y = x * unit, y * unit
    return x, y