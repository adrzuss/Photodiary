from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session, current_app
from db.db import get_db;
from api.comunes import getProvincias, allowed_file
from api.api_configuracion import getDatosConfiguracion, actualizarConfiguracion, actualizarConfigInformes, getDatosInformes
from datetime import date
from werkzeug.utils import secure_filename
import os

configuracion_bp = Blueprint('configuracion_bp', __name__, template_folder='templates/configuracion')


@configuracion_bp.route('/abmConfiguracion', methods=['GET', 'POST'])
def abmConfiguracion():
    if 'user' in session:
        idUsuario = session['user_id']
        provincias, error = getProvincias()
        print('veamos la configuración')
        if request.method == 'GET':
            datosConfig, error = getDatosConfiguracion()
            usuario = datosConfig[0]
            #comprobar si existe archivo
            user_folder_docs = os.path.join(current_app.config['UPLOAD_FOLDER'], usuario)
            user_folder_img = os.path.join(current_app.config['IMG_USER_FOLDER'], usuario)
            print(f'doc: {user_folder_docs} - img: {user_folder_img}')
            img_logo = os.path.join(user_folder_img, f"{idUsuario}_logo.jpg")
            pdf_recibo = os.path.join(user_folder_docs, f"{idUsuario}_recibo.pdf")
            print(f'recibo: {pdf_recibo} - avatar: {img_logo}')
            return render_template('configuracion.html', provincias=provincias, datosConfig=datosConfig, im_logo=img_logo, pdf_recibo=pdf_recibo)
        elif request.method == 'POST': 
            usuario = request.form['usuario']
            provincia = request.form['provincia']
            celular = request.form['celular']
            mail = request.form['mail']
            empresa = request.form['empresa']
            interesCuota = request.form['interesCuota']
            interesPunitorio = request.form['interesPunitorio']
            if request.form.get('controlProductos') != None:
                controlProductos = 'S'
            else:
                controlProductos = 'N'
                
            # comprobamos y cargamos los archivos
            
            # Verificamos si el POST request tiene el campo 'pdf_file'
            if 'recibo' not in request.files:
                return 'No pdf_file part', 400
    
            pdf_recibo = request.files['recibo']
    
            # Verificamos si el POST request tiene el campo 'logo'
            if 'logo' not in request.files:
                return 'No logo part', 400
    
            logo = request.files['logo']    
            
            # Si el usuario no selecciona un archivo, el navegador también enviará un archivo vacío sin nombre
            if pdf_recibo.filename == '' or logo.filename == '':
                return 'No selected file', 400
            
            if pdf_recibo and allowed_file(pdf_recibo.filename) and logo and allowed_file(logo.filename):
                pdf_recibo_ext = pdf_recibo.filename.rsplit('.', 1)[1].lower()
                logo_ext = logo.filename.rsplit('.', 1)[1].lower()
                
                # Generamos los nuevos nombres de archivo
                pdf_new_filename_recibo = f"{idUsuario}_recibo.{pdf_recibo_ext}"
                logo_new_filename = f"{idUsuario}_logo.{logo_ext}"
                
                pdf_new_filename_recibo = secure_filename(pdf_new_filename_recibo)
                logo_new_filename = secure_filename(logo_new_filename)
                
                # Creamos directorio para el usuario si no existe
                user_folder_docs = os.path.join(current_app.config['UPLOAD_FOLDER'], usuario)
                os.makedirs(user_folder_docs, exist_ok=True)
                
                user_folder_img = os.path.join(current_app.config['IMG_USER_FOLDER'], usuario)
                os.makedirs(user_folder_img, exist_ok=True)
                
                # Guardamos los archivos
                pdf_recibo.save(os.path.join(user_folder_docs, pdf_new_filename_recibo))
                logo.save(os.path.join(user_folder_img, logo_new_filename))
            else:
                return 'File type not allowed', 400
            
            #-----------------------    
            error = actualizarConfiguracion(usuario, provincia, celular, mail, empresa, interesCuota, interesPunitorio, controlProductos)
            datosConfig, error = getDatosConfiguracion()
            flash("Datos de configuración grabados")      
            return render_template('configuracion.html', provincias=provincias, datosConfig=datosConfig)
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))

@configuracion_bp.route('/configInformes', methods=['GET', 'POST'])
def configInformes():
    if 'user' in session:
        if request.method == 'GET':
            datosInformes, error = getDatosInformes()
            return render_template('config-informes.html', datosInformes=datosInformes)
        elif request.method == 'POST': 
            usuario = request.form['usuario']
            provincia = request.form['provincia']
            celular = request.form['celular']
            mail = request.form['mail']
            empresa = request.form['empresa']
            interesCuota = request.form['interesCuota']
            interesPunitorio = request.form['interesPunitorio']
            if request.form.get('controlProductos') != None:
                controlProductos = 'S'
            else:
                controlProductos = 'N'
            
            error = actualizarConfigInformes()
            datosConfig, error = getDatosInformes()
            flash("Datos de configuración grabados")      
            return render_template('config-informes.html', datosConfig=datosConfig)
    else:
        flash("Finalizó el tiempo de la sesión. Debe reingresar")      
        return redirect(url_for('index'))