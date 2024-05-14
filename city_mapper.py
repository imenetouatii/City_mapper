#import needed libraries 
import folium, io, json, sys, math, random, os
import time
import pytz
import datetime
import psycopg2
from folium.plugins import Draw, MousePosition, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#-------------------------------------------------

# this function allows us to convert 0 to moday , 1 to tuesday etc
# we used it in query_dep_time to get the departure time of an itinerary
def weekday_string (day_int ) :  
    day_string= [ 'monday' , 'tuesday', 'wednesday','thursday','friday','saturday' , 'sunday']
    return day_string [day_int]


#-------------------------------------------------       
#main window class
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(600, 600)
	
        main = QWidget()
        self.setCentralWidget(main)
    
        #set the font 
        self.setFont(QFont('Helvetica',10))
        #change color 
        self.setStyleSheet("background-color: #00a791;")
        #customize the window
        title = "Detroit Public Transport App"
        # set the title
        self.setWindowTitle(title)

        #set the icon 
        self.setWindowIcon(QIcon("detroit_logo.png"))

   
        main.setLayout(QVBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        self.webView = myWebView()
		
        controls_panel = QHBoxLayout()
        # split the window into 2 sections , one for the table
        mysplit = QSplitter(Qt.Vertical)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)

        main.layout().addLayout(controls_panel)
        main.layout().addWidget(mysplit)

        _label = QLabel('From: ', self)
        _label.setFixedSize(30,20)
        self.from_box = QComboBox() 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.from_box)

        _label = QLabel('  To: ', self)
        _label.setFixedSize(20,20)
        self.to_box = QComboBox() 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.to_box)

        _label = QLabel('Hops: ', self)
        _label.setFixedSize(20,20)
        self.hop_box = QComboBox() 
        #self.hop_box.addItems( ['1', '2', '3', '4', '5'] )
        #garder que hops 3 
        self.hop_box.addItems( ['1', '2', '3', '4', '5'] )
        self.hop_box.setCurrentIndex( 0 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.hop_box)

        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.button_Go)
        controls_panel.addWidget(self.go_button)
           
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.button_Clear)
        controls_panel.addWidget(self.clear_button)

        self.maptype_box = QComboBox()
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        controls_panel.addWidget(self.maptype_box)
           
        self.connect_DB()

        self.startingpoint = True
                   
        self.show()
        

   #connect to database (here i used localhost as host)
    def connect_DB(self):
        self.conn = psycopg2.connect( host = "localhost",database="detroit_time", user = "postgres", password="azerty")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT DISTINCT name FROM (STOPS INNER JOIN network_combined ON STOPS.stop_i = network_combined.from_stop_i) ORDER BY name""")
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))

   #double click on a table row 
    def table_Click(self):
        k = 0
        prev_lat = 0
        for col in self.hop_list[self.tableWidget.currentRow()] :
            if (k % 3) == 0:
                lst = col.split(',')
                lat = float(lst[0])
                lon = float(lst[1]) 

                if prev_lat != 0:
                    self.webView.addSegment( prev_lat, prev_lon, lat, lon )
                prev_lat = lat
                prev_lon = lon

                self.webView.addMarker( lat, lon )
            k = k + 1
        

    def button_Go(self):
        self.tableWidget.clearContents()
        
        #the from station chosen by the user
        _fromstation = str(self.from_box.currentText())
        #the to station 
        _tostation = str(self.to_box.currentText())
        #number of hops 
        _hops = int(self.hop_box.currentText())

        

        #-------------- get current day and time
        # detroit time 

        detroit_now = datetime.datetime.now(pytz.timezone('America/New_York'))
        # weekday() return 0 for monday , 1 for tuesday etc..
        detroit_day = detroit_now.weekday()
        # convert the 0 for monday to the string 'monday'
        detroit_day = weekday_string (detroit_day)
        # extract time from datetime 
        detroit_time= detroit_now.time()

        # -------------------------------- 
        # we store the hop results in hop_list
        self.hop_list = []
        # we store the hop dep time
        self.time_list = []
        #we store latitudes , length og list is the number of stops in the hop
        self.lat_list = []
        #we store longitude , length of list is the number of stops in the hop
        self.lon_list =[]
        # -------------------------------- query for hop1
        if _hops >= 1 : 
            query_hop1 = f"WITH stop_all "\
            f"(stop_I , route_I , trip_I , stop_order, "\
            f"route_name , lat,lon , stop_name) "\
            f"AS (SELECT DISTINCT * "\
            f"FROM "\
            f"(trip_stops "\
            f"JOIN trips using (trip_I) "\
            f"JOIN routes using(route_I) "\
            f"JOIN stops using(stop_I))) "\
            f"\nSELECT distinct  A.stop_name as stop1,  A.route_name as BUS, B.stop_name as stop2  , "\
            f" A.stop_I,  A.lat, A.lon , B.stop_I ,  B.lat , B.lon , A.route_I  "\
            f"FROM stop_all as A , stop_all as B "\
            f"WHERE A.trip_I= B.trip_I "\
            f"AND A.stop_order < B.stop_order "\
            f"AND A.stop_name = $${_fromstation}$$ "\
            f"AND B.stop_name = $${_tostation}$$; "\

            self.cursor.execute(query_hop1)
            self.conn.commit()
            hop_rows = self.cursor.fetchall()


            # extract data to use for query_dep_time
            for row in hop_rows :
                row = list(row)
                
                # for departure time
                _fromstation_I = row[3]

                # for arrival time
                _tostation_I = row[6]
                
                # first  route_I 
                route_I = row[9]
                
                # get the dep_time of the next two trips of the route
                query_dep_time = f"SELECT  distinct dep_time  "\
                f"FROM ( network_temporal join trips using (trip_I) ) AS N "\
                f"WHERE N.from_stop_I = $${_fromstation_I}$$ "\
                f"AND  N.dep_day IN ( '$${detroit_day}$$'  , 'everyday') "\
                f"AND N.dep_time >=  '$${detroit_time}$$' "  \
                f"AND N.route_I = $${route_I}$$  "\
                f"order by dep_time asc  ; "\
                
                
                self.cursor.execute(query_dep_time)
                self.conn.commit()
                time_rows = self.cursor.fetchall()

                # len ( time_rows) != 0  -> if there are departure times available 
                # we add the trip information to hop_list
                # and the dep_time information to time_list
                
                if len(time_rows) != 0  :
                    
                    # in hop_list we add [from_stop_name , route_name , to_stop_name]
                    self.hop_list.append([row[0] ,  row[1]  , row[2]])
                    # in time_list we add [first_departure_time , second_departure_time]
                    self.time_list.append([list(time_rows[0])[0] , list(time_rows[1])[0]])
                    # in lat_list we add [from_stop_lat , to_stop_lat]
                    self.lat_list.append([row[4], row[7]])
                    # in lon_list we add [from_stop_lon , to_stop_lon]
                    self.lon_list.append([row[5] , row[8]])

            print ( self.hop_list)
            print(self.time_list)
        
        if _hops >= 2 : 

            self.cursor.execute(""f" WITH stop_all (stop_I , route_I , trip_I , stop_order, route_name , lat,lon , stop_name) AS (SELECT DISTINCT * FROM (trip_stops JOIN trips using (trip_I) JOIN routes using(route_I) JOIN stops using(stop_I))) SELECT distinct A.stop_name as stop1,A.route_name as BUS,B.stop_name as stop2 , C.route_name as BUS , D.stop_name as stop3 FROM stop_all as A , stop_all as B , stop_all as C , stop_all as D WHERE A.stop_order < B.stop_order AND A.trip_I= B.trip_I AND A.stop_name = $${_fromstation}$$ AND A.stop_I <> B.stop_I AND B.stop_I = C.stop_I AND A.route_I <> C.route_I AND C.stop_I <> D.stop_I And C.trip_I = D.trip_I AND C.stop_order < D.stop_order AND D.stop_name = $${_tostation}$$""")
            self.conn.commit()
            
            hop_rows = self.cursor.fetchall()
            print('hop2_rows ' , hop_rows)
            for row in hop_rows :
                self.hop_list.append([row[0] ,  row[1]  , row[2] , row[3], row[4]])
                print ('rows : ' , self.hop_list)
            
        
        if _hops >= 3 :
            self.cursor.execute(""f" WITH stop_all (stop_I , route_I , trip_I , stop_order, route_name , lat,lon , stop_name) AS (SELECT DISTINCT * FROM (trip_stops JOIN trips using (trip_I) JOIN routes using(route_I) JOIN stops using(stop_I))) SELECT  distinct A.stop_name as stop1 ,A.route_name as BUS , B1.stop_name as stop2 , B2.route_name as BUS, C1.stop_name as stop3, C2.route_name as BUS ,D.stop_name as stop_4 FROM stop_all as A ,stop_all as B1 ,stop_all as B2, stop_all as C1 , stop_all as C2 , stop_all as D WHERE A.stop_name = $${_fromstation}$$ AND  D.stop_name = $${_tostation}$$ AND A.trip_I =B1.trip_I AND B2.trip_I = C1.trip_I AND C2.trip_I = D.trip_I AND B1.stop_I =B2.stop_I AND C1.stop_I =C2.stop_I AND B2.stop_order < C1.stop_order AND A.stop_order < B1.stop_order AND C2.stop_order < D.stop_order AND A.route_I <> B2.route_I AND A.route_I <> C2.route_I AND B2.route_I <> C2.route_I""")
            self.conn.commit()
            hop_rows = self.cursor.fetchall()
            print('hop3_rows ' , hop_rows)
            for row in hop_rows :
                self.hop_list.append([row[0] ,  row[1]  , row[2] , row[3], row[4], row[5] ,row[6]])
                print ('rows : ' , self.hop_list)
            
        
        
        if len(self.hop_list) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        # get the number of hops we found = rows of table
        numrows = len(self.hop_list)
        # we add the rows related to the dep times
        # we will be giving 2 dep_times for hop =1
        
        numrows += len(self.time_list) * 2
        # get the length of the row related to the longest hop = cols of table
        numcols = len(self.hop_list[-1])

        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)

        # putting the stops and buses of the itinerary in the rows
        r = 0
        for row in self.hop_list : 
            c = 0
            for col in row :
                print(str(col))
                self.tableWidget.setItem(r, c, QTableWidgetItem(str(col)))
                c = c + 1
            r = r + 1
            #putting the times of the itinerary in rows
            # we only did this functionality for hop 1 
            if len(self.time_list) > 0 :
                for time in self.time_list :
                    # we add to the rows counter r , everytime we add a row
                    self.tableWidget.setItem(r , 0 , QTableWidgetItem(str(time[0])))
                    r += 1
                    self.tableWidget.setItem(r , 0 , QTableWidgetItem(str(time[1])))
                    r+= 1
                

        header = self.tableWidget.horizontalHeader()
        j = 0
        while j < numcols : 
            header.setSectionResizeMode(j, QHeaderView.ResizeToContents)
            j = j+1
        
        self.update()	


    def button_Clear(self):
        self.webView.clearMap(self.maptype_box.currentIndex())
        self.startingpoint = True
        self.update()


    def mouseClick(self, lat, lng):
        self.webView.addPointMarker(lat, lng)

        print(f"Clicked on: latitude {lat}, longitude {lng}")
        self.cursor.execute(""f" WITH mytable (distance, name) AS (SELECT ( ABS(lat-({lat})) + ABS(lon-({lng})) ), name FROM STOPS) SELECT A.name FROM mytable as A WHERE (A.distance <=  (SELECT min(B.distance) FROM mytable as B)) """)
        self.conn.commit()
        rows = self.cursor.fetchall()
        #print('Closest STATION is: ', rows[0][0])
        if self.startingpoint :
            self.from_box.setCurrentIndex(self.from_box.findText(rows[0][0], Qt.MatchFixedString))
        else :
            self.to_box.setCurrentIndex(self.to_box.findText(rows[0][0], Qt.MatchFixedString))
        self.startingpoint = not self.startingpoint



