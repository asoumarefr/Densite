WITH table1 AS 
(
SELECT nom_classe, st_area(st_intersection(t1.geom, t2.geom)) as sup
FROM  densite_65.ocs t1, densite_65.commune t2
WHERE nom IN {0}
AND code_dept in ('65')
AND st_intersects(t1.geom, t2.geom)
GROUP BY nom_classe, st_intersection(t1.geom, t2.geom)
)
SELECT nom_classe, cast((sum(sup))as decimal (18,2)) AS superficie
FROM table1
GROUP BY nom_classe
ORDER BY nom_classe;
	
	
