from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from db.db import get_db;
from datetime import datetime, timedelta

calendario_bp = Blueprint('calendario_bp', __name__, template_folder='templates/calendario')

@calendario_bp.route('/calendario')
def calendario():
    """
    desde = date.today()
    hasta = date.today()
    db, cur = get_db()
    idUsuario = session['user_id']
    cur.execute("select fecha, hora, nombre_evento from eventos where idusuario = ? and fecha between ? and ?", (idUsuario, desde, hasta))
    ev = cur.fetchall()
    eventos = [] 
    for evento in ev:
        fecha = evento[0].strftime("%Y-%m-%d")
        e = {'title': evento[2], 'start': fecha, 'color': 'blue'}
        eventos.append(e)    
    db.commit()
    cur.execute("select c.dia, c.hora, cli.nombre, cli.apellido "
                "from citas c "
                "join clientes cli "
                "  on cli.id = c.idcliente "
                "where "
                "cli.idusuario = ? and c.dia between ? and ?", (idUsuario, desde, hasta))
    ct = cur.fetchall()
    for cita in ct:
        fecha = cita[0].strftime("%Y-%m-%d")
        e = {'title': cita[3] + ' ' + cita[2] , 'start': fecha, 'color': 'red'}
        eventos.append(e)
    """
    
    return render_template('calendario.html')


@calendario_bp.route('/getEventos', methods=['GET'])
def getEventos():
    print('En get eventos')
    desde = request.args.get('start')
    hasta = request.args.get('end')
    print(f'Desde: {desde} - hasta: {hasta}')
    idUsuario = session['user_id']
    db, cur = get_db()
    cur.execute("select e.fecha, e.hora, e.nombre_evento, te.color "
                "from eventos e "
                "join tipo_eventos te "
                "  on te.id = e.tipo_evento and te.idusuario = e.idusuario "
                "where e.idusuario = ? and e.fecha between ? and ?", (idUsuario, desde, hasta))
    ev = cur.fetchall()
    print('eventos')
    print(ev)
    events = [] 
    for evento in ev:
        fecha = evento[0].strftime("%Y-%m-%d")
        color = evento[3]
        e = {'title': 'Evento: ' + evento[2], 'start': fecha, 'color': color}
        events.append(e)    
    db.commit()
    cur.execute("select c.dia, c.hora, cli.nombre, cli.apellido, te.color "
                "from citas c "
                "join clientes cli "
                "  on cli.id = c.idcliente "
                "join tipo_eventos te "
                "  on te.id = c.idtipo_evento and te.idusuario = cli.idusuario "
                "where "
                "cli.idusuario = ? and c.dia between ? and ?", (idUsuario, desde, hasta))
    ct = cur.fetchall()
    print('citas')
    print(ct)
    for cita in ct:
        fecha = cita[0].strftime("%Y-%m-%d")
        hora = str(cita[1])
        hora2 = str(cita[1] + timedelta(minutes=30))
        
        diaHora = fecha + 'T' + hora
        diaHora2 = fecha + 'T' + hora2
        color = cita[4]
        print(f'diahora: {diaHora}')
        e = {'title': 'Cita: ' + cita[3] + ' ' + cita[2] , 'start': diaHora, 'end': diaHora2, 'allDay': 'false', 'color': color}
        events.append(e)
        print(events)
    return jsonify(events)
