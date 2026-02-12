# ASSUMPTIONS

1. Se utiliza español en documentación, reporte y dashboard.
2. Runtime objetivo: Python 3.11.
3. RFM se construye en modo proxy desde `clientes` (no existe llave `cliente_id` en ventas).
4. Pronóstico mensual: top 12 ingredientes por impacto, horizonte de 6 meses.
5. Parquet es preferente; CSV actúa como fallback operativo.
6. `POLARS=1` es opcional para acelerar lecturas/agregaciones.
7. El costo de ingredientes faltante se estima por receta o razón por categoría.
8. El costo operativo se prorratea por ticket mensual en cada sucursal.
