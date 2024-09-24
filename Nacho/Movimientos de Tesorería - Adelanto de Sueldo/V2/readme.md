## README: Lógica de Grabación del Adelanto de Sueldo

### Descripción General

Este sistema está diseñado para manejar el proceso de grabación de adelantos de sueldo, incluyendo la actualización del campo `CONCEPTO` en la tabla `SBA04`. La solución se basa en una combinación de triggers y un procedimiento almacenado para asegurar que el concepto se actualice correctamente tras la inserción de datos en las tablas relevantes.

### Componentes y Funcionalidad

1. **Tabla Temporal: `SBA04_TempConcepto`**

   - **Propósito**: Almacenar temporalmente los datos necesarios para actualizar el campo `CONCEPTO` en la tabla `SBA04`.
   - **Cuándo se utiliza**: Después de la inserción en la tabla `SBA04`, para guardar los datos de concepto que se deben aplicar en `SBA04`.

2. **Trigger en `SBA04`: `TRG_UpdateConcepto_AdelantoSueldo`**

   - **Propósito**: Capturar los registros insertados en `SBA04` que cumplen ciertos criterios (`COD_COMP = 'VAL'`, `TIPO_COD_RELACIONADO = 'L'`, y `ID_LEGAJO` no es NULL) y almacenar estos datos en la tabla temporal `SBA04_TempConcepto`.
   - **Cuándo se ejecuta**: Inmediatamente después de la inserción en `SBA04`.
   - **Acción**: Inserta datos en `SBA04_TempConcepto` con el concepto calculado basado en el nombre y apellido del legajo.

3. **Stored Procedure: `UpdateSBA04Concepto`**

   - **Propósito**: Actualizar el campo `CONCEPTO` en `SBA04` usando los datos almacenados en la tabla temporal `SBA04_TempConcepto`.
   - **Cuándo se ejecuta**: Es llamado por un trigger en `SBA04` una vez que se ha completado la inserción en esta tabla.
   - **Acción**: Actualiza `SBA04` con la información de la tabla temporal y luego limpia la tabla temporal `SBA04_TempConcepto`.

4. **Trigger en `SBA04`: `TRG_CallUpdateSBA04Concepto`**

   - **Propósito**: Activar la ejecución del stored procedure `UpdateSBA04Concepto` después de que se ha insertado un registro en `SBA04` que cumpla con los criterios definidos.
   - **Cuándo se ejecuta**: Inmediatamente después de la inserción en `SBA04`.
   - **Acción**: Llama al stored procedure para actualizar la columna `CONCEPTO` en `SBA04` con los datos de la tabla temporal.

### Flujo de Ejecución

1. **Inserción en `SBA04`**:
   - El trigger `TRG_UpdateConcepto_AdelantoSueldo` se activa.
   - Los datos relevantes se insertan en `SBA04_TempConcepto`.

2. **Inserción en `SBA04`**:
   - El trigger `TRG_CallUpdateSBA04Concepto` se activa.
   - Llama al stored procedure `UpdateSBA04Concepto`.

3. **Actualización en `SBA04`**:
   - El stored procedure `UpdateSBA04Concepto` actualiza el campo `CONCEPTO` en `SBA04` con los datos de `SBA04_TempConcepto`.
   - Limpia la tabla temporal `SBA04_TempConcepto` después de la actualización.

### Consideraciones

- **Tabla Temporal**: Asegúrate de que la tabla temporal `SBA04_TempConcepto` se maneje adecuadamente para evitar datos obsoletos o conflictos.
- **Integridad de Datos**: Verifica que todos los triggers y stored procedures funcionen correctamente para mantener la integridad de los datos y evitar errores durante el proceso de actualización.

---

Si necesitas más detalles o ajustes en el `README`, no dudes en decírmelo.