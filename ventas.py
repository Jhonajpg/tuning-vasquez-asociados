"""Ventas, anulaciones, compras de inventario, historial y reportes."""
import json
from datetime import datetime
from pathlib import Path
from productos import productos, actualizar_stock, reponer_stock, obtener_producto
from algoritmos import quicksort, busqueda_binaria

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / 'ventas.json'
COMPRAS_ARCHIVO = BASE / 'compras.json'
RESPALDOS = BASE / 'respaldos'
MAX_RESPALDOS = 5

ventas = []
compras = []

def _respaldo(archivo, prefijo):
    if not archivo.exists():
        return
    import shutil
    RESPALDOS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    shutil.copy2(archivo, RESPALDOS / f'{prefijo}_{stamp}.json.bak')
    archivos = sorted(RESPALDOS.glob(f'{prefijo}_*.json.bak'),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    for viejo in archivos[MAX_RESPALDOS:]:
        viejo.unlink(missing_ok=True)

def cargar_lista(archivo):
    if not archivo.exists():
        return []
    try:
        with archivo.open(encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def guardar_ventas():
    _respaldo(ARCHIVO, 'ventas')
    temporal = ARCHIVO.with_suffix('.tmp')
    with temporal.open('w', encoding='utf-8') as f:
        json.dump(ventas, f, ensure_ascii=False, indent=2)
    temporal.replace(ARCHIVO)

def guardar_compras():
    _respaldo(COMPRAS_ARCHIVO, 'compras')
    temporal = COMPRAS_ARCHIVO.with_suffix('.tmp')
    with temporal.open('w', encoding='utf-8') as f:
        json.dump(compras, f, ensure_ascii=False, indent=2)
    temporal.replace(COMPRAS_ARCHIVO)

ventas.extend(cargar_lista(ARCHIVO))
compras.extend(cargar_lista(COMPRAS_ARCHIVO))

def siguiente_id():
    return max((int(v['id']) for v in ventas), default=0) + 1

def siguiente_id_compra():
    return max((int(c['id']) for c in compras), default=0) + 1

def productos_ordenados():
    return quicksort(productos[:])

def realizar_venta(carrito, pago):
    if not carrito:
        return False, 'El carrito está vacío.', None
    total = round(sum(float(x['subtotal']) for x in carrito), 2)
    if pago < total:
        return False, 'El monto entregado es insuficiente.', None

    # Validar todo antes de descontar para evitar operaciones parciales.
    for item in carrito:
        p = busqueda_binaria(productos_ordenados(), int(item['codigo']))
        if p is None or int(item['cantidad']) > p[3]:
            return False, f"Stock insuficiente para {item['nombre']}.", None

    for item in carrito:
        if not actualizar_stock(int(item['codigo']), int(item['cantidad'])):
            return False, f"No se pudo actualizar el stock de {item['nombre']}.", None

    venta = {
        'id': siguiente_id(),
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'items': carrito,
        'total': total,
        'pago': round(pago, 2),
        'vuelto': round(pago - total, 2),
        'estado': 'ACTIVA'
    }
    ventas.append(venta)
    guardar_ventas()
    return True, 'Venta registrada correctamente.', venta

def anular_venta(numero):
    venta = next((v for v in ventas if int(v['id']) == int(numero)), None)
    if venta is None:
        return False, 'No existe la venta indicada.'
    if venta['estado'] == 'ANULADA':
        return False, 'La venta ya está anulada.'

    # Reponer todas las unidades vendidas.
    for item in venta['items']:
        if not reponer_stock(int(item['codigo']), int(item['cantidad'])):
            return False, f"No se pudo reponer {item['nombre']}."

    venta['estado'] = 'ANULADA'
    venta['anulada_en'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    guardar_ventas()
    return True, 'Venta anulada y stock restaurado correctamente.'

def registrar_compra(codigo, cantidad, costo_unitario=0):
    """Registra una compra de inventario y aumenta el stock."""
    if cantidad <= 0:
        return False, 'La cantidad debe ser mayor que cero.', None

    producto = obtener_producto(int(codigo))
    if producto is None:
        return False, 'El producto no existe.', None

    if costo_unitario < 0:
        return False, 'El costo unitario no puede ser negativo.', None

    if not reponer_stock(int(codigo), int(cantidad)):
        return False, 'No se pudo aumentar el stock.', None

    compra = {
        'id': siguiente_id_compra(),
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'codigo': producto[0],
        'nombre': producto[1],
        'cantidad': int(cantidad),
        'costo_unitario': round(float(costo_unitario), 2),
        'total': round(float(costo_unitario) * int(cantidad), 2),
        'estado': 'REGISTRADA'
    }
    compras.append(compra)
    guardar_compras()
    return True, 'Compra registrada y stock aumentado correctamente.', compra

def reporte_ventas():
    activas = [v for v in ventas if v['estado'] == 'ACTIVA']
    anuladas = [v for v in ventas if v['estado'] == 'ANULADA']
    totales = {}
    for v in activas:
        for item in v['items']:
            totales[item['nombre']] = totales.get(item['nombre'], 0) + int(item['cantidad'])
    return {
        'ventas_activas': len(activas),
        'ventas_anuladas': len(anuladas),
        'unidades_vendidas': sum(int(i['cantidad']) for v in activas for i in v['items']),
        'total_recaudado': round(sum(float(v['total']) for v in activas), 2),
        'productos_mas_vendidos': [
            {'nombre': n, 'cantidad': c}
            for n, c in sorted(totales.items(), key=lambda x: x[1], reverse=True)
        ]
    }
