--Se arma esta query para que @Marcos pueda armar su programa a medida para la generación de Etiquetas en Campo Verde

/*Esta consulta es el buscador del programa donde se busca por Cod. Barra o Descripción del Artículo*/
-- Columnas que trae: 
-- * Descripción Artículo
-- * Codigo de Barras 
-- * Precio
-- * Fecha de Modificación del Precio
-- ** Se filtra por los que son "Tipo no controla"
-- ** Se filtra por Lista de Precios = '10'
-- ** Se agrega la búsqueda "Descripción" y "Codigo de Barras" para que el usuario pueda buscar por algún dato puntual e imprimir esa etiqueta.
-- **Filtro por rango de fecha de modificación del precio.
SELECT
  STA11.COD_ARTICU AS [CÓDIGO DE ARTÍCULO],
  STA11.DESCRIPCIO AS [DESCRIPCIÓN ARTÍCULO], -- Descripción del artículo
  STA11.COD_BARRA AS [CÓDIGO DE BARRAS], -- Código de Barras
  REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS INT), 1), '.', ',') AS [PRECIO], -- Precio > Formatea el precio sin separador de miles
  CONVERT(VARCHAR, GVA17.FECHA_MODI, 103) AS [FECHA MODIFICACIÓN PRECIO], -- Fecha de Modificación del Precio en formato DD/MM/YYYY
  CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_SI)[1]', 'nvarchar(max)') AS [IMPRESO]
FROM STA11
JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU -- JOIN con la tabla de precios
WHERE STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO NO CONTROLA' -- Filtro para solo traer los "Tipo No Controla"
AND STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_SI)[1]', 'NVARCHAR(MAX)') = 'N' -- Filtro para solo traer los Etiquetas NO Impresas
AND GVA17.NRO_DE_LIS = '10' -- Filtra por Lista de Precios = '10'
AND (
  (STA11.DESCRIPCIO LIKE '%%' OR STA11.COD_BARRA LIKE '%%') -- Filtro para buscar por descripción o código de barras
  OR GVA17.FECHA_MODI BETWEEN '' AND '' -- Filtro por rango de fecha de modificación del precio (como ejemplo)
);



/*Esta consulta es el filtro del programa donde se busca por Fecha de Modificación del Precio*/
-- Columnas que trae: 
-- * Descripción Artículo
-- * Codigo de Barras 
-- * Precio
-- * Fecha de Modificación del Precio
-- ** Se filtra por los que son "Tipo no controla".
-- ** Se filtra por Lista de Precios = '10'.
-- ** Se trae los Precios qye aún no fueron impresos.
SELECT
  STA11.COD_ARTICU AS [CÓDIGO DE ARTÍCULO],
  STA11.DESCRIPCIO AS [DESCRIPCIÓN ARTÍCULO], -- Descripción del artículo
  STA11.COD_BARRA AS [CÓDIGO DE BARRAS], -- Código de Barras
  REPLACE(CONVERT(VARCHAR, CAST(GVA17.PRECIO AS DECIMAL(18, 2)), 1), '.', ',') AS [PRECIO], -- Precio > Formatea el precio sin separador de miles
  CONVERT(VARCHAR, GVA17.FECHA_MODI, 103) AS [FECHA MODIFICACIÓN PRECIO], -- Fecha de Modificación del Precio en formato DD/MM/YYYY
  CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_SI)[1]', 'nvarchar(max)') AS [IMPRESO] --Lee la columna "Impreso" de la STA11
FROM STA11
JOIN GVA17 ON STA11.COD_ARTICU = GVA17.COD_ARTICU -- JOIN con la tabla de precios
WHERE STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO NO CONTROLA' --Filtro para solo traer los "Tipo No Controla"
AND STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_SI)[1]', 'NVARCHAR(MAX)') = 'N'; --Filtro para solo traer los Etiquetas Impresa
AND GVA17.NRO_DE_LIS = '10' -- Filtra por Lista de Precios = '10'



/*Este UPDATE es el que usa Marcos para cambiar al "Imprimir" la etiqueta el campo en el ABM del Artículo pero cambia toda la estructura del "Campo Adicional"*/
Update STA11 set CAMPOS_ADICIONALES = 
'<CAMPOS_ADICIONALES>
  <CA_INFORMACION_PARA_BALANZA>TIPO NO CONTROLA </CA_INFORMACION_PARA_BALANZA>
  <CA_SI>N</CA_SI>
</CAMPOS_ADICIONALES>'
WHERE STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO NO CONTROLA' AND COD_ARTICU = ''

/*Este UPDATE es el que usa Marcos para cambiar al "Imprimir" la etiqueta el campo en el ABM del Artículo pero cambia solamente la estructura que nos interesa a nosotros*/
Update STA11 SET CAMPOS_ADICIONALES = 
        CAST(REPLACE(
            CAST(CAMPOS_ADICIONALES AS NVARCHAR(MAX)), 
            '<CA_SI>S</CA_SI>', 
            '<CA_SI>N</CA_SI>'
        ) AS XML)
WHERE STA11.CAMPOS_ADICIONALES.value('(/CAMPOS_ADICIONALES/CA_INFORMACION_PARA_BALANZA)[1]', 'NVARCHAR(MAX)') = 'TIPO NO CONTROLA' AND COD_ARTICU = ''
