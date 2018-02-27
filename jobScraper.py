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

def initBrowser():
    path_to_chromedriver = PATH + "chromedriver"
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--incognito')

    browser = webdriver.Chrome(executable_path = path_to_chromedriver, chrome_options = options)
    return browser

def rand_wait():
    min_s = 2.0
    max_s = 6.0
    sleep(randrange(min_s, max_s))

def searchJobs(keyword, location, browser):
    nPages = 1
    jobCount = 0
    
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
            jobPostings = browser.find_elements_by_class_name('jl')
            for job in jobPostings:
                job.click()
                rand_wait()
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
    
    print("Writing...")
    outfile = open(filename, "wb")
    outfile.writelines(descList)
    outfile.close()
    print("Write complete.")
    return jobCount

def parseData():
    print("Parsing...")
    infile = open(filename, "r")
    exclude = string.punctuation.replace("+", "")

    for line in infile:
        line = line.translate(None, exclude)
        for word in line.split():
            word = ''.join(filter(lambda c: c in string.printable, word)).lower()
            if word in languages:
                languages[word] += 1

    infile.close()
    print("Parse complete.")


def displayStats(nJobs):
    print("\nNumber of Jobs Language Appeared in:")
    for key in languages:
        print key.upper() + ": " + str(languages[key]) + " - " + str(round(float(languages[key])/float(nJobs) * 100.0, 2)) + "%"
    print

def beginGlassdoor(browser, url):
    keyword = 'software engineer'
    location = 'Raleigh, NC'

    
    browser.get(url)
    browser.find_element_by_id('KeywordSearch').clear()
    browser.find_element_by_id('LocationSearch').clear()
    rand_wait()
    
    nJobs = searchJobs(keyword, location, browser)
    parseData()
    displayStats(nJobs)

def main():
    url = "https://www.glassdoor.com/index.htm"
    browser = initBrowser()
    beginGlassdoor(browser, url)

if __name__ == "__main__":
    main()