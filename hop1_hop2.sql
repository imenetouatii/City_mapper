----------------------query to get examples to test hop1
WITH stop_all
(stop_I , route_I , trip_I , stop_order,
route_name , lat,lon , stop_name)
AS (SELECT DISTINCT *
FROM
(trip_stops
JOIN trips using (trip_I)
JOIN routes using(route_I)
JOIN stops using(stop_I)))

SELECT  distinct A.stop_name as stop1 , B.stop_name as stop2 
FROM stop_all as A ,stop_all as B 
WHERE A.stop_order < B.stop_order
AND A.trip_I =B.trip_I
AND A.stop_I <> B.stop_I
AND A.stop_name = '17117 9 MILE'
order by A.stop_name , B.stop_name;
------ examples 2
WITH stop_all
(stop_I , route_I , trip_I , stop_order,
route_name , lat,lon , stop_name)
AS (SELECT DISTINCT *
FROM
(trip_stops
JOIN trips using (trip_I)
JOIN routes using(route_I)
JOIN stops using(stop_I)))

SELECT  distinct A.stop_name as stop1 , B.stop_name as stop2 
FROM stop_all as A ,stop_all as B 
WHERE A.stop_order < B.stop_order
AND A.trip_I =B.trip_I
AND A.stop_I <> B.stop_I
AND B.stop_name = '14TH & POPLAR'
order by A.stop_name , B.stop_name;


-------------------------- hop 1

WITH stop_all
(stop_I , route_I , trip_I , stop_order,
route_name , lat,lon , stop_name)
AS (SELECT DISTINCT *
FROM
(trip_stops
JOIN trips using (trip_I)
JOIN routes using(route_I)
JOIN stops using(stop_I)))

SELECT distinct A.stop_name as stop1,A.route_name as BUS,B.stop_name as stop2
FROM stop_all as A , stop_all as B
WHERE A.trip_I= B.trip_I
AND A.stop_order < B.stop_order
AND A.stop_name = '1300 LAFAYETTE'
AND B.stop_name = 'GRAND BLVD & MILWAUKEE';

----------------------query to get examples to test hop2
SELECT  distinct A.name as stop1 , B.name as stop2 , D.name as stop_3
FROM stops_all as A ,stops_all as B , stops_all as C , stops_all as D
WHERE A.stop_order < B.stop_order
AND A.trip_I =B.trip_I
AND A.name ='1300 LAFAYETTE'

AND B.stop_I = C.stop_I
AND C.trip_I = D.trip_I
AND C.stop_order < D.stop_order
AND A.route_I <> C.route_I

limit 10;
--------------------------- hop 2

WITH stop_all
(stop_I , route_I , trip_I , stop_order,
route_name , lat,lon , stop_name)
AS (SELECT DISTINCT *
FROM
(trip_stops
JOIN trips using (trip_I)
JOIN routes using(route_I)
JOIN stops using(stop_I)))

SELECT distinct A.stop_name as stop1,A.route_name as BUS,B.stop_name as stop2 , C.route_name as BUS , D.stop_name as stop3
FROM stop_all as A , stop_all as B , stop_all as C , stop_all as D

WHERE A.stop_order < B.stop_order
AND A.trip_I= B.trip_I
AND A.stop_name = '1300 LAFAYETTE'
AND A.stop_I <> B.stop_I
AND B.stop_I = C.stop_I
AND A.route_I <> C.route_I
AND C.stop_I <> D.stop_I
And C.trip_I = D.trip_I
AND C.stop_order < D.stop_order
AND D.stop_name = 'GRAND BLVD & MILWAUKEE';

---------------------- hop 3

------------ requette pour exemple ( n'arrte pas de tourner si je precise A.stop_name uniquement , quand je precise les deux comme ici j'ai 0 rows)
--------- pour les requettes pour trouver les exemples pour hop1 et hop2 je precise un arret sinon ça fait trop pour la requette
---- la j'essaye de trouver un stop qui me permettra de trouver des exemple pour tester le hop3

WITH stop_all
(stop_I , route_I , trip_I , stop_order,
route_name , lat,lon , stop_name)
AS (SELECT DISTINCT *
FROM
(trip_stops
JOIN trips using (trip_I)
JOIN routes using(route_I)
JOIN stops using(stop_I)))

SELECT  distinct A.stop_name as stop1 , B1.stop_name as stop2 ,  C1.stop_name as stop3, D.stop_name as stop_4
FROM stop_all as A ,stop_all as B1 ,stop_all as B2, stop_all as C1 , stop_all as C2 , stop_all as D


WHERE A.stop_name ='1300 LAFAYETTE'
AND C2.stop_name ='GRAND BLVD & MILWAUKEE'
AND A.trip_I =B1.trip_I
AND B2.trip_I = C1.trip_I
AND C2.trip_I = D.trip_I

AND B1.stop_I =B2.stop_I
AND C1.stop_I =C2.stop_I

AND B2.stop_order < C1.stop_order
AND A.stop_order < B1.stop_order
AND C2.stop_order < D.stop_order

AND A.route_I <> B2.route_I
AND A.route_I <> C2.route_I
AND B2.route_I <> C2.route_I;

---------------------- query for hop3 ( elle donne 0 rows , je ne sais pas si erreur ou si il n'esiste pas de trajet)
WITH stop_all
(stop_I , route_I , trip_I , stop_order,
route_name , lat,lon , stop_name)
AS (SELECT DISTINCT *
FROM
(trip_stops
JOIN trips using (trip_I)
JOIN routes using(route_I)
JOIN stops using(stop_I)))

SELECT  distinct A.stop_name as stop1 ,A.route_name as BUS , B1.stop_name as stop2 , B2.route_name as BUS, C1.stop_name as stop3, C2.route_name as BUS ,D.stop_name as stop_4
FROM stop_all as A ,stop_all as B1 ,stop_all as B2, stop_all as C1 , stop_all as C2 , stop_all as D

WHERE A.stop_name =' Moross & Mack'
AND  D.stop_name = '1300 LAFAYETTE'

AND A.trip_I =B1.trip_I
AND B2.trip_I = C1.trip_I
AND C2.trip_I = D.trip_I

AND B1.stop_I =B2.stop_I
AND C1.stop_I =C2.stop_I

AND B2.stop_order < C1.stop_order
AND A.stop_order < B1.stop_order
AND C2.stop_order < D.stop_order

AND A.route_I <> B2.route_I
AND A.route_I <> C2.route_I
AND B2.route_I <> C2.route_I;