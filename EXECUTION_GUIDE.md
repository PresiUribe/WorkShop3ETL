# 🚀 GUÍA DE EJECUCIÓN PASO A PASO

## Workshop 3: ETL Process using Apache Kafka + Machine Learning

---

## ⚙️ CONFIGURACIÓN INICIAL (Solo una vez)

### 1. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

1. Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Editar `.env` con tus credenciales de MySQL:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=TU_PASSWORD_AQUI
DB_NAME=happiness_predictions
```

### 3. Crear base de datos en MySQL

Abrir MySQL Workbench y ejecutar el archivo `database/create_database.sql`

O desde terminal:
```bash
mysql -u root -p < database/create_database.sql
```

### 4. Colocar los archivos CSV

Copiar tus 5 archivos CSV en la carpeta `data/raw/`:
- 2015.csv
- 2016.csv
- 2017.csv
- 2018.csv
- 2019.csv

---

## 🔍 VERIFICAR SISTEMA (Opcional pero recomendado)

```bash
cd src
python system_check.py
```

Este script verifica:
- ✓ Python version
- ✓ Paquetes instalados
- ✓ Archivo .env
- ✓ Archivos CSV
- ✓ Conexión a Kafka
- ✓ Conexión a MySQL

---

## 🎯 EJECUCIÓN DEL PROYECTO

### PASO 1: Iniciar Kafka

Abrir **3 ventanas de CMD/Terminal diferentes**:

#### Terminal 1 - Zookeeper
```bash
cd C:\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

#### Terminal 2 - Kafka Server
```bash
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

#### Terminal 3 - Crear Topic
```bash
cd C:\kafka
.\bin\windows\kafka-topics.bat --create --topic happiness-data --bootstrap-server localhost:9092
```

**IMPORTANTE:** Mantener las primeras 2 ventanas abiertas durante todo el proceso.

---

### PASO 2: Entrenar el Modelo

```bash
cd src
python train_model.py
```

**Qué hace este script:**
1. ✅ Carga los 5 CSV files
2. ✅ Combina todos los datos
3. ✅ Limpia datos (maneja valores faltantes)
4. ✅ Divide datos 70% entrenamiento / 30% prueba
5. ✅ Entrena modelo de regresión lineal
6. ✅ Evalúa el modelo (R², MAE, RMSE)
7. ✅ Guarda el modelo en `models/happiness_model.pkl`
8. ✅ Guarda datos de prueba en `data/processed/test_data.csv`

**Salida esperada:**
```
==================================================
HAPPINESS SCORE PREDICTION - MODEL TRAINING
==================================================
Loading CSV files...
  Loaded 2015.csv: 158 rows
  Loaded 2016.csv: 157 rows
  ...
==================================================
MODEL EVALUATION
==================================================
R² Score: 0.9876
Mean Absolute Error (MAE): 0.1234
Root Mean Squared Error (RMSE): 0.1567
==================================================
```

---

### PASO 3: Iniciar Kafka Consumer

Abrir una **nueva terminal**:

```bash
cd src
python kafka_consumer.py
```

**Qué hace este script:**
1. ✅ Carga el modelo entrenado (.pkl)
2. ✅ Se conecta a MySQL
3. ✅ Se conecta a Kafka topic
4. ✅ Espera mensajes del Producer
5. ✅ Hace predicciones para cada mensaje
6. ✅ Guarda resultados en la base de datos

**Salida esperada:**
```
============================================================
KAFKA CONSUMER - HAPPINESS PREDICTION & DATABASE STORAGE
============================================================

Loading model from models/happiness_model.pkl...
✓ Model loaded successfully!
✓ Connected to MySQL database: happiness_predictions
✓ Kafka Consumer connected to topic 'happiness-data'

============================================================
Waiting for messages... (Press Ctrl+C to stop)
============================================================
```

**NO CERRAR ESTA VENTANA** - Dejarla corriendo.

---

### PASO 4: Iniciar Kafka Producer

Abrir **otra nueva terminal**:

```bash
cd src
python kafka_producer.py
```

**Qué hace este script:**
1. ✅ Carga datos de prueba
2. ✅ Se conecta a Kafka
3. ✅ Envía cada registro uno por uno (1 segundo entre cada uno)
4. ✅ Muestra progreso

**Salida esperada:**
```
============================================================
KAFKA PRODUCER - HAPPINESS DATA STREAMING
============================================================

Loading data from data/processed/test_data.csv...
Loaded 47 records
Kafka Producer connected to localhost:9092

Starting to send records to topic 'happiness-data'...
Delay between messages: 1 second(s)

