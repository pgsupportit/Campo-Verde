--TRIGGER EN LA "SBA04" QUE INSERTA EN LA TABLA TEMPORAL LOS DATOS: 
--N_COMP, COD_COMP, ID_SBA02, CONCEPTO, ID_LEGAJO

CREATE TRIGGER [dbo].[TRG_SBA04_TempConcepto]
ON [dbo].[SBA04]
AFTER INSERT
AS
BEGIN
    -- Verifica si hay algún registro con COD_COMP = 'VAL', TIPO_COD_RELACIONADO = 'L' y ID_LEGAJO no es NULL en la inserción
    IF EXISTS (
        SELECT 1 
        FROM inserted 
        WHERE COD_COMP = 'VAL'  -- Tipo de Comprobante = "Vales"
        AND TIPO_COD_RELACIONADO = 'L' -- Código Relacionado sea "Legajo"
        AND ID_LEGAJO IS NOT NULL -- El Legajo no sea NULL.
    )
    BEGIN
        -- Inserta los datos en la tabla temporal SBA04_TempConcepto
        INSERT INTO SBA04_TempConcepto (N_COMP, COD_COMP, ID_LEGAJO, TIPO_COD_RELACIONADO, CONCEPTO, ID_SBA02)
        SELECT i.N_COMP, i.COD_COMP, i.ID_LEGAJO, i.TIPO_COD_RELACIONADO,
               'ANT. SUELDO ' + L.NOMBRE + ' ' + L.APELLIDO, i.ID_SBA02
        FROM inserted i
        JOIN LEGAJO L
            ON i.ID_LEGAJO = L.ID_LEGAJO
        WHERE i.TIPO_COD_RELACIONADO = 'L'
          AND i.COD_COMP = 'VAL';
    END
END;
GO

-- Habilita el TRIGGER
ALTER TABLE [dbo].[SBA04] ENABLE TRIGGER [TRG_SBA04_TempConcepto];
GO