from datetime import *
from dateutil.relativedelta import *
import calendar
import xyllmd
from collections import *
import csv
import json
import re
from zipfile import ZipFile, BadZipfile
from os.path import basename, splitext
from urllib2 import Request, urlopen, HTTPError
from cStringIO import StringIO

# widx = list(xrange(0,25))
# cl = list(xrange(1,39))
CLUSTERS = 39
WEEKS = 25
TODAY = date.today()
CRIMES = ["HOMICIDE & ASSAULT W/DANGEROUS WEAPON", "ROBBERY", "BURGLARY", "THEFT F/AUTO"]

#dict of week ids and start dates, built in setup()
weeks = {}

#display names and offense codes, w/ raw input fields as keys
offenses = { \
            "ARSON": {"code": "ar", "js": None, "col_header": "Arson"},  \
            "HOMICIDE & ASSAULT W/DANGEROUS WEAPON": {"code": "ah", "js": "Homicide and assault with dangerous weapon", "col_header": None},  \
            "HOMICIDE": {"code": "ho", "js": None, "col_header": "Homicide"},  \
            "ASSAULT W/DANGEROUS WEAPON": {"code": "as",  "js": None, "col_header": "Assault"},  \
            "BURGLARY": {"code": "bu", "js": "Burglary", "col_header": "Burglary"},  \
            "THEFT F/AUTO": {"code": "ta", "js": "Theft from auto", "col_header": "Theft_auto"},  \
            "THEFT/OTHER": {"code": "to", "js": "Other thefts", "col_header": "Theft_other"}, \
            "MOTOR VEHICLE THEFT": {"code": "mt", "js": "Motor vehicle theft", "col_header": "MV_Theft"}, \
            "ROBBERY": {"code": "ro", "js": "Robbery", "col_header": "Robbery"},  \
            "SEX ABUSE": {"code": "sa", "js": None, "col_header": "Sex_abuse"}  \
}

def read_zip(year):
  url = "http://data.octo.dc.gov/feeds/crime_incidents/archive/crime_incidents_%i_CSV.zip"%year

  filename = re.sub('[^\w\._ ]', '', basename(url))
  name, extension = splitext(filename)

  request = Request(url)
  try:
      response = urlopen(request)
  except HTTPError:
      raise
  data = StringIO(response.read())

  if extension == '.zip':
      try:
          zipfile = ZipFile(data)
      except BadZipFile:
          raise

      namelist = zipfile.namelist()
      data = zipfile.read(namelist[0])
  else:
      data = data.getvalue()
  return data


def setup():
    global weeks
    #populate weeks dict, for past 25 weeks, set key 0 is most recent monday, 1 the previous monday, etc.
    for i in range(0,WEEKS+1):
      #weekday = MO(-1) maps to most recent monday (i.e. week 0), convert 0 -> 25 to -1 -> -26
      counter = -i-1
      out_date = TODAY+relativedelta(weekday=MO(counter))
      weeks[i] = {"date": out_date, "wid": get_wid(out_date), "wstart": format_date(out_date)}


def get_date(date_str):
  #parse source data date string of form "1/14/2014 21:08 PM" and create date object
  date_str = date_str.split(" ")[0]
  date_list = date_str.split("/")
  month = int(date_list[0])
  day = int(date_list[1])
  year = int(date_list[2])
  #if csv formatting changes dd/mm/yyyy to dd/mm/yy, correct it
  if (year < 1900):
    if (year >= 80):
      year += 1900
    else:
      year += 2000

  return date(year,month,day)

def get_wid(in_date):
  #isocalendar function retuns list of 4 digit year, week number, day number
  #ISO 8601 standards define week number 1 as first week in a year with 4 or more days
  year = in_date.isocalendar()[0]
  week = in_date.isocalendar()[1]

  #add trailing 0 to single digit weeks
  if len(str(week)) == 1:
    week = "0"+str(week)
  else:
    week = str(week)

  return str(year)+week

