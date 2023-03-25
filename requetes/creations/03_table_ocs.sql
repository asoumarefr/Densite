CREATE TABLE IF NOT EXISTS densite_65.ocs (
    id SERIAL NOT NULL PRIMARY KEY,
    code_12 integer,
    classe integer,
    nom_classe varchar(255),
    superficie double precision,
    date_update date DEFAULT now(),
    user_update varchar(255) DEFAULT user,
    geom geometry(MultiPolygon, 2154)
);


-- DROP INDEX ocs.sidx_ocs_geom;
CREATE INDEX sidx_ocs_geom
  ON densite_65.ocs
  USING gist
  (geom);


COMMENT ON COLUMN densite_65.ocs.code_12 IS 'Code de classification';


GRANT SELECT, INSERT, UPDATE, DELETE,  TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA densite_65 TO public;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA densite_65 TO public;