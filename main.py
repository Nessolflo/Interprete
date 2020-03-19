import re
import os

regexCompile = "(COMPILE|compile|Compile) ([a-zA-Z0-9]+).x"
regexRun = "(RUN|run|Run) ([a-zA-Z0-9]+).x"
regexLoad = "(LOAD|load|Load) ([a-zA-Z0-9]+).py"
regexDefinir = "DEFINIR ([a-zA-Z][a-zA-Z0-9_]*) COMO (ENTERO|TEXTO|LOGICO|REAL);"
regexSet = '([a-z][a-zA-Z0-9_]*)<-([0-9.]+|".*"|Falso|Verdadero|([a-zA-Z0-9_.]*\s?(\+|\*|\-|\/)\s?[a-zA-Z0-9_.]+)|[a-zA-Z]*);'
regexExpresion ="[a-zA-Z0-9]+(\+|\*|\-|\/)[a-zA-Z0-9]+((\+|\*|\-|\/)[a-zA-Z0-9])*"
regexFloatType = '^[\-]{0,1}[0-9]{1,}(([\.\,]{0,1}[0-9]{1,})|([0-9]{0,}))$'
regexIntType = "(^\d+$)"
regexStringType = '".*"'
regexBooleanType = "True|False"
regexToRead = "LEER ([a-zA-Z][a-zA-Z0-9_]*);"
regexToWrite = "ESCRIBIR ('?.*'?);"
regexCondition = "SI ('?.*'?)"
regexMientras = "MIENTRAS ('?.*'?) HACER"
regexEndCondition = "FINSI"
regexEndMientras = "FINMIENTRAS"
regexElseCondition = "SINO"
nombreVariable = []
valoresVariable = []
tipoVariable = []
regexVariable = []
tabs = int(0)
archivo = None
archivoSalida = None


def interpretarArchivo(nombre):
    print("Interpretando ....")
    file = open(nombre, "r")
    os.system('python ' + file.name)


def getNombreArchivo(primerLinea, regex):
    subLinea = re.findall(regex, primerLinea)[0]
    return subLinea[1]


def inicializarArchivos(nombreArchivo):
    global archivo
    global archivoSalida
    archivo = open(nombreArchivo + ".x", "r")
    archivoSalida = open(nombreArchivo + ".py", "w")


def escribir(archivo, valor):
    txtTabs = ""
    if tabs > 0:
        for tab in range(tabs):
            txtTabs += "\t"
    archivo.writelines(txtTabs + valor + "\n")
    # print(valor)


def crearVariable(nombre, tipo):
    global nombreVariable
    global tipoVariable

    if nombreVariable.count(nombre) >= 1:
        return False
    nombreVariable.append(nombre)
    tipoVariable.append(tipo)
    if tipo == "ENTERO":
        regexVariable.append(regexIntType)
        asignarValorVariable(nombre, 0)
    elif tipo == "TEXTO":
        regexVariable.append(regexStringType)
        asignarValorVariable(nombre, '""')
    elif tipo == "LOGICO":
        regexVariable.append(regexBooleanType)
        asignarValorVariable(nombre, True)
    elif tipo == "REAL":
        regexVariable.append(regexFloatType)
        asignarValorVariable(nombre, 0.0)
    return True


def cumpleRegex(regex, dato):
    return bool(re.search(regex, str(dato)))


def agregarTab():
    global tabs
    tabs = tabs + 1


def quitarTab():
    global tabs
    tabs = tabs - 1


def asignarValorVariable(nombre, valor):
    global nombreVariable
    global tipoVariable
    # Verficamos que la variable exista
    if nombreVariable.count(nombre) == 1:
        # Buscamos la posicion dentro del arreglo
        index = nombreVariable.index(nombre)
        # Validamos si el indice esta dentro del tamaño del arreglo
        if len(valoresVariable) > index:
            # validamos si es una expresion es una asignacion normal
            if cumpleRegex(regexVariable[index], valor):
                valoresVariable[index] = valor
            # Validamos si es una expresion
            elif cumpleRegex(regexExpresion, valor):
                valoresVariable[index] = valor
            else:
                return False
        else:
            if cumpleRegex(regexVariable[index], valor):
                valoresVariable.append(valor)
            else:
                return False
        return True
    else:
        return False


def generarArchivo(archivo, archivoSalida):
    print("Traduciendo ....")
    for linea in archivo.readlines():
        # Validamos la linea definir
        if bool(re.search(regexDefinir, linea)):
            codigo = re.findall(regexDefinir, linea)
            codigo = codigo[0]  # Donde la posición 0 es el nombre y la posición 1 es el tipo
            if crearVariable(codigo[0], codigo[1]):
                escribir(archivoSalida, codigo[0] + " = " + str(valoresVariable[-1]))
            else:
                escribir(archivoSalida, "ERROR, el tipo de datos no se reconoce.")
        # Validamos la linea asignar valor d<-False
        elif bool(re.search(regexSet, linea)):
            codigo = re.findall(regexSet, linea)
            codigo = codigo[0]
            nombreVariable = codigo[0]
            valorVariable = codigo[1]
            if valorVariable == "Verdadero":
                valorVariable = "True"
            elif valorVariable == "Falso":
                valorVariable = "False"
            if asignarValorVariable(nombreVariable, valorVariable):
                escribir(archivoSalida, nombreVariable + " = " + valorVariable)
            else:
                escribir(archivoSalida,
                         "ERROR, el tipo de dato para la variable " + nombreVariable + " no es el correcto.")
        elif bool(re.search(regexToRead, linea)):
            variable = re.findall(regexToRead, linea)[0]
            escribir(archivoSalida, variable + ' = input()')
        elif bool(re.search(regexToWrite, linea)):
            valor = re.findall(regexToWrite, linea)[0]
            escribir(archivoSalida, "print('" + valor + "')")
        elif bool(re.search(regexMientras, linea)):
            condicion = re.findall(regexMientras, linea)[0]
            escribir(archivoSalida, "while " + condicion + ":")
            agregarTab()
        elif bool(re.search(regexCondition, linea)):
            condicion = re.findall(regexCondition, linea)[0]
            escribir(archivoSalida, "if " + condicion + ":")
            agregarTab()
        elif bool(re.search(regexEndCondition, linea)):
            quitarTab()
        elif bool(re.search(regexEndMientras, linea)):
            quitarTab()
        elif bool(re.search(regexElseCondition, linea)):
            quitarTab()
            escribir(archivoSalida, "else:")
            agregarTab()

    archivoSalida.close()
    archivo.close()
    print("Archivo generado: " + archivoSalida.name)
    interpretarArchivo(archivoSalida.name)


def main():
    global tabs
    global archivoSalida
    global archivo
    primerLinea = input("#>>")
    if bool(re.search(regexCompile, primerLinea)):
        inicializarArchivos(getNombreArchivo(primerLinea, regexCompile))
        generarArchivo(archivo, archivoSalida)

    elif bool(re.search(regexRun, primerLinea)):
        nombre = getNombreArchivo(primerLinea, regexRun)
        inicializarArchivos(nombre)
        generarArchivo(archivo, archivoSalida)

    elif bool(re.search(regexLoad, primerLinea)):
        interpretarArchivo(getNombreArchivo(primerLinea, regexLoad) + ".py")

    elif primerLinea == "exit":
        print("Saliendo ....")
    else:
        print("ERROR, COMANDO NO RECONOCIDO")


main()
