# Airflow_Prediction
Predicción basada en datos de temperatura y humedad utilizando Python y Apache Airflow.

## Requisitos previos
- **Python** 3.7 o superior.
- **Docker** para construir y ejecutar los contenedores.
- **Apache Airflow** (1.10+). Configura la variable `AIRFLOW_HOME` y desactiva la carga de ejemplos con `AIRFLOW__CORE__LOAD_EXAMPLES=False` si es necesario.

## Inicialización del DAG
1. Inicializa Airflow (el comando puede variar según la versión):
   ```bash
   export AIRFLOW_HOME=~/airflow
   airflow db init      # Airflow 2.x
   # o bien
   airflow initdb       # Airflow 1.10
   ```
2. Copia `airflow/tasksAndDAGS.py` al directorio `dags` de tu instalación de Airflow.
3. Arranca el scheduler y el webserver:
   ```bash
   airflow scheduler &
   airflow webserver -p 8080 &
   ```
4. Activa y ejecuta el DAG `forecasting` desde la interfaz web o con:
   ```bash
   airflow dags trigger forecasting
   ```

Al completarse el flujo se crean y despliegan dos microservicios Docker:
- `microservice_v1` escucha en el puerto **80**.
- `microservice_v2` escucha en el puerto **81**.

## Ejecutar los tests
Tras entrenar los modelos (por ejemplo mediante el DAG) puedes lanzar las pruebas unitarias de cada versión:
```bash
cd src/v1
python3 test.py      # pruebas de la versión 1

cd ../v2
python3 test.py      # pruebas de la versión 2
```

Author: Pablo Luque Moreno, University of Granada, Spain
