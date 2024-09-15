# ANÁLISIS DEL CONSUMO ALIMENTARIO EN ESPAÑA 
## MODELO DE PRONÓSTICO DE CONSUMO POR GRUPOS DE ALIMENTOS
Este repositorio proporciona un análisis de los datos de consumo alimentario en España, con el objetivo de modelizar el consumo per cápita de diferentes series de alimentos. Los principales componentes del proyecto son:

1. Análisis Exploratorio de Datos (EDA):
Realización de un análisis exhaustivo de los datos de consumo alimentario para identificar patrones, tendencias y anomalías en el comportamiento del consumo.

2. Modelización de Series Temporales:
Estudio End-to-End (E2E) de modelos de series temporales tanto univariantes como multivariantes.

3. Productivización del Modelo:
Creación de una API y una pequeña aplicación web para el despliegue del modelo.

## Datasets
Los datos utilizados en este estudio provienen del Panel de Consumo Alimentario en Hogares, gestionado por el Ministerio de Agricultura, Pesca y Alimentación y elaborado con información proporcionada por TAYLOR NELSON SOFRES S.A.U. Este panel ofrece una visión detallada de la demanda de alimentos en los hogares españoles, incluyendo información sobre las compras realizadas, su costo y las características de los hogares. El panel abarca todos los hogares de la Península, Baleares y Canarias, excluyendo Ceuta y Melilla. Es importante destacar que no se consideran las compras realizadas por empresas, turistas o en establecimientos de hostelería.
La carpeta dataset está organizada en dos subcarpetas principales, cada una con una función específica:

- Dataset_origen:
Contiene los archivos de datos en formato .xlsx que provienen de la fuente original mencionada en el proyecto.Estos archivos son los datos sin procesar que se utilizarán como base para el análisis y la transformación.

- Dataset_final:
Contiene los conjuntos de datos transformados y procesados en formato .csv y .pkl. La diferencia entre el archivo .csv y el .pkl es que en el .pkl solo se incluyen los grupos de alimentos seleccionados, y en el .csv todos los alimentos de la fuente origen. 

## Notebooks
Este repositorio incluye 5 notebooks en Jupyter que detallan cada etapa del análisis y la modelización, así como los resultados obtenidos y las decisiones tomadas durante el proceso.
- TFM_01_crear_datasets: En este primer notebook se desarrolla el dataset de trabajo a partir de la fuente de datos original y se almacenan los nuevos datasets en formato .csv.
- TFM_02_depurar_datasets: En este notebook se depuran los datasets y se almacenan los nuevos en formato pickle y .csv, para que en los siguientes notebooks se trabaje con estos datos.
- TFM_03_exploracion_EDA: Se realiza una exploración de los conjuntos de datos.
- TFM_04_modelos_series: Se lleva a cabo un estudio E2E con diferentes modelos univariantes y multivariantes, evaluando su rendimiento.
- TFM_05_API: Definición de la API y pruebas de comunicación.

## License
El conjunto de datos en este repositorio está licenciado. Consulta el archivo [LICENSE](LICENSE.md) para conocer los derechos y limitaciones de la licencia.

