/*
SELECT *
FROM  densite_65.commune;

	TRUNCATE densite_65.commune;
*/

-- DROP FUNCTION   densite_65.fc_check_erreur_comm; 
CREATE OR REPLACE FUNCTION densite_65.fc_check_erreur_comm ()
RETURNS trigger AS
$BODY$
BEGIN

IF NEW.geom IS NULL OR st_isvalid(NEW.geom) = FALSE 
	THEN RAISE exception  
	'code_12 %. Le champs geom est NULL OU INVALIDE pour la commune : %', NEW.id, NEW.nom;

ELSEIF NEW.geom IN (SELECT DISTINCT geom FROM  densite_65.commune )
	THEN RAISE exception  
	'id : % Commune %. Cette géométrie existe déjà', NEW.id, NEW.nom;
RETURN NEW;

END IF ;
RETURN NEW;
END;

$BODY$ 
LANGUAGE plpgsql;


--- DROP TRIGGER IF EXISTS tr_controle_geom_comm ON densite_65.commune
CREATE TRIGGER tr_controle_geom_comm
BEFORE UPDATE OR INSERT
ON densite_65.commune
FOR EACH ROW
EXECUTE PROCEDURE densite_65.fc_check_erreur_comm();
COMMENT ON TRIGGER tr_controle_geom_comm ON densite_65.commune IS 'Vérification des erreurs géométriques';

GRANT EXECUTE ON FUNCTION densite_65.fc_check_erreur_comm() TO public;