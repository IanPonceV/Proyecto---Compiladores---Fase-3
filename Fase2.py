import ply.yacc as yacc
from Fase1 import TipoToken

# Fase 2 - Analizador Sintáctico LALR(1) con Integración Semántica (MiniLang)
#operador
# 3. ADAPTADOR LÉXICO (Puente entre Fase 1 y PLY)
class AdaptadorLexicoPLY:
    def __init__(self, lista_tokens, parser_ref=None):
        self.lista_tokens = [t for t in lista_tokens if t.tipo != TipoToken.FIN_ARCHIVO]
        self.pos = 0
        self.parser_ref = parser_ref 

    def token(self):
        if self.pos < len(self.lista_tokens):
            tok_original = self.lista_tokens[self.pos]
            self.pos += 1
            import ply.lex as lex
            tok_ply = lex.LexToken()
            tok_ply.type = tok_original.tipo
            tok_ply.value = tok_original.valor
            tok_ply.lineno = tok_original.linea
            tok_ply.lexpos = tok_original.col_inicio
            #guardar último token
            if self.parser_ref:
                self.parser_ref.ultimo_token = tok_ply
            return tok_ply
        return None

# 4. ANALIZADOR SINTÁCTICO (PARSER LALR)
class AnalizadorSintactico:
    # Lista de tokens (Sin LLAVE_IZQ, LLAVE_DER ni PUNTO_Y_COMA para evitar warnings)
    tokens = [
        'ID', 'NUMERO_ENTERO', 'NUMERO_FLOTANTE', 'CADENA_LITERAL', 'BOOLEANO_LITERAL',
        'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 'MODULO',
        'MAYOR_QUE', 'MENOR_QUE', 'MAYOR_IGUAL', 'MENOR_IGUAL', 'IGUAL_QUE', 'DIFERENTE_QUE',
        'ASIGNACION', 'PARENTESIS_IZQ', 'PARENTESIS_DER',
        'DOS_PUNTOS', 'COMA', 'NUEVA_LINEA', 'INDENTAR', 'DESINDENTAR',
        'IF', 'ELSE', 'WHILE', 'INT', 'FLOAT', 'STRING', 'BOOL', 'VOID', 'RETURN', 'DEF', 'READ', 'WRITE',
        'AND', 'OR', 'NOT'
    ]

    # Precedencia y asociatividad para evitar ambigüedades matemáticas
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('left', 'IGUAL_QUE', 'DIFERENTE_QUE', 'MAYOR_QUE', 'MENOR_QUE', 'MAYOR_IGUAL', 'MENOR_IGUAL'),
        ('left', 'SUMA', 'RESTA'),
        ('left', 'MULTIPLICACION', 'DIVISION', 'MODULO'),
    )

    def __init__(self, semantico):
        self.errores_sintacticos = []
        self.semantico = semantico
        self.ultimo_token = None  
        self.parser = yacc.yacc(module=self)

    # REGLAS GRAMATICALES BNF -> PLY
    def p_program(self, p):
        '''program : statement_list'''
        pass

    def p_statement_list(self, p):
        '''statement_list : statement statement_list
                          | statement'''
        pass

    def p_statement(self, p):
        '''statement : var_decl
                     | assignment
                     | if_stmt
                     | while_stmt
                     | func_decl
                     | func_call_stmt
                     | io_stmt
                     | return_stmt
                     | empty_line'''
        pass

    # Modo Pánico: Recuperación de Errores Sintácticos
    def p_statement_error(self, p):
        '''statement : error NUEVA_LINEA'''
        pass 

    def p_empty_line(self, p):
        '''empty_line : NUEVA_LINEA'''
        pass

    # --- INTEGRACIÓN SEMÁNTICA: DECLARACIONES Y TIPOS ---
    def p_type(self, p):
        '''type : INT 
                | FLOAT 
                | STRING 
                | BOOL 
                | VOID'''
        p[0] = p[1] # Guardamos el tipo de dato para que suba en el árbol

    def p_var_decl(self, p):
        '''var_decl : type ID ASIGNACION expression NUEVA_LINEA
                    | type ID NUEVA_LINEA'''
        tipo_var = p[1]
        nombre_var = p[2]
        linea = p.lineno(2)

        # 1. Declaramos la variable en la memoria
        if self.semantico.declarar_variable(nombre_var, tipo_var, linea):
            # 2. Si tiene asignación (=), guardamos el valor
            if len(p) == 6: 
                expr = p[4]
                if expr and expr.get('tipo') != 'error':
                    self.semantico.asignar_valor(nombre_var, expr['valor'], expr['tipo'], linea)

    def p_var_decl_error(self, p):
        '''var_decl : type ID ASIGNACION error NUEVA_LINEA'''
        self.errores_sintacticos.append(
            f"Línea {p.lineno(3)} | Error Sintáctico: Expresión inválida en la asignación."
        )

    def p_assignment(self, p):
        '''assignment : ID ASIGNACION expression NUEVA_LINEA'''
        nombre_var = p[1]
        expr = p[3]
        linea = p.lineno(1)

        # Solo asignamos si la expresión es válida matemáticamente
        if expr and expr.get('tipo') != 'error':
            self.semantico.asignar_valor(nombre_var, expr['valor'], expr['tipo'], linea)

    # --- ESTRUCTURAS DE CONTROL ---
    def p_if_stmt(self, p):
        '''if_stmt : IF expression DOS_PUNTOS NUEVA_LINEA INDENTAR statement_list DESINDENTAR else_clause'''
        pass
    
    def p_if_error(self, p):
        '''if_stmt : IF error DOS_PUNTOS NUEVA_LINEA INDENTAR statement_list DESINDENTAR'''
        self.errores_sintacticos.append(
            f"Línea {p.lineno(1)} | Error Sintáctico: Condición inválida en 'if'."
        )

    def p_else_clause(self, p):
        '''else_clause : ELSE DOS_PUNTOS NUEVA_LINEA INDENTAR statement_list DESINDENTAR
                       | empty'''
        pass

    def p_while_stmt(self, p):
        '''while_stmt : WHILE expression DOS_PUNTOS NUEVA_LINEA INDENTAR statement_list DESINDENTAR'''
        pass

    def p_while_error(self, p):
        '''while_stmt : WHILE error DOS_PUNTOS NUEVA_LINEA INDENTAR statement_list DESINDENTAR'''
        self.errores_sintacticos.append(
            f"Línea {p.lineno(1)} | Error Sintáctico: Condición inválida en 'while'."
        )

    def p_func_decl(self, p):
        '''func_decl : DEF ID PARENTESIS_IZQ param_list PARENTESIS_DER DOS_PUNTOS NUEVA_LINEA INDENTAR statement_list DESINDENTAR'''
        pass

    def p_param_list(self, p):
        '''param_list : type ID more_params
                      | empty'''
        pass

    def p_more_params(self, p):
        '''more_params : COMA type ID more_params
                       | empty'''
        pass

    def p_func_call_stmt(self, p):
        '''func_call_stmt : ID PARENTESIS_IZQ arg_list PARENTESIS_DER NUEVA_LINEA'''
        pass
    
    def p_func_call_error(self, p):
        '''func_call_stmt : ID PARENTESIS_IZQ error PARENTESIS_DER NUEVA_LINEA'''
        self.errores_sintacticos.append(
            f"Línea {p.lineno(1)} | Error Sintáctico: Argumentos inválidos en llamada a función."
        )
    
    def p_io_stmt(self, p):
        '''io_stmt : READ PARENTESIS_IZQ ID PARENTESIS_DER NUEVA_LINEA
                   | WRITE PARENTESIS_IZQ expression PARENTESIS_DER NUEVA_LINEA'''
        pass

    def p_return_stmt(self, p):
        '''return_stmt : RETURN expression NUEVA_LINEA'''
        pass

    # --- INTEGRACIÓN SEMÁNTICA: EXPRESIONES Y MATEMÁTICAS ---
    def p_expression_binop(self, p):
        '''expression : expression SUMA expression
                      | expression RESTA expression
                      | expression MULTIPLICACION expression
                      | expression DIVISION expression
                      | expression MODULO expression
                      | expression MAYOR_QUE expression
                      | expression MENOR_QUE expression
                      | expression MAYOR_IGUAL expression
                      | expression MENOR_IGUAL expression
                      | expression IGUAL_QUE expression
                      | expression DIFERENTE_QUE expression
                      | expression AND expression
                      | expression OR expression'''
        izq = p[1]
        tipo_token = p.slice[2].type
        mapa_operadores = {
            'SUMA': '+',
            'RESTA': '-',
            'MULTIPLICACION': '*',
            'DIVISION': '/',
            'MODULO': '%',
            'MAYOR_QUE': '>',
            'MENOR_QUE': '<',
            'MAYOR_IGUAL': '>=',
            'MENOR_IGUAL': '<=',
            'IGUAL_QUE': '==',
            'DIFERENTE_QUE': '!=',
            'AND': 'and',
            'OR': 'or'
        }
        operador = mapa_operadores.get(tipo_token)
        der = p[3]
        linea = p.lineno(2)

        # Si ya había un error en las ramas inferiores, lo propagamos
        if not izq or not der or izq.get('tipo') == 'error' or der.get('tipo') == 'error':
            p[0] = {'tipo': 'error', 'valor': None}
            return

        # Validar semánticamente la operación
        res_tipo = self.semantico.resolver_operacion_matematica(izq['tipo'], der['tipo'], operador, linea)
        
        # Calcular el valor real
        res_valor = None
        if res_tipo != 'error' and izq['valor'] is not None and der['valor'] is not None:
            try:
                if operador == '+': res_valor = izq['valor'] + der['valor']
                elif operador == '-': res_valor = izq['valor'] - der['valor']
                elif operador == '*': res_valor = izq['valor'] * der['valor']
                elif operador == '/': 
                    res_valor = izq['valor'] / der['valor'] if der['valor'] != 0 else 0
            except:
                pass # Manejo silencioso de errores matemáticos extremos

        p[0] = {'tipo': res_tipo, 'valor': res_valor}

    def p_expression_not(self, p):
        '''expression : NOT expression'''
        p[0] = {'tipo': 'bool', 'valor': None} # Simplificado para validación

    def p_expression_group(self, p):
        '''expression : PARENTESIS_IZQ expression PARENTESIS_DER'''
        p[0] = p[2]

    def p_expression_factor(self, p):
        '''expression : NUMERO_ENTERO
                      | NUMERO_FLOTANTE
                      | CADENA_LITERAL
                      | BOOLEANO_LITERAL
                      | ID'''
        tipo_token = p.slice[1].type
        valor_token = p[1]
        linea = p.lineno(1)

        if tipo_token == 'NUMERO_ENTERO':
            p[0] = {'tipo': 'int', 'valor': int(valor_token)}
        elif tipo_token == 'NUMERO_FLOTANTE':
            p[0] = {'tipo': 'float', 'valor': float(valor_token)}
        elif tipo_token == 'CADENA_LITERAL':
            p[0] = {'tipo': 'string', 'valor': valor_token.replace('"', '')}
        elif tipo_token == 'BOOLEANO_LITERAL':
            p[0] = {'tipo': 'bool', 'valor': valor_token == 'true'}
        elif tipo_token == 'ID':
            # Buscar en la tabla de símbolos
            simbolo = self.semantico.obtener_simbolo(valor_token, linea)
            if simbolo:
                p[0] = {'tipo': simbolo.tipo_dato, 'valor': simbolo.valor}
            else:
                p[0] = {'tipo': 'error', 'valor': None}

    def p_expression_func_call(self, p):
        '''expression : ID PARENTESIS_IZQ arg_list PARENTESIS_DER'''
        p[0] = {'tipo': 'void', 'valor': None} # Por defecto en esta fase

    def p_arg_list(self, p):
        '''arg_list : expression more_args
                    | empty'''
        pass

    def p_more_args(self, p):
        '''more_args : COMA expression more_args
                     | empty'''
        pass

    def p_empty(self, p):
        'empty :'
        pass

    # --- MANEJO DE ERRORES ---
    def p_error(self, p):
        if not p:
            self.errores_sintacticos.append(
                "Error Sintáctico: Fin de archivo inesperado. Posible instrucción incompleta."
            )
            return
        tipo = p.type
        valor = p.value
        linea = p.lineno
        if tipo == 'NUEVA_LINEA':
            if self.ultimo_token:
                if self.ultimo_token.type == 'ASIGNACION':
                    msg = f"Línea {linea} | Error Sintáctico: Falta una expresión después del '='."
                elif self.ultimo_token.type in ['SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 'MODULO']:
                    msg = f"Línea {linea} | Error Sintáctico: Operador sin operando derecho."
                elif self.ultimo_token.type in ['MAYOR_QUE', 'MENOR_QUE', 'IGUAL_QUE']:
                    msg = f"Línea {linea} | Error Sintáctico: Comparación incompleta."
                else:
                    msg = f"Línea {linea} | Error Sintáctico: La instrucción está incompleta."
            else:
                msg = f"Línea {linea} | Error Sintáctico: Salto de línea inesperado."

        elif tipo == 'INDENTAR':
            msg = f"Línea {linea} | Error Sintáctico: Indentación inesperada."
        elif tipo == 'DESINDENTAR':
            msg = f"Línea {linea} | Error Sintáctico: Cierre de bloque inesperado o mala indentación."
        elif tipo == 'ID':
            msg = f"Línea {linea} | Error Sintáctico: Identificador inesperado '{valor}'. Puede faltar operador o palabra clave."
        elif tipo in ['SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION']:
            msg = f"Línea {linea} | Error Sintáctico: Operador '{valor}' mal ubicado."
        elif tipo == 'DOS_PUNTOS':
            msg = f"Línea {linea} | Error Sintáctico: Uso incorrecto de ':'."
        else:
            msg = f"Línea {linea} | Error Sintáctico: Token inesperado '{valor}' (Tipo: {tipo})."

        self.errores_sintacticos.append(msg)
        self.parser.errok()

    def analizar_sintaxis(self, adaptador_lexico):
        self.errores_sintacticos = []
        self.parser.parse(lexer=adaptador_lexico)
        return self.errores_sintacticos
