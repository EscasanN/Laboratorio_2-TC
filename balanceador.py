def esta_balanceada(expresion):
    pila = []
    pares = {')': '(', ']': '[', '}': '{'}
    pasos = []
    balanceada = True

    for i, caracter in enumerate(expresion):
        if caracter in '([{':
            pila.append(caracter)
            pasos.append(f"Paso {i + 1}: '{caracter}' -> push     => pila: {pila}")
        elif caracter in ')]}':
            if pila and pila[-1] == pares[caracter]:
                pila.pop()
                pasos.append(f"Paso {i + 1}: '{caracter}' -> pop      => pila: {pila}")
            else:
                pasos.append(f"Paso {i + 1}: '{caracter}' -> error    => pila: {pila}")
                balanceada = False
                break
        else:
            pasos.append(f"Paso {i + 1}: '{caracter}' -> ignorar  => pila: {pila}")

    if balanceada and not pila:
        pasos.append("Fin: pila vacía, expresión balanceada")
        return True, pasos
    elif balanceada and pila:
        pasos.append(f"Fin: pila no vacía => {pila}")
        return False, pasos
    else:
        return False, pasos


def procesar_archivo(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            expresion = linea.strip()
            print(f"\nLínea {numero_linea}: {expresion}")
            balanceada, pasos = esta_balanceada(expresion)
            for paso in pasos:
                print(paso)
            print("Resultado:", "Expresión balanceada" if balanceada else "No balanceada")


if __name__ == "__main__":
    archivo = "expresiones.txt"
    print(f"\nProcesando archivo: {archivo}")
    procesar_archivo(archivo)
