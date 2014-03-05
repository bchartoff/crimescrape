Crime Scraper
==========

This is a very simple, single use-case scraper for DC crime data. Still, a few lessons can be learned from its implementation.

##Scraping

Because the [source data](http://crimemap.dc.gov/CrimeMapSearch.aspx) required form navigation (dropdowns, checkboxes, etc.) to download a csv, I used the [selenium package](http://docs.seleniumhq.org/) which automates browswer functionality (in this case, Firefox). Running this script locally opens Firefox, navigates the form, and downloads the file (ignoring the "save" dialog box).

##Running remotely

Because this script runs on a remote Ubuntu server, I had to run Firefox with a headless driver (i.e. a browswer driver with no Graphical User Interface), which I did using the [Xvfb display server](http://www.x.org/archive/X11R7.7/doc/man/man1/Xvfb.1.xhtml). From the server I ran:

####Installation:
```
$ apt-get install xvfb
```

####Set Xvfb's display number to one unlikey to be used (:98 in this case):
```
$ Xvfb :98 -ac
``` 

####Set environment display number to 98:
```
$ export DISPLAY=:98
``` 

Now the selenium script can run remotely.

##Scheduling the script:

I wrote the following cron job to schedule the script (since the DC crime data updates daily)

```
0 5 * * * rm -f /home/ubuntu/data/SearchResults* && export DISPLAY=:98 && /usr/bin/python /home/ubuntu/crimescrape.py
```

Every night at 5:00 AM, the script deletes the old data file (SearchResults.txt), sets the environment display, and runs the python scraper

##Hosting the data

I installed [nginx](http://wiki.nginx.org/Main) on the server, then modified the nginx config file:
```
vim /etc/nginx/nginx.conf
```

And modified the location of static files in the http/server block

```
http{
  server {
      location / {
          root /path/to/data;
      }
  }
}
```
Then just navigate to http://your-server's-IP/ to download the most recent version SearchResults.txt