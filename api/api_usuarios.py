from flask import session, current_app
from db.db import get_db
from datetime import datetime, date
import mariadb
import hashlib
import os


def registrar_usuario(nombre, apellido, provincia, localidad, email, celular, clave, usuario, nombreEmpresa):
    error = None
    con, cur = get_db()
    cur.execute("select nombre, apellido from usuarios where mail = ? ", (email,))
    for (nombre, apellido) in cur:
        error = 'El usuario ya existe'
        return error
    
    try:
        alta = date.today()
        idProvincia = 1
        sentencia = "insert into usuarios(nombre, apellido, usr, clave, mail, provincia, celular, alta, empresa) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        datos = (nombre, apellido, usuario, clave, email, idProvincia, celular, alta, nombreEmpresa)
        cur.execute(sentencia, datos)    
    except mariadb.Error as e:
        error = f'Error registrando datos de usuario: {e}'  
        print(error)      
    con.commit()    
    return error    

def check_usr_credentials(usr, clave):
    error = None
    con, cur = get_db()
    #md5 = hashlib.md5(clave.encode())
    #clave = md5.hexdigest()
    cur.execute("select id, usr, nombre, apellido, empresa from usuarios where usr = ? and clave = ?", (usr, clave))
    row = cur.fetchone()
    usuario = {}
    if row == None:
        error = {'error': 'usuario y/o contraseña inválidos'}
    else:    
        usuario['Id'] = row[0]
        usuario['Usuario'] = row[1]
        usuario['Nombre'] = row[3] + ', ' + row[2]
        usuario['Empresa'] = row[4]
        user_folder_img = os.path.join(current_app.config['IMG_USER_FOLDER'], str(usuario['Id']))
        usuario['avatar'] = os.path.join(user_folder_img, f"{usuario['Id']}_logo.jpg")
    con.commit()    
    return usuario, error

def get_usr_data(usr):
    error = None
    con, cur = get_db()
    #md5 = hashlib.md5(clave.encode())
    #clave = md5.hexdigest()
    cur.execute("select U.ID, U.USUARIO, trim(U.NOMBRE) NOMBRE from credenciales_usuario U where U.USUARIO = ?", (usr,))
    row = cur.fetchone()
    usuario = {}
    if row == None:
        error = {'error': 'usuario no encontrado'}
    else:    
        usuario = cur.to_dict(row)  
    con.commit()    
    return usuario, error

def save_usr_log(usuario, autorizacion, mensaje, tipoMsg, cripPass):
    error = None
    #con, cur = get_db()
    hora = datetime.now().time()
    dia = datetime.today()
    #grabar el ingreso al sistema
    #cur.execute("insert into autorizaciones (HORA, MENSAJE, AUTORIZACION, IDEMPLEADO, FECHA, TIPO_MSG, USUARIO) values(?, ?, ?, ?, ?, ?, ?)", (hora, mensaje, autorizacion, usuario, dia, tipoMsg, cripPass))
    #con.commit()
    return error

def get_user_db(usr, clave):
    error = None
    con, cur = get_db()
    #IP servidor
    userDB = {}
    cur.execute("select NOMBRE_EMPRESA, SERVER_HOST, PORT_HOST, PATH_HOST, BDNAME_HOST "
                "from credenciales_usuario U "
                "where "
                "U.USUARIO = ? and U.CLAVE = ?", (usr, clave))
    row = cur.fetchone()
    dato = {}
    if row == None:
        error = {'error': 'Error obteniendo configuración de la base de datos'}
    else:    
        dato = cur.to_dict(row)    
    userDB['NOMBRE_EMPRESA'] = dato["NOMBRE_EMPRESA"]    
    userDB['IPBD'] = dato["SERVER_HOST"]    
    userDB['PORTBD'] = dato["PORT_HOST"]
    userDB['PASOBD'] = dato["PATH_HOST"]
    userDB['ARCHIVOBD'] = dato["BDNAME_HOST"]
    
    con.commit() 
    return userDB, error 

def get_datos_usuario(usuario):
    error = None
    con, cur = get_db()
    usuario = session['user_id']
    print(f'usuario: {usuario}')
    cur.execute("select nombre, apellido, usr, clave, mail, provincia, celular, empresa from usuarios where id = ?", (usuario,))
    row = cur.fetchone()
    datos = {}
    datos['nombre'] = row[0] 
    datos['apellido'] = row[1]
    datos['usr'] = row[2]
    datos['clave'] = row[3]
    datos['mail'] = row[4]
    datos['provincia'] = row[5]
    datos['celular'] = row[6]
    datos['empresa'] = row[7]
    print(row[7])
    print(datos['empresa'])
    con.commit()
    return datos, error

def grabar_datos_usuario(usuario, id_usr):
    error = None
    try:
      con, cur = get_db()
      datos = (usuario['nombre'], usuario['apellido'], usuario['usuario'], usuario['email'], usuario['provincia'], usuario['celular'], usuario['empresa'], id_usr)
      cur.execute("update usuarios set nombre = ?, apellido = ?, usr = ?, mail = ?, provincia = ?, celular = ?, empresa = ? where id = ?", (datos))
      con.commit()
    except mariadb.Error as e:
        error = f'Error grabando datos de usuario: {e}'
    return error      