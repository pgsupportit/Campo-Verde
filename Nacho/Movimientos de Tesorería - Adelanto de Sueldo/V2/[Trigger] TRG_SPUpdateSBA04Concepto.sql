--SE CREA EL TRIGGER QUE EJECUTA EL SP "UpdateSBA04Concepto"
CREATE TRIGGER [dbo].[TRG_SPUpdateSBA04Concepto]
ON [dbo].SBA04
AFTER INSERT
AS
BEGIN
    -- Verifica si hay algún registro con COD_COMP = 'VAL' y TIPO_COD_RELACIONADO = 'L' en la inserción
    IF EXISTS (
        SELECT 1 
        FROM inserted 
        WHERE COD_COMP = 'VAL'  -- Tipo de Comprobante = "Vales"
        AND TIPO_COD_RELACIONADO = 'L' -- Código Relacionado sea "Legajo"
    )
    BEGIN
        -- Llama al Stored Procedure para actualizar SBA04
        EXEC [dbo].[UpdateSBA04Concepto];
    END
END;
GO