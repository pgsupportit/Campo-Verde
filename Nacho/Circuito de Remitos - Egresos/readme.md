# Documentación del Repositorio de SQL para "CampoVerde".
Este desarrollo tiene la creación de una tabla temporal y tres triggers.

## Table:

### Nombre:
- Nombre de la tabla temporal: `Dbo.VariablesGlobales`

### Descripción:
- Esta tabla temporal lo que hace es almacenar un valor temporal.

### Funcionalidad:
- Esta tabla temporal lo que hace es almacenar el NCOMP_IN_S generado por el calculo del trigger: [TR_INSERT_EGRESO_ENCABEZADO] y luego lo actualiza en los demás triggers.

## Trigger:

### Nombre:
- Nombre del trigger: `TR_INSERT_EGRESO_ENCABEZADO`

### Descripción:
- Este trigger se dispara cuando se graba el encabezado del Remito de Compras en la STA14.

### Funcionalidad:
- Esta creado en la dbo.STA14 y se ejecuta cuando termina de grabar el Encabezado del Remito de Compras para grabar automáticamente el Encabezado de Comprobante de Salida hacia la otra Sucursal.

## Trigger:

### Nombre:
- Nombre del Trigger: `TR_INSERT_EGRESO_RENGLONES`

### Descripción:
- Este trigger se dispara cuando se graban los Renglones del Remito de Compras en la STA20 y automáticamente graban los Renglones del Egreso de Stock repitiendo y respetando todo lo del Remito.

### Funcionalidad:
- Esta creado en la dbo.STA20 y se ejecuta cuando termina de grabar los Renglones del Remito de Compras para grabar automáticamente los Renglones del Comprobante de Salida hacia la otra Sucursal.

## Trigger:

#### Nombre:
- Nombre del Trigger: `TR_UPDATE_STA14_ON_CPA_OC_REMITO`

#### Descripción:
- Se ejecuta cuando se grabo la relación entre la Orden de Compra y el Remito.

#### Funcionalidad:
- Como la relación entre el Remito de Compras y la Orden de Compra se graba al final de la grabación del "Ingreso del Remito", lo que hace es buscar por medio del "NCOMP_IN_S" que se guardo en la tabla temporal "VariablesGlobales" el NCOMP_IN_S del Egreso que se grabó mediante el Trigger anterior y coloca en la STA14 el NRO_SUCURSAL_DESTINO que se grabo con la Orden de Compra.

## Contribución:

## Problemas y Sugerencias:

## Licencia:
Este proyecto está bajo la Licencia [Punto-Gestion].
