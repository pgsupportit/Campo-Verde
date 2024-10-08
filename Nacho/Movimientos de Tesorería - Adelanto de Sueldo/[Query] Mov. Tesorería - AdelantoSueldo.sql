SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
SET DATEFORMAT DMY 
SET DATEFIRST 7 
SET DEADLOCK_PRIORITY -8;

WITH MovimientosMonto AS (
    SELECT 
        COD_COMP, 
        N_COMP, 
        SUM(CASE WHEN D_H = 'D' THEN MONTO ELSE 0 END) AS [Monto del Movimiento]
    FROM 
        CTA29
    GROUP BY 
        COD_COMP, 
        N_COMP
)

SELECT 
    CTA28.COD_COMP AS [Tipo],
    CTA28.N_COMP + '/' + LTRIM(STR(CTA28.BARRA)) AS [Comprobante],
    CTA28.FECHA AS [Fecha],
    CTA28.CONCEPTO AS [Concepto],
    CASE 
        WHEN CTA28.CLASE = '1' THEN 'COBROS' 
        WHEN CTA28.CLASE = '2' THEN 'PAGOS' 
        WHEN CTA28.CLASE = '3' THEN 'DEPOSITOS' 
        WHEN CTA28.CLASE = '4' THEN 'OTROS MOVIMIENTOS Y CARTERA' 
        WHEN CTA28.CLASE = '5' THEN 'RECHAZO DE CHEQUES PROPIOS' 
        WHEN CTA28.CLASE = '6' THEN 'RECHAZO DE CHEQUES DE TERCEROS' 
        WHEN CTA28.CLASE = '7' THEN 'OTROS MOVIMIENTOS' 
        WHEN CTA28.CLASE = '8' THEN 'TRANSFERENCIA DE CHEQUES DIFERIDOS A BANCO' 
        WHEN CTA28.CLASE = '9' THEN 'TRANSFERENCIA ENTRE CARTERAS' 
    END AS [Clase],
    CTA28.N_COMP AS [Nro. comprobante],
    MovimientosMonto.[Monto del Movimiento],
	SUCURSAL. DESC_SUCURSAL
FROM 
    CTA28
LEFT JOIN MovimientosMonto ON CTA28.COD_COMP = MovimientosMonto.COD_COMP AND CTA28.N_COMP = MovimientosMonto.N_COMP
JOIN SUCURSAL ON SUCURSAL.NRO_SUCURSAL = CTA28.NRO_SUCURS
