"""
excepciones.py
--------------
Jerarquía de excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, de modo que el programa principal puede
capturar cualquier error del dominio con un solo bloque except, sin ocultar
errores inesperados de Python (que se capturan aparte).
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ."""

    def __init__(self, mensaje, codigo="FJ-000"):
        # Llamamos al constructor de Exception para conservar el mensaje estándar
        super().__init__(mensaje)
        # Guardamos el mensaje legible para el usuario
        self.mensaje = mensaje
        # Guardamos un código de error que facilita buscar el evento en el log
        self.codigo = codigo

    def __str__(self):
        # Representación uniforme: [CÓDIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un dato obligatorio en una operación."""

    def __init__(self, parametro):
        # Construimos el mensaje indicando qué parámetro faltó
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'", "FJ-001")


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no superan las validaciones."""

    def __init__(self, mensaje):
        super().__init__(f"Cliente inválido: {mensaje}", "FJ-100")


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando un servicio se crea con datos o parámetros incorrectos."""

    def __init__(self, mensaje):
        super().__init__(f"Servicio inválido: {mensaje}", "FJ-200")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio que no está disponible."""

    def __init__(self, nombre_servicio):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible", "FJ-201")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no puede crearse por datos incorrectos."""

    def __init__(self, mensaje):
        super().__init__(f"Reserva inválida: {mensaje}", "FJ-300")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una acción no válida para el estado actual."""

    def __init__(self, mensaje):
        super().__init__(f"Operación no permitida: {mensaje}", "FJ-301")


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un valor ilógico."""

    def __init__(self, mensaje):
        super().__init__(f"Cálculo inconsistente: {mensaje}", "FJ-400")
