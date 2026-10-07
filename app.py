from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from algoritmos import quicksort, busqueda_binaria, combinacion_backtracking, algoritmo_voraz, total_seleccion
from productos import productos, registrar_producto, editar_producto
from ventas import ventas, compras, realizar_venta, anular_venta, registrar_compra, reporte_ventas

BASE = Path(__file__).resolve().parent
app = FastAPI(title='TUNING VASQUEZ & ASOCIADOS', version='3.0')
app.mount('/static', StaticFiles(directory=str(BASE / 'static')), name='static')

class ProductoIn(BaseModel):
    codigo: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)

class ProductoEditarIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)

class ItemIn(BaseModel):
    codigo: int
    cantidad: int = Field(gt=0)

class VentaIn(BaseModel):
    items: list[ItemIn]
    pago: float = Field(ge=0)

class CompraIn(BaseModel):
    codigo: int = Field(gt=0)
    cantidad: int = Field(gt=0)
    costo_unitario: float = Field(ge=0)

class PresupuestoIn(BaseModel):
    monto: float = Field(gt=0)

def productos_json():
    return [{'codigo': p[0], 'nombre': p[1], 'precio': p[2], 'stock': p[3]} for p in productos]

@app.get('/', response_class=HTMLResponse)
def inicio():
    return (BASE / 'templates' / 'index.html').read_text(encoding='utf-8')

@app.get('/api/dashboard')
def dashboard():
    r = reporte_ventas()
    return {
        'productos': len(productos),
        'stock_total': sum(p[3] for p in productos),
        'compras': len(compras),
        **r
    }

@app.get('/api/productos')
def listar_productos(q: str = '', ordenar: str = 'codigo'):
    lista = productos[:]
    if q.strip():
        termino = q.strip().lower()
        if termino.isdigit():
            ordenada = quicksort(lista[:])
            p = busqueda_binaria(ordenada, int(termino))
            lista = [p] if p else []
        else:
            lista = [p for p in lista if termino in p[1].lower()]
    if ordenar == 'precio':
        lista.sort(key=lambda p: p[2])
    elif ordenar == 'stock':
        lista.sort(key=lambda p: p[3])
    else:
        quicksort(lista)
    return productos_json() if not q.strip() and ordenar == 'codigo' else [
        {'codigo': p[0], 'nombre': p[1], 'precio': p[2], 'stock': p[3]} for p in lista
    ]

@app.post('/api/productos')
def crear_producto(data: ProductoIn):
    ok, msg = registrar_producto(data.codigo, data.nombre, data.precio, data.stock)
    if not ok:
        raise HTTPException(400, msg)
    return {'mensaje': msg, 'productos': productos_json()}

@app.put('/api/productos/{codigo}')
def actualizar_producto(codigo: int, data: ProductoEditarIn):
    ok, msg = editar_producto(codigo, data.nombre, data.precio, data.stock)
    if not ok:
        raise HTTPException(400, msg)
    return {'mensaje': msg, 'productos': productos_json()}

@app.post('/api/compras')
def crear_compra(data: CompraIn):
    ok, msg, compra = registrar_compra(data.codigo, data.cantidad, data.costo_unitario)
    if not ok:
        raise HTTPException(400, msg)
    return {'mensaje': msg, 'compra': compra, 'productos': productos_json()}

@app.get('/api/compras')
def historial_compras():
    return compras

@app.post('/api/ventas')
def crear_venta(data: VentaIn):
    carrito = []
    for x in data.items:
        p = next((p for p in productos if p[0] == x.codigo), None)
        if not p:
            raise HTTPException(400, f'Producto {x.codigo} no encontrado.')
        carrito.append({
            'codigo': p[0], 'nombre': p[1], 'precio': p[2],
            'cantidad': x.cantidad, 'subtotal': round(p[2] * x.cantidad, 2)
        })
    ok, msg, venta = realizar_venta(carrito, data.pago)
    if not ok:
        raise HTTPException(400, msg)
    return {'mensaje': msg, 'venta': venta}

@app.get('/api/ventas')
def historial():
    return ventas

@app.post('/api/ventas/{numero}/anular')
def cancelar(numero: int):
    ok, msg = anular_venta(numero)
    if not ok:
        raise HTTPException(400, msg)
    return {'mensaje': msg}

@app.get('/api/reporte')
def reporte():
    return reporte_ventas()

@app.post('/api/presupuesto')
def presupuesto(data: PresupuestoIn):
    mejor = combinacion_backtracking(productos, data.monto)
    voraz = algoritmo_voraz(productos, data.monto)
    total_mejor = total_seleccion(mejor)
    total_voraz = total_seleccion(voraz)
    return {
        'presupuesto': data.monto,
        'backtracking': {
            'items': mejor, 'total': total_mejor,
            'restante': round(data.monto - total_mejor, 2)
        },
        'voraz': {
            'items': voraz, 'total': total_voraz,
            'restante': round(data.monto - total_voraz, 2)
        }
    }
