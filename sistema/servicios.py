"""
servicios.py
------------
Clase abstracta Servicio y tres servicios especializados:
    - ReservaSala
    - AlquilerEquipo
    - AsesoriaEspecializada

Aplica herencia (todas heredan de Servicio), polimorfismo (cada una calcula
su costo, se describe y valida sus parámetros a su manera) y sobrecarga de
métodos (varias formas de calcular el costo).
"""

from abc import abstractmethod                   # Para declarar métodos abstractos
from functools import singledispatchmethod       # Sobrecarga por tipo de argumento
from .entidad import EntidadBase
from .excepciones import (ServicioInvalidoError, CalculoInconsistenteError,
                          ParametroFaltanteError)

# Impuesto por defecto (IVA Colombia 19 %)
IVA = 0.19


class Servicio(EntidadBase):
    """Clase abstracta que define lo común a todos los servicios."""

    def __init__(self, nombre, tarifa_hora, disponible=True):
        # Constructor de la entidad base con prefijo "SRV"
        super().__init__("SRV")
        # Validamos que el nombre exista
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("nombre del servicio")
        # Guardamos el nombre de forma protegida (un guion bajo)
        self._nombre = str(nombre).strip()
        # La tarifa se asigna mediante su propiedad, que la valida
        self.tarifa_hora = tarifa_hora
        # Indicador de disponibilidad del servicio
        self._disponible = bool(disponible)

    # ---------------- Propiedades ----------------

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @tarifa_hora.setter
    def tarifa_hora(self, valor):
        try:
            # Convertimos a número decimal; falla si es texto no numérico
            valor = float(valor)
        except (TypeError, ValueError) as error:
            # Encadenamos el error original para conservar la causa en el log
            raise ServicioInvalidoError(f"la tarifa '{valor}' no es un número") from error
        # Una tarifa debe ser positiva
        if valor <= 0:
            raise ServicioInvalidoError(f"la tarifa debe ser mayor que cero (recibido {valor})")
        self._tarifa_hora = valor

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        """Permite habilitar o deshabilitar el servicio."""
        self._disponible = bool(estado)

    # ---------------- Métodos abstractos (polimorfismo) ----------------

    @abstractmethod
    def calcular_costo_base(self, duracion):
        """Costo sin impuestos ni descuentos; cada servicio lo calcula distinto."""

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida la duración y reglas propias de cada servicio."""

    # ---------------- Métodos "sobrecargados" ----------------
    # Python no admite varias funciones con el mismo nombre; la sobrecarga se
    # implementa con parámetros opcionales (calcular_costo) y con despacho por
    # tipo de argumento (cotizar, mediante singledispatchmethod).

    def calcular_costo(self, duracion, impuesto=None, descuento=None):
        """
        Variantes de uso:
            calcular_costo(h)                     -> costo base
            calcular_costo(h, impuesto=0.19)      -> base + impuesto
            calcular_costo(h, descuento=0.10)     -> base - descuento
            calcular_costo(h, 0.19, 0.10)         -> base - descuento + impuesto
        """
        # Primero validamos los parámetros propios del servicio
        self.validar_parametros(duracion)
        # Costo base calculado polimórficamente por la subclase
        costo = self.calcular_costo_base(duracion)
        # Si se pidió descuento, debe estar entre 0 % y 50 %
        if descuento is not None:
            if not 0 <= descuento <= 0.5:
                raise CalculoInconsistenteError(f"descuento {descuento:.0%} fuera de rango (0 % a 50 %)")
            costo -= costo * descuento
        # Si se pidió impuesto, debe estar entre 0 % y 30 %
        if impuesto is not None:
            if not 0 <= impuesto <= 0.3:
                raise CalculoInconsistenteError(f"impuesto {impuesto:.0%} fuera de rango (0 % a 30 %)")
            costo += costo * impuesto
        # Control final: un costo nunca puede ser negativo o cero
        if costo <= 0:
            raise CalculoInconsistenteError(f"el costo calculado ({costo}) no es válido")
        # Redondeamos a pesos enteros
        return round(costo, 0)

    @singledispatchmethod
    def cotizar(self, parametro):
        """Sobrecarga por tipo: si el tipo no está registrado, es un error."""
        raise CalculoInconsistenteError(f"no se puede cotizar con un dato de tipo {type(parametro).__name__}")

    @cotizar.register
    def _(self, horas: int):
        # Variante 1: se recibe un entero -> cotización con IVA
        return self.calcular_costo(horas, impuesto=IVA)

    @cotizar.register
    def _(self, horas: float):
        # Variante 2: se recibe un decimal -> se redondea hacia arriba la hora
        import math
        return self.calcular_costo(math.ceil(horas), impuesto=IVA)

    @cotizar.register
    def _(self, opciones: dict):
        # Variante 3: se recibe un diccionario con opciones
        if "duracion" not in opciones:
            raise ParametroFaltanteError("duracion")
        return self.calcular_costo(opciones["duracion"],
                                   impuesto=opciones.get("impuesto", IVA),
                                   descuento=opciones.get("descuento"))

    # ---------------- Utilidades comunes ----------------

    def _validar_duracion(self, duracion, minimo, maximo):
        """Validación genérica de duración en horas, reutilizada por las hijas."""
        # La duración debe ser numérica (bool se excluye porque es subclase de int)
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool):
            raise ServicioInvalidoError(f"la duración '{duracion}' debe ser numérica")
        if not minimo <= duracion <= maximo:
            raise ServicioInvalidoError(
                f"'{self.nombre}' admite de {minimo} a {maximo} horas (recibido {duracion})")

    def validar(self):
        # Validación del objeto: comprobamos nombre y tarifa
        return bool(self._nombre) and self._tarifa_hora > 0


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        # La capacidad debe ser un entero positivo de máximo 100 personas
        if not isinstance(capacidad, int) or not 1 <= capacidad <= 100:
            raise ServicioInvalidoError(f"capacidad de sala '{capacidad}' inválida (1 a 100)")
        self._capacidad = capacidad

    def validar_parametros(self, duracion):
        # Las salas se reservan de 1 a 12 horas
        self._validar_duracion(duracion, 1, 12)

    def calcular_costo_base(self, duracion):
        costo = self.tarifa_hora * duracion
        # Salas grandes (más de 30 personas) tienen recargo del 15 %
        if self._capacidad > 30:
            costo *= 1.15
        return costo

    def describir(self):
        return (f"{self.id} | Sala '{self.nombre}' | {self._capacidad} personas | "
                f"${self.tarifa_hora:,.0f}/h | {'Disponible' if self.disponible else 'No disponible'}")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portátiles, video beam, etc.)."""

    def __init__(self, nombre, tarifa_hora, unidades, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(unidades, int) or unidades < 1:
            raise ServicioInvalidoError(f"unidades '{unidades}' inválidas (entero mayor que 0)")
        self._unidades = unidades

    def validar_parametros(self, duracion):
        # Los equipos se alquilan de 1 a 72 horas
        self._validar_duracion(duracion, 1, 72)

    def calcular_costo_base(self, duracion):
        # Tarifa por hora por cada unidad + seguro del 5 %
        return self.tarifa_hora * duracion * self._unidades * 1.05

    def describir(self):
        return (f"{self.id} | Equipo '{self.nombre}' x{self._unidades} | "
                f"${self.tarifa_hora:,.0f}/h por unidad | {'Disponible' if self.disponible else 'No disponible'}")


class AsesoriaEspecializada(Servicio):
    """Asesorías con un especialista, con nivel que afecta el precio."""

    # Multiplicador de tarifa según el nivel del asesor
    NIVELES = {"basico": 1.0, "avanzado": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="basico", disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not especialidad:
            raise ParametroFaltanteError("especialidad")
        # El nivel debe ser uno de los definidos en NIVELES
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"nivel '{nivel}' no existe; use {list(self.NIVELES)}")
        self._especialidad = especialidad
        self._nivel = nivel

    def validar_parametros(self, duracion):
        # Las asesorías duran de 1 a 8 horas
        self._validar_duracion(duracion, 1, 8)

    def calcular_costo_base(self, duracion):
        return self.tarifa_hora * duracion * self.NIVELES[self._nivel]

    def describir(self):
        return (f"{self.id} | Asesoría '{self.nombre}' ({self._especialidad}, nivel {self._nivel}) | "
                f"${self.tarifa_hora:,.0f}/h | {'Disponible' if self.disponible else 'No disponible'}")