def get_widx(in_date):
  #in_date = get_date(date_str)
  #for a given date, determine the previous monday
  in_monday = in_date+relativedelta(weekday=MO(-1))
  
  for week in weeks:
    #determine week number that matches the same start day (monday)
    if in_monday == weeks[week]['date']:
      return week
  #if date is not w/in the past 25 weeks, return None
  return None


def format_date(in_date):
  disp_months = {1: 'Jan.', 2: 'Feb.', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'Sept.', 10: 'Oct.', 11: 'Nov.', 12: 'Dec.'}
  return ("%s %s"%(disp_months[in_date.month],in_date.day)) #python string comprehensinos allow for %s to stand in for a var string, 
  #%i for an int, etc. "I ate %i %s" %(num, fruits) is the same as "I ate " + str(num) + " " + fruits


def parse_data():
  #open csv's for the last two years
  this_year = read_zip(TODAY.year)
  last_year = read_zip(TODAY.year-1)

  this_year_reader = csv.reader(StringIO(this_year),delimiter=',')
  last_year_reader = csv.reader(StringIO(last_year),delimiter=',')

  out_file = open("two_year_data.csv","wb")
  data_file_writer = csv.writer(out_file)

  #merge the two csvs
  for row in this_year_reader:
    data_file_writer.writerow(row)
  discard = last_year_reader.next()
  for row in last_year_reader:
    data_file_writer.writerow(row)

  out_file.close()

  #read from the merged csv
  data_file = csv.reader(open("two_year_data.csv","rU"))

  #get rid of header row
  head = data_file.next()
  data = []
  for row in data_file:
    #parse relavent fields
    date_str = row[1]
    offense = row[3]
    method = row[4]
    cluster = row[13]
    ccn = row[0]
    xblock = row[7]
    yblock = row[8]

    #call methods to convert fields to proper format
    in_date = get_date(date_str)
    wid = get_wid(in_date)
    widx = get_widx(in_date)
    cluster = int(cluster.replace("Cluster","").strip()) if cluster != "" else -1
    offense_code = offenses[offense]["code"]
    coords = xyllmd.xy_to_latlon(xblock,yblock)
    lat = coords[0]
    lon = coords[1]
    gun = "G" if method == "GUN" else ""

    data.append({"date":in_date, "wid":wid, "ccn": ccn, "widx":widx, "cluster": cluster, "offense_code": offense_code, "lat": lat, "lon": lon, "gun": gun})
  return data


def build_output(data):
  cluster_out = {}
  weekly_out = {}
  total_out = {}

  for entry in data:
    #go through data row by row
    entry_date = entry["date"]
    cluster = entry["cluster"]
    widx = entry["widx"]
    if not widx:
    #if row not in the past 25 weeks, continue
      continue

    offense_code = entry["offense_code"]
    if offense_code in ["as", "ho"]:
      #bundle assaults and homicides together
      bundled_code = "ah"
    elif offense_code in ["ro","bu","ta"]:
      bundled_code = offense_code
    else:
      #skip other crime types (arson, sex offenses, etc.)
      continue

    #build ouput for cluster js files, which tracks latest date and cumulative offenses
    if cluster not in cluster_out:
      cluster_out[cluster] = {widx:{"ah":0,"ro":0,"bu":0,"ta":0},"lastdate":entry_date}
    else:
      if widx not in cluster_out[cluster]:
        cluster_out[cluster][widx] = {"ah":0,"ro":0,"bu":0,"ta":0}
    
    cluster_out[cluster][widx][bundled_code] += 1
    cluster_out[cluster]["lastdate"] = entry_date if entry_date > cluster_out[cluster]["lastdate"] else cluster_out[cluster]["lastdate"]

    #build output for total js file, which tracks latest date and cumulative offenses, not separated by cluster
    if widx not in total_out:
      total_out[widx] = {"ah":0,"ro":0,"bu":0,"ta":0}
      total_out["lastdate"] = entry_date

    total_out[widx][bundled_code] += 1
    total_out["lastdate"] = entry_date if entry_date > total_out["lastdate"] else total_out["lastdate"]

    #build output for weekly js files, which contain lists of selected data from each row (ie each crime)
    if widx not in weekly_out:
      weekly_out[widx] = [entry]
    else:
      weekly_out[widx].append(entry)

  write_clusters(cluster_out)
  write_weekly(weekly_out)
  write_total(total_out)


