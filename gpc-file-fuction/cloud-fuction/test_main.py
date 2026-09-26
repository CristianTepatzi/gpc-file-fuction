import logging

import pytest
from cloudevents.http import CloudEvent

from main import process_file


# Prueba del escenario exitoso.
#
# Se simula un evento de Cloud Storage sin necesidad
# de subir realmente un archivo a Google Cloud.
def test_process_file_success(capsys):

    # Se construye un CloudEvent de prueba.
    #
    # El tipo de evento corresponde a un objeto de Storage
    # que terminó de cargarse correctamente.
    event = CloudEvent(
        {
            "type": "google.cloud.storage.object.v1.finalized",
            "source": (
                "//storage.googleapis.com/projects/_/"
                "buckets/gcp-challenge-files-cristian"
            ),
            "subject": "objects/documento.txt",
        },
        {
            # Bucket utilizado en el proyecto.
            "bucket": "gcp-challenge-files-cristian",

            # Nombre del archivo simulado.
            "name": "documento.txt",

            # Tamaño simulado del archivo en bytes.
            "size": "100",

            # Tipo MIME del archivo.
            "contentType": "text/plain",
        },
    )

    # Ejecutamos la función utilizando el evento simulado.
    process_file(event)

    # capsys permite capturar lo que la función
    # imprime mediante print().
    captured = capsys.readouterr()

    # Verificamos que el nombre del archivo
    # aparezca en la salida.
    assert "documento.txt" in captured.out

    # Verificamos que el tamaño también sea registrado.
    assert "100" in captured.out

    # Verificamos que se registre el tipo MIME.
    assert "text/plain" in captured.out


# Prueba del escenario de error.
#
# En este caso se genera un evento incompleto
# para comprobar que la función pueda detectar
# información obligatoria faltante.
def test_process_file_error(caplog):

    # Creamos un evento que solamente contiene
    # el nombre del bucket, pero no el nombre del archivo.
    event = CloudEvent(
        {
            "type": "google.cloud.storage.object.v1.finalized",
            "source": (
                "//storage.googleapis.com/projects/_/"
                "buckets/gcp-challenge-files-cristian"
            ),
        },
        {
            "bucket": "gcp-challenge-files-cristian"
        },
    )

    # Capturamos los mensajes de nivel ERROR
    # generados durante la ejecución.
    with caplog.at_level(logging.ERROR):

        # Como falta el nombre del archivo,
        # esperamos que la función lance ValueError.
        with pytest.raises(ValueError):
            process_file(event)

    # Comprobamos que el mensaje de error
    # haya sido registrado correctamente.
    assert "Error al procesar el archivo" in caplog.text

