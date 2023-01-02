-- DROP FUNCTION   densite_65.fc_maj_champs_sup; 
CREATE OR REPLACE FUNCTION densite_65.fc_maj_champs_sup ()
RETURNS trigger AS
$BODY$
BEGIN
IF NEW.geom IS NOT NULL THEN

	NEW.superficie = st_area(NEW.geom);
	RETURN NEW;

END IF ;
RETURN NEW;

END;
$BODY$ 
LANGUAGE plpgsql;

/*
SELECT *
FROM  densite_65.commune;

TRUNCATE densite_65.commune;
*/


--- DROP TRIGGER IF EXISTS tr_maj_champs_sup ON densite_65.commune
CREATE TRIGGER tr_maj_champs_sup
BEFORE UPDATE OR INSERT
ON densite_65.commune
FOR EACH ROW
WHEN (pg_trigger_depth() = 0)
EXECUTE PROCEDURE densite_65.fc_maj_champs_sup();
COMMENT ON TRIGGER tr_maj_champs_sup ON densite_65.commune IS 'MAJ du champs superficie';


GRANT EXECUTE ON FUNCTION densite_65.fc_maj_champs_sup() TO public;

GRANT EXECUTE ON FUNCTION densite_65.fc_maj_champs_sup() TO asoumare;
