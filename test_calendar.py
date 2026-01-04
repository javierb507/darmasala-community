"""
Script de prueba para el sistema de calendario centralizado.
Verifica todas las funcionalidades del módulo calendar_utils.
"""

from datetime import date, time, datetime
from utils.calendar_utils import (
    CalendarioAcademico,
    PeriodoPago,
    HorarioSemanalHelper,
    crear_contexto_calendario
)


def test_calendario_academico():
    """Prueba las funcionalidades del CalendarioAcademico."""
    print("=" * 60)
    print("TEST 1: CalendarioAcademico")
    print("=" * 60)

    cal = CalendarioAcademico(2025)

    # Test 1: Formato académico
    formato = cal.get_año_academico_formato()
    assert formato == "25/26", f"Error: esperado '25/26', obtenido '{formato}'"
    print(f"OK - Año académico: {formato}")

    # Test 2: Períodos mensuales
    periodos_mensuales = cal.generar_periodos_mensuales()
    assert len(periodos_mensuales) == 12, f"Error: esperado 12 períodos, obtenido {len(periodos_mensuales)}"
    print(f"OK - Períodos mensuales: {len(periodos_mensuales)}")

    # Test 3: Períodos bimensuales
    periodos_bi = cal.generar_periodos_bimensuales()
    assert len(periodos_bi) == 6, f"Error: esperado 6 períodos, obtenido {len(periodos_bi)}"
    print(f"OK - Períodos bimensuales: {len(periodos_bi)}")

    # Test 4: Formatear fecha
    fecha_test = date(2025, 3, 15)
    fecha_corta = CalendarioAcademico.formatear_fecha(fecha_test, 'corto')
    assert fecha_corta == "15/03/2025", f"Error en formato corto: {fecha_corta}"
    print(f"OK - Formato fecha corto: {fecha_corta}")

    fecha_iso = CalendarioAcademico.formatear_fecha(fecha_test, 'iso')
    assert fecha_iso == "2025-03-15", f"Error en formato ISO: {fecha_iso}"
    print(f"OK - Formato fecha ISO: {fecha_iso}")

    # Test 5: Parsear fecha
    fecha_parseada = CalendarioAcademico.parsear_fecha("2025-03-15", 'iso')
    assert fecha_parseada == fecha_test, f"Error al parsear fecha: {fecha_parseada}"
    print(f"OK - Parsear fecha: {fecha_parseada}")

    # Test 6: Rango de semana
    inicio, fin = CalendarioAcademico.get_rango_semana(date(2025, 1, 15))  # Miércoles
    assert inicio.weekday() == 0, "Error: inicio de semana no es lunes"
    assert fin.weekday() == 6, "Error: fin de semana no es domingo"
    print(f"OK - Rango de semana: {inicio} a {fin}")

    # Test 7: Calcular hora fin
    hora_inicio = time(9, 0)
    hora_fin = CalendarioAcademico.calcular_hora_fin(hora_inicio, 75)
    assert hora_fin == time(10, 15), f"Error en cálculo hora fin: {hora_fin}"
    print(f"OK - Calcular hora fin: {hora_inicio} + 75min = {hora_fin}")

    # Test 8: Verificar matrícula vigente
    fecha_matricula_vigente = date(2025, 9, 1)
    es_vigente = cal.verificar_matricula_vigente(fecha_matricula_vigente)
    assert es_vigente, "Error: matrícula debería ser vigente"
    print(f"OK - Matrícula vigente: {es_vigente}")

    print("\nTODOS LOS TESTS DE CalendarioAcademico PASARON!\n")


def test_periodo_pago():
    """Prueba las funcionalidades del PeriodoPago."""
    print("=" * 60)
    print("TEST 2: PeriodoPago")
    print("=" * 60)

    # Test 1: Período mensual
    periodo_mensual = PeriodoPago(2025, 3, pagado=True)
    assert not periodo_mensual.es_bimensual, "Error: no debería ser bimensual"
    assert periodo_mensual.nombre_corto == "Mar", f"Error: nombre esperado 'Mar', obtenido '{periodo_mensual.nombre_corto}'"
    assert periodo_mensual.clase_css == "bg-success", "Error: clase CSS incorrecta"
    print(f"OK - Período mensual: {periodo_mensual.nombre_corto} ({periodo_mensual.clase_css})")

    # Test 2: Período bimensual
    periodo_bi = PeriodoPago(2025, 1, 2, pagado=False)
    assert periodo_bi.es_bimensual, "Error: debería ser bimensual"
    assert periodo_bi.nombre_corto == "Ene/Feb", f"Error: nombre esperado 'Ene/Feb', obtenido '{periodo_bi.nombre_corto}'"
    assert periodo_bi.clase_css == "bg-danger", "Error: clase CSS incorrecta"
    print(f"OK - Período bimensual: {periodo_bi.nombre_corto} ({periodo_bi.clase_css})")

    # Test 3: Contiene mes
    assert periodo_bi.contiene_mes(1), "Error: debería contener enero"
    assert periodo_bi.contiene_mes(2), "Error: debería contener febrero"
    assert not periodo_bi.contiene_mes(3), "Error: no debería contener marzo"
    print(f"OK - Contiene mes: {periodo_bi.nombre_corto} contiene meses 1 y 2")

    # Test 4: Tooltip
    tooltip = periodo_bi.tooltip
    assert "Pendiente" in tooltip, f"Error en tooltip: {tooltip}"
    print(f"OK - Tooltip: {tooltip}")

    print("\nTODOS LOS TESTS DE PeriodoPago PASARON!\n")


