document.addEventListener("DOMContentLoaded", function () {
    function actualizarFechas() {
        const alimentoSeleccionado = document.getElementById('alimentos').value;

        console.log('Alimento seleccionado:', alimentoSeleccionado);

        if (alimentoSeleccionado === "") {
            alert("Por favor, selecciona un alimento.");
            return;
        }

        fetch(`http://127.0.0.1:5000/obtener_fechas?alimento=${encodeURIComponent(alimentoSeleccionado)}`)
        .then(response => response.json())
        .then(data => {
            console.log('Datos recibidos:', data);

            if (data.fechas && Array.isArray(data.fechas)) {
                const camposFecha = document.querySelectorAll('input[id^="field"]');
                console.log('Campos de fecha encontrados:', camposFecha);

                if (camposFecha.length < data.fechas.length) {
                    console.error('No hay suficientes campos de fecha en el formulario.');
                    return;
                }

                camposFecha.forEach((campo, index) => {
                    if (index < data.fechas.length) {
                        campo.value = data.fechas[index];
                        console.log(`Campo ${campo.id} actualizado con la fecha: ${data.fechas[index]}`);
                    }
                });
            } else {
                console.error('Error al obtener las fechas:', data.error);
            }
        })
        .catch(error => {
            console.error('Error al obtener las fechas:', error);
        });
    }
    let chartInstance = null;  // Variable global para almacenar la instancia del gráfico

    function renderizarGrafico(data) {
        const ctx = document.getElementById('prediccionesChart').getContext('2d');
    
        // Si ya existe un gráfico, destrúyelo
        if (chartInstance) {
            chartInstance.destroy();
        }
        //Obtener el nombre del alimento desde los datos
        const alimento = data.alimento || 'Alimento Desconocido'; // Utiliza un nombre predeterminado si no se encuentra el alimento

        // Crear un nuevo gráfico
        chartInstance = new Chart(ctx, {
            type: 'line', // Tipo de gráfico
            data: {
                labels: data.fecha, // Las fechas son las etiquetas del gráfico
                datasets: [{
                    label: `Predicciones ${alimento}`,
                    data: data.prediccion, // Datos de las predicciones
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    x: {

                        title: {
                            display: true,
                            text: 'Fecha'
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 12
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Consumo per cápita'
                        }
                    }
                }
            }
 
        });
    }
    

    document.getElementById('actualizarFechas').addEventListener('click', actualizarFechas);

    document.getElementById('consumoForm').addEventListener('submit', function (event) {
        event.preventDefault();

        const alimentoSeleccionado = document.getElementById('alimentos').value;
        console.log('Alimento seleccionado en el envío del formulario:', alimentoSeleccionado);

        const consumo = Array.from(document.querySelectorAll('input[name="consumo[]"]')).map(input => input.value);
        const gasto = Array.from(document.querySelectorAll('input[name="gasto[]"]')).map(input => input.value);
        const precio = Array.from(document.querySelectorAll('input[name="precio[]"]')).map(input => input.value);
        const gastoExogenas = Array.from(document.querySelectorAll('input[name="gasto_exogenas[]"]')).map(input => input.value);
        const precioExogenas = Array.from(document.querySelectorAll('input[name="precio_exogenas[]"]')).map(input => input.value);

        console.log('Valores de consumo:', consumo);
        console.log('Valores de gasto:', gasto);
        console.log('Valores de precio:', precio);
        console.log('Valores de gasto exógeno:', gastoExogenas);
        console.log('Valores de precio exógeno:', precioExogenas);
        

        const datosEnviar = {
            fechas: Array.from(document.querySelectorAll('input[id^="field"]')).map(input => input.value),
            alimento: alimentoSeleccionado,
            consumo: consumo,
            gasto: gasto,
            precio: precio,
            gasto_exogenas: gastoExogenas,
            precio_exogenas: precioExogenas
        };

        console.log('Datos a enviar a la API:', datosEnviar);

        fetch('http://127.0.0.1:5000/enviar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosEnviar)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta de la API:', data);
            alert('Datos enviados correctamente!');

            // Renderizar gráfico con los datos de la respuesta
            renderizarGrafico(data);

            // Limpiar los campos del formulario
            document.getElementById('consumoForm').reset();
            const camposFecha = document.querySelectorAll('input[id^="field"]');
            camposFecha.forEach(campo => campo.value = '');
            document.getElementById('alimentos').selectedIndex = 0;
        })
        .catch(error => {
            console.error('Error al enviar los datos:', error);
            alert('Ocurrió un error al enviar los datos.');
        });
    });
});
