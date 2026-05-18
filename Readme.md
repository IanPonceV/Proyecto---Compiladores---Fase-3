PROYECTO FASE 3: TABLA DE SIMBOLOS Y COMPROBACION DE TIPOS MINILANG

Este proyecto contiene la implementacion practica de la Fase 3 para el compilador del lenguaje MiniLang. Utilizando a las recomendaciones recibidas en la fase anterior, decidimos cambiar nuestra arquitectura a una solucion totalmente modular para integrar la semantica de manera limpia y que fuera mas facil de hacer mantenimiento.

FUNCIONAMIENTO Y DECISIONES DE DISENO:
Decidimos segmentar el codigo en cuatro modulos principales basados en sus responsabilidades. El archivo Fase1.py contiene el analizador lexico que procesa el texto y controla los bloques de indentacion. El archivo Fase2.py maneja el analizador sintactico usando PLY. El archivo Fase3.py es el nuevo modulo que almacena la memoria de las variables y ejecuta las reglas de validacion. Finalmente, el archivo Interfaz.py es como su nombre lo menciona la interfaz graficá que captura el codigo fuente y maneja el flujo de compilacion entre las tres fases.

LO QUE MAS SE DIFICULTO:
Lo que mas nos dificulto durante el desarrollo de esta fase fue lograr que la gramatica de PLY en la Fase 2 se comunicara correctamente con la memoria semantica de la Fase 3. Interceptar los valores y tipos en medio de las reglas  para subirlos por el arbol sintactico requirió mucho analisis, prueba y error. Ademas, integrar la tabla de simbolos en la interfaz grafica para que se vaciara y se actualizara dinamicamente en tiempo real con cada ejecucion represento un gran reto de logica de programación.

ESTRUCTURA DE LA TABLA DE SIMBOLOS Y COMO LE DAMOS MANTENIMIENTO:
Nuestra tabla de simbolos representa el mapa de memoria del compilador. Diseñamos una clase llamada Simbolo que funciona como un contenedor de datos donde cada registro guarda el nombre del identificador, el tipo de dato y el valor calculado en tiempo de ejecucion y la linea exacta donde fue declarado.

Para darle mantenimiento a esta tabla, utilizamos un diccionario de Python que nos permite busquedas rapidas. El mantenimiento es completamente dinamico porque cada vez que el usuario presiona el boton de ejecutar en la interfaz, el programa destruye la memoria anterior y crea una nueva instancia en blanco. Conforme PLY detecta declaraciones y asignaciones, invoca nuestros metodos para registrar o actualizar los simbolos. Al finalizar, exportamos esta tabla a un archivo de texto con extension .out, cumpliendo asi con los requisitos de la rubrica.

ESTRATEGIAS DE COMPROBACION DE TIPOS USADAS:
Validamos los tipos de forma ascendente y aplicamos reglas de coercion muy estrictas. La asignacion basica es valida solo si el tipo de la variable coincide exactamente con el tipo de la expresion recibida. Como unica coercion de ampliacion permitida, el compilador deja guardar de forma implicita un valor int dentro de una variable float, convirtiendo el numero automaticamente a decimal. Cualquier otro intento de mezclar tipos incompatibles es bloqueado.

Para la resolucion de expresiones matematicas, establecimos que operar un int con un float siempre produce un float. El operador de suma fue sobrecargado para permitir la concatenacion si detecta un tipo string. Finalmente, hicimos que todas las operaciones relacionales devuelvan siempre un tipo bool.

ESTRATEGIA DE ERRORES SEMANTICOS:
Para asegurar que el compilador no detenga su ejecucion abruptamente al encontrar fallas logicas, implementamos una estrategia basada en el modo panico con recuperacion. Cuando el analizador detecta una infraccion, como utilizar una variable no declarada o mezclar tipos erroneos, llama un metodo que registra la falla y la linea en una lista interna, permitiendo que el analisis continue hasta el final del documento.

Para evitar que un error inicial cause fallos falsos en formulas largas, asignamos un tipo especial llamado error a cualquier subexpresion invalida, entonces si las operaciones siguientes detectan este tipo de error, silencian las alertas adicionales, logrando aislar el problema y mostrando al usuario reportes directos en la consola de la interfaz.

CAMBIOS REALIZADOS:
Fase 1: Eliminamos tokens innecesarios (llaves y punto y coma) para adaptar el escáner a la estructura por indentación y evitar advertencias de PLY. Agregamos operadores lógicos (and, or, not) y mejoramos la claridad de los mensajes de error.

Fase 2: Conectamos el parser con la memoria semántica en la Fase 3. Reescribimos todas las reglas gramaticales para que ahora detecten tipos y valores, permitiendo enviarlos a la tabla de símbolos para declarar variables y evaluar operaciones. Además, perfeccionamos el modo pánico para que el proyecto se recupere automáticamente de los errores sin detener la ejecución.
