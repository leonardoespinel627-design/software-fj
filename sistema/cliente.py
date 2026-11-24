"""
cliente.py
----------
Clase Cliente con encapsulación de datos personales y validaciones estrictas.
"""

import re                                         # Expresiones regulares para validar formatos
from .entidad import EntidadBase                  # Clase abstracta padre
from .excepciones import ClienteInvalidoError, ParametroFaltanteError


class Cliente(EntidadBase):
    """Cliente de Software FJ. Sus datos son privados y se validan al asignarse."""

    # Patrón de correo: texto@texto.dominio
    _PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
    # Patrón de nombre: solo letras (con tildes y ñ) y espacios, de 3 a 60 caracteres
    _PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")

    def __init__(self, nombre, documento, correo, telefono):
        # Llamamos al constructor de EntidadBase con el prefijo "CLI"
        super().__init__("CLI")
        # Usamos los setters (propiedades) para que cada dato se valide al asignarse
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        # Validación final del objeto completo
        self.validar()

    # ---------------- Propiedades encapsuladas ----------------

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        # Verificamos que el dato exista y no sea solo espacios
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("nombre")
        # Normalizamos espacios sobrantes
        valor = str(valor).strip()
        # Validamos el formato con la expresión regular
        if not self._PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(f"el nombre '{valor}' contiene caracteres no válidos")
        # Guardamos el valor en un atributo privado (name mangling con __)
        self.__nombre = valor.title()

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("documento")
        valor = str(valor).strip()
        # El documento debe tener solo dígitos y entre 6 y 10 cifras
        if not valor.isdigit() or not 6 <= len(valor) <= 10:
            raise ClienteInvalidoError(f"el documento '{valor}' debe tener de 6 a 10 dígitos")
        self.__documento = valor

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("correo")
        valor = str(valor).strip().lower()
        if not self._PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(f"el correo '{valor}' no tiene un formato válido")
        self.__correo = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError("telefono")
        try:
            # Intentamos convertir a entero para comprobar que sea numérico
            int(str(valor).strip())
        except ValueError as error:
            # Encadenamiento de excepciones: el ValueError original queda como causa
            raise ClienteInvalidoError(f"el teléfono '{valor}' no es numérico") from error
        valor = str(valor).strip()
        # Celular colombiano: 10 dígitos que empiezan por 3
        if len(valor) != 10 or not valor.startswith("3"):
            raise ClienteInvalidoError(f"el teléfono '{valor}' debe tener 10 dígitos e iniciar en 3")
        self.__telefono = valor

    # ---------------- Métodos sobrescritos de EntidadBase ----------------

    def validar(self):
        """Comprueba que todos los datos obligatorios hayan quedado asignados."""
        for campo in ("nombre", "documento", "correo", "telefono"):
            # getattr con valor por defecto evita AttributeError si algo no se asignó
            if not getattr(self, campo, None):
                raise ParametroFaltanteError(campo)
        return True

    def describir(self):
        # Ocultamos parte del documento para proteger el dato personal
        doc_oculto = "*" * (len(self.documento) - 4) + self.documento[-4:]
        return f"{self.id} | {self.nombre} | Doc: {doc_oculto} | {self.correo}"
