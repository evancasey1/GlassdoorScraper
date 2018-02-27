# -*- coding: utf-8 -*-

from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from random import uniform, randrange
import string

PATH = "/Users/EvanCasey/Documents/Development/Drivers/"
filename = "jobDescriptions.txt"

languages = {"c++":0, 
            "c":0,
            "python":0,
            "javascript":0,
            "java":0,
            "ruby":0,
            "c#":0,
            "sql":0,
            "php":0,
            "html":0,
            "css":0}

#Handles creation of browser
def initBrowser():
    path_to_chromedriver = PATH + "chromedriver"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--incognito')

    browser = webdriver.Chrome(executable_path = path_to_chromedriver, chrome_options = options)
    return browser

#sleeps for a random period between min and max in order to stay undected
def rand_wait():
    min_s = 2.0
    max_s = 6.0
    sleep(randrange(min_s, max_s))

#searches jobs on 'keyword' at 'location' and returns the amount of jobs that it found
def searchJobs(keyword, location, browser):
    nPages = 1 #number of pages to search before quitting
    jobCount = 0
    
    browser.find_element_by_id('KeywordSearch').clear()
    browser.find_element_by_id('LocationSearch').clear()
    rand_wait()
    browser.find_element_by_id('KeywordSearch').send_keys(keyword)
    browser.find_element_by_id('LocationSearch').send_keys(location)
    rand_wait()
    browser.find_element_by_id('HeroSearchButton').click()
    rand_wait()
    
    base_url = browser.current_url
    jobDict = {}
    descList = []
    
    for i in range(nPages):
        try:
            rand_wait()
            jobPostings = browser.find_elements_by_class_name('jl') #get all job listings
            for job in jobPostings:
                job.click() #click the job so that the job description info is available
                rand_wait()

                #This try/except block exists to circumvent a popup Glassdoor shows
                #when clicking on a job for the first time
                try:
                    browser.find_element_by_class_name('mfp-close').click()
                except:
                    pass

                descList.append(browser.find_element_by_class_name("jobDescriptionContent").text)
                jobCount += 1
            
            browser.find_element_by_class_name('next').click()
        except Exception as e:
            print(e)
            pass
    
    #write the description data into one file
    print("Writing...")
    outfile = open(filename, "wb")
    outfile.writelines(descList)
    outfile.close()
    print("Write complete.")
    return jobCount

#scans the text for the keywords specified in languages
def parseData():
    print("Parsing...")
    infile = open(filename, "r")
    exclude = string.punctuation.replace("+", "")
    exclude = exclude.replace("#", "")

    for line in infile:
        line = line.translate(None, exclude) #removes punctuation
        for word in line.split():
            word = ''.join(filter(lambda c: c in string.printable, word)).lower()
            if word in languages:
                languages[word] += 1

    infile.close()
    print("Parse complete.")

#Provides analysis on the data. 
#TODO:
#   Provide graphs and other (more meaningful) statistics
#   Fix output to be more visually appealing
def displayStats(nJobs):
    print("\nNumber of Times Language Appeared:")
    for key in languages:
        print key.upper() + ": " + str(languages[key]) + " - " + str(round(float(languages[key])/float(nJobs) * 100.0, 2)) + "%"
    print "Total Jobs Found: " + str(nJobs) + "\n"

#Drives the program. Provides logical control
def main():
    url = "https://www.glassdoor.com/index.htm"
    keyword = 'software engineer'
    location = 'Raleigh, NC'

    browser = initBrowser()
    browser.get(url)

    nJobs = searchJobs(keyword, location, browser)
    parseData()
    displayStats(nJobs)

if __name__ == "__main__":
    main()