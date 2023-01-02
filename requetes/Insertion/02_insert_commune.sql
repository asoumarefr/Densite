INSERT INTO densite_65.commune
(
	nom,
    insee,
    population,
	code_dept,
	geom
)
VALUES 
(%s, %s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 2154));
