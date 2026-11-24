"""
entidad.py
----------
Clase abstracta EntidadBase: representa cualquier entidad general del sistema
(clientes, servicios y reservas heredan de ella).
"""

from abc import ABC, abstractmethod   # Herramientas para definir clases abstractas
from datetime import datetime         # Para guardar la fecha de creación


class EntidadBase(ABC):
    """Entidad general con identificador único y fecha de creación."""

    # Contadores por tipo de entidad (prefijo) para generar IDs consecutivos
    _contadores = {}

    def __init__(self, prefijo):
        # Incrementamos el contador del prefijo (si no existe, inicia en 0)
        EntidadBase._contadores[prefijo] = EntidadBase._contadores.get(prefijo, 0) + 1
        # Generamos un ID legible, p. ej. "CLI-0001" o "SRV-0004"
        self.__id = f"{prefijo}-{EntidadBase._contadores[prefijo]:04d}"
        # Guardamos el momento exacto en que se creó la entidad
        self.__fecha_creacion = datetime.now()

    @property
    def id(self):
        """Identificador único (solo lectura: no tiene setter)."""
        return self.__id

    @property
    def fecha_creacion(self):
        """Fecha y hora de creación (solo lectura)."""
        return self.__fecha_creacion

    @abstractmethod
    def describir(self):
        """Cada entidad debe saber describirse (se implementa en las hijas)."""

    @abstractmethod
    def validar(self):
        """Cada entidad debe validar su propio estado interno."""

    def __str__(self):
        # Al imprimir cualquier entidad se usa su propia descripción (polimorfismo)
        return self.describir()
