// Función para cargar los datos en las tablas
function cargarDatos() {
    // Obtener fechas desde el formulario
    var fechaDesde = document.getElementById('fecha_desde').value;
    var fechaHasta = document.getElementById('fecha_hasta').value;

    // Realizar solicitud AJAX para obtener datos principales
    $.ajax({
        url: '/get_articulos_ordcompras',
        type: 'GET',
        data: { fecha_desde: fechaDesde, fecha_hasta: fechaHasta },
        success: function(data) {
            // Limpiar tabla principal
            $('#tabla_principal tbody').empty();

            // Llenar tabla principal con datos recibidos
            data.forEach(function(item) {
                $('#tabla_principal tbody').append(
                    '<tr>' +
                    '<td>' + item.articulo + '</td>' +
                    '<td>' + item.precio + '</td>' +
                    '<td>' + item.stock + '</td>' +
                    '<td contenteditable="true"></td>' + // Columna editable para cantidad
                    '<td><input type="number" value="' + item.precio + '"></td>' + // Campo editable para precio
                    '<td><input type="checkbox"></td>' + // Checkbox para selección
                    '</tr>'
                );
            });
        }
    });

    // Realizar solicitud AJAX para obtener datos de stocks
    // Esto es solo un ejemplo, deberás implementar la lógica para obtener los datos de las sucursales
    $.ajax({
        url: '/get_stock_data',
        type: 'GET',
        data: { fecha_desde: fechaDesde, fecha_hasta: fechaHasta },
        success: function(data) {
            // Limpiar tabla de stocks
            $('#tabla_stocks tbody').empty();

            // Llenar tabla de stocks con datos recibidos
            data.forEach(function(item) {
                $('#tabla_stocks tbody').append(
                    '<tr>' +
                    '<td>' + item.sucursal + '</td>' +
                    '<td>' + item.stock + '</td>' +
                    '</tr>'
                );
            });
        }
    });
}

// Función para guardar cambios
$('#guardar_cambios').click(function() {
    // Crear array para almacenar datos modificados
    var cambios = [];

    // Recorrer filas de la tabla principal
    $('#tabla_principal tbody tr').each(function() {
        // Obtener datos de la fila
        var articulo = $(this).find('td:eq(0)').text();
        var cantidad = $(this).find('td:eq(3)').text();
        var precio = $(this).find('td:eq(4) input').val();
        var seleccionado = $(this).find('td:eq(5) input[type="checkbox"]').prop('checked');

        // Agregar datos al array solo si la fila está seleccionada
        if (seleccionado) {
            cambios.push({ articulo: articulo, cantidad: cantidad, precio: precio });
        }
    });

    // Realizar solicitud AJAX para guardar cambios
    $.ajax({
        url: '/save_changes',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(cambios),
        success: function(response) {
            // Actualizar datos en las tablas después de guardar cambios
            cargarDatos();
        }
    });
});

// Llamar a la función cargarDatos al cargar la página
$(document).ready(function() {
    cargarDatos();
});