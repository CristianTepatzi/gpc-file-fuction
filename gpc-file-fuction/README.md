Día 1 — Configuración avanzada de la infraestructura de GCP
1. Descripción del proyecto

Este proyecto corresponde al reto técnico “Día 1 — Configuración avanzada de la infraestructura de GCP”.

El objetivo es implementar una infraestructura básica en Google Cloud Platform (GCP) capaz de recibir archivos mediante un bucket de Cloud Storage, detectar automáticamente cuando se carga un archivo y procesar su información mediante una Cloud Function.

La función obtiene información básica del archivo recibido, como:

Nombre del archivo.
Tamaño.
Tipo de contenido.
Bucket donde fue almacenado.

Posteriormente, esta información es registrada en Cloud Logging, permitiendo comprobar que el flujo de procesamiento funciona correctamente.

2. Objetivo

Implementar y probar una solución serverless en Google Cloud que permita:

Configurar un proyecto de GCP.
Habilitar los servicios necesarios.
Crear y configurar un bucket de Cloud Storage.
Configurar permisos mediante IAM.
Crear una Cloud Function utilizando Python.
Ejecutar automáticamente la función cuando se cargue un archivo.
Registrar información del archivo en Cloud Logging.
Implementar manejo de errores.
Crear pruebas unitarias para validar el comportamiento de la función.
Documentar la infraestructura y las pruebas realizadas.
3. Arquitectura de la solución

El flujo implementado es el siguiente:

                    ┌─────────────────────┐
                    │       Usuario       │
                    │                     │
                    │   Carga un archivo  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Cloud Storage     │
                    │                     │
                    │ gcp-challenge-files │
                    └──────────┬──────────┘
                               │
                               │ Evento:
                               │ Object Finalized
                               ▼
                    ┌─────────────────────┐
                    │      Eventarc       │
                    │                     │
                    │ Detecta el evento   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Cloud Function    │
                    │    process-file     │
                    │                     │
                    │ Python 3.12         │
                    └──────────┬──────────┘
                               │
                               │ Información del
                               │ archivo
                               ▼
                    ┌─────────────────────┐
                    │   Cloud Logging     │
                    │                     │
                    │ Registro de eventos │
                    └─────────────────────┘
Flujo

El funcionamiento de la solución es:

1. Carga del archivo

El usuario coloca un archivo dentro del bucket:

gcp-challenge-files-cristian

2. Generación del evento

Cloud Storage genera un evento cuando el objeto termina de cargarse.

El tipo de evento utilizado es:

google.cloud.storage.object.v1.finalized

3. Eventarc

Eventarc recibe el evento y lo utiliza para activar la Cloud Function.

4. Cloud Function

La función process_file recibe el evento y obtiene:

bucket
name
size
contentType

5. Cloud Logging

La información obtenida se registra para poder consultar posteriormente qué archivo fue procesado.

4. Tecnologías utilizadas
Tecnología	Uso
Google Cloud Platform	Infraestructura cloud
Cloud Storage	Almacenamiento de archivos
Cloud Functions	Procesamiento serverless
Eventarc	Activación mediante eventos
Pub/Sub	Transporte interno utilizado por Eventarc
Cloud Logging	Registro de información y errores
Cloud Build	Construcción y despliegue
Python 3.12	Lenguaje utilizado para la función
pytest	Pruebas unitarias
Cloud Shell	Entorno de desarrollo
5. Proyecto de Google Cloud

El proyecto utilizado para el reto es:

gcp-cloud-challenge-cristian

Número del proyecto:

207578830060

La configuración se puede comprobar mediante:

gcloud config get-value project
6. APIs habilitadas

Para implementar la solución se habilitaron los servicios necesarios de Google Cloud.

Entre los principales servicios utilizados se encuentran:

Cloud Storage
Cloud Functions
Eventarc
Pub/Sub
Cloud Logging
Cloud Build

También existen APIs adicionales utilizadas internamente por los servicios administrados de Google Cloud.

Para consultar las APIs habilitadas:

gcloud services list --enabled

7. Configuración de Cloud Storage

Se creó el bucket:

gcp-challenge-files-cristian

Región:

northamerica-northeast1

Clase de almacenamiento:

STANDARD

El bucket utiliza:

Uniform bucket-level access.
Public Access Prevention heredado.
Soft delete.
Política de ciclo de vida.

7.1 Política de ciclo de vida

Se configuró una política para eliminar automáticamente los objetos después de:

30 días

Esto permite evitar que archivos antiguos permanezcan almacenados indefinidamente.

7.2 Soft Delete

El bucket cuenta con una política de eliminación temporal de:

7 días

Esto permite conservar temporalmente los objetos eliminados antes de su eliminación definitiva.

7.3 Acceso uniforme

Se utiliza:

Uniform bucket-level access: true

Esto permite administrar el acceso mediante IAM a nivel del bucket en lugar de utilizar permisos individuales heredados de objetos.

8. Configuración de IAM

Se configuraron permisos para permitir que los servicios necesarios puedan interactuar correctamente.

También se creó un usuario de prueba mediante una cuenta de servicio:

gcp-test-user@gcp-cloud-challenge-cristian.iam.gserviceaccount.com

Los permisos asignados al usuario de prueba son:

roles/storage.objectCreator
roles/storage.objectViewer

Estos permisos permiten:

Crear objetos dentro del bucket.
Consultar objetos existentes.

No se le asignaron permisos administrativos sobre el proyecto.

9. Cloud Function

La función creada se llama:

process-file

Configuración principal:

Configuración	Valor
Nombre	process-file
Generación	2nd gen
Runtime	Python 3.12
Región	northamerica-northeast1
Entry point	process_file
Trigger	Cloud Storage
Bucket	gcp-challenge-files-cristian
Evento	Object Finalized
10. Código de la función

El archivo principal es:

main.py

Código utilizado:

import logging

import functions_framework
from cloudevents.http import CloudEvent


@functions_framework.cloud_event
def process_file(cloud_event: CloudEvent):
    try:
        data = cloud_event.data

        bucket = data.get("bucket")
        name = data.get("name")
        size = data.get("size")
        content_type = data.get("contentType")

        if not bucket or not name:
            raise ValueError("El evento no contiene bucket o nombre del archivo")

        print(
            f"Archivo recibido | "
            f"bucket={bucket} | "
            f"nombre={name} | "
            f"tamaño={size} bytes | "
            f"tipo={content_type}"
        )

    except Exception:
        logging.exception("Error al procesar el archivo")
        raise
11. Explicación del código
Importación de librerías
import logging

Permite registrar errores y obtener información útil cuando ocurre una excepción.

import functions_framework

Permite utilizar el framework necesario para ejecutar la función en Google Cloud Functions.

from cloudevents.http import CloudEvent

Permite trabajar con los eventos enviados mediante CloudEvents.

Decorador CloudEvent
@functions_framework.cloud_event

Indica que la función recibe un evento CloudEvent.

Esta configuración es importante porque la función no trabaja como una función HTTP tradicional.

Función principal
def process_file(cloud_event: CloudEvent):

La función recibe el evento generado cuando un objeto termina de cargarse en Cloud Storage.

Obtención de información
data = cloud_event.data

Obtiene los datos enviados dentro del evento.

Después se recuperan los datos principales:

bucket = data.get("bucket")
name = data.get("name")
size = data.get("size")
content_type = data.get("contentType")

Estos datos representan:

Variable	Información
bucket	Bucket donde se almacenó el archivo
name	Nombre del archivo
size	Tamaño del archivo
content_type	Tipo MIME del archivo
12. Manejo de errores

Se utiliza:

try:

para intentar procesar el evento.

Posteriormente se valida que existan los datos mínimos necesarios:

if not bucket or not name:
    raise ValueError("El evento no contiene bucket o nombre del archivo")

Si falta alguno de estos valores, se genera un error controlado.

Finalmente:

except Exception:
    logging.exception("Error al procesar el archivo")
    raise

registra información detallada del error y vuelve a lanzar la excepción.

Esto permite que el problema pueda ser identificado posteriormente mediante los registros de Google Cloud.

13. Dependencias

El archivo:

requirements.txt

contiene:

functions-framework==3.*
cloudevents==1.*

Estas dependencias permiten ejecutar la función utilizando el framework de Functions y procesar los eventos CloudEvent.

14. Pruebas unitarias

Para validar el funcionamiento de la función se utilizó:

pytest

Se realizaron dos pruebas principales.

14.1 Prueba de éxito

La primera prueba genera un evento simulado con información válida:

def test_process_file_success(capsys):

Se verifica que la función procese correctamente:

documento.txt
100 bytes
text/plain

También se utiliza:

capsys

para capturar la salida generada por print().

La prueba verifica que la información esperada aparezca en la salida.

14.2 Prueba de error

La segunda prueba genera un evento al que le falta el nombre del archivo.

Se espera que la función genere:

ValueError

Además, se verifica que el error quede registrado mediante:

caplog
15. Resultado de las pruebas

Las pruebas fueron ejecutadas mediante:

pytest -v

Resultado:

test_main.py::test_process_file_success PASSED
test_main.py::test_process_file_error PASSED

2 passed in 0.19s

Por lo tanto:

2 pruebas ejecutadas
2 pruebas exitosas
0 pruebas fallidas
16. Prueba de integración real

Después de validar la función mediante pruebas unitarias, se realizó una prueba utilizando directamente Cloud Storage.

Se creó el archivo:

prueba4.txt

Contenido:

Prueba definitiva de Cloud Functions

Posteriormente se cargó al bucket mediante:

gcloud storage cp prueba4.txt gs://gcp-challenge-files-cristian/

La carga fue exitosa.

El archivo tenía un tamaño de:

37 bytes
17. Resultado de la prueba real

Después de cargar el archivo se consultaron los registros de Cloud Logging.

Se obtuvo el siguiente registro:

Archivo recibido |
bucket=gcp-challenge-files-cristian |
nombre=prueba4.txt |
tamaño=37 bytes |
tipo=text/plain

Esto demuestra que el flujo completo funcionó correctamente:

Cloud Storage
      ↓
Evento Object Finalized
      ↓
Eventarc
      ↓
Cloud Function
      ↓
Procesamiento del archivo
      ↓
Cloud Logging
18. Consulta de logs

Los registros pueden consultarse utilizando:

gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="process-file" AND resource.labels.revision_name="process-file-00004-fus"' \
  --limit 20 \
  --format="value(timestamp,severity,textPayload)"

El registro generado permitió comprobar:

Bucket utilizado.
Nombre del archivo.
Tamaño.
Tipo de contenido.
Fecha y hora del procesamiento.
19. Configuración de Eventarc

La función utiliza un trigger de Eventarc:

process-file-658520

El evento configurado es:

google.cloud.storage.object.v1.finalized

El filtro del bucket es:

gcp-challenge-files-cristian

Esto significa que el trigger se activa cuando un objeto termina de cargarse en ese bucket.

Eventarc utiliza internamente Pub/Sub para transportar el evento hasta el servicio de destino.

20. Revisión de versiones

Durante el desarrollo se realizaron diferentes despliegues de la función.

La versión utilizada finalmente fue:

process-file-00004-fus

Esta revisión recibió el 100 % del tráfico.

El despliegue final quedó en estado:

ACTIVE
21. Problema encontrado durante el desarrollo

Durante una de las primeras pruebas se presentó el siguiente error:

TypeError:
process_file() takes 1 positional argument but 2 were given

El problema se produjo porque inicialmente la función no estaba configurada correctamente para recibir un CloudEvent.

La solución fue utilizar:

@functions_framework.cloud_event

y definir la función como:

def process_file(cloud_event: CloudEvent):

Después de realizar este cambio y volver a desplegar la función, el evento pudo ser recibido correctamente.

22. Validación final

La solución fue validada mediante dos tipos de pruebas:

Pruebas unitarias
2 pruebas
2 exitosas
0 fallidas
Prueba de integración

Se cargó:

prueba4.txt

y la función registró correctamente:

bucket
nombre
tamaño
tipo de contenido

Por lo tanto, se comprobó el funcionamiento de extremo a extremo de la solución.

23. Evidencias

Para complementar la documentación se pueden agregar capturas de pantalla de:

Evidencia 1 — Proyecto GCP

Captura de la consola mostrando:

gcp-cloud-challenge-cristian
Evidencia 2 — Bucket

Captura del bucket:

gcp-challenge-files-cristian

Mostrando su configuración.

Evidencia 3 — Lifecycle

Captura donde se observe:

Delete objects after 30 days
Evidencia 4 — IAM

Captura de los permisos asignados a:

gcp-test-user
Evidencia 5 — Cloud Function

Captura de:

process-file

mostrando que se encuentra activa.

Evidencia 6 — Trigger

Captura de Eventarc mostrando:

google.cloud.storage.object.v1.finalized
Evidencia 7 — Pruebas unitarias

Captura de la terminal mostrando:

2 passed
Evidencia 8 — Cloud Logging

Captura del registro:

Archivo recibido | bucket=... | nombre=prueba4.txt | tamaño=37 bytes | tipo=text/plain

Esta última evidencia es especialmente importante porque demuestra que la función recibió y procesó realmente un archivo.

24. Estructura del proyecto

La estructura utilizada es:

gcp-file-function/
│
├── main.py
├── test_main.py
├── requirements.txt
└── README.md
main.py

Contiene la Cloud Function.

test_main.py

Contiene las pruebas unitarias.

requirements.txt

Contiene las dependencias necesarias.

README.md

Contiene la documentación del proyecto, configuración, arquitectura y evidencias.

25. Conclusión

Durante el presente reto se implementó una infraestructura serverless utilizando diferentes servicios de Google Cloud Platform.

La solución permite almacenar archivos en Cloud Storage y ejecutar automáticamente una Cloud Function cuando un archivo termina de cargarse.

La función desarrollada en Python obtiene información básica del archivo y la registra en Cloud Logging. Además, se implementó manejo de errores y pruebas unitarias utilizando pytest.

La solución fue comprobada tanto mediante pruebas unitarias como mediante una prueba de integración real. En esta última se cargó el archivo prueba4.txt al bucket y se confirmó posteriormente en Cloud Logging que la función recibió el evento y obtuvo correctamente el nombre, tamaño y tipo de contenido del archivo.

El proyecto permitió trabajar de manera práctica con conceptos de:

Cloud Storage.
Cloud Functions.
Eventarc.
Pub/Sub.
Cloud Logging.
IAM.
Cloud Build.
Python.
CloudEvents.
Pruebas unitarias.

De esta manera se logró implementar y validar un flujo completo de procesamiento de archivos basado en eventos dentro de Google Cloud Platform lo cual me ayudo a complementar mis hablidades dentro de la parte de la nube y ser considerado para la vacante contemplando mi habilidad de autodidacta.
