from selenium import webdriver

#set download directory and do not show firefox download save dialog
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) #2 denotes custom save directory (0 -> default and 1 -> desktop)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', '/home/ubuntu/data/')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.txt')

#point to crime map
browser = webdriver.Firefox(firefox_profile=profile)
browser.get("http://crimemap.dc.gov/CrimeMapSearch.aspx")

#select data for 1 year prior to current date
year_button = browser.find_element_by_css_selector("input[value='Last Year']")
year_button.click()

#select "Other Geographic Area" tab
other_tab = browser.find_element_by_css_selector("a[href='#tabs-GeoOther']")
other_tab.click()

#select "District Boundary" from dropdown
district_boundary_option = browser.find_element_by_xpath("//select[@name='location_other_location']/option[text()='District Boundary']")
district_boundary_option.click()

#click search
search_button = browser.find_element_by_css_selector("input#btnSearch")
search_button.click()

#click download data
download = browser.find_element_by_css_selector("a[title='Download Data']")
download.click()

#select data format (.txt)
text_button = browser.find_element_by_css_selector("input#radFormat2")
text_button.click()


#select all fields in data
check_fields = ["chkFldANC","chkFldBlock","chkFldCensusBlockGroup","chkFldCensusTract","chkFldCCN","chkFldDistrict","chkFldMethod","chkFldNeighborhoodCluster","chkFldOffense","chkFldPSA","chkFldReportDate","chkFldStartDate","chkFldEndDate","chkFldShift","chkFldVotingPrecinct","chkFldWard","chkFldMapCoord"]
for field in check_fields:
	browser.find_element_by_css_selector("input[name=\"%s\"]"%field).click()

#click download button
get_data = browser.find_element_by_css_selector("input[value='Get Data']")
get_data.click()

browser.close()
