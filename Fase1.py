# Tipos de token y clases
class TipoToken:
    # Palabras Clave
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    BOOL = 'BOOL'
    VOID = 'VOID'
    RETURN = 'RETURN'
    DEF = 'DEF'
    READ = 'READ'
    WRITE = 'WRITE'
    
    # Operadores lógicos
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    # Literales e Identificadores
    ID = 'ID'
    NUMERO_ENTERO = 'NUMERO_ENTERO'
    NUMERO_FLOTANTE = 'NUMERO_FLOTANTE'
    CADENA_LITERAL = 'CADENA_LITERAL'
    BOOLEANO_LITERAL = 'BOOLEANO_LITERAL' 
    
    # Operadores y Símbolos
    SUMA = 'SUMA' 
    RESTA = 'RESTA' 
    MULTIPLICACION = 'MULTIPLICACION'
    DIVISION = 'DIVISION'
    MODULO = 'MODULO'
    MAYOR_QUE = 'MAYOR_QUE'
    MENOR_QUE = 'MENOR_QUE'
    MAYOR_IGUAL = 'MAYOR_IGUAL'
    MENOR_IGUAL = 'MENOR_IGUAL'
    IGUAL_QUE = 'IGUAL_QUE'
    DIFERENTE_QUE = 'DIFERENTE_QUE'
    ASIGNACION = 'ASIGNACION'
    PARENTESIS_IZQ = 'PARENTESIS_IZQ'
    PARENTESIS_DER = 'PARENTESIS_DER'
    DOS_PUNTOS = 'DOS_PUNTOS'
    COMA = 'COMA'
    
    # Control
    NUEVA_LINEA = 'NUEVA_LINEA'
    INDENTAR = 'INDENTAR'
    DESINDENTAR = 'DESINDENTAR'
    FIN_ARCHIVO = 'EOF'
    DESCONOCIDO = 'UNKNOWN'


class Token:
    def __init__(self, tipo, valor, linea, col_inicio, col_fin):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.col_inicio = col_inicio
        self.col_fin = col_fin

    def __str__(self):
        if self.tipo in [TipoToken.NUEVA_LINEA, TipoToken.INDENTAR, TipoToken.DESINDENTAR, TipoToken.FIN_ARCHIVO]:
            return f"<{self.tipo}> línea {self.linea}, col {self.col_inicio}-{self.col_fin}"
        return f"<{self.tipo}> línea {self.linea}, col {self.col_inicio}-{self.col_fin}: '{self.valor}'"


class ErrorLexico:
    def __init__(self, linea, columna, mensaje):
        self.linea = linea
        self.columna = columna
        self.mensaje = mensaje

    def __str__(self):
        # Formato mejorado para la consola de la interfaz gráfica
        return f"Línea {self.linea}, Columna {self.columna} | Error Léxico: {self.mensaje}"


#Analizaro léxico a partir de acá

class AnalizadorLexico:
    def __init__(self):
        # Se inicializan las variables vacías. El código se pasa en el método analizar()
        self.fuente = ""
        self.longitud = 0
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.pila_indentacion = [0] 
        self.tokens = []
        self.errores = []
        
        self.palabras_clave = {
            "if": TipoToken.IF, "else": TipoToken.ELSE, "while": TipoToken.WHILE,
            "int": TipoToken.INT, "float": TipoToken.FLOAT, "string": TipoToken.STRING,
            "bool": TipoToken.BOOL, "void": TipoToken.VOID, "return": TipoToken.RETURN,
            "def": TipoToken.DEF, "read": TipoToken.READ, "write": TipoToken.WRITE,
            "true": TipoToken.BOOLEANO_LITERAL, "false": TipoToken.BOOLEANO_LITERAL,
            "and": TipoToken.AND, "or": TipoToken.OR, "not": TipoToken.NOT
        }

    def analizar(self, codigo_fuente):
        # Reiniciar el estado para cada ejecución
        self.fuente = codigo_fuente.replace('\r\n', '\n') + '\n'
        self.longitud = len(self.fuente)
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.pila_indentacion = [0] 
        self.tokens = []
        self.errores = []

        inicio_de_linea = True 
        while self.posicion < self.longitud:
            caracter = self.fuente[self.posicion]

            if inicio_de_linea:
                if caracter == '\n':
                    self.posicion += 1; self.linea += 1; self.columna = 1; continue
                if caracter == '#':
                    self.saltar_comentario(); continue
                if caracter.isspace():
                    espacios = self.contar_indentacion()
                    if self.posicion < self.longitud and self.fuente[self.posicion] not in ['\n', '#']:
                        self.procesar_indentacion(espacios)
                        inicio_de_linea = False
                    continue
                else:
                    self.procesar_indentacion(0)
                    inicio_de_linea = False
            
            if caracter.isspace():
                if caracter == '\n':
                    self.tokens.append(Token(TipoToken.NUEVA_LINEA, "\\n", self.linea, self.columna, self.columna))
                    self.posicion += 1; self.linea += 1; self.columna = 1
                    inicio_de_linea = True
                else:
                    self.posicion += 1; self.columna += 1
                continue

            if caracter == '#':
                self.saltar_comentario(); continue 

            if caracter.isalpha() or caracter == '_':
                self.escanear_identificador(); continue

            if caracter.isdigit():
                self.escanear_numero(); continue

            if caracter == '"':
                self.escanear_cadena(); continue

            if self.escanear_operador(caracter):
                continue

            # Registro de error léxico con el nuevo formato
            self.errores.append(ErrorLexico(self.linea, self.columna, f"Carácter inesperado '{caracter}'"))
            self.posicion += 1; self.columna += 1

        while len(self.pila_indentacion) > 1:
            self.pila_indentacion.pop()
            self.tokens.append(Token(TipoToken.DESINDENTAR, "", self.linea, self.columna, self.columna))
        
        return self.tokens, self.errores

    def contar_indentacion(self):
        contador = 0
        pos_temporal = self.posicion
        while pos_temporal < self.longitud and self.fuente[pos_temporal] in [' ', '\t']:
            contador += 4 if self.fuente[pos_temporal] == '\t' else 1
            pos_temporal += 1
        chars_consumidos = pos_temporal - self.posicion
        self.posicion = pos_temporal
        self.columna += chars_consumidos
        return contador

    def procesar_indentacion(self, espacios):
        nivel_actual = self.pila_indentacion[-1]
        if espacios > nivel_actual:
            self.pila_indentacion.append(espacios)
            self.tokens.append(Token(TipoToken.INDENTAR, "", self.linea, 1, espacios))
        elif espacios < nivel_actual:
            while espacios < self.pila_indentacion[-1]:
                self.pila_indentacion.pop()
                self.tokens.append(Token(TipoToken.DESINDENTAR, "", self.linea, 1, espacios))
                if len(self.pila_indentacion) == 0: 
                    self.pila_indentacion.append(0)
                    break
            if self.pila_indentacion[-1] != espacios:
                self.errores.append(ErrorLexico(self.linea, 1, "Indentación inválida (no coincide con niveles previos)"))

    def saltar_comentario(self):
        while self.posicion < self.longitud and self.fuente[self.posicion] != '\n':
            self.posicion += 1

    def escanear_identificador(self):
        col_inicio = self.columna
        pos_inicio = self.posicion
        while self.posicion < self.longitud and (self.fuente[self.posicion].isalnum() or self.fuente[self.posicion] == '_'):
            self.posicion += 1; self.columna += 1
        lexema = self.fuente[pos_inicio:self.posicion]
        if len(lexema) > 31:
            self.errores.append(ErrorLexico(self.linea, col_inicio, "Identificador excede 31 caracteres (truncado)"))
            lexema = lexema[:31] 
        tipo_token = self.palabras_clave.get(lexema, TipoToken.ID)
        if lexema in ["true", "false"]:
            tipo_token = TipoToken.BOOLEANO_LITERAL
        self.tokens.append(Token(tipo_token, lexema, self.linea, col_inicio, self.columna - 1))

    def escanear_numero(self):
        col_inicio = self.columna
        pos_inicio = self.posicion
        es_flotante = False
        while self.posicion < self.longitud and self.fuente[self.posicion].isdigit():
            self.posicion += 1; self.columna += 1
        if self.posicion < self.longitud and self.fuente[self.posicion] == '.':
            es_flotante = True
            self.posicion += 1; self.columna += 1
            if self.posicion >= self.longitud or not self.fuente[self.posicion].isdigit():
                 self.errores.append(ErrorLexico(self.linea, self.columna, "Número flotante mal formado"))
            while self.posicion < self.longitud and self.fuente[self.posicion].isdigit():
                self.posicion += 1; self.columna += 1
        lexema = self.fuente[pos_inicio:self.posicion]
        tipo = TipoToken.NUMERO_FLOTANTE if es_flotante else TipoToken.NUMERO_ENTERO
        self.tokens.append(Token(tipo, lexema, self.linea, col_inicio, self.columna - 1))

    def escanear_cadena(self):
        col_inicio = self.columna
        self.posicion += 1; self.columna += 1 
        pos_inicio_contenido = self.posicion
        while self.posicion < self.longitud and self.fuente[self.posicion] != '"' and self.fuente[self.posicion] != '\n':
            self.posicion += 1; self.columna += 1
        if self.posicion >= self.longitud or self.fuente[self.posicion] == '\n':
            self.errores.append(ErrorLexico(self.linea, col_inicio, "Cadena sin cerrar antes de fin de línea"))
            lexema = self.fuente[pos_inicio_contenido:self.posicion]
            self.tokens.append(Token(TipoToken.CADENA_LITERAL, lexema + '"', self.linea, col_inicio, self.columna - 1))
            return
        lexema = self.fuente[pos_inicio_contenido:self.posicion]
        self.posicion += 1; self.columna += 1 
        self.tokens.append(Token(TipoToken.CADENA_LITERAL, lexema + '"', self.linea, col_inicio, self.columna - 1))

    def escanear_operador(self, caracter):
        col_inicio = self.columna
        siguiente_char = self.fuente[self.posicion + 1] if self.posicion + 1 < self.longitud else ''
        dobles = {'>=': TipoToken.MAYOR_IGUAL, '<=': TipoToken.MENOR_IGUAL, '==': TipoToken.IGUAL_QUE, '!=': TipoToken.DIFERENTE_QUE}
        
        # Eliminados LLAVE_IZQ, LLAVE_DER y PUNTO_Y_COMA para evitar warnings en PLY
        simples = {'+': TipoToken.SUMA, '-': TipoToken.RESTA, '*': TipoToken.MULTIPLICACION, '/': TipoToken.DIVISION,
                   '%': TipoToken.MODULO, '(': TipoToken.PARENTESIS_IZQ, ')': TipoToken.PARENTESIS_DER, 
                   ',': TipoToken.COMA, ':': TipoToken.DOS_PUNTOS, '>': TipoToken.MAYOR_QUE, '<': TipoToken.MENOR_QUE, '=': TipoToken.ASIGNACION}
        
        combinacion = caracter + siguiente_char
        if combinacion in dobles:
            self.tokens.append(Token(dobles[combinacion], combinacion, self.linea, col_inicio, col_inicio + 2))
            self.posicion += 2; self.columna += 2; return True
        
        if caracter in simples:
            self.tokens.append(Token(simples[caracter], caracter, self.linea, col_inicio, col_inicio + 1))
            self.posicion += 1; self.columna += 1; return True
            
        return False
