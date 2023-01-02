DROP TRIGGER IF EXISTS tr_maj_champs ON densite_65.ocs;
DROP TRIGGER IF EXISTS tr_controle_geom ON densite_65.ocs;

DROP FUNCTION   IF EXISTS  densite_65.fc_maj_champs_check_erreur; 
DROP FUNCTION   IF EXISTS fc_check_erreur;
DROP FUNCTION   IF EXISTS fc_maj_champs; 

DROP TABLE  IF EXISTS  densite_65.ocs;
DROP TABLE densite_65.commune;



DROP SCHEMA densite_65 CASCADE;