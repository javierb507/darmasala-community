"""
Utilidades centralizadas para manejo de calendario, fechas y períodos de pago.

Este módulo proporciona funciones reutilizables para:
- Cálculo de períodos de pago mensuales y bimensuales
- Formateo de fechas académicas
- Generación de calendarios de pagos
- Validación de períodos
"""

from datetime import datetime, date, time, timedelta
from typing import List, Dict, Tuple, Optional
from calendar import monthrange


# Constantes
MESES_NOMBRES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

MESES_NOMBRES_COMPLETOS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
DIAS_SEMANA_CORTOS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


class PeriodoPago:
    """Representa un período de pago (mensual o bimensual)."""

    def __init__(self, año: int, mes_inicio: int, mes_fin: int = None, pagado: bool = False):
        """
        Args:
            año: Año del período
            mes_inicio: Mes de inicio (1-12)
            mes_fin: Mes de fin para períodos bimensuales (1-12), None para mensuales
            pagado: Si el período está pagado
        """
        self.año = año
        self.mes_inicio = mes_inicio
        self.mes_fin = mes_fin if mes_fin else mes_inicio
        self.pagado = pagado
        self.es_bimensual = mes_fin is not None and mes_fin != mes_inicio

    @property
    def nombre_corto(self) -> str:
        """Retorna el nombre corto del período (ej: 'Ene/Feb', 'Mar')."""
        if self.es_bimensual:
            return f"{MESES_NOMBRES[self.mes_inicio-1]}/{MESES_NOMBRES[self.mes_fin-1]}"
        return MESES_NOMBRES[self.mes_inicio-1]

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del período."""
        if self.es_bimensual:
            return f"{MESES_NOMBRES_COMPLETOS[self.mes_inicio-1]}/{MESES_NOMBRES_COMPLETOS[self.mes_fin-1]} {self.año}"
        return f"{MESES_NOMBRES_COMPLETOS[self.mes_inicio-1]} {self.año}"

    @property
    def clase_css(self) -> str:
        """Retorna la clase CSS según el estado de pago."""
        return "bg-success" if self.pagado else "bg-danger"

    @property
    def icono(self) -> str:
        """Retorna el icono según el estado de pago."""
        return "✅" if self.pagado else "❌"

    @property
    def tooltip(self) -> str:
        """Retorna el texto del tooltip."""
        estado = "Pagado" if self.pagado else "Pendiente"
        return f"{self.icono} {estado}: {self.nombre_completo}"

    def contiene_mes(self, mes: int) -> bool:
        """Verifica si un mes está contenido en este período."""
        return self.mes_inicio <= mes <= self.mes_fin


class CalendarioAcademico:
    """Maneja la lógica del calendario académico y períodos de pago."""

    def __init__(self, año_actual: Optional[int] = None):
        """
        Args:
            año_actual: Año a usar, por defecto el año actual
        """
        self.año = año_actual if año_actual else datetime.now().year
        self.mes_actual = datetime.now().month

    def get_año_academico_formato(self, año: Optional[int] = None) -> str:
        """
        Retorna el formato académico del año (ej: '25/26' para 2025-2026).

        Args:
            año: Año base, por defecto usa el año del calendario
        """
        año_base = año if año else self.año
        año_siguiente = año_base + 1
        return f"{año_base % 100:02d}/{año_siguiente % 100:02d}"

    def generar_periodos_mensuales(self, año: Optional[int] = None) -> List[PeriodoPago]:
        """
        Genera lista de períodos mensuales para el año.

        Args:
            año: Año para generar períodos, por defecto usa el año del calendario

        Returns:
            Lista de 12 PeriodoPago mensuales
        """
        año_usar = año if año else self.año
        return [PeriodoPago(año_usar, mes) for mes in range(1, 13)]

    def generar_periodos_bimensuales(self, año: Optional[int] = None) -> List[PeriodoPago]:
        """
        Genera lista de períodos bimensuales para el año.

        Args:
            año: Año para generar períodos, por defecto usa el año del calendario

        Returns:
            Lista de 6 PeriodoPago bimensuales
        """
        año_usar = año if año else self.año
        periodos = []
        for bimestre in range(6):
            mes1 = bimestre * 2 + 1
            mes2 = bimestre * 2 + 2
            periodos.append(PeriodoPago(año_usar, mes1, mes2))
        return periodos

    def generar_periodos_con_pagos(self, es_bimensual: bool, pagos: list, año: Optional[int] = None) -> List[PeriodoPago]:
        """
        Genera períodos de pago marcando cuáles están pagados.

        Args:
            es_bimensual: Si los períodos son bimensuales
            pagos: Lista de objetos Pago del alumno
            año: Año para generar períodos

        Returns:
            Lista de PeriodoPago con estado de pago actualizado
        """
        año_usar = año if año else self.año

        # Generar períodos base
        if es_bimensual:
            periodos = self.generar_periodos_bimensuales(año_usar)
        else:
            periodos = self.generar_periodos_mensuales(año_usar)

        # Marcar períodos pagados
        for pago in pagos:
            if pago.tipo_pago != 'cuota' or not pago.mes:
                continue

            # Extraer año y mes del pago (formato: YYYY-MM)
            try:
                pago_año, pago_mes = map(int, pago.mes.split('-'))
                if pago_año != año_usar:
                    continue

                # Marcar el período correspondiente como pagado
                for periodo in periodos:
                    if periodo.contiene_mes(pago_mes):
                        periodo.pagado = True
                        break
            except (ValueError, AttributeError):
                continue

        return periodos

    @staticmethod
    def formatear_fecha(fecha: date, formato: str = 'corto') -> str:
        """
        Formatea una fecha según el formato especificado.

        Args:
            fecha: Objeto date a formatear
            formato: 'corto' (dd/mm/yyyy), 'largo' (DD de Mes de YYYY), 'iso' (YYYY-MM-DD)

        Returns:
            Fecha formateada como string
        """
        if not fecha:
            return ''

        if formato == 'iso':
            return fecha.strftime('%Y-%m-%d')
        elif formato == 'largo':
            dia = fecha.day
            mes = MESES_NOMBRES_COMPLETOS[fecha.month - 1]
            año = fecha.year
            return f"{dia} de {mes} de {año}"
        else:  # formato corto
            return fecha.strftime('%d/%m/%Y')

    @staticmethod
    def parsear_fecha(fecha_str: str, formato: str = 'iso') -> Optional[date]:
        """
        Parsea un string a objeto date.

        Args:
            fecha_str: String con la fecha
            formato: 'iso' (YYYY-MM-DD), 'corto' (dd/mm/yyyy), 'month' (YYYY-MM)

        Returns:
            Objeto date o None si hay error
        """
        if not fecha_str:
            return None

        try:
            if formato == 'iso':
                return datetime.strptime(fecha_str, '%Y-%m-%d').date()
            elif formato == 'corto':
                return datetime.strptime(fecha_str, '%d/%m/%Y').date()
            elif formato == 'month':
                # Para input type="month" (YYYY-MM)
                return datetime.strptime(fecha_str + '-01', '%Y-%m-%d').date()
        except ValueError:
            return None

        return None

    @staticmethod
    def calcular_hora_fin(hora_inicio: time, duracion_minutos: int = 75) -> time:
        """
        Calcula la hora de finalización sumando minutos.

        Args:
            hora_inicio: Hora de inicio
            duracion_minutos: Duración en minutos (por defecto 75 = 1h15m)

        Returns:
            Hora de finalización
        """
        inicio_dt = datetime.combine(date.today(), hora_inicio)
        fin_dt = inicio_dt + timedelta(minutes=duracion_minutos)
        return fin_dt.time()

    @staticmethod
    def get_primer_dia_mes(año: int, mes: int) -> date:
        """Retorna el primer día del mes."""
        return date(año, mes, 1)

    @staticmethod
    def get_ultimo_dia_mes(año: int, mes: int) -> date:
        """Retorna el último día del mes."""
        ultimo_dia = monthrange(año, mes)[1]
        return date(año, mes, ultimo_dia)

    @staticmethod
    def get_rango_semana(fecha: Optional[date] = None) -> Tuple[date, date]:
        """
        Retorna el rango de fechas de la semana (lunes a domingo).

        Args:
            fecha: Fecha de referencia, por defecto hoy

        Returns:
            Tupla (fecha_inicio_semana, fecha_fin_semana)
        """
        if not fecha:
            fecha = date.today()

        # Calcular inicio de semana (lunes)
        dias_desde_lunes = fecha.weekday()
        inicio_semana = fecha - timedelta(days=dias_desde_lunes)

        # Calcular fin de semana (domingo)
        fin_semana = inicio_semana + timedelta(days=6)

        return inicio_semana, fin_semana

    @staticmethod
    def get_mes_nombre(mes: int, completo: bool = False) -> str:
        """
        Retorna el nombre del mes.

        Args:
            mes: Número del mes (1-12)
            completo: Si True retorna nombre completo, sino nombre corto

        Returns:
            Nombre del mes
        """
        if not 1 <= mes <= 12:
            return ''

        if completo:
            return MESES_NOMBRES_COMPLETOS[mes - 1]
        return MESES_NOMBRES[mes - 1]

    @staticmethod
    def get_dia_semana_nombre(dia: int, completo: bool = True) -> str:
        """
        Retorna el nombre del día de la semana.

        Args:
            dia: Número del día (0=Lunes, 6=Domingo)
            completo: Si True retorna nombre completo, sino nombre corto

        Returns:
            Nombre del día
        """
        if not 0 <= dia <= 6:
            return ''

        if completo:
            return DIAS_SEMANA[dia]
        return DIAS_SEMANA_CORTOS[dia]

    def verificar_matricula_vigente(self, fecha_matricula: Optional[date], año_academico: Optional[int] = None) -> bool:
        """
        Verifica si la matrícula está vigente para el año académico.

        Args:
            fecha_matricula: Fecha en que se pagó la matrícula
            año_academico: Año académico a verificar, por defecto el actual

        Returns:
            True si la matrícula está vigente
        """
        if not fecha_matricula:
            return False

        año_verificar = año_academico if año_academico else self.año
        return fecha_matricula.year == año_verificar

    def get_meses_transcurridos(self, desde_mes: int = 1) -> int:
        """
        Retorna cuántos meses han transcurrido en el año actual.

        Args:
            desde_mes: Mes desde el que contar (por defecto enero)

        Returns:
            Número de meses transcurridos
        """
        if self.mes_actual >= desde_mes:
            return self.mes_actual - desde_mes + 1
        return 0


class HorarioSemanalHelper:
    """Helper para gestión de horarios semanales."""

    @staticmethod
    def formatear_horario(hora_inicio: time, hora_fin: time) -> str:
        """
        Formatea un rango de horas.

        Args:
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin

        Returns:
            String formateado (ej: "09:00 - 10:15")
        """
        return f"{hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}"

    @staticmethod
    def parsear_hora(hora_str: str) -> Optional[time]:
        """
        Parsea un string a objeto time.

        Args:
            hora_str: String en formato HH:MM

        Returns:
            Objeto time o None si hay error
        """
        try:
            return datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            return None

    @staticmethod
    def generar_horas_disponibles(hora_inicio: int = 8, hora_fin: int = 22) -> List[str]:
        """
        Genera lista de horas disponibles para horarios.

        Args:
            hora_inicio: Hora de inicio (por defecto 8)
            hora_fin: Hora de fin (por defecto 22)

        Returns:
            Lista de strings con horas en formato HH:00
        """
        return [f"{hora:02d}:00" for hora in range(hora_inicio, hora_fin)]


# Función de conveniencia para usar en templates Jinja2
def crear_contexto_calendario(año: Optional[int] = None) -> Dict:
    """
    Crea un diccionario con utilidades de calendario para usar en templates.

    Args:
        año: Año a usar, por defecto el actual

    Returns:
        Diccionario con funciones y constantes de calendario
    """
    calendario = CalendarioAcademico(año)

    return {
        'calendario': calendario,
        'meses_nombres': MESES_NOMBRES,
        'meses_completos': MESES_NOMBRES_COMPLETOS,
        'dias_semana': DIAS_SEMANA,
        'formatear_fecha': CalendarioAcademico.formatear_fecha,
        'formatear_horario': HorarioSemanalHelper.formatear_horario,
        'current_year': calendario.año,
        'current_month': calendario.mes_actual,
    }
