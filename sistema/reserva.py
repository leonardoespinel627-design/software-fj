"""
reserva.py
----------
Clase Reserva: integra cliente, servicio, duración y estado. Implementa
confirmación, cancelación y procesamiento con manejo de excepciones.
"""

from .entidad import EntidadBase
from .cliente import Cliente
from .servicios import Servicio, IVA
from .excepciones import (ReservaInvalidaError, OperacionNoPermitidaError,
                          ServicioNoDisponibleError, CalculoInconsistenteError,
                          SoftwareFJError)
from .logger import registrar_evento, registrar_error


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    # Estados posibles de una reserva
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"

    def __init__(self, cliente, servicio, duracion):
        super().__init__("RES")
        # Comprobamos los tipos: deben ser objetos Cliente y Servicio reales
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("el cliente indicado no es un objeto Cliente")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("el servicio indicado no es un objeto Servicio")
        self.__cliente = cliente
        self.__servicio = servicio
        try:
            # La duración la valida el propio servicio (polimorfismo)
            servicio.validar_parametros(duracion)
        except SoftwareFJError as error:
            # Encadenamiento: la reserva falla, pero conservamos el motivo del servicio
            raise ReservaInvalidaError(f"duración no aceptada por el servicio ({error.mensaje})") from error
        self.__duracion = duracion
        # Toda reserva inicia pendiente y sin costo calculado
        self.__estado = Reserva.PENDIENTE
        self.__costo = None

    # ---------------- Propiedades de solo lectura ----------------

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    @property
    def costo(self):
        return self.__costo

    # ---------------- Operaciones ----------------

    def confirmar(self, descuento=None):
        """Confirma la reserva calculando su costo final (try/except/else)."""
        # Solo se puede confirmar una reserva pendiente
        if self.__estado != Reserva.PENDIENTE:
            raise OperacionNoPermitidaError(f"no se puede confirmar una reserva {self.__estado}")
        # El servicio debe estar disponible en este momento
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(self.__servicio.nombre)
        try:
            # Intentamos calcular el costo con IVA y descuento opcional
            costo = self.__servicio.calcular_costo(self.__duracion, impuesto=IVA, descuento=descuento)
        except CalculoInconsistenteError as error:
            # Registramos el detalle y relanzamos encadenado como error de reserva
            registrar_error(error, f"Confirmación de {self.id}")
            raise ReservaInvalidaError("no fue posible calcular el costo") from error
        else:
            # El bloque else solo se ejecuta si NO hubo excepción
            self.__costo = costo
            self.__estado = Reserva.CONFIRMADA
            registrar_evento(f"Reserva {self.id} confirmada por ${costo:,.0f}")
        return self.__costo

    def cancelar(self, motivo="Sin motivo"):
        """Cancela la reserva si aún no ha sido procesada."""
        if self.__estado == Reserva.PROCESADA:
            raise OperacionNoPermitidaError("una reserva ya procesada no se puede cancelar")
        if self.__estado == Reserva.CANCELADA:
            raise OperacionNoPermitidaError("la reserva ya estaba cancelada")
        self.__estado = Reserva.CANCELADA
        registrar_evento(f"Reserva {self.id} cancelada. Motivo: {motivo}")

    def procesar(self, pago):
        """Procesa el pago de una reserva confirmada (try/except/finally)."""
        registrar_evento(f"Inicio de procesamiento de {self.id}")
        try:
            # Solo se procesa lo confirmado
            if self.__estado != Reserva.CONFIRMADA:
                raise OperacionNoPermitidaError(f"solo se procesan reservas confirmadas (estado: {self.__estado})")
            # El pago debe ser numérico; float() lanza ValueError si no lo es
            pago = float(pago)
            # El pago debe cubrir el costo total
            if pago < self.__costo:
                raise CalculoInconsistenteError(
                    f"pago insuficiente: ${pago:,.0f} de ${self.__costo:,.0f}")
            # Si todo está bien, cambiamos el estado y calculamos el cambio
            self.__estado = Reserva.PROCESADA
            cambio = pago - self.__costo
            registrar_evento(f"Reserva {self.id} procesada. Cambio entregado: ${cambio:,.0f}")
            return cambio
        except ValueError as error:
            # Un pago no numérico se convierte en un error del dominio, encadenado
            raise CalculoInconsistenteError(f"el pago '{pago}' no es un valor numérico") from error
        finally:
            # finally se ejecuta SIEMPRE, haya o no error: dejamos traza del cierre
            registrar_evento(f"Fin de procesamiento de {self.id} (estado: {self.__estado})")

    # ---------------- Métodos sobrescritos ----------------

    def validar(self):
        return self.__cliente is not None and self.__servicio is not None and self.__duracion > 0

    def describir(self):
        costo = f"${self.__costo:,.0f}" if self.__costo else "sin calcular"
        return (f"{self.id} | {self.__cliente.nombre} -> {self.__servicio.nombre} | "
                f"{self.__duracion} h | {self.__estado} | {costo}")
