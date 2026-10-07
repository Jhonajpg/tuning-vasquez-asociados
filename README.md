# TUNING VASQUEZ & ASOCIADOS — Sistema Web

Sistema de gestión de inventario y ventas desarrollado con Python + FastAPI + HTML/CSS/JavaScript.

## Mejoras implementadas

- Cambio completo de nombre a **TUNING VASQUEZ & ASOCIADOS**.
- Registro de productos.
- **Edición de datos del producto:** nombre, precio y stock.
- Búsqueda por código o nombre.
- Ordenamiento con Quicksort.
- Búsqueda binaria por código.
- **Compras de productos para aumentar stock.**
- Historial de compras con fecha, cantidad, costo unitario y total.
- Nueva venta con carrito.
- Validación de stock y cálculo de vuelto.
- **Anulación de ventas**, restaurando automáticamente las unidades al inventario.
- Historial de ventas con estados ACTIVA/ANULADA.
- Reporte de ventas y productos más vendidos.
- Consulta de productos que se pueden comprar con un monto usando backtracking y algoritmo voraz.
- Persistencia en archivos JSON y respaldos automáticos.

## Ejecutar en Windows

### Opción 1: con PowerShell o CMD

```text
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py -m uvicorn app:app --reload
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8000
```

### Opción 2: ejecutar con un archivo BAT

Haz doble clic en `iniciar.bat`. El archivo crea/usa el entorno virtual, instala las dependencias y abre el servidor.

## Estructura

- `app.py`: API web y rutas.
- `algoritmos.py`: Quicksort, búsqueda binaria, backtracking y voraz.
- `productos.py`: inventario, edición y persistencia.
- `ventas.py`: ventas, anulaciones, compras y reportes.
- `templates/index.html`: interfaz.
- `static/styles.css`: diseño responsive.
- `static/app.js`: interacción del navegador.
- `productos.json`: inventario.
- `ventas.json`: historial de ventas.
- `compras.json`: historial de compras.
