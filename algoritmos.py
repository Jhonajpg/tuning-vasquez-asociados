"""Algoritmos del sistema: Quicksort, búsqueda binaria, backtracking y voraz."""

def particionar(productos, inicio, fin):
    pivote = productos[fin][0]
    i = inicio - 1
    for j in range(inicio, fin):
        if productos[j][0] <= pivote:
            i += 1
            productos[i], productos[j] = productos[j], productos[i]
    productos[i + 1], productos[fin] = productos[fin], productos[i + 1]
    return i + 1


def quicksort(productos, inicio=0, fin=None):
    if fin is None:
        fin = len(productos) - 1
    if inicio < fin:
        pivote = particionar(productos, inicio, fin)
        quicksort(productos, inicio, pivote - 1)
        quicksort(productos, pivote + 1, fin)
    return productos


def busqueda_binaria(productos, codigo):
    inicio, fin = 0, len(productos) - 1
    while inicio <= fin:
        medio = (inicio + fin) // 2
        if productos[medio][0] == codigo:
            return productos[medio]
        if codigo < productos[medio][0]:
            fin = medio - 1
        else:
            inicio = medio + 1
    return None


def _backtracking(productos, indice, presupuesto, seleccion, mejor):
    if indice >= len(productos) or presupuesto <= 0:
        total = round(sum(x['subtotal'] for x in seleccion), 2)
        if total > mejor['total']:
            mejor['total'], mejor['seleccion'] = total, seleccion.copy()
        return
    codigo, nombre, precio, stock = productos[indice]
    if precio <= 0 or stock <= 0:
        _backtracking(productos, indice + 1, presupuesto, seleccion, mejor)
        return
    maximo = min(stock, int((presupuesto + 1e-9) // precio))
    for cantidad in range(maximo, -1, -1):
        subtotal = round(precio * cantidad, 2)
        if cantidad:
            seleccion.append({'codigo': codigo, 'nombre': nombre, 'precio': precio,
                              'cantidad': cantidad, 'subtotal': subtotal})
        _backtracking(productos, indice + 1, round(presupuesto - subtotal, 2), seleccion, mejor)
        if cantidad:
            seleccion.pop()
        if mejor['total'] == mejor['presupuesto']:
            return


def combinacion_backtracking(productos, presupuesto):
    if presupuesto <= 0:
        return []
    disponibles = [p for p in productos if p[2] > 0 and p[3] > 0]
    mejor = {'total': 0.0, 'presupuesto': round(presupuesto, 2), 'seleccion': []}
    _backtracking(disponibles, 0, round(presupuesto, 2), [], mejor)
    return mejor['seleccion']


def algoritmo_voraz(productos, presupuesto):
    if presupuesto <= 0:
        return []
    disponibles = sorted((p for p in productos if p[2] > 0 and p[3] > 0), key=lambda p: p[2], reverse=True)
    seleccion, restante = [], round(presupuesto, 2)
    for codigo, nombre, precio, stock in disponibles:
        cantidad = min(stock, int((restante + 1e-9) // precio))
        if cantidad:
            subtotal = round(precio * cantidad, 2)
            seleccion.append({'codigo': codigo, 'nombre': nombre, 'precio': precio,
                              'cantidad': cantidad, 'subtotal': subtotal})
            restante = round(restante - subtotal, 2)
        if restante <= 0:
            break
    return seleccion


def total_seleccion(seleccion):
    return round(sum(item['subtotal'] for item in seleccion), 2)
