--SE CREA UN PROCEDURE LLAMADO "UpdateSBA04Concepto" QUE MODIFICA EL UPDATE EN LA SBA04.CONCEPTO POR LO DE LA TABLA TEMPORAL
CREATE PROCEDURE [dbo].[UpdateSBA04Concepto]
AS
BEGIN
    -- Actualiza el campo CONCEPTO en la tabla SBA04 usando los datos de la tabla temporal
    UPDATE S
    SET CONCEPTO = T.CONCEPTO
    FROM SBA04 S
    JOIN SBA04_TempConcepto T
        ON S.N_COMP = T.N_COMP COLLATE Modern_Spanish_CI_AI
        AND S.ID_SBA02 = T.ID_SBA02
    WHERE T.COD_COMP = 'VAL'
    AND T.TIPO_COD_RELACIONADO = 'L';

    -- Limpiar la tabla temporal si ya no es necesaria
    TRUNCATE TABLE SBA04_TempConcepto;
END;
GO