[1/47] Sent: Denmark (2016) - Partition: 0, Offset: 0
[2/47] Sent: Switzerland (2016) - Partition: 0, Offset: 1
...
```

**OBSERVAR:** En la ventana del Consumer verás las predicciones en tiempo real:

```
[Message 1] Denmark (2016)
  Actual Score:    7.5260
  Predicted Score: 7.5143
  Error:           0.0117
  ✓ Saved to database

[Message 2] Switzerland (2016)
  Actual Score:    7.5090
  Predicted Score: 7.4987
  Error:           0.0103
  ✓ Saved to database
```

---

### PASO 5: Analizar Resultados

Después de que el Producer termine, ejecutar:

```bash
cd src
python analyze_predictions.py
```

**Qué hace este script:**
1. ✅ Se conecta a MySQL
2. ✅ Carga todas las predicciones
3. ✅ Calcula métricas globales (R², MAE, RMSE)
4. ✅ Analiza por región
5. ✅ Analiza por año
6. ✅ Muestra mejores y peores predicciones
7. ✅ Genera visualizaciones en `visualizations/prediction_analysis.png`

**Salida esperada:**
```
============================================================
PREDICTION ANALYSIS FROM DATABASE
============================================================

✓ Connected to database: happiness_predictions
✓ Loaded 47 predictions from database

============================================================
OVERALL METRICS
============================================================
R² Score: 0.9876
MAE: 0.1234
RMSE: 0.1567
Mean Prediction Error: 0.1234
...
```

---

## 📊 VERIFICAR EN MYSQL

Abrir MySQL Workbench y ejecutar:

```sql
USE happiness_predictions;

-- Ver todas las predicciones
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;

-- Ver error promedio por país
SELECT country, 
       AVG(prediction_error) as avg_error,
       COUNT(*) as predictions
FROM predictions
GROUP BY country
ORDER BY avg_error;

-- Ver mejores predicciones
SELECT country, year, 
       actual_happiness_score, 
       predicted_happiness_score,
       prediction_error
FROM predictions
ORDER BY prediction_error
LIMIT 10;
```

---

## 🛑 DETENER EL SISTEMA

### 1. Detener Producer y Consumer
- Ir a cada ventana y presionar `Ctrl + C`

### 2. Detener Kafka Server
- Ir a la ventana del Kafka Server y presionar `Ctrl + C`

### 3. Detener Zookeeper
- Ir a la ventana de Zookeeper y presionar `Ctrl + C`

---

## ❌ SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'kafka'"
```bash
pip install kafka-python
```

### Error: "Cannot connect to MySQL"
- Verificar que MySQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos exista

### Error: "Cannot connect to Kafka"
- Verificar que Zookeeper esté corriendo (puerto 2181)
- Verificar que Kafka esté corriendo (puerto 9092)
```bash
netstat -an | findstr 2181
netstat -an | findstr 9092
```

### Error: "Model file not found"
- Ejecutar primero `train_model.py`
- Verificar que existe `models/happiness_model.pkl`

### Error: "No CSV files found"
- Verificar que los CSV estén en `data/raw/`
- Verificar que tengan extensión .csv

---

## 📋 CHECKLIST DE EJECUCIÓN

Marcar cada paso al completarlo:

- [ ] Instalé dependencias (`pip install -r requirements.txt`)
- [ ] Configuré archivo `.env` con credenciales de MySQL
- [ ] Creé la base de datos ejecutando `create_database.sql`
- [ ] Coloqué mis 5 CSV en `data/raw/`
- [ ] Ejecuté `system_check.py` (opcional)
- [ ] Inicié Zookeeper
- [ ] Inicié Kafka Server
- [ ] Creé el topic de Kafka
- [ ] Ejecuté `train_model.py` exitosamente
- [ ] Inicié `kafka_consumer.py`
- [ ] Inicié `kafka_producer.py`
- [ ] Vi predicciones en tiempo real en el Consumer
- [ ] Ejecuté `analyze_predictions.py`
- [ ] Verifiqué resultados en MySQL Workbench
- [ ] Generé visualizaciones en PowerBI/Tableau/Looker

---

## 🎓 ENTREGABLES PARA EL WORKSHOP

1. ✅ README.md
2. ✅ Notebook/Script de entrenamiento con modelo .pkl
3. ✅ Código de Kafka Producer
4. ✅ Código de Kafka Consumer
5. ✅ Base de datos con predicciones
6. ✅ Visualizaciones (PowerBI/Tableau/Looker)
7. ✅ Reporte con:
   - Descripción de datasets
   - Hallazgos de EDA
   - Proceso de entrenamiento
   - Métricas de evaluación
   - Discusión del proceso de streaming

---

**¡Éxito con tu proyecto! 🚀**
