from flask import Flask, render_template, session, url_for, redirect, request, flash, Response, request, g
import json
from db.db import init_app, get_db
from api.comunes import formatear_moneda
from api.api_clientes import citasDesdeHasta, eventosDesdeHasta, getProximosEventos, getProximasCuotas, getCuotasVencidas, getProximasCitas
from api.api_ventas import cuotasPendPeriodo

from datetime import date, timedelta, datetime
import calendar
from dateutil.relativedelta import relativedelta
from ventas.ventas import ventas_bp
from productos.productos import productos_bp
from acceso.accesos import accesos_bp, logout
from creditos.creditos import creditos_bp
from usuarios.usuarios import usuarios_bp
from compras.compras import compras_bp
from clientes.clientes import clientes_bp
from calendario.calendario import calendario_bp
from configuracion.configuracion import configuracion_bp
from bancos.bancos import bancos_bp

app = Flask('__name__')
app.secret_key = '123456qwerty+_.,102939847566'

# Carpeta donde se guardarán los archivos subidos
UPLOAD_FOLDER = 'uploads/'
IMG_USER_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMG_USER_FOLDER'] = IMG_USER_FOLDER

#app.config['SESSION_PERMANENT'] = False
#app.config['SESSION_TYPE'] = 'filesystem'
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 2)
#app.config['SESSION_REFRESH_EACH_REQUEST'] = True
#app.config['SESSION_COOKIE_HTTPONLY'] = True

app.register_blueprint(ventas_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(accesos_bp)
app.register_blueprint(creditos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(calendario_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(bancos_bp)

#tiempo de la sesion
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
# Configura Flask-Login

@app.before_request
def before_request():
    #tiempo de la sesion
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    g.user = None
    if 'user' in session:
        g.user = session['user']
    else:
        session_ended()

def session_ended():
    logout()

@app.route('/')
def index():
    if ('user' in session):
        print(f'el usuario {session["user"]}')
        return redirect(url_for('tablero'))
    else:
      return render_template('login.html')  

@app.route('/tablero', methods = ['GET'])
def tablero():
    if ('user' in session):
        if request.method == 'GET':
            desde = request.args.get('fechaConsultaDesde')
            hasta = request.args.get('fechaConsultaHasta')
            if desde == None:
                desde = date.today()
            if hasta == None:
                hasta = date.today()
            #Cantidad de eventos    
            meses = []
            eventos = []
            meses.append('Enero')
            meses.append('Febrero')
            meses.append('Marzo')
            meses.append('Abril')
            meses.append('Mayo')
            
            eventos.append('1')
            eventos.append('3')
            eventos.append('3')
            eventos.append('2')
            eventos.append('5')
            #Fin cant. eventos
            #Tipo eventos
            tipoEventos = []
            tipoEventos.append('Boda')
            tipoEventos.append('XV')
            tipoEventos.append('Bautismo')
            cantTipoEventos = []
            cantTipoEventos.append(5)
            cantTipoEventos.append(7)
            cantTipoEventos.append(2)
            #Fin tipo eventos
            #Cantidad citas
            desde = date.today()
            hasta = date.today()
            citasHoy, error = citasDesdeHasta(desde, hasta)
            start = desde - timedelta(days=desde.weekday())
            end = start + timedelta(days=6)
            hasta = end
            citasSemana, error = citasDesdeHasta(desde, hasta)
            #Fin cantidad citas
            
            desdeMes = datetime.today().replace(day=1)
            hastaMes = desdeMes + relativedelta(day = calendar.monthrange(desdeMes.year, desdeMes.month)[1])
            eventosDelMes, error = eventosDesdeHasta(desdeMes, hastaMes)
            error, pendientesEsteMes = cuotasPendPeriodo(desdeMes, hastaMes)
                        
            desdeMesQueViene = desdeMes + relativedelta(months = 1)
            hastaMesQueViene = desdeMesQueViene + relativedelta(day = calendar.monthrange(desdeMesQueViene.year, desdeMesQueViene.month)[1])
            eventosProximoMes, error = eventosDesdeHasta(desdeMesQueViene, hastaMesQueViene)
            error, pendientesProximoMes = cuotasPendPeriodo(desdeMesQueViene, hastaMesQueViene)
            proximosEventos, error = getProximosEventos()
            proximasCuotas, error = getProximasCuotas()
            cuotasVencidas, error = getCuotasVencidas()
            proximasCitas, error = getProximasCitas()
            return render_template('tablero.html', meses=meses, eventos=eventos, tipoEventos=tipoEventos, cantTipoEventos=cantTipoEventos, citasHoy=citasHoy,
                                                   citasSemana=citasSemana, eventosDelMes=eventosDelMes, eventosProximoMes=eventosProximoMes, pendientesEsteMes=pendientesEsteMes,
                                                   pendientesProximoMes=pendientesProximoMes, proximosEventos=proximosEventos, proximasCuotas=proximasCuotas,
                                                   cuotasVencidas=cuotasVencidas, proximasCitas=proximasCitas)
        
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))    


@app.route('/en_construccion')
def en_construccion():
    return render_template('under-construction.html')

@app.route('/tablas')
def tablas():
    return render_template('tables.html')

if __name__ == '__main__':
    init_app(app)
    app.run(debug = True)
    
    