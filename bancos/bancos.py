from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from api.api_bancos import get_datos_cuenta, getCuentas, actualizarCuenta, agregarCuenta, getMovimientosCuenta
from datetime import date

bancos_bp = Blueprint('bancos_bp', __name__, template_folder='templates/bancos')

@bancos_bp.route('/abmBancos', methods=['GET', 'POST'])
@bancos_bp.route('/abmBancos/<idCuenta>', methods=['GET', 'POST'])
def abmBancos(idCuenta = None):
    if 'user' in session:
        error = None
        datosCuenta = []
        if request.method == 'GET':
            if idCuenta != None:
                datosCuenta, error = get_datos_cuenta(idCuenta)
                print(datosCuenta)
            if idCuenta == '-1':
                datosCuenta = []    
        elif request.method == 'POST':
            idCuenta = request.form['idCuenta']
            cuenta = request.form['cuenta']
            nroCuenta = request.form['nroCuenta']
            cbu = request.form['cbu']
            alias = request.form['alias']
            if idCuenta != '':
                datosCuenta, error = actualizarCuenta(idCuenta, cuenta, nroCuenta, cbu, alias)
            else:    
                datosCuenta, error = agregarCuenta(cuenta, nroCuenta, cbu, alias)
            if error is None:
                flash('Datos de cuenta/billetera grabado')  
            else:
                flash('Error grabando cuenta/billetera', 'error')          
        cuentasBancarias, error = getCuentas()        
        return render_template('abm-bancos.html', cuentasBancarias=cuentasBancarias, datosCuenta=datosCuenta)
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

@bancos_bp.route('/listadoMovimientos', methods=['GET'])
def listadoMovimientos():
    if 'user' in session:
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        cuenta = request.args.get('banco')
        print(f'la cuenta: {cuenta}')
        if desde is None:
            desde = date.today()
        if hasta is None:
            hasta = date.today()
        cuentasBancarias, error = getCuentas()
        movimientos = []
        if cuenta != None:
            movimientos, error = getMovimientosCuenta(cuenta, desde, hasta)
        return render_template('movimientos-bancarios.html', movimientos=movimientos, cuentasBancarias=cuentasBancarias, desde=desde, hasta=hasta)    
    else:        
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))