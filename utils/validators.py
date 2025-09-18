"""
Validadores personalizados para la aplicación
"""
import re
from datetime import datetime, date

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

class Validators:
    
    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        if not email:
            return True  # Email es opcional
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Formato de email inválido")
        return True
    
    @staticmethod
    def validate_phone(phone):
        """Validar formato de teléfono español"""
        if not phone:
            return True  # Teléfono es opcional
        
        # Limpiar espacios y caracteres especiales
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Patrones válidos para España
        patterns = [
            r'^\+34[6-9]\d{8}$',  # +34 seguido de móvil
            r'^[6-9]\d{8}$',      # Móvil sin prefijo
            r'^\+34[8-9]\d{8}$',  # +34 seguido de fijo
            r'^[8-9]\d{8}$'       # Fijo sin prefijo
        ]
        
        if not any(re.match(pattern, clean_phone) for pattern in patterns):
            raise ValidationError("Formato de teléfono inválido. Use formato español (ej: 612345678)")
        return True
    
    @staticmethod
    def validate_nif_cif(nif_cif):
        """Validar formato de NIF/CIF español"""
        if not nif_cif:
            return True  # Es opcional
        
        nif_cif = nif_cif.upper().replace(' ', '').replace('-', '')
        
        # Validar NIF (DNI)
        if re.match(r'^\d{8}[A-Z]$', nif_cif):
            return Validators._validate_nif(nif_cif)
        
        # Validar CIF
        if re.match(r'^[A-Z]\d{7}[A-Z0-9]$', nif_cif):
            return Validators._validate_cif(nif_cif)
        
        raise ValidationError("Formato de NIF/CIF inválido")
    
    @staticmethod
    def _validate_nif(nif):
        """Validar dígito de control del NIF"""
        letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
        number = int(nif[:8])
        letter = nif[8]
        
        if letters[number % 23] != letter:
            raise ValidationError("NIF inválido - dígito de control incorrecto")
        return True
    
    @staticmethod
    def _validate_cif(cif):
        """Validar dígito de control del CIF"""
        # Implementación simplificada - en producción usar algoritmo completo
        return True
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validar que la fecha de fin sea posterior a la de inicio"""
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end_date <= start_date:
                raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        return True
    
    @staticmethod
    def validate_positive_amount(amount):
        """Validar que el importe sea positivo"""
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValidationError("El importe debe ser mayor que cero")
            if amount > 999999.99:
                raise ValidationError("El importe es demasiado alto")
            return True
        except (ValueError, TypeError):
            raise ValidationError("Importe inválido")
    
    @staticmethod
    def validate_required_field(value, field_name):
        """Validar que un campo requerido no esté vacío"""
        if not value or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"El campo {field_name} es obligatorio")
        return True
    
    @staticmethod
    def validate_age_range(birth_date, min_age=0, max_age=120):
        """Validar que la edad esté en un rango válido"""
        if not birth_date:
            return True
        
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < min_age or age > max_age:
            raise ValidationError(f"La edad debe estar entre {min_age} y {max_age} años")
        
        if birth_date > today:
            raise ValidationError("La fecha de nacimiento no puede ser futura")
        
        return True
    
    @staticmethod
    def validate_invoice_number(invoice_number):
        """Validar formato de número de factura"""
        if not invoice_number or not invoice_number.strip():
            raise ValidationError("El número de factura es obligatorio")
        
        # Permitir varios formatos comunes
        patterns = [
            r'^[A-Z]{1,3}-?\d{4,}$',  # ABC-1234 o ABC1234
            r'^\d{4,}$',              # 1234
            r'^F-?\d{4,}$'            # F-1234 o F1234
        ]
        
        if not any(re.match(pattern, invoice_number.upper()) for pattern in patterns):
            raise ValidationError("Formato de número de factura inválido")
        
        return True

# Decorador para validación automática
def validate_form_data(validators_dict):
    """
    Decorador para validar datos de formulario automáticamente
    
    Uso:
    @validate_form_data({
        'email': Validators.validate_email,
        'phone': Validators.validate_phone,
        'amount': Validators.validate_positive_amount
    })
    def my_route():
        # Los datos ya están validados aquí
        pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request, flash
            
            for field_name, validator in validators_dict.items():
                field_value = request.form.get(field_name)
                try:
                    validator(field_value)
                except ValidationError as e:
                    flash(f"Error en {field_name}: {str(e)}", 'error')
                    return redirect(request.url)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator