from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from api.api_usuarios import get_datos_usuario, grabar_datos_usuario
from datetime import date
from api.comunes import formatear_moneda

usuarios_bp = Blueprint('usuarios_bp', __name__, template_folder='templates/usuarios')

@usuarios_bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'GET':
        usr = session['user_id']
        datos, error = get_datos_usuario(usr)
        return render_template('perfil.html', datos=datos)
    if request.method == 'POST':
        usr = session['user_id']
        datos = {}
        datos["nombre"] = request.form['Nombre']
        datos["apellido"]  = request.form['Apellido']
        datos["provincia"] = request.form['Provincia']
        datos["email"]= request.form['Email']
        datos["celular"] = request.form['Celular']
        datos["usuario"] = request.form['Usuario']
        datos["empresa"] = request.form['Empresa']
        error = grabar_datos_usuario(datos, usr)
        if error == None:
            flash("Datos de usuario grabados")
            return redirect( url_for('tablero'))
        else:    
            flash(f"Error grabando datos de usuario: {error}", "error")
            return redirect( url_for('usuarios_bp.perfil'))