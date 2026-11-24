"""
logger.py
---------
Registro de eventos y errores en un archivo de texto (logs/software_fj.log).

Es el ÚNICO uso de archivos en el sistema: la información de clientes,
servicios y reservas vive solo en objetos y listas en memoria.
"""

import logging          # Módulo estándar de Python para registrar eventos
import os               # Para construir rutas y crear la carpeta de logs

# Carpeta donde se guardará el archivo de logs (junto al proyecto)
CARPETA_LOGS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
# Ruta completa del archivo de logs
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")


def _crear_logger():
    """Configura y devuelve el logger del sistema."""
    # Creamos la carpeta de logs si no existe (exist_ok evita error si ya existe)
    os.makedirs(CARPETA_LOGS, exist_ok=True)
    # Obtenemos un logger con nombre propio para no mezclarlo con otros
    logger = logging.getLogger("SoftwareFJ")
    # Nivel mínimo: registramos desde mensajes informativos (INFO) hacia arriba
    logger.setLevel(logging.INFO)
    # Evitamos agregar manejadores duplicados si el módulo se importa varias veces
    if not logger.handlers:
        # Manejador que escribe en el archivo, en modo "append" y con UTF-8
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
        # Formato de cada línea: fecha | nivel | mensaje
        formato = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s",
                                    datefmt="%Y-%m-%d %H:%M:%S")
        # Asignamos el formato al manejador
        manejador.setFormatter(formato)
        # Conectamos el manejador al logger
        logger.addHandler(manejador)
    # Devolvemos el logger listo para usar
    return logger


# Instancia única del logger, compartida por todos los módulos
_logger = _crear_logger()


def registrar_evento(mensaje):
    """Registra un evento normal del sistema (nivel INFO)."""
    try:
        # Intentamos escribir el evento en el archivo
        _logger.info(mensaje)
    except OSError:
        # Si el disco falla, no detenemos la aplicación: solo avisamos en pantalla
        print(f"(No se pudo escribir en el log) {mensaje}")


def registrar_error(error, contexto=""):
    """Registra un error (nivel ERROR), incluyendo la causa si fue encadenado."""
    try:
        # Texto base: contexto de la operación + tipo y mensaje del error
        texto = f"{contexto} -> {type(error).__name__}: {error}"
        # Si la excepción fue encadenada con "raise ... from ...", anotamos la causa
        if error.__cause__ is not None:
            texto += f" | Causa original: {type(error.__cause__).__name__}: {error.__cause__}"
        # Escribimos el error en el archivo de logs
        _logger.error(texto)
    except OSError:
        # Igual que arriba: el fallo del log nunca debe tumbar el programa
        print(f"(No se pudo escribir en el log) {error}")


def registrar_advertencia(mensaje):
    """Registra una situación anómala que no es un error (nivel WARNING)."""
    try:
        _logger.warning(mensaje)
    except OSError:
        print(f"(No se pudo escribir en el log) {mensaje}")
