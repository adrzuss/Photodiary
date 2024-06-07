from flask import jsonify, session, url_for
from db.db import get_db
from api.comunes import CustomError
import datetime

def getDatosConfiguracion():
    error = None
    try:
        con, cur = get_db()
        idUser = session['user_id']
        cur.execute('select usr, provincia, celular, mail, empresa, control_productos, interes_cuota, interes_punitorio, logo, foto from usuarios where id = ?', (idUser,))
        configuracion = cur.fetchone()
        con.commit()
        return configuracion, error
    except Exception as e:
        error = e
        print(f'Error conultado configuración: {e}')
        return jsonify({'error': str(e)}), 500

def actualizarConfiguracion(usuario, provincia, celular, mail, empresa, interesCuota, interesPunitorio, controlProductos):
    error = None
    try:
        con, cur = get_db()
        idUser = session['user_id']
        cur.execute('update usuarios set usr = ?, provincia = ?, celular = ?, mail = ?, empresa = ?, control_productos = ?, interes_cuota = ?, interes_punitorio = ? where id = ?', (usuario, provincia, celular, mail, empresa, controlProductos, interesCuota, interesPunitorio, idUser))
        con.commit()
        return idUser, error
    except Exception as e:
        error = e
        print(f'Error conultado configuración: {e}')
        return jsonify({'error': str(e)}), 500    
    
def actualizarConfigInformes():
    pass

def getDatosInformes():
    error = None
    datosInformes = []
    return datosInformes, error
#datosConfig, error 