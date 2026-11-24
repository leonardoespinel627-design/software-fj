# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Curso **Programación (213023)** – UNAD · Fase 4 – Prácticas simuladas
Autor: **Óscar Leonardo Parra Espinel**

Aplicación orientada a objetos en Python, **sin base de datos**, que gestiona clientes, servicios
(reserva de salas, alquiler de equipos y asesorías especializadas) y reservas. Toda la información
vive en objetos y listas en memoria; el único archivo que se usa es el **log de eventos y errores**.

## Ejecución

Requiere Python 3.8 o superior (sin librerías externas).

```bash
python main.py
```

La simulación ejecuta 28 operaciones (registros válidos e inválidos de clientes, creación correcta e
incorrecta de servicios, reservas exitosas y fallidas, pagos y cancelaciones) y termina sin
interrupciones. Los eventos quedan en `logs/software_fj.log`.

## Estructura

```
software_fj/
├── main.py                 # Simulación de operaciones y resumen final
├── sistema/
│   ├── excepciones.py      # Excepciones personalizadas (jerarquía SoftwareFJError)
│   ├── logger.py           # Registro de eventos y errores en archivo
│   ├── entidad.py          # Clase abstracta EntidadBase
│   ├── cliente.py          # Cliente con encapsulación y validaciones
│   ├── servicios.py        # Servicio (abstracta) + ReservaSala, AlquilerEquipo, AsesoriaEspecializada
│   ├── reserva.py          # Reserva: confirmar, cancelar, procesar
│   └── gestor.py           # SistemaGestion: listas internas de clientes, servicios y reservas
└── logs/                   # Se crea automáticamente al ejecutar
```

## Cómo se cumple cada requisito

| Requisito | Dónde |
|---|---|
| Clase abstracta de entidades generales | `EntidadBase` (`entidad.py`) |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados `__` con propiedades y regex |
| Servicio abstracto + 3 especializados | `Servicio` → `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| Polimorfismo y métodos sobrescritos | `calcular_costo_base`, `describir`, `validar_parametros` |
| Reserva con confirmación, cancelación y procesamiento | `Reserva.confirmar`, `cancelar`, `procesar` |
| Métodos sobrecargados | `calcular_costo(duracion, impuesto=None, descuento=None)` y `cotizar` con `@singledispatchmethod` (int, float, dict) |
| Excepciones personalizadas | `excepciones.py` (8 clases) |
| try/except, try/except/else, try/except/finally | `main.ejecutar` (los cuatro bloques), `Reserva.confirmar` (else), `Reserva.procesar` (finally) |
| Encadenamiento de excepciones | `raise ... from error` en `cliente.py`, `servicios.py`, `reserva.py`, `gestor.py` |
| Archivo de logs | `logger.py` → `logs/software_fj.log` |
| Mínimo 10 operaciones simuladas | `main.py` (28 operaciones) |

## Nota sobre la sobrecarga en Python

Python no permite definir dos métodos con el mismo nombre y distinta firma (la segunda definición reemplaza
a la primera). Por eso la sobrecarga se implementa de las dos formas idiomáticas del lenguaje:
**parámetros opcionales** y **despacho por tipo** con `functools.singledispatchmethod`.
