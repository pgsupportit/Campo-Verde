/*Este trigger se incluye por un desarrollo que pidieron para la impresión de etiquetas. Lo que hace es ante un cambio de precio en la Lista 10, se desmarca el tilde de "IMPRESIÓN ETIQUETA" de 'S' a 'N'*/
--Esta versión solamente cambia el valor del Campo Adicional de "IMPRESIÓN ETIQUETA" y no toda la estructura.
CREATE TRIGGER TRG_UpdatePrice
ON GVA17
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Actualizar solo el nodo <CA_SI> a 'N' en el campo XML CAMPOS_ADICIONALES de STA11 cuando se modifique el precio en GVA17
    UPDATE STA11
    SET CAMPOS_ADICIONALES = 
        CAST(REPLACE(
            CAST(CAMPOS_ADICIONALES AS NVARCHAR(MAX)), 
            '<CA_SI>S</CA_SI>', 
            '<CA_SI>N</CA_SI>'
        ) AS XML)
    FROM STA11 WITH (NOLOCK)
    INNER JOIN inserted i WITH (NOLOCK) ON STA11.COD_ARTICU = i.COD_ARTICU
    INNER JOIN deleted d WITH (NOLOCK) ON i.COD_ARTICU = d.COD_ARTICU
    WHERE i.PRECIO <> d.PRECIO
    AND STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') in ('TIPO NO CONTROLA', 'TIPO PLU N si es UNITARIO')
    AND i.NRO_DE_LIS = '10';
END;

