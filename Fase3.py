import os

class Simbolo:
    """
    Representa una variable o función almacenada en la memoria del compilador.
    """
    def __init__(self, nombre, tipo_dato, linea, valor=None):
        self.nombre = nombre
        self.tipo_dato = tipo_dato.lower() # int, float, string, bool, void
        self.linea = linea
        self.valor = valor

    def __str__(self):
        # Formato de columna para que el archivo .out se vea ordenado y profesional
        val = self.valor if self.valor is not None else "NULL"
        return f"{self.nombre:<15} | {self.tipo_dato:<10} | {str(val):<15} | {self.linea}"


class AnalizadorSemantico:
    """
    Cerebro de la Fase 3. Gestiona la memoria (Tabla de Símbolos),
    verifica los tipos de datos y recupera errores lógicos.
    """
    def __init__(self):
        # Diccionario para acceso rápido: {'nombre_variable': objeto_Simbolo}
        self.tabla_simbolos = {}
        self.errores_semanticos = []

    def declarar_variable(self, nombre, tipo, linea):
        """ Registra una nueva variable en la memoria si no existe. """
        if nombre in self.tabla_simbolos:
            self.registrar_error(linea, f"Redeclaración de variable: '{nombre}' ya fue declarada previamente.")
            return False
        
        self.tabla_simbolos[nombre] = Simbolo(nombre, tipo, linea)
        return True

    def obtener_simbolo(self, nombre, linea):
        """ Busca una variable. Lanza error si se usa sin declarar. """
        if nombre not in self.tabla_simbolos:
            self.registrar_error(linea, f"Variable no declarada: Intentando usar '{nombre}' sin declararla antes.")
            return None
        return self.tabla_simbolos[nombre]

    def asignar_valor(self, nombre, valor, tipo_valor_obtenido, linea):
        """ Asigna un valor a una variable, verificando que los tipos sean compatibles. """
        simbolo = self.obtener_simbolo(nombre, linea)
        if not simbolo:
            return False

        # Verificamos si la matemática y los tipos permiten la asignación
        if self.verificar_coercion(simbolo.tipo_dato, tipo_valor_obtenido, linea):
            simbolo.valor = valor
            return True
        return False

    def verificar_coercion(self, tipo_esperado, tipo_obtenido, linea):
        """ Comprueba si 'tipo_obtenido' puede guardarse dentro de 'tipo_esperado'. """
        # Si venía un error desde el parser, lo ignoramos para no saturar la consola
        if tipo_esperado == 'error' or tipo_obtenido == 'error':
            return False

        tipo_esperado = tipo_esperado.lower()
        tipo_obtenido = tipo_obtenido.lower()

        # 1. Si son exactamente el mismo tipo, es válido
        if tipo_esperado == tipo_obtenido:
            return True
        
        # 2. Coerción permitida: Se puede guardar un INT en un FLOAT
        if tipo_esperado == 'float' and tipo_obtenido == 'int':
            return True
        
        # Cualquier otra combinación es un error de incompatibilidad
        self.registrar_error(linea, f"Incompatibilidad de tipos: No se puede asignar un valor '{tipo_obtenido}' a una variable de tipo '{tipo_esperado}'.")
        return False

    def resolver_operacion_matematica(self, tipo_izq, tipo_der, operador, linea):
        """ Define qué tipo de dato resulta al operar dos variables o literales. """
        if tipo_izq == 'error' or tipo_der == 'error':
            return 'error'

        tipo_izq = tipo_izq.lower()
        tipo_der = tipo_der.lower()

        # Operaciones Aritméticas (+, -, *, /, %)
        if operador in ['+', '-', '*', '/', '%']:
            if tipo_izq in ['int', 'float'] and tipo_der in ['int', 'float']:
                # Si hay un float involucrado, el resultado se "contamina" a float
                if tipo_izq == 'float' or tipo_der == 'float':
                    return 'float'
                return 'int'
            
            # Concatenación de cadenas (Strings)
            if operador == '+' and (tipo_izq == 'string' or tipo_der == 'string'):
                return 'string'

        # Operaciones Relacionales (==, !=, <, >, <=, >=)
        if operador in ['==', '!=', '<', '>', '<=', '>=']:
            if tipo_izq in ['int', 'float'] and tipo_der in ['int', 'float']:
                return 'bool'
            if tipo_izq == tipo_der: # Permite comparar dos strings o dos booleanos
                return 'bool'

        # Operaciones Lógicas (and, or)
        if operador in ['and', 'or', 'AND', 'OR']:
            if tipo_izq == 'bool' and tipo_der == 'bool':
                return 'bool'

        # Si no cayó en ninguno de los casos válidos, es un error
        self.registrar_error(linea, f"Operación inválida: No se puede aplicar el operador '{operador}' entre '{tipo_izq}' y '{tipo_der}'.")
        return 'error'

    def registrar_error(self, linea, mensaje):
        """ Guarda el error semántico para mostrarlo al final (Modo Pánico) """
        error_msg = f"Línea {linea} | Error Semántico: {mensaje}"
        self.errores_semanticos.append(error_msg)

    def exportar_tabla(self, ruta_archivo="tabla_simbolos.out"):
        """ 
        REQUISITO DE LA RÚBRICA (25 PTS): Genera el archivo físico .out con la tabla.
        """
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write("="*65 + "\n")
                f.write(f"{'NOMBRE':<15} | {'TIPO':<10} | {'VALOR ACTUAL':<15} | {'LÍNEA DECLARACIÓN'}\n")
                f.write("="*65 + "\n")
                
                if not self.tabla_simbolos:
                    f.write("La tabla de símbolos está vacía.\n")
                else:
                    for nombre, simbolo in self.tabla_simbolos.items():
                        f.write(str(simbolo) + "\n")
                
                f.write("="*65 + "\n")
        except Exception as e:
            print(f"Ocurrió un error al intentar exportar la tabla: {e}")