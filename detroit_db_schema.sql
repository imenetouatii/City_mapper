CREATE TABLE routes ( route_I 	 int  PRIMARY KEY , route_name 	 text );

CREATE TABLE trips (trip_I	 int PRIMARY KEY , route_I	 int,
FOREIGN KEY (route_I) references routes
);

CREATE TABLE stops (stop_I	 int  PRIMARY KEY ,  lat	 numeric(20,17), lon	 numeric(20,17) , name	  text 
);

CREATE TABLE network_temporal_day (from_stop_I	 int  ,  to_stop_I	 int  , dep_time 	  text , arr_time	 text, trip_I 	 int,
PRIMARY KEY (from_stop_I , to_stop_I , dep_time , arr_time, trip_I) ,
FOREIGN KEY (from_stop_I) references stops,
FOREIGN KEY (to_stop_I) references stops,
FOREIGN KEY (trip_I) references trips
);

CREATE TABLE network_temporal_week (from_stop_I	 int  ,  to_stop_I	 int  , dep_date_time 	  text , arr_date_time	 text, trip_I 	 int,
PRIMARY KEY (from_stop_I , to_stop_I , dep_date_time , arr_date_time, trip_I) ,
FOREIGN KEY (from_stop_I) references stops,
FOREIGN KEY (to_stop_I) references stops,
FOREIGN KEY (trip_I) references trips
);

CREATE TABLE network_walk ( from_stop_I	 int ,  to_stop_I	 int  , d	  int , d_walk	 int,
PRIMARY KEY (from_stop_I , to_stop_I )
);

CREATE TABLE network_combined( from_stop_I	 int  ,  to_stop_I	 int , d	 int  , duration_avg	 numeric(20,15) ,n_vehicles	 int, route_I_counts	 text ,
PRIMARY KEY (from_stop_I , to_stop_I ),
FOREIGN KEY (from_stop_I) references stops,
FOREIGN KEY (to_stop_I) references stops
);

