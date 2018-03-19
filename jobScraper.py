# -*- coding: utf-8 -*-

from selenium import webdriver
from time import sleep
from random import uniform
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import operator
import string

PATH = "/<PATH>/chromedriver"
filename = "jobDescriptions.txt"


#keys must be lowercase
keyword_dict = {"c++":0, 
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

#keyword_dict = {"master":0, "bachelor":0, "phd":0, "bs":0, "ms":0}

#Handles creation of browser
def initBrowser():
    path_to_chromedriver = PATH
    
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
    sleep(uniform(min_s, max_s))

#searches jobs on 'keyword' at 'location' and returns the amount of jobs that it found
def searchJobs(keyword, location, browser):
    nPages = 1 #number of pages to search before quitting
    jobCount = 0
    
    #Clears the search boxes and populates them with the 
    #keyword and location
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

#scans the text for the keywords specified in keyword_dict
def parseData():
    print("Parsing...")
    infile = open(filename, "r")
    exclude = string.punctuation.replace("+", "")
    exclude = exclude.replace("#", "")

    for line in infile:
        line = line.translate(None, exclude) #removes punctuation
        for word in line.split():
            word = ''.join(filter(lambda c: c in string.printable, word)).lower()
            if word in keyword_dict:
                keyword_dict[word] += 1

    infile.close()
    print("Parse complete.")

def getKeywordDF():
    result = []
    for key in keyword_dict:
        for i in range(keyword_dict[key]):
            result.append(key)

    return pd.DataFrame({'keyword':result})

#Provides analysis on the data. 
#TODO:
#   Provide graphs and other (more meaningful) statistics
#   Fix output to be more visually appealing
def displayStats(nJobs):
    #sorted list of tuples representing the keyword_dict [(key, value), ...]
    sorted_values = sorted(keyword_dict.items(), key=operator.itemgetter(1))
    sorted_values.reverse()
    print("\nNumber of Times Keyword Appeared:")
    for i in range(len(sorted_values)):
        percentage = round((float(sorted_values[i][1]) / float(nJobs)) * 100, 2)
        print sorted_values[i][0] + ": " + str(sorted_values[i][1]) + " - " + str(percentage) + "%"
    
    print "Total Jobs Found: " + str(nJobs) + "\n"

    #Seaborn bar chart
    df = pd.DataFrame({'keyword': keyword_dict.keys(), 'occurences': keyword_dict.values()})
    df = df.sort_values(by=['occurences'], ascending=False)
    sns.set_style("whitegrid")
    ax = sns.barplot(x='keyword', y='occurences', data=df)
    fig = ax.get_figure()
    fig.savefig('plots/plot.png')
    plt.show()
    

#Drives the program. Provides logical control
def main():
    url = "https://www.glassdoor.com/index.htm"
    keyword = 'software engineer'
    location = 'Raleigh, NC'

    browser = initBrowser()
    browser.get(url)

    nJobs = searchJobs(keyword, location, browser)
    #nJobs = 1
    parseData()
    displayStats(nJobs)

if __name__ == "__main__":
    main()