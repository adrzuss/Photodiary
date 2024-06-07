from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from api.api_creditos import get_cant_cred_sucursales, get_cant_clientes_cred, get_cobranzas_cred, get_cobranzas_sucs
from db.db import get_db;
from datetime import date

creditos_bp = Blueprint('creditos_bp', __name__, template_folder='templates/creditos')

@creditos_bp.route("/creditos_otorgados")
def creditos_otorgados():
    if request.method == 'GET':
        desde = request.args.get('fechaDesde')
        hasta = request.args.get('fechaHasta')
        if desde == None:
            desde = date.today()
        if hasta == None:
            hasta = date.today()
    
    rows, error = get_cant_cred_sucursales(desde, hasta)
    if error == None:
        creditos = []
        sucursales = []
        for row in rows:
            creditos.append(row['CANT_OP_CRE'])
            sucursales.append(row['SUCURSAL'])
    rows, error = get_cant_clientes_cred(desde, hasta)    
    clientesCred = []
    clientesCred.append(rows[0]['CANT_CRED_CLIENTES_NUEVOS'])
    clientesCred.append(rows[0]['CANT_CRED'])
    clientesLeyendas = ['Clientes nuevos','Clientes']
   
    return render_template('creditos-otorgados.html', fechaDesde=desde, fechaHasta=hasta, creditos=creditos, sucursales=sucursales, clientesCred=clientesCred, clientesLeyendas=clientesLeyendas)
    
    
@creditos_bp.route("/cobranzas_creditos")
def cobranzas_creditos():
    if request.method == 'GET':
        desde = request.args.get('fechaDesde')
        hasta = request.args.get('fechaHasta')
        if desde == None:
            desde = date.today()
        if hasta == None:
            hasta = date.today()
    
    cobranzas, error = get_cobranzas_cred(desde, hasta)
    
    rows, error = get_cobranzas_sucs(desde, hasta)
    if error == None:
        cobranzasSucs = []
        sucursales = []
        for row in rows:
            cobranzasSucs.append(row['TOT_VENCIMIENTOS'])
            sucursales.append(row['NOM_SUC'])
        print(cobranzasSucs)
        print(sucursales)
    if error == None:
        return render_template('cobranzas-creditos.html', fechaDesde=desde, fechaHasta=hasta, cobranzas=cobranzas, cobranzasSucs=cobranzasSucs, sucursales=sucursales)
    
