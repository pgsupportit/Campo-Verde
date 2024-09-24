ALTER TRIGGER TR_INSERT_EGRESO_RENGLONES
ON STA20
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
	--Declaro las variables de @UltimoNCompInS y @MaxRenglon.. El primero va a buscar el número de NComp_in_S que se grabo en la tabla temporal "dbo.VariablesGlobales". La segunda "@MaxRenglon" trabaja en el calculo de los renglones del egreso.
    DECLARE @UltimoNCompInS CHAR(8), @MaxRenglon INT;

    -- Obtener el último número de comprobante interno insertado en "dbo.VariablesGlobales"
    SELECT @UltimoNCompInS = Valor FROM VariablesGlobales WHERE NombreVariable = 'UltimoNCompInS';

	-- Verificar si el talonario en STA14 es 103 y el inserted es 'RP'
    IF EXISTS (
        SELECT 1
			FROM inserted i
				JOIN STA14 s ON i.NCOMP_IN_S = s.NCOMP_IN_S AND i.TCOMP_IN_S = s.TCOMP_IN_S
        WHERE s.TALONARIO = '103' AND i.TCOMP_IN_S = 'RP'
    )
    BEGIN
        -- Generar una secuencia para los números de renglón
        SELECT @MaxRenglon = ISNULL(MAX(N_RENGL_S), 0) FROM STA20 WHERE NCOMP_IN_S = @UltimoNCompInS AND TCOMP_IN_S = 'VS';

    -- Insertar en STA20 (Egreso de Stock)
    INSERT INTO STA20 (
        [FILLER], 
		[CAN_EQUI_V], 
		[CANT_DEV], 
		[CANT_OC], 
		[CANT_PEND], 
		[CANT_SCRAP], 
		[CANTIDAD],
        [COD_ARTICU], 
		[COD_DEPOSI], 
		[DEPOSI_DDE], 
		[EQUIVALENC], 
		[FECHA_MOV], 
		[N_ORDEN_CO],
        [N_RENGL_OC], 
		[N_RENGL_S], 
		[NCOMP_IN_S], 
		[PLISTA_REM], 
		[PPP_EX], 
		[PPP_LO], 
		[PRECIO],
		[PRECIO_REM], 
		[TCOMP_IN_S], 
		[TIPO_MOV], 
		[COD_CLASIF], 
		[CANT_FACTU], 
		[DCTO_FACTU],
        [CANT_DEV_2], 
		[CANT_PEND_2], 
		[CANTIDAD_2], 
		[CANT_FACTU_2], 
		[ID_MEDIDA_STOCK_2],
        [ID_MEDIDA_STOCK], 
		[ID_MEDIDA_VENTAS], 
		[ID_MEDIDA_COMPRA], 
		[UNIDAD_MEDIDA_SELECCIONADA],
        [PRECIO_REMITO_VENTAS], 
		[CANT_OC_2], 
		[RENGL_PADR], 
		[COD_ARTICU_KIT], 
		[PROMOCION],
        [PRECIO_ADICIONAL_KIT], 
		[TALONARIO_OC], 
		[ID_STA11], 
		[ID_STA14], 
		[COD_DEPOSI_INGRESO]
    )
    SELECT 
        [FILLER], 
		[CAN_EQUI_V], 
		[CANT_DEV], 
		[CANT_OC], 
		'0.0000000', 
		[CANT_SCRAP], 
		[CANTIDAD],
        [COD_ARTICU],
		[COD_DEPOSI],
		[DEPOSI_DDE],
		[EQUIVALENC],
		[FECHA_MOV],
		'', --Este dato para el Egreso de Stock es transparente.
        '0',--Este dato para el Egreso de Stock es transparente.
        @MaxRenglon + ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS N_RENGL_S,  -- Generar el número de renglón secuencialmente
        @UltimoNCompInS, 
		[PLISTA_REM], 
		[PPP_EX], 
		[PPP_LO], 
		[PRECIO], 
		[PRECIO_REM],
        'VS',  -- Tipo de Comprobante Interno de Egreso.
        'S',  -- Tipo "Salida" de Stock
        [COD_CLASIF], 
		[CANT_FACTU], 
		[DCTO_FACTU], 
		[CANT_DEV_2], 
		[CANT_PEND_2], 
		[CANTIDAD_2],
        [CANT_FACTU_2], 
		[ID_MEDIDA_STOCK_2], 
		[ID_MEDIDA_STOCK], 
		NULL, 
		[ID_MEDIDA_COMPRA], 
		'P',
        [PRECIO_REMITO_VENTAS], 
		[CANT_OC_2], 
		[RENGL_PADR], 
		[COD_ARTICU_KIT], 
		[PROMOCION],
        [PRECIO_ADICIONAL_KIT], 
		'0', --Este dato para el Egreso es transparente. 
		[ID_STA11], 
		[ID_STA14], 
		[COD_DEPOSI_INGRESO]
    FROM inserted
		WHERE TCOMP_IN_S = 'RP' AND COD_DEPOSI = '99';
	END;
	--exec sp_RecomposicionSaldosStock;1 /*Esto se comenta debido a que al no entrar en el bucle, se corre siempre la Recomposición cada vez que se graba algo en la STA20*/
END;