import logging

import functions_framework
from cloudevents.http import CloudEvent


# Se utiliza el decorador cloud_event porque la función
# será ejecutada mediante un evento de Cloud Storage.
#
# Al utilizar CloudEvent, podemos acceder de forma estructurada
# a la información enviada por el evento, como:
# bucket, nombre del archivo, tamaño y tipo MIME.
@functions_framework.cloud_event
def process_file(cloud_event: CloudEvent):

    try:
        # Obtenemos los datos enviados dentro del evento.
        #
        # En este caso, el evento proviene de Cloud Storage
        # cuando un archivo termina de cargarse correctamente.
        data = cloud_event.data

        # Nombre del bucket donde se almacenó el archivo.
        bucket = data.get("bucket")

        # Nombre/ruta del objeto almacenado.
        name = data.get("name")

        # Tamaño del archivo en bytes.
        size = data.get("size")

        # Tipo MIME del archivo, por ejemplo:
        # text/plain, image/png, application/pdf, etc.
        content_type = data.get("contentType")

        # Se valida que el evento tenga como mínimo
        # el bucket y el nombre del archivo.
        #
        # Estos datos son necesarios para identificar
        # qué archivo provocó la ejecución de la función.
        if not bucket or not name:
            raise ValueError(
                "El evento no contiene bucket o nombre del archivo"
            )

        # Se utiliza print() para generar un mensaje visible
        # en Cloud Logging durante la ejecución de la función.
        #
        # Se incluyen los principales metadatos solicitados:
        # bucket, nombre, tamaño y tipo de archivo.
        print(
            f"Archivo recibido | "
            f"bucket={bucket} | "
            f"nombre={name} | "
            f"tamaño={size} bytes | "
            f"tipo={content_type}"
        )

    except Exception:
        # logging.exception() registra el mensaje de error
        # junto con información de la excepción.
        #
        # Esto facilita la identificación de problemas
        # durante la ejecución de la Cloud Function.
        logging.exception("Error al procesar el archivo")

        # Se vuelve a lanzar la excepción para que el sistema
        # considere la ejecución como fallida.
        #
        # Esto evita ocultar errores y permite que los servicios
        # de Google Cloud puedan detectar correctamente el fallo.
        raise
