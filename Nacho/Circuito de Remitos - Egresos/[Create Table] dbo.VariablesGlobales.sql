/*Se crea una tabla llamada "VariablesGlobales" donde se va a guardar el dato de @UltimoNCompInS para luego llamarlo desde el Trigger de la Sta20*/
CREATE TABLE VariablesGlobales (
    NombreVariable NVARCHAR(50),
    Valor NVARCHAR(MAX)
);