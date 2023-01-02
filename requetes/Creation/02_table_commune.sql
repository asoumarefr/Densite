CREATE TABLE IF NOT EXISTS densite_65.commune (
    id SERIAL NOT NULL PRIMARY KEY,
    nom varchar(255),
    insee varchar(5),
    population integer,
	code_dept integer,
    superficie double precision,
    date_update date DEFAULT now(),
    user_update varchar(255) DEFAULT user,
    geom geometry(MultiPolygon, 2154)
); 
GRANT SELECT, INSERT, UPDATE, DELETE,  TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA densite_65 TO public;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA densite_65 TO public;
