from flask import Flask, request, jsonify
from flask_cors import CORS  
import pandas as pd
import pickle
import os
from sklearn.metrics import mean_squared_error
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir todos los orígenes


# DIRECTORIOS SERIES Y MODELOS
"""
Ajustar los directorios de las series y modelos guardados. Recordar tener siempre una backup porque la API sobreescribirá todo.
"""
series_dir = './series/'
modelos_dir = './modelos/'



# FUNCIONES------------------------------------------------------------------------------------------------------------------------------
def cargar_serie(alimento):
    """
    Función que devuelve un dataframe de la serie a analizar. El nombre de la serie guardada debe tener un 
    formato específico: 'serie_nombrealimento.csv'. 

    Args:
        alimento (str): El nombre del alimento para el cual se desea cargar la serie. El nombre debe ser tal 
                        como se encuentra en el archivo, por ejemplo, 'T.FRUTAS FRESCAS'. Esto se fija en la 
                        interfaz de usuario con lista desplegable para evitar introducir un nombre erróneo. 

    Returns:
        pd.DataFrame: DataFrame de la serie correspondiente al alimento.
    """
    file_path = os.path.join(series_dir, f"serie_{alimento}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        raise FileNotFoundError(f"Serie para {alimento} no encontrada.")


def cargar_modelo(alimento):
    """
    Función para cargar el modelo de la sere seleccionado desde un archivo en formato pickle. 

    Args:
        alimento (str): El nombre del alimento para el cual se desea cargar la serie. El nombre debe ser tal 
                        como se encuentra en el archivo, por ejemplo, 'T.FRUTAS FRESCAS'. Esto se fija en la 
                        interfaz de usuario con lista desplegable para evitar introducir un nombre erróneo. 

    Returns:
        MODELO: El modelo cargado desde el archivo pickle.
    """
    file_path = os.path.join(modelos_dir, f"modelo_{alimento}.pkl")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)

def guardar_modelo(modelo, alimento):
    """
    Función para guardar un modelo en un archivo pickle.

    Args:
        modelo: El modelo que deseas guardar.
        alimento (str): El nombre del alimento para nombrar el archivo de modelo.
    """
    # Crear el directorio si no existe
    if not os.path.exists(modelos_dir):
        os.makedirs(modelos_dir)

    # Definir la ruta del archivo
    file_path = os.path.join(modelos_dir, f"modelo_{alimento}.pkl")

    # Guardar el modelo en un archivo pickle
    with open(file_path, 'wb') as file:
        pickle.dump(modelo, file)

    print(f"Modelo guardado correctamente en {file_path}")



def generar_fechas_a_partir_del_año(year):
    """
    Genera una lista de fechas con el formato %Y-%m-01.

    Args:
        year (int): El año a partir del cual se generarán las fechas. 

    Returns:
        List[str]: Una lista de fechas en formato de cadena ('YYYY-MM-DD') correspondientes al primer día de cada mes del año especificado.
    """
    fechas = []
    
    # Generar las fechas para cada mes del año especificado
    for mes in range(1, 13):  # Meses de 1 a 12
        fecha_futuro = pd.Timestamp(year=year, month=mes, day=1)
        fechas.append(fecha_futuro.strftime('%Y-%m-%d'))
    return fechas


# ENDPOINTS API------------------------------------------------------------------------------------------------------------------------------
@app.route('/obtener_fechas', methods=['GET'])
def obtener_fechas():
    """
    Obtiene una lista de fechas a partir del último año de una serie de datos para el alimento especificado.

    Returns:
        JSON: Un objeto JSON que contiene una lista de fechas generadas a partir del último año disponible en 
              la serie de datos.
    """
    # Obtener el parámetro 'alimento' de la solicitud
    alimento = request.args.get('alimento')

    try:
        # Cargar la serie para el alimento especificado
        serie_old = cargar_serie(alimento)
        serie_old['Fecha'] = pd.to_datetime(serie_old['Fecha'], format='%Y-%m-%d')
        serie_old = serie_old.set_index('Fecha')
        serie_old = serie_old.sort_index()

        # Obtener el último año del DataFrame
        ultimo_year = serie_old.index[-1].year
        ultimo_year =ultimo_year +1
        # Generar las fechas a partir de la última fecha
        fechas = generar_fechas_a_partir_del_año(ultimo_year)
        return jsonify({"fechas": fechas})
    
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ocurrió un error inesperado."}), 500
    


@app.route('/enviar', methods=['POST'])
def enviar_datos():
    data = request.get_json()
    alimento = data.get('alimento')
    #año_entrante = data.get('año')

    # Crear el DataFrame a partir de los datos recibidos:
    # DF1: Datos año introducido
    df = pd.DataFrame({
        'Fecha': data['fechas'],
        'CONSUMO X CAPITA': data['consumo'],
        'PRECIO MEDIO kg ó litros': data['precio'],
        'GASTO X CAPITA': data['gasto']
    })
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%d')
    df = df.set_index('Fecha')
    df = df.sort_index()

    
    # DF2: Datos variables exógenas para pronosticar el nuevo año
    df_exog_new=pd.DataFrame({
        'PRECIO MEDIO kg ó litros': data['precio_exogenas'],
        'GASTO X CAPITA': data['gasto_exogenas']
    })
    df_exog_new['GASTO X CAPITA'] = pd.to_numeric(df_exog_new['GASTO X CAPITA'], errors='coerce')
    df_exog_new['PRECIO MEDIO kg ó litros'] = pd.to_numeric(df_exog_new['PRECIO MEDIO kg ó litros'], errors='coerce')
    
      
    # DF3: Cargar la serie existente para el alimento seleccionado
    serie_old = cargar_serie(alimento)
    serie_old['Fecha'] = pd.to_datetime(serie_old['Fecha'], format='%Y-%m-%d')
    serie_old = serie_old.set_index('Fecha')
    serie_old = serie_old.sort_index()
    
    # Obtener el año de la primera fecha de df
    año_nuevo = df.index.year[0]

    # Comprobar si el año de df ya existe en serie_old
    if año_nuevo in serie_old.index.year:
        print(f'El año {año_nuevo} ya existe en la serie para {alimento}. No se realizará la actualización.')
        return jsonify({'status': 'info', 'message': f'El año {año_nuevo} ya existe en la serie para {alimento}. No se realizará la actualización.'})
    
    else:
        # 1.ACTUALIZAR SERIE CON NUEVOS DATOS
        serie_actualizada = pd.concat([serie_old, df]).sort_index()
        serie_actualizada['GASTO X CAPITA'] = pd.to_numeric(serie_actualizada['GASTO X CAPITA'], errors='coerce')
        serie_actualizada['PRECIO MEDIO kg ó litros'] = pd.to_numeric(serie_actualizada['PRECIO MEDIO kg ó litros'], errors='coerce')
        serie_actualizada['CONSUMO X CAPITA'] = pd.to_numeric(serie_actualizada['PRECIO MEDIO kg ó litros'], errors='coerce')
        
        # Guardar la nueva serie en un archivo CSV. Vigilar sobreescribe la existente
        #nuevo_csv_path = os.path.join(series_dir, f"serie_{alimento}.csv")
        #serie_actualizada.to_csv(nuevo_csv_path)
        #print(f'Serie para {alimento} guardada correctamente en {nuevo_csv_path}.')
        
        serie_actualizada= serie_actualizada.asfreq('MS')
        serie_actualizada= serie_actualizada.sort_index()
   
        steps=24
        train = serie_actualizada[:-12]
        test = serie_actualizada[-steps:]
        test_old=test[:-12]
        train_old=serie_actualizada[:-24]
        test_new=test[-12:]

        exog_variables = ['GASTO X CAPITA', 'PRECIO MEDIO kg ó litros']
        
        # 2.PRONOSTICO MODELO_OLD
        # Cargar el modelo para el alimento
        modelo = cargar_modelo(alimento)
        modelo.fit(y=train_old['CONSUMO X CAPITA'], exog=train_old[exog_variables]) 
        fcast_SARIMAX_old = modelo.predict(steps=12, exog=test_old[exog_variables])
        rmse_old= np.sqrt(mean_squared_error(test_old['CONSUMO X CAPITA'], fcast_SARIMAX_old))
        
        # 3.PRONOSTICO MODELO_NEW AÑO INTRODUCIDO
        modelo.fit(y=train['CONSUMO X CAPITA'], exog=train[exog_variables])
        fcast_SARIMAX_new = modelo.predict(steps=12, exog=test_new[exog_variables])
        rmse_new = np.sqrt(mean_squared_error(test_new['CONSUMO X CAPITA'], fcast_SARIMAX_new))
        

        rmse_new=0.00000001#Solo para testear

        # 4.COMPARAR RMSE
        # Calcular el porcentaje de cambio en RMSE
        if rmse_old != 0:  # Asegúrate de que rmse_old no sea 0 para evitar división por cero
            porcentaje_cambio = ((rmse_new - rmse_old) / rmse_old) * 100
        else:
            porcentaje_cambio = float('inf')  # Si rmse_old es 0, cualquier cambio será considerado como infinito
        
        # Verificar si el RMSE nuevo se desvía en un 10% o más respecto al antiguo
        if rmse_new > rmse_old and porcentaje_cambio >= 10:
            resultado = f"El RMSE del modelo nuevo ha aumentado en un {porcentaje_cambio:.2f}% respecto al modelo antiguo en el año anterior, lo que representa un empeoramiento."
            return jsonify({
                'status': 'warning',
                'message': resultado,
                'rmse_old': rmse_old,
                'rmse_new': rmse_new,
                'porcentaje_cambio': porcentaje_cambio
            })
        else:
            resultado = "El modelo nuevo se mantiene en los resultados de RMSE del modelo antiguo en el año anterior."

        
        # 5. REENTRENO MODELO CON TODOS LOS DATOS
            modelo.fit(y=serie_actualizada['CONSUMO X CAPITA'], exog=serie_actualizada[exog_variables])
            guardar_modelo(modelo,alimento)
            
        # 6.PRONOSTICO NUEVO AÑO FUTURO    
            fechas_2025 = pd.date_range(start='2025-01-01', end='2025-12-01', freq='MS')
            df_fechas_2025 = pd.DataFrame({'Fecha': fechas_2025 })
            df_combined = df_fechas_2025.join(df_exog_new)
            df_combined = df_combined.set_index('Fecha')
            df_combined.index = pd.to_datetime(df_combined.index)
            df_combined = df_combined.asfreq('MS')

            fcast_SARIMAX_new = modelo.predict(steps=12, exog=df_combined)
            fechas_predicciones = fcast_SARIMAX_new.index[-12:].to_period('M').to_timestamp().strftime('%Y-%m-01').tolist()
            valores_predicciones = fcast_SARIMAX_new.values[-12:].tolist()


            # Mostrar el resultado
            print(resultado)
            return jsonify({
                'status': 'success',
                'message': 'Datos recibidos, serie actualizada, y pronóstico calculado correctamente',
                'rmse_old': rmse_old,
                'rmse_new': rmse_new,
                'fecha':fechas_predicciones,
                'prediccion':valores_predicciones,
                'alimento':alimento
            })

if __name__ == '__main__':
    app.run(debug=True)