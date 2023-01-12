/*
SELECT *
FROM  densite_65.ocs;

	TRUNCATE densite_65.ocs;
*/

-- DROP FUNCTION   densite_65.fc_check_erreur; 
CREATE OR REPLACE FUNCTION densite_65.fc_check_erreur ()
RETURNS trigger AS
$BODY$
BEGIN

IF NEW.geom IS NULL OR st_isvalid(NEW.geom) = FALSE 
	THEN RAISE exception  
	'code_12 %. Le champs geom est NULL OU INVALIDE geom : %', NEW.id, NEW.geom;
/*
ELSEIF NEW.geom IN (SELECT geom FROM  densite_65.ocs )
	THEN RAISE exception  
	'%. Cette géométrie existe déjà', NEW.geom;
RETURN NEW;
*/

END IF ;
RETURN NEW;
END;

$BODY$ 
LANGUAGE plpgsql;


--- DROP TRIGGER IF EXISTS tr_controle_geom ON densite_65.ocs
CREATE TRIGGER tr_controle_geom
BEFORE UPDATE OR INSERT
ON densite_65.ocs
FOR EACH ROW
EXECUTE PROCEDURE densite_65.fc_check_erreur();
COMMENT ON TRIGGER tr_controle_geom ON densite_65.ocs IS 'Vérification des erreurs géométriques';


GRANT EXECUTE ON FUNCTION densite_65.fc_check_erreur() TO public;