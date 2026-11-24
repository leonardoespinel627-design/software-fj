"""
gestor.py
---------
SistemaGestion: administra las listas internas de clientes, servicios y
reservas (sin base de datos: todo vive en memoria).
"""

from .cliente import Cliente
from .servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from .reserva import Reserva
from .excepciones import (ClienteInvalidoError, ServicioInvalidoError,
                          ReservaInvalidaError, ParametroFaltanteError)
from .logger import registrar_evento


class SistemaGestion:
    """Punto central del sistema Software FJ."""

    # Tabla que relaciona el tipo de servicio (texto) con su clase
    TIPOS_SERVICIO = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self):
        # Listas internas privadas: son el "almacenamiento" del sistema
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        registrar_evento("=== Sistema Software FJ iniciado ===")

    # ---------------- Clientes ----------------

    def registrar_cliente(self, nombre, documento, correo, telefono):
        """Crea y guarda un cliente, evitando documentos duplicados."""
        # Regla de negocio: no puede haber dos clientes con el mismo documento
        if any(c.documento == str(documento).strip() for c in self.__clientes):
            raise ClienteInvalidoError(f"ya existe un cliente con documento {documento}")
        # La clase Cliente valida todos los datos en su constructor
        cliente = Cliente(nombre, documento, correo, telefono)
        self.__clientes.append(cliente)
        registrar_evento(f"Cliente registrado: {cliente.describir()}")
        return cliente

    def buscar_cliente(self, documento):
        """Devuelve el cliente con ese documento o lanza KeyError."""
        for cliente in self.__clientes:
            if cliente.documento == str(documento):
                return cliente
        raise KeyError(documento)

    # ---------------- Servicios ----------------

    def crear_servicio(self, tipo, **datos):
        """Crea un servicio del tipo indicado ('sala', 'equipo' o 'asesoria')."""
        if not tipo:
            raise ParametroFaltanteError("tipo de servicio")
        try:
            # Buscamos la clase en el diccionario; KeyError si el tipo no existe
            clase = self.TIPOS_SERVICIO[tipo]
        except KeyError as error:
            raise ServicioInvalidoError(f"tipo '{tipo}' desconocido; use {list(self.TIPOS_SERVICIO)}") from error
        try:
            # Creamos el servicio; TypeError si faltan o sobran argumentos
            servicio = clase(**datos)
        except TypeError as error:
            raise ServicioInvalidoError(f"parámetros incorrectos para '{tipo}': {error}") from error
        self.__servicios.append(servicio)
        registrar_evento(f"Servicio creado: {servicio.describir()}")
        return servicio

    def buscar_servicio(self, nombre):
        """Devuelve el servicio con ese nombre o lanza KeyError."""
        for servicio in self.__servicios:
            if servicio.nombre.lower() == str(nombre).lower():
                return servicio
        raise KeyError(nombre)

    # ---------------- Reservas ----------------

    def crear_reserva(self, documento_cliente, nombre_servicio, duracion):
        """Crea una reserva a partir del documento del cliente y el nombre del servicio."""
        try:
            cliente = self.buscar_cliente(documento_cliente)
            servicio = self.buscar_servicio(nombre_servicio)
        except KeyError as error:
            # Encadenamiento: el KeyError interno se convierte en error de reserva
            raise ReservaInvalidaError(f"no existe el cliente o servicio '{error.args[0]}'") from error
        reserva = Reserva(cliente, servicio, duracion)
        self.__reservas.append(reserva)
        registrar_evento(f"Reserva creada: {reserva.describir()}")
        return reserva

    # ---------------- Consultas ----------------

    @property
    def clientes(self):
        # Devolvemos una copia para que nadie modifique la lista interna desde afuera
        return list(self.__clientes)

    @property
    def servicios(self):
        return list(self.__servicios)

    @property
    def reservas(self):
        return list(self.__reservas)
