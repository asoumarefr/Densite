/*
SELECT *
FROM  densite_65.ocs;

TRUNCATE densite_65.ocs;
*/

-- DROP FUNCTION   densite_65.fc_maj_champs; 
CREATE OR REPLACE FUNCTION densite_65.fc_maj_champs ()
RETURNS trigger AS
$BODY$
BEGIN

IF NEW.code_12 IS NOT NULL THEN
	UPDATE  densite_65.ocs t1
	
	SET nom_classe = 
	CASE WHEN NEW.code_12 BETWEEN 100 AND 199 THEN 'Territoires artificialisés'
		WHEN NEW.code_12 BETWEEN 200 AND 299 THEN 'Territoire agricole'
		WHEN NEW.code_12 BETWEEN 300 AND 399 THEN 'Forêts et milieux semi-naturels'
		WHEN NEW.code_12 BETWEEN 400 AND 499 THEN 'Zones humides'
		WHEN NEW.code_12 BETWEEN 500 AND 599 THEN 'Surfaces en eau'
		ELSE '' END ,

	classe = 
	CASE WHEN NEW.code_12 BETWEEN 100 AND 199 THEN 1
		WHEN NEW.code_12 BETWEEN 200 AND 299 THEN 2
		WHEN NEW.code_12 BETWEEN 300 AND 399 THEN 3
		WHEN NEW.code_12 BETWEEN 400 AND 499 THEN 4
		WHEN NEW.code_12 BETWEEN 500 AND 599 THEN 5
		ELSE 0 END,
	superficie = st_area(NEW.geom)
	WHERE t1.id = NEW.id ;
	RETURN NEW;

END IF ;
RETURN NEW;

END;
$BODY$ 
LANGUAGE plpgsql;


--- DROP TRIGGER IF EXISTS tr_maj_champs ON densite_65.ocs
CREATE TRIGGER tr_maj_champs
AFTER UPDATE OR INSERT
ON densite_65.ocs
FOR EACH ROW
WHEN (pg_trigger_depth() = 0)
EXECUTE PROCEDURE densite_65.fc_maj_champs();
COMMENT ON TRIGGER tr_maj_champs ON densite_65.ocs IS 'MAJ des champs';

GRANT EXECUTE ON FUNCTION densite_65.fc_maj_champs() TO public;