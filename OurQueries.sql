/*Creer la base de données*/
CREATE DATABASE ptappdb;

/*1 - requete pour afficher les noms de stations*/
SELECT DISTINCT name FROM STOPS ORDER BY name;

/*test : afficher les id des stations (passed)*/
SELECT DISTINCT from_stop_i FROM network_combined ORDER BY from_stop_i;

/*2- requete pour afficher les trajets (comme tp5)*/
SELECT DISTINCT A.name , A.route_type, B.name 
FROM (STOPS INNER JOIN network_combined ON (STOPS.stop_i = network_combined.from_stop_I) AS A) 
CROSS JOIN (STOPS INNER JOIN network_combined ON (STOPS.stop_i = network_combined.to_stop_I) AS B)
WHERE (A.route_type = B.route_type);


/*test : afficher les trajets sans les noms*/
SELECT DISTINCT A.from_stop_i , A.route_type, B.to_stop_i
FROM network_combined AS A, network_combined AS B
WHERE (A.from_stop_i = $${_fromstation}$$) AND (B.to_stop_i = $${_tostation}$$) AND (A.route_type = B.route_type);

SELECT DISTINCT A.name , A.route_type, B.name
FROM (STOPS INNER JOIN network_combined ON (STOPS.stop_i = $${_fromstation}$$ ) ) AS A
CROSS JOIN (STOPS INNER JOIN network_combined ON (STOPS.stop_i = $${_tostation}$$)) AS B
WHERE (A.from_stop_i = $${_fromstation}$$) AND (A.to_stop_i = $${_tostation}$$);



/*hops 1 */
SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long FROM metros as A, metros as B WHERE A.nom_long = $${_fromstation}$$ AND B.nom_long = $${_tostation}$$ AND A.res_com = B.res_com
/*For hops 2 */
SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long, C.res_com, D.geo_point_2d, D.nom_long FROM metros as A, metros as B, metros as C, metros as D WHERE A.nom_long = $${_fromstation}$$ AND D.nom_long = $${_tostation}$$ AND A.res_com = B.res_com AND B.nom_long = C.nom_long AND C.res_com = D.res_com AND A.res_com <> C.res_com AND A.nom_long <> B.nom_long AND B.nom_long <> D.nom_long


/*My hops 1*/
SELECT DISTINCT A.name , A.route_type, B.name FROM (STOPS INNER JOIN network_combined ON (STOPS.name = $${_fromstation}$$ ) ) AS A CROSS JOIN (STOPS INNER JOIN network_combined ON (STOPS.name = $${_tostation}$$)) AS B WHERE A.from_stop_i IN (SELECT stop_I FROM STOPS WHERE name = $${_fromstation}$$ ) AND A.to_stop_i IN (SELECT stop_i FROM STOPS WHERE name = $${_tostation}$$)

/*My hops 2*/
SELECT DISTINCT A.name, A.route_type, B.name , C.route_type, D.name FROM (STOPS INNER JOIN network_combined ON (STOPS.name = $${_fromstation}$$ ) ) AS A CROSS JOIN (STOPS INNER JOIN network_combined ON (STOPS.name = $${_tostation}$$)) AS B WHERE A.from_stop_i IN (SELECT stop_I FROM STOPS WHERE name = $${_fromstation}$$ ) AND D.to_stop_i IN (SELECT stop_i FROM STOPS WHERE name = $${_tostation}$$)