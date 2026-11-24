"""
main.py
-------
Simulación del Sistema Integral de Gestión de Clientes, Servicios y Reservas
de la empresa Software FJ.

Ejecuta más de 10 operaciones completas (válidas e inválidas) para demostrar
que la aplicación sigue funcionando aunque ocurran errores.

Curso: Programación (213023) - UNAD
Autor: Óscar Leonardo Parra Espinel
"""

from sistema.gestor import SistemaGestion
from sistema.excepciones import SoftwareFJError
from sistema.logger import registrar_error, registrar_evento, ARCHIVO_LOG

# Contadores globales para el resumen final
resultados = {"exitosas": 0, "fallidas": 0}


def ejecutar(numero, descripcion, operacion):
    """
    Ejecuta una operación protegida. Pase lo que pase, el programa continúa.
    Usa try / except / else / finally.
    """
    print(f"\n[{numero:02d}] {descripcion}")
    try:
        # Ejecutamos la operación recibida (una función sin argumentos)
        resultado = operacion()
    except SoftwareFJError as error:
        # Errores previstos del dominio: se informan y se registran
        resultados["fallidas"] += 1
        print(f"     ✗ ERROR CONTROLADO {error}")
        if error.__cause__ is not None:
            print(f"       Causa original: {type(error.__cause__).__name__}: {error.__cause__}")
        registrar_error(error, f"Operación {numero:02d} - {descripcion}")
    except Exception as error:
        # Cualquier error inesperado también se captura: la app no se cae
        resultados["fallidas"] += 1
        print(f"     ✗ ERROR INESPERADO {type(error).__name__}: {error}")
        registrar_error(error, f"Operación {numero:02d} (inesperado) - {descripcion}")
    else:
        # Solo si no hubo excepción
        resultados["exitosas"] += 1
        print(f"     ✓ OK -> {resultado}")
    finally:
        # Siempre se ejecuta: deja constancia de que la operación terminó
        registrar_evento(f"Operación {numero:02d} finalizada")


def main():
    sistema = SistemaGestion()
    # Diccionario para conservar referencias a las reservas creadas con éxito
    reservas = {}

    print("=" * 70)
    print("   SOFTWARE FJ - Sistema de Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)

    # ---------------- CLIENTES ----------------
    ejecutar(1, "Registrar cliente válido (Ana Gómez)",
             lambda: sistema.registrar_cliente("Ana Gómez", "1012345678", "ana.gomez@correo.com", "3104567890"))
    ejecutar(2, "Registrar cliente válido (Carlos Ruiz)",
             lambda: sistema.registrar_cliente("Carlos Ruiz", "79876543", "carlos.ruiz@correo.co", "3209876543"))
    ejecutar(3, "Registrar cliente con correo inválido",
             lambda: sistema.registrar_cliente("Luisa Mora", "52123456", "luisa.correo.com", "3001112233"))
    ejecutar(4, "Registrar cliente con teléfono no numérico (excepción encadenada)",
             lambda: sistema.registrar_cliente("Pedro Díaz", "1098765432", "pedro@correo.com", "310-ABC-123"))
    ejecutar(5, "Registrar cliente sin nombre (parámetro faltante)",
             lambda: sistema.registrar_cliente("", "1023456789", "sin.nombre@correo.com", "3151234567"))
    ejecutar(6, "Registrar cliente con documento duplicado",
             lambda: sistema.registrar_cliente("Ana María Gómez", "1012345678", "otra@correo.com", "3104567891"))

    # ---------------- SERVICIOS ----------------
    ejecutar(7, "Crear servicio: Sala de juntas (40 personas)",
             lambda: sistema.crear_servicio("sala", nombre="Sala Andes", tarifa_hora=80000, capacidad=40))
    ejecutar(8, "Crear servicio: Alquiler de 5 portátiles",
             lambda: sistema.crear_servicio("equipo", nombre="Portátiles", tarifa_hora=15000, unidades=5))
    ejecutar(9, "Crear servicio: Asesoría experta en ciberseguridad",
             lambda: sistema.crear_servicio("asesoria", nombre="Asesoría Ciberseguridad", tarifa_hora=120000,
                                            especialidad="Ciberseguridad", nivel="experto"))
    ejecutar(10, "Crear servicio con tarifa negativa",
             lambda: sistema.crear_servicio("sala", nombre="Sala Fantasma", tarifa_hora=-5000, capacidad=10))
    ejecutar(11, "Crear servicio de tipo inexistente (excepción encadenada)",
             lambda: sistema.crear_servicio("transporte", nombre="Bus", tarifa_hora=50000))
    ejecutar(12, "Crear asesoría con nivel inválido",
             lambda: sistema.crear_servicio("asesoria", nombre="Asesoría Redes", tarifa_hora=90000,
                                            especialidad="Redes", nivel="maestro"))
    ejecutar(13, "Crear servicio con parámetro sobrante (TypeError encadenado)",
             lambda: sistema.crear_servicio("equipo", nombre="Video beam", tarifa_hora=20000, unidades=2, color="negro"))

    # ---------------- MÉTODOS SOBRECARGADOS ----------------
    def demo_sobrecarga():
        sala = sistema.buscar_servicio("Sala Andes")
        return (f"base={sala.calcular_costo(3):,.0f} | con IVA={sala.calcular_costo(3, impuesto=0.19):,.0f} | "
                f"con 10% dto={sala.calcular_costo(3, descuento=0.10):,.0f} | "
                f"cotizar(int)={sala.cotizar(3):,.0f} | cotizar(float 2.5)={sala.cotizar(2.5):,.0f} | "
                f"cotizar(dict)={sala.cotizar({'duracion': 3, 'descuento': 0.2}):,.0f}")
    ejecutar(14, "Variantes del cálculo de costos (sobrecarga)", demo_sobrecarga)
    ejecutar(15, "Cotizar con un tipo de dato no soportado (lista)",
             lambda: sistema.buscar_servicio("Portátiles").cotizar([1, 2]))

    # ---------------- RESERVAS ----------------
    def reserva_exitosa():
        reserva = sistema.crear_reserva("1012345678", "Sala Andes", 4)
        reservas["ana"] = reserva
        costo = reserva.confirmar()
        return f"{reserva.describir()} (costo ${costo:,.0f})"
    ejecutar(16, "Reserva exitosa: Ana reserva Sala Andes 4 h y confirma", reserva_exitosa)

    def reserva_con_descuento():
        reserva = sistema.crear_reserva("79876543", "Asesoría Ciberseguridad", 2)
        reservas["carlos"] = reserva
        reserva.confirmar(descuento=0.15)
        return reserva.describir()
    ejecutar(17, "Reserva exitosa con 15 % de descuento: Carlos, asesoría 2 h", reserva_con_descuento)

    ejecutar(18, "Reserva con duración fuera de rango (20 h de asesoría)",
             lambda: sistema.crear_reserva("79876543", "Asesoría Ciberseguridad", 20))
    ejecutar(19, "Reserva para un cliente inexistente",
             lambda: sistema.crear_reserva("99999999", "Portátiles", 3))

    def reserva_no_disponible():
        equipo = sistema.buscar_servicio("Portátiles")
        equipo.cambiar_disponibilidad(False)        # Simulamos equipos en mantenimiento
        reserva = sistema.crear_reserva("1012345678", "Portátiles", 6)
        reservas["no_disp"] = reserva
        return reserva.confirmar()
    ejecutar(20, "Confirmar reserva de un servicio NO disponible", reserva_no_disponible)

    ejecutar(21, "Confirmar con descuento ilógico del 80 % (cálculo inconsistente)",
             lambda: sistema.crear_reserva("79876543", "Sala Andes", 2).confirmar(descuento=0.8))

    ejecutar(22, "Procesar pago insuficiente de la reserva de Ana",
             lambda: reservas["ana"].procesar(100000))
    ejecutar(23, "Procesar pago no numérico (excepción encadenada)",
             lambda: reservas["ana"].procesar("mil pesos"))
    ejecutar(24, "Procesar pago completo de la reserva de Ana",
             lambda: f"cambio ${reservas['ana'].procesar(500000):,.0f}")
    ejecutar(25, "Intentar cancelar la reserva ya procesada de Ana",
             lambda: reservas["ana"].cancelar("Cambio de planes"))
    ejecutar(26, "Cancelar la reserva de Carlos (válido)",
             lambda: reservas["carlos"].cancelar("El cliente reprogramó") or reservas["carlos"].describir())
    ejecutar(27, "Confirmar una reserva ya cancelada",
             lambda: reservas["carlos"].confirmar())
    ejecutar(28, "Acceso a una reserva que nunca se creó (error inesperado de Python)",
             lambda: reservas["inexistente"].procesar(1000))

    # ---------------- RESUMEN ----------------
    print("\n" + "=" * 70)
    print("RESUMEN DE LA SIMULACIÓN")
    print("=" * 70)
    print(f"Operaciones exitosas: {resultados['exitosas']}")
    print(f"Operaciones fallidas controladas: {resultados['fallidas']}")
    print(f"\nClientes registrados ({len(sistema.clientes)}):")
    for c in sistema.clientes:
        print("  -", c)                          # __str__ llama a describir() (polimorfismo)
    print(f"\nServicios creados ({len(sistema.servicios)}):")
    for s in sistema.servicios:
        print("  -", s)
    print(f"\nReservas ({len(sistema.reservas)}):")
    for r in sistema.reservas:
        print("  -", r)
    print(f"\nEl sistema terminó sin interrupciones. Log de eventos: {ARCHIVO_LOG}")
    registrar_evento("=== Simulación finalizada sin interrupciones ===")


# Punto de entrada: solo se ejecuta si se corre este archivo directamente
if __name__ == "__main__":
    main()
