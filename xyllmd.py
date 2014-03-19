from math import *
import csv

csv_in = csv.reader(open("test_data.csv","rU"))
csv_out = csv.writer(open("test_data_out.csv","wb"))

#----------- start of xy2LL ;
#DATA _NULL_ ; 
# xs= 398943
# ys= 133729
# lat= 0.0  
# lon= 0.0 

# XY2LL.sas ;
# Formula Converts X,Y  Stateplane to Lat/Long
# original For Texas North Central Stateplane 4202
#  --------- for MD state plane meters ;
# incoming vars are xs and ys ; 
# results are lat lon ; 

def xy_to_latlon(xs,ys):
  mx= float(xs)
  my= float(ys)

  if mx > 0 and my > 0:

    # Convert StatePlane to Meters ;  * not needed --------- MD is already meters ; 
    # mx = mx * 0.304800609
    # my = my * 0.304800609

    #Set up the coordinate system parameters. ;
    a = 6378137				#major radius of ellipsoid, map units (NAD 83) ;
    e = 0.08181922146			#eccentricity of ellipsoid (NAD 83) ;
    angRad = 0.01745329252 #number of radians in a degree ;
    pi4 = pi / 4

    #-------- these changed for coordinate system ;

    p0 = 37.66666666666666 * angRad  #latitude of origin ;
    p1 = 38.3  * angRad                    #latitude of first standard parallel ;
    p2 = 36.16666667 * angRad      #latitude of second standard parallel ;
    c0 = -77.0 * angRad             #central meridian ;
    x0 = 400000.0              #False easting of central meridian, map units ;
    y0 = 0 * 0.304800609           #False northing ;


    #Calculate the coordinate system constants ;
    c1 = cos(p1) / sqrt(1 - ((e ** 2) * sin(p1) ** 2)) 

    c2 = cos(p2) / sqrt(1 - ((e ** 2) * sin(p2) ** 2)) 

    t0 = tan(pi4 - (p0 / 2)) 

    t1 = tan(pi4 - (p1 / 2)) 

    t2 = tan(pi4 - (p2 / 2)) 

    t0 = t0 / (((1 - (e * (sin(p0)))) / (1 + (e * (sin(p0))))) ** (e / 2)) 

    t1 = t1 / (((1 - (e * (sin(p1)))) / (1 + (e * (sin(p1))))) ** (e / 2)) 

    t2 = t2 / (((1 - (e * (sin(p2)))) / (1 + (e * (sin(p2))))) ** (e / 2)) 

    n = log(c1 / c2) / log(t1 / t2) 

    f = c1 / (n * (t1 ** n)) 

    rho0 = a * f * (t0 ** n) 



    #Convert the coordinate to Latitude/Longitude ;

    #Calculate the Longitude ;

    mx = mx - x0                      #Apply Easting Factor ;

    my = my - y0                      #Apply Northing Factor ;

    pi2 = pi4 * 2 

    rho = sqrt((mx ** 2) + ((rho0 - my) ** 2))

    theta = atan(mx / (rho0 - my)) 

    t = (rho / (a * f)) ** (1 / n) 

    lon = (theta / n) + c0 


    #Estimate the Latitude ;

    lat0 = pi2 - (2 * atan(t))


    #Substitute the estimate into the iterative calculation that
    #converges on the correct Latitude value;

    part1 = (1 - (e * sin(lat0))) / (1 + (e * sin(lat0))) ;

    lat1 = pi2 - (2 * atan(t * (part1 ** (e / 2)))) ;


    while ( abs(lat1 - lat0) < 0.000000002 ):

      lat0 = lat1

      part1 = (1 - (e * sin(lat0))) / (1 + (e * sin(lat0)))

      lat1 = pi2 - (2 * atan(t * (part1 ** (e / 2))))


    #Convert from radians to degrees;

    lat = lat1 / angRad 

    lon = lon / angRad 

    return(lat,lon)

# print xy_to_latlon(398943,133729)


# head = csv_in.next()
# csv_out.writerow(head)

# for row in csv_in:
#   latlon = xy_to_latlon(float(row[5]),float(row[6]))
#   row[9] = latlon[1]
#   row[10] = latlon[0]
#   csv_out.writerow(row)


