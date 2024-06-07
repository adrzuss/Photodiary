from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, after_this_request
from api.api_ventas import getFacturasVta, getPagosPendientes, getPagosRealizados, getDatosReciboPendiente, grabarPagoRecibo, grabarCaja
from api.api_productos import getGrupos, getMarcas
from api.api_bancos import getCuentas
from datetime import date
from api.comunes import formatear_moneda, getPunitorios, coord

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyPDF2 import PdfWriter, PdfReader
import io


ventas_bp = Blueprint('ventas_bp', __name__, template_folder='templates/ventas')

@ventas_bp.route('/facturasVentas', methods=['GET'])
def facturasVentas():
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if desde == None:
            desde = date.today()
        if hasta == None:
            hasta = date.today()
        error, ventas = getFacturasVta(desde, hasta)    
    return render_template('facturas-vta.html', desde = desde, hasta = hasta, ventas=ventas)

@ventas_bp.route('/pagosPendientes', methods=['GET'])
def pagosPendientes():
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if desde == None:
            desde = date.today()
        if hasta == None:
            hasta = date.today()
        error, pendientes = getPagosPendientes(desde, hasta)    
    return render_template('pagos-pendientes.html', desde = desde, hasta = hasta, pendientes=pendientes)

@ventas_bp.route('/pagosRealizados', methods=['GET'])
def pagosRealizados():
    if request.method == 'GET':
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        if desde == None:
            desde = date.today()
        if hasta == None:
            hasta = date.today()
        error, realizados = getPagosRealizados(desde, hasta)    
    return render_template('pagos-realizados.html', desde = desde, hasta = hasta, realizados=realizados)

@ventas_bp.route('/reciboPago/<idcc>', methods=['GET'])
def reciboPago(idcc):
    datosRecibo, error = getDatosReciboPendiente(idcc)
    datosPunitorios, error = getPunitorios()
    cuentasBancarias, error = getCuentas()
    punitorios = datosPunitorios[0]
    vto = datosRecibo[3]
    dias = (date.today() - vto).days
    if dias > 0:
        interes = ((((punitorios*12)/360) * dias)*(datosRecibo[4]))/100
        importeActualizado = datosRecibo[4] + interes
    else:
        importeActualizado = formatear_moneda(datosRecibo[4])
        interes = 0
        dias = 0
    interes = interes
    importeCuota = formatear_moneda(datosRecibo[4])
    hoy = date.today()
    return render_template('recibo-pago.html', idRecibo=idcc, datosRecibo=datosRecibo, importeCuota=importeCuota, dias=dias, hoy=hoy, interes=interes, importeActualizado=importeActualizado, cuentasBancarias=cuentasBancarias)

@ventas_bp.route('/grabarRecibo', methods=['POST'])
def grabarRecibo():
    if request.method == 'POST':
        idcc = request.form['idrecibo']
        pago = request.form['importeActualizado']
        idCliente = request.form['idcliente']
        cliente = request.form['nombre']
        fechaPago = request.form['fechaPago']
        cuota = request.form['cuota']
        evento = request.form['evento']
        
        efectivo = float(request.form['efectivo'])
        cuentaBancaria = request.form['cuentaBancaria']
        banco = float(request.form['banco'])
        detalle = f'{cliente} - pago cuota {cuota} - evento {evento}'

        error = grabarPagoRecibo(idcc)
        error = grabarCaja(fechaPago, efectivo, cuentaBancaria, banco, detalle)
        
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        # Asegúrate de ajustar las coordenadas (x, y) a las posiciones específicas en tu PDF
        can.drawString(*coord(55, 192, mm), f"{cliente}")
        #can.drawString(165, 545, f"{cliente}")
        can.drawString(100, 525, f"{fechaPago}")
        can.drawString(80, 430, f"{evento}")
        can.drawString(80, 400, f"{cuota}")
        can.drawString(380, 170, f"{pago}")
        
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open("modelo_recibo.pdf", "rb"))
        output = PdfWriter()

        for page_num in range(len(existing_pdf.pages)):
            page = existing_pdf.pages[page_num]
            if page_num == 0:
                page.merge_page(new_pdf.pages[0])
            output.add_page(page)

        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        flash('Recibo de pago tenerado')
        return send_file(output_stream, as_attachment=True, download_name=f"recibo_{cliente}_{cuota}.pdf")
        
        
        
"""
        
        # Comprobación de los datos recibidos
        if error is None:
            pdf = FPDF(orientation="landscape", format="A5")
            pdf.add_page()

            # Intentar añadir un logo (ajustar la ruta según corresponda)
            logo_path = 'static/img/users/logo.jpg'
            if os.path.exists(logo_path):
                try:
                    pdf.image(logo_path, 160, 8, 33)
                except Exception as e:
                    print(f"Error al añadir el logo: {e}")

            # Establecer fuente y tamaño de letra
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(0, 10, "Recibo de pago", ln=True)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 20, f"Fecha: {fechaPago}", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Recibí de: {cliente}", ln=True)
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, f"Importe: {pago}", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Detalle: {evento} - {cuota}", ln=True)
            pdf.cell(150, 10, f"Firma y aclaración", ln=True)
            

            # Crear archivo temporal para el PDF
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_file_path = temp_file.name
                pdf.output(temp_file_path)
                print(f"Archivo PDF generado en: {temp_file_path}")

                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(temp_file_path)
                        print(f"Archivo temporal eliminado: {temp_file_path}")
                    except Exception as error:
                        print(f"Error al eliminar el archivo temporal: {error}")
                    return response

                # Usar send_file para enviar el archivo
                return send_file(temp_file_path, as_attachment=True, download_name=f"recibo_{cliente}_{cuota}.pdf", mimetype='application/pdf')
            except Exception as e:
                print(f"Error en generar_pdf: {e}")
                flash('Se produjo un error al generar el PDF')
                return redirect(url_for('clientes_bp.abmClientes', id=idCliente))
        else:   
            print(f"Error en generar_pdf: {e}")
            flash('Se produjo un error al generar el PDF')
            return redirect(url_for('clientes_bp.abmClientes', id=idCliente)) 
"""            
        
        
"""
@ventas_bp.route('/grabarRecibo', methods=['POST'])
def grabarRecibo():
    if request.method == 'POST':
        idcc = request.form['idrecibo']
        pago = request.form['importeActualizado']
        idCliente = request.form['idcliente']
        cliente = request.form['nombre']
        fechaPago = request.form['fechaPago']
        cuota = request.form['cuota']
        evento = request.form['evento']

        error = grabarPagoRecibo(idcc)
        # Comprobación de los datos recibidos
        if error is None:
            pdf = FPDF(orientation="landscape", format="A5")
            pdf.add_page()

            # Intentar añadir un logo (ajustar la ruta según corresponda)
            logo_path = 'static/img/users/logo.jpg'
            if os.path.exists(logo_path):
                try:
                    pdf.image(logo_path, 160, 8, 33)
                except Exception as e:
                    print(f"Error al añadir el logo: {e}")

            # Establecer fuente y tamaño de letra
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(0, 10, "Recibo de pago", ln=True)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 20, f"Fecha: {fechaPago}", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Recibí de: {cliente}", ln=True)
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, f"Importe: {pago}", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Detalle: {evento} - {cuota}", ln=True)
            pdf.cell(150, 10, f"Firma y aclaración", ln=True)
            

            # Crear archivo temporal para el PDF
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_file_path = temp_file.name
                pdf.output(temp_file_path)
                print(f"Archivo PDF generado en: {temp_file_path}")

                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(temp_file_path)
                        print(f"Archivo temporal eliminado: {temp_file_path}")
                    except Exception as error:
                        print(f"Error al eliminar el archivo temporal: {error}")
                    return response

                # Usar send_file para enviar el archivo
                return send_file(temp_file_path, as_attachment=True, download_name=f"recibo_{cliente}_{cuota}.pdf", mimetype='application/pdf')
            except Exception as e:
                print(f"Error en generar_pdf: {e}")
                flash('Se produjo un error al generar el PDF')
                return redirect(url_for('clientes_bp.abmClientes', id=idCliente))
        else:   
            print(f"Error en generar_pdf: {e}")
            flash('Se produjo un error al generar el PDF')
            return redirect(url_for('clientes_bp.abmClientes', id=idCliente)) 
"""        