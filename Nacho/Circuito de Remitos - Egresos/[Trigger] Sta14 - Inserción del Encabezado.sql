ALTER TRIGGER TR_INSERT_EGRESO_ENCABEZADO
ON STA14
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

	IF EXISTS (SELECT 1 FROM inserted WHERE TCOMP_IN_S = 'RP' AND TALONARIO = '103')
	BEGIN
	-- Se vacía la tabla "dbo.VariablesGlobales" para limpiarla.
	DELETE FROM VariablesGlobales;

    -- Definir variables para los últimos números de comprobante
    DECLARE @UltimoNComp CHAR(14), @UltimoNCompInS CHAR(8)

	/*Se obtiene tanto el "número interno" como el "número de comprobante" a grabar*/
    -- Obtener el último número de comprobante interno de los tipos de comprobante "VS" (Egreso).
		SELECT @UltimoNCompInS = ISNULL(RIGHT('00000000' + CAST(MAX(CAST(RTRIM(LTRIM(NCOMP_IN_S)) AS INT)) + 1 AS VARCHAR(8)), 8), '00000001')
		FROM STA14 WHERE TCOMP_IN_S = 'VS';
	-- Obtener el próximo número de comprobante de la tabla STA17.PROXIMO
		SELECT @UltimoNComp = ' ' + RIGHT('00000000000000' + CAST(ISNULL(PROXIMO, 0) AS VARCHAR(13)), 13) FROM STA17 WHERE TALONARIO = '99'; --Talonario de Stock > Egreso.
	

	--Se inserta en "VariablesGlobales" (Tabla Temporal) el valor del Numero Interno calculado.
	INSERT INTO VariablesGlobales (NombreVariable, Valor) VALUES ('UltimoNCompInS', @UltimoNCompInS);
	

    -- Insertar en STA14 (Egreso de Stock)
    INSERT INTO STA14 (
        [FILLER]
        ,[COTIZ]
        ,[EXPORTADO]
        ,[EXP_STOCK]
        ,[FECHA_ANU]
        ,[FECHA_MOV]
        ,[HORA]
        ,[LISTA_REM]
        ,[LOTE]
        ,[LOTE_ANU]
        ,[MON_CTE]
        ,[MOTIVO_REM]
        ,[N_COMP]
        ,[N_REMITO]
        ,[NCOMP_IN_S]
        ,[NCOMP_ORIG]
        ,[NRO_SUCURS]
        ,[OBSERVACIO]
        ,[SUC_ORIG]
        ,[T_COMP]
        ,[TALONARIO]
        ,[TCOMP_IN_S]
        ,[TCOMP_ORIG]
        ,[USUARIO]
        ,[COD_TRANSP]
        ,[HORA_COMP]
        ,[ID_A_RENTA]
        ,[DOC_ELECTR]
        ,[COD_CLASIF]
        ,[AUDIT_IMP]
        ,[IMP_IVA]
        ,[IMP_OTIMP]
        ,[IMPORTE_BO]
        ,[IMPORTE_TO]
        ,[DIFERENCIA]
        ,[SUC_DESTIN]
        ,[T_DOC_DTE]
        ,[LEYENDA1]
        ,[LEYENDA2]
        ,[LEYENDA3]
        ,[LEYENDA4]
        ,[LEYENDA5]
        ,[DCTO_CLIEN]
        ,[T_INT_ORI]
        ,[N_INT_ORI]
        ,[FECHA_INGRESO]
        ,[HORA_INGRESO]
        ,[USUARIO_INGRESO]
        ,[TERMINAL_INGRESO]
        ,[IMPORTE_TOTAL_CON_IMPUESTOS]
        ,[CANTIDAD_KILOS]
        ,[ID_DIRECCION_ENTREGA]
        ,[IMPORTE_GRAVADO]
        ,[IMPORTE_EXENTO]
        ,[ID_STA13]
        ,[NRO_SUCURSAL_DESTINO_REMITO]
    )
    SELECT 
        [FILLER]
        ,[COTIZ]
        ,[EXPORTADO]
        ,[EXP_STOCK]
        ,[FECHA_ANU]
        ,[FECHA_MOV]
        ,[HORA]
        ,[LISTA_REM]
        ,[LOTE]
        ,[LOTE_ANU]
        ,[MON_CTE]
        ,'' --En un movimiento normal de Egreso, se graba el dato en blanco.
        , @UltimoNComp -- Último número de comprobante calculado desde la STA17.PROXIMO (Stock > Talonarios)
        ,[N_REMITO]
        , @UltimoNCompInS -- Último número de comprobante interno calculado desde STA14 y grabado en "Variables Globales"
        ,[NCOMP_ORIG]
        ,[NRO_SUCURS]
        ,[OBSERVACIO]
        ,[SUC_ORIG]
        ,'99' -- Tipo de Comprobante de Egreso
        ,'99' -- Talonario de Egreso.
        ,'VS' -- Tipo de Comprobante Interno de Egreso.
        ,[TCOMP_ORIG]
        ,[USUARIO]
        ,[COD_TRANSP]
        ,[HORA_COMP]
        ,[ID_A_RENTA]
        ,[DOC_ELECTR]
        ,[COD_CLASIF]
        ,[AUDIT_IMP]
        ,[IMP_IVA]
        ,[IMP_OTIMP]
        ,[IMPORTE_BO]
        ,[IMPORTE_TO]
        ,'' --En un movimiento normal de Egreso, se graba el dato en blanco.
        ,[NRO_SUCURSAL_DESTINO_REMITO] -- Lo que carguen en el Remito como Suc. Destino iría al campo "Suc. Destino" para el Egreso.
        ,[T_DOC_DTE]
        ,[LEYENDA1]
        ,[LEYENDA2]
        ,[LEYENDA3]
        ,[LEYENDA4]
        ,[LEYENDA5]
        ,[DCTO_CLIEN]
        ,[T_INT_ORI]
        ,[N_INT_ORI]
        ,[FECHA_INGRESO]
        ,[HORA_INGRESO]
        ,[USUARIO_INGRESO]
        ,[TERMINAL_INGRESO]
        ,[IMPORTE_TOTAL_CON_IMPUESTOS]
        ,[CANTIDAD_KILOS]
        ,[ID_DIRECCION_ENTREGA]
        ,[IMPORTE_GRAVADO]
        ,[IMPORTE_EXENTO]
        ,[ID_STA13]
        ,[NRO_SUCURSAL_DESTINO_REMITO]
    FROM inserted
		WHERE TCOMP_IN_S = 'RP' AND TALONARIO = '103';

-- Actualizar el próximo número de comprobante en la tabla STA17.PROXIMO. Comprobante de Egreso (Stock > Egreso)
UPDATE STA17 SET Proximo = Proximo + 1 WHERE TALONARIO = '99';
	END;
END;