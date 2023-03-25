INSERT INTO densite_65.ocs
(
	code_12,
	geom
)
VALUES 
(%s, ST_SetSRID(ST_GeomFromText(%s), 2154));