class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()

        self.maptypes = ["OpenStreetMap", "Stamen Terrain", "stamentoner", "cartodbpositron"]
        self.setMap(0)

    
    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object
    
    def handleClick(self, msg):

        # we get the coordinates of the clickded point in the dict data
        data = json.loads(msg)
        # we access the latitude and longitude of the clicked point
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']
        
        window.mouseClick(lat, lng)
    


    #my handle click 


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{lat}}, {{lon}}] ).addTo({{map}});
        L.circleMarker(
            [{{lat}}, {{lon}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), lat=lat, lon=lng)
        self.page().runJavaScript(js)


    def addPointMarker(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{lat}}, {{lon}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), lat=lat, lon=lng)
        self.page().runJavaScript(js)


    def setMap (self, i):
        #put detroit coordonates
        self.mymap = folium.Map(location=[42.3700, -83.0807], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)

        self.mymap = self.add_customjs(self.mymap)

        page = WebEnginePage(self)
        self.setPage(page)

        data = io.BytesIO()
        self.mymap.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())

    def clearMap(self, index):
        self.setMap(index)



class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
      print(msg)
      if 'coordinates' in msg:
        self.parent.handleClick(msg)


			
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    
    #page pre home
    splash = QSplashScreen()
    splash.setPixmap(QPixmap('city_of_detroit.png').scaled(700, 700))
    splash.show()
    splash.showMessage('<h1 style="color:black;">Welcome to Detroit Public Transport APP</h1>', 
                   Qt.AlignTop | Qt.AlignHCenter, Qt.white)    
    time.sleep(1)
# +++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
