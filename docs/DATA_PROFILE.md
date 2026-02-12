# DATA_PROFILE

Resumen de perfil de datos inferido antes de modelar.

## sales
- Fuente seleccionada: `json`
- Archivo: `data\raw\json\ventascsv.json`
- Filas: 5000
- Columnas (18): Ticket_ID, Fecha, Hora, Dia_Semana, Mes, Sucursal_ID, Sucursal_Nombre, Ciudad, Platillo, Categoria, Precio_Unitario, Cantidad, Total_Venta, Costo_Ingredientes, Margen_Bruto, Metodo_Pago, Propina, Total_con_Propina
- Top faltantes (%):
  - `Ticket_ID`: 0.00%
  - `Fecha`: 0.00%
  - `Hora`: 0.00%
  - `Dia_Semana`: 0.00%
  - `Mes`: 0.00%

## customers
- Fuente seleccionada: `json`
- Archivo: `data\raw\json\clientes.json`
- Filas: 1500
- Columnas (17): Cliente_ID, Nombre, Fecha_Registro, Miembro_Lealtad, Categoria_Cliente, Sucursal_Preferida, Ciudad_Preferida, Visitas_Ultimo_Año, Gasto_Promedio, Gasto_Total_Estimado, Puntos_Lealtad, Ultima_Visita, Calificacion_Satisfaccion, NPS_Score, Comentario_Encuesta, Canal_Adquisicion, Acepta_Promociones
- Top faltantes (%):
  - `Cliente_ID`: 0.00%
  - `Nombre`: 0.00%
  - `Fecha_Registro`: 0.00%
  - `Miembro_Lealtad`: 0.00%
  - `Categoria_Cliente`: 0.00%

## branches
- Fuente seleccionada: `json`
- Archivo: `data\raw\json\sucursales.json`
- Filas: 10
- Columnas (24): Sucursal_ID, Nombre_Sucursal, Ciudad, Direccion, Codigo_Postal, Zona, Nivel_Socioeconomico, Capacidad_Personas, Numero_Empleados, Horario_Apertura, Horario_Cierre, Horarios_Pico, Renta_Mensual, Servicios_Mensual, Nomina_Mensual, Costos_Operativos_Total, Ingresos_Promedio_Mensual, Margen_Operativo, Rentabilidad_Porcentaje, Cercania_Puntos_Interes, Competencia_Cercana, Estacionamiento, Año_Apertura, Años_Operacion
- Top faltantes (%):
  - `Sucursal_ID`: 0.00%
  - `Nombre_Sucursal`: 0.00%
  - `Ciudad`: 0.00%
  - `Direccion`: 0.00%
  - `Codigo_Postal`: 0.00%

## inventory
- Fuente seleccionada: `json`
- Archivo: `data\raw\json\inventarios.json`
- Filas: 2000
- Columnas (23): Registro_ID, Fecha, Mes, Sucursal_ID, Sucursal_Nombre, Ciudad, Ingrediente, Categoria_Ingrediente, Unidad, Proveedor, Cantidad_Pedida, Precio_Unitario, Costo_Total_Compra, Cantidad_Desperdiciada, Costo_Desperdicio, Porcentaje_Desperdicio, Motivo_Desperdicio, Stock_Actual, Stock_Minimo, Estado_Stock, Necesita_Reorden, Frecuencia_Reabastecimiento, Vida_Util_Dias
- Top faltantes (%):
  - `Registro_ID`: 0.00%
  - `Fecha`: 0.00%
  - `Mes`: 0.00%
  - `Sucursal_ID`: 0.00%
  - `Sucursal_Nombre`: 0.00%

## digital
- Fuente seleccionada: `json`
- Archivo: `data\raw\json\canales_digitales.json`
- Filas: 1200
- Columnas (20): Registro_ID, Fecha, Mes, Dia_Semana, Sucursal_ID, Sucursal_Nombre, Ciudad, Plataforma, Tipo_Interaccion, Contenido, Sentimiento, Calificacion, Alcance, Engagement, Tasa_Engagement, Campaña_Asociada, Costo_Campaña, Respondido, Tiempo_Respuesta_Horas, Conversion
- Top faltantes (%):
  - `Registro_ID`: 0.00%
  - `Fecha`: 0.00%
  - `Mes`: 0.00%
  - `Dia_Semana`: 0.00%
  - `Sucursal_ID`: 0.00%
