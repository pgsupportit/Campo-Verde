/*Se crea la vista de "Información para importación en la Balanza"*/
CREATE VIEW INFORMACIONPARABALANZA AS (
SELECT 
  STA11.COD_ARTICU AS [COD. ARTICULO], -- Código de Artículo
  DESCRIPCIO AS [DESCRIPCIÓN ARTÍCULO], -- Descripción del artículo
  REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS DECIMAL(18, 2)), 1), '.', ',') AS [PRECIO], -- Formatea el precio sin separador de miles
  STA11.COD_ARTICU AS [COD. PLU], -- Código del Artículo
  '1' AS [COD. DEPARTAMENTO], -- Código Departamento (Siempre es 1)
  CASE 
    WHEN STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO PLU N si es UNITARIO' THEN 'N' -- Campos Adicionales = Tipo Plu N
    WHEN STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO PLU P si es PESABLE' THEN 'P' -- Campos Adicionales = Tipo Plu P
    ELSE 'NO CONTROLA' -- Si no, NO Controla
  END AS [TIPO PLU],
  '1' AS [COD. ETIQUETA], -- Código Etiqueta (Siempre es 1)
  '0' AS [IMPRESIÓN FECHA],
  GVA17.NRO_DE_LIS AS [LISTA PRECIOS], -- Número de Lista de Precios para filtrar en la consulta
  GVA17.FECHA_MODI AS [FECHA MODIFICACIÓN PRECIO] -- Fecha de Modificación del Precio para filtrar por las últimas modificaciones
FROM STA11
JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU; -- JOIN con la tabla de precios
)



/*Consulta agregada en las Consultas Externas*/
SET DATEFORMAT DMY
SELECT * FROM INFORMACIONPARABALANZA