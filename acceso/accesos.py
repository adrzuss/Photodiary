from flask import Blueprint, request, session, flash, render_template, redirect, url_for, current_app
from api.comunes import getProvincias
from api.api_usuarios import get_usr_data, save_usr_log, check_usr_credentials, get_user_db, registrar_usuario
from datetime import timedelta

accesos_bp = Blueprint('accesos_bp', __name__)

@accesos_bp.route('/ingresar', methods = ['POST'])
def ingresar():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        usuario, error = check_usr_credentials(usuario, clave)
        if error == None:
            session['usr_name'] = usuario['Nombre']
            session['user'] = usuario['Usuario']
            session['user_id'] = usuario['Id']
            session['empresa'] = usuario['Empresa']
            session['avatar'] = usuario['avatar']
            session.permanent = True
            current_app.permanent_session_lifetime = timedelta(minutes=5)
            save_usr_log(usuario['Usuario'], clave, 'Ingreso sistema web', 6666, '')
            return redirect(url_for('tablero'))
        else:
            flash(f"Nombre de usuario y/o clave erroneos", "error")
    return render_template('login.html')

@accesos_bp.route('/registrar', methods = ['POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['registroNombre']
        apellido = request.form['registroApellido']
        provincia = request.form['registroProvincia']
        localidad = request.form['registroLocalidad']
        email = request.form['registroEmail']
        celular = request.form['registroCelular']
        usuario = request.form['registroUsuario']
        clave = request.form['registroClave']
        claveReingreso = request.form['registroRepitoClave']
        nombreEmpresa = request.form['registroEmpresa']
        if clave == claveReingreso:
            #Registro el usuario
            error = registrar_usuario(nombre, apellido, provincia, localidad, email, celular, clave, usuario, nombreEmpresa)
            if error == None:
                flash(f"Su registro fue creado con éxito", "info")
            else:
                errorMsg = f"Error registrando usuario: ", {error}
                flash(errorMsg, "error")  
            return redirect(url_for('index'))
        else:
            flash(f"La clave y la verifiación de clave no coinciden", "error")
            return redirect(url_for('accesos_bp.register'))
    return render_template('login.html')

@accesos_bp.route('/logout')
def logout():
    if 'user' in session:
        flash(f"Sesión finalizada", session['user'])
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('idEmpresa', None)
    session.pop('IPDB', None)
    session.pop('PASODB', None)
    session.pop('ARCHIVODB', None)
    session.pop('PORTDB', None)
    session.pop('DB_CONFIGURADA', None)
    session.pop('EMPRESA', None)
    session.pop('NFANTASIA', None)
    if 'avatar' in session:
        session.pop('avatar')
    return redirect(url_for('index'))    

@accesos_bp.route('/forgot_password')
def forgot_password():
    return render_template('forgot-password.html')    

@accesos_bp.route('/register')
def register():
    provincias, error = getProvincias()
    return render_template('register.html', provincias=provincias)    
