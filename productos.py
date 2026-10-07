"""Inventario persistente para TUNING VASQUEZ & ASOCIADOS."""
import json
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / 'productos.json'
RESPALDOS = BASE / 'respaldos'
MAX_RESPALDOS = 5

PRODUCTOS_INICIALES = [
    (105, 'Protector de motor', 120.00, 5),
    (101, 'Espejo deportivo', 45.00, 10),
    (104, 'Puños deportivos', 25.00, 20),
    (102, 'Manija de freno', 35.00, 8),
    (103, 'Direccionales LED', 60.00, 15),
]

def _normalizar(datos):
    return [(int(p[0]), str(p[1]), float(p[2]), int(p[3])) for p in datos]

def _respaldo():
    if not ARCHIVO.exists():
        return
    RESPALDOS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    shutil.copy2(ARCHIVO, RESPALDOS / f'productos_{stamp}.json.bak')
    archivos = sorted(RESPALDOS.glob('productos_*.json.bak'),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    for viejo in archivos[MAX_RESPALDOS:]:
        viejo.unlink(missing_ok=True)

def guardar_productos(lista):
    _respaldo()
    temporal = ARCHIVO.with_suffix('.tmp')
    with temporal.open('w', encoding='utf-8') as f:
        json.dump([list(p) for p in lista], f, ensure_ascii=False, indent=2)
    temporal.replace(ARCHIVO)

def cargar_productos():
    if not ARCHIVO.exists():
        datos = list(PRODUCTOS_INICIALES)
        guardar_productos(datos)
        return datos
    try:
        with ARCHIVO.open(encoding='utf-8') as f:
            return _normalizar(json.load(f))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        datos = list(PRODUCTOS_INICIALES)
        guardar_productos(datos)
        return datos

productos = cargar_productos()

def existe_codigo(codigo):
    return any(p[0] == codigo for p in productos)

def obtener_producto(codigo):
    return next((p for p in productos if p[0] == codigo), None)

def registrar_producto(codigo, nombre, precio, stock):
    nombre = str(nombre).strip()
    if codigo <= 0:
        return False, 'El código debe ser mayor que cero.'
    if existe_codigo(codigo):
        return False, 'El código ya existe.'
    if not nombre:
        return False, 'El nombre no puede estar vacío.'
    if precio <= 0:
        return False, 'El precio debe ser mayor que cero.'
    if stock < 0:
        return False, 'El stock no puede ser negativo.'
    productos.append((codigo, nombre, round(precio, 2), stock))
    guardar_productos(productos)
    return True, 'Producto registrado correctamente.'

def editar_producto(codigo, nombre, precio, stock):
    """Actualiza los datos editables de un producto existente."""
    nombre = str(nombre).strip()
    if not nombre:
        return False, 'El nombre no puede estar vacío.'
    if precio <= 0:
        return False, 'El precio debe ser mayor que cero.'
    if stock < 0:
        return False, 'El stock no puede ser negativo.'

    for i, p in enumerate(productos):
        if p[0] == codigo:
            productos[i] = (codigo, nombre, round(precio, 2), int(stock))
            guardar_productos(productos)
            return True, 'Producto actualizado correctamente.'
    return False, 'El producto no existe.'

def actualizar_stock(codigo, cantidad):
    if cantidad <= 0:
        return False
    for i, p in enumerate(productos):
        if p[0] == codigo:
            if p[3] < cantidad:
                return False
            productos[i] = (p[0], p[1], p[2], p[3] - cantidad)
            guardar_productos(productos)
            return True
    return False

def reponer_stock(codigo, cantidad):
    if cantidad <= 0:
        return False
    for i, p in enumerate(productos):
        if p[0] == codigo:
            productos[i] = (p[0], p[1], p[2], p[3] + cantidad)
            guardar_productos(productos)
            return True
    return False