def write_total(data):
  out_file = open("js/dc_weeks.js","w")
  #python dicts do not preserve order, but the OrderedDict object behaves as a similar hashmap, while
  #remembering the order of key entry
  out_dict = OrderedDict()

  out_dict["updated"] = format_date(TODAY)
  out_dict["lastdate"] = format_date(data["lastdate"])
  out_dict["weeks"] = []

  for widx in range(0,WEEKS+1):
    entry = OrderedDict()
    entry["widx"] = widx
    entry["wid"] = weeks[widx]["wid"]
    entry["wstart"] = weeks[widx]["wstart"]
    try:
      entry["ah"] = data[widx]["ah"]
      entry["ro"] = data[widx]["ro"]
      entry["bu"] = data[widx]["bu"]
      entry["ta"] = data[widx]["ta"]
    except KeyError:
      #if widx is not in data, still write to js file w/ 0 offenses
      entry["ah"] = 0
      entry["ro"] = 0
      entry["bu"] = 0
      entry["ta"] = 0

    out_dict["weeks"].append(entry)

  out_file.write(json.dumps(out_dict, sort_keys=False))
  out_file.close()




def write_clusters(data):
  
  for cluster in range(1,CLUSTERS + 1):
    out_file = open("js/cl_%i_weeks.js"%cluster,"w")
    out_dict = OrderedDict()
    out_dict["updated"] = format_date(TODAY)
    out_dict["lastdate"] = format_date(data[cluster]["lastdate"])
    out_dict["cluster"] = cluster
    out_dict["weeks"] = []
    for widx in range(0,WEEKS+1):
      entry = OrderedDict()
      entry["widx"] = widx
      entry["wid"] = weeks[widx]["wid"]
      entry["wstart"] = weeks[widx]["wstart"]
      try:
        entry["ah"] = data[cluster][widx]["ah"]
        entry["ro"] = data[cluster][widx]["ro"]
        entry["bu"] = data[cluster][widx]["bu"]
        entry["ta"] = data[cluster][widx]["ta"]

      except KeyError:
        #if cluster or widx are not in data, still write to js file with 0 offenses
        entry["ah"] = 0
        entry["ro"] = 0
        entry["bu"] = 0
        entry["ta"] = 0

      out_dict["weeks"].append(entry)

    out_file.write(json.dumps(out_dict, sort_keys=False))
    out_file.close()

def write_weekly(data):
  for crime in CRIMES:
    for widx in range(0, WEEKS+1):
      out_file = open("js/dc_%s_%s.js" %(offenses[crime]["code"],weeks[widx]["wid"]),"w")

      out_dict = OrderedDict()
      out_dict["widx"] = widx
      out_dict["wid"] = weeks[widx]["wid"]
      out_dict["wstart"] = weeks[widx]["wstart"]
      out_dict["offense"] = offenses[crime]["js"]

      temp_markers = []


      try:
       events = data[widx]
      except KeyError:
        #if week is not in sourch data, write an empty marker list to the file and continue
        out_dict["total"] = len(temp_markers)
        out_dict["markers"] = temp_markers
        out_file.write(json.dumps(out_dict, sort_keys=False))
        out_file.close()

        continue      

      for event in events:
        entry = OrderedDict()
        if event["offense_code"] != offenses[crime]["code"]:
          continue
        entry["ccn"] = event["ccn"]
        entry["x"] = event["lat"]
        entry["y"] = event["lon"]
        entry["o"] = event["offense_code"]
        entry["g"] = event["gun"]
        entry["d"] = format_date(event["date"])

        temp_markers.append(entry)
      #markers stored in temp list so that length of marker list can be calculated after population, while still
      #preserving key order ("total" before marker list)
      out_dict["total"] = len(temp_markers)
      out_dict["markers"] = temp_markers

      out_file.write(json.dumps(out_dict, sort_keys=False))
      out_file.close()

setup()
build_output(parse_data())