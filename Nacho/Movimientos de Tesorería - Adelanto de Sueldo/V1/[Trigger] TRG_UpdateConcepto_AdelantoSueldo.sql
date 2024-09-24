/*ESTE TRIGGER CORRESPONDE A UNA VERSIÓN VIEJA QUE NOS DA ERROR AL MOMENTO DE GRABAR. ESTE TRIGGER SE ELIMINO DIRECTAMENTE DE LA BASE DE DATOS*/
CREATE TRIGGER TRG_UPDATECONCEPTO_ADELANTOSUELDO
ON SBA04
AFTER INSERT
AS
BEGIN
    -- VERIFICA SI HAY ALGÚN REGISTRO CON COD_COMP = 'VAL', TIPO_COD_RELACIONADO = 'L' Y ID_LEGAJO NO ES NULL EN LA INSERCIÓN
    IF EXISTS (
        SELECT 1 
        FROM INSERTED 
        WHERE COD_COMP = 'VAL'  --TIPO DE COMPROBANTE = "VALES"
        AND TIPO_COD_RELACIONADO = 'L' --CODIGO RELACIONADO SEA "LEGAJO"
        AND ID_LEGAJO IS NOT NULL --EL LEGAJO NO SEA NULL.
    )
    BEGIN
        -- ACTUALIZA EL CAMPO CONCEPTO EN LA TABLA SBA04 COLOCANDOLA LEYENDA: "ADELANTO SUELDO [NOMBRE Y APELLIDO DEL LEGAJO]
        UPDATE S
        SET CONCEPTO = 'ADELANTO SUELDO ' + L.NOMBRE + ' ' + L.APELLIDO --LA COLUMNA DE "CONCEPTO" TIENE 40 CARACTERES.
        FROM SBA04 S
        JOIN LEGAJO L
            ON S.ID_LEGAJO = L.ID_LEGAJO
        WHERE S.TIPO_COD_RELACIONADO = 'L'
        AND S.COD_COMP = 'VAL'
        AND EXISTS (
            SELECT 1
            FROM INSERTED I
            WHERE I.ID_LEGAJO = S.ID_LEGAJO
              AND I.TIPO_COD_RELACIONADO = 'L'
        );
    END
END;