def test_horario_helper():
    """Prueba las funcionalidades del HorarioSemanalHelper."""
    print("=" * 60)
    print("TEST 3: HorarioSemanalHelper")
    print("=" * 60)

    # Test 1: Formatear horario
    hora_inicio = time(9, 0)
    hora_fin = time(10, 15)
    horario_str = HorarioSemanalHelper.formatear_horario(hora_inicio, hora_fin)
    assert horario_str == "09:00 - 10:15", f"Error: esperado '09:00 - 10:15', obtenido '{horario_str}'"
    print(f"OK - Formatear horario: {horario_str}")

    # Test 2: Parsear hora
    hora_parseada = HorarioSemanalHelper.parsear_hora("14:30")
    assert hora_parseada == time(14, 30), f"Error al parsear hora: {hora_parseada}"
    print(f"OK - Parsear hora: {hora_parseada}")

    # Test 3: Generar horas disponibles
    horas = HorarioSemanalHelper.generar_horas_disponibles(8, 12)
    assert len(horas) == 4, f"Error: esperado 4 horas, obtenido {len(horas)}"
    assert horas[0] == "08:00", f"Error: primera hora incorrecta {horas[0]}"
    print(f"OK - Horas disponibles: {len(horas)} horas generadas")

    print("\nTODOS LOS TESTS DE HorarioSemanalHelper PASARON!\n")


def test_contexto_calendario():
    """Prueba la creación del contexto de calendario para templates."""
    print("=" * 60)
    print("TEST 4: Contexto para Templates")
    print("=" * 60)

    ctx = crear_contexto_calendario(2025)

    # Verificar que todas las claves existen
    claves_requeridas = ['calendario', 'meses_nombres', 'meses_completos',
                        'dias_semana', 'formatear_fecha', 'formatear_horario',
                        'current_year', 'current_month']

    for clave in claves_requeridas:
        assert clave in ctx, f"Error: falta la clave '{clave}' en el contexto"

    print(f"OK - Contexto contiene todas las claves requeridas: {', '.join(claves_requeridas)}")

    # Verificar tipos
    assert isinstance(ctx['calendario'], CalendarioAcademico), "Error: calendario no es CalendarioAcademico"
    assert isinstance(ctx['meses_nombres'], list), "Error: meses_nombres no es lista"
    assert len(ctx['meses_nombres']) == 12, "Error: meses_nombres no tiene 12 elementos"
    assert isinstance(ctx['dias_semana'], list), "Error: dias_semana no es lista"
    assert len(ctx['dias_semana']) == 7, "Error: dias_semana no tiene 7 elementos"
    print(f"OK - Tipos de datos correctos")

    print("\nTODOS LOS TESTS DE Contexto PASARON!\n")


def test_integracion_pagos():
    """Prueba la integración con pagos simulados."""
    print("=" * 60)
    print("TEST 5: Integración con Pagos")
    print("=" * 60)

    cal = CalendarioAcademico(2025)

    # Simular pagos
    class PagoMock:
        def __init__(self, mes, tipo_pago='cuota'):
            self.mes = mes
            self.tipo_pago = tipo_pago

    pagos = [
        PagoMock("2025-01"),  # Enero pagado
        PagoMock("2025-02"),  # Febrero pagado
        PagoMock("2025-05"),  # Mayo pagado
    ]

    # Test 1: Períodos mensuales con pagos
    periodos = cal.generar_periodos_con_pagos(False, pagos)
    assert len(periodos) == 12, "Error: debería haber 12 períodos"
    assert periodos[0].pagado, "Error: enero debería estar pagado"
    assert periodos[1].pagado, "Error: febrero debería estar pagado"
    assert not periodos[2].pagado, "Error: marzo no debería estar pagado"
    assert periodos[4].pagado, "Error: mayo debería estar pagado"
    print(f"OK - Períodos mensuales con pagos: 3 de 12 pagados")

    # Test 2: Períodos bimensuales con pagos
    periodos_bi = cal.generar_periodos_con_pagos(True, pagos)
    assert len(periodos_bi) == 6, "Error: debería haber 6 períodos bimensuales"
    assert periodos_bi[0].pagado, "Error: Ene/Feb debería estar pagado (ambos meses pagados)"
    assert not periodos_bi[1].pagado, "Error: Mar/Abr no debería estar pagado"
    assert periodos_bi[2].pagado, "Error: May/Jun debería estar pagado (mayo pagado)"
    print(f"OK - Períodos bimensuales con pagos: correctamente marcados")

    print("\nTODOS LOS TESTS DE Integración PASARON!\n")


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 60)
    print("EJECUTANDO TESTS DEL SISTEMA DE CALENDARIO")
    print("=" * 60 + "\n")

    try:
        test_calendario_academico()
        test_periodo_pago()
        test_horario_helper()
        test_contexto_calendario()
        test_integracion_pagos()

        print("=" * 60)
        print("TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("=" * 60)
        print("\nEl sistema de calendario centralizado funciona correctamente.")
        print("Ahora puedes usar las utilidades en toda la aplicación.\n")

        return 0

    except AssertionError as e:
        print(f"\nERROR EN TEST: {e}\n")
        return 1
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
