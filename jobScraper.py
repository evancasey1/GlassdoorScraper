# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
from random import uniform
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import operator
import string

PATH = "/Users/EvanCasey/Documents/Development/Drivers/chromedriver"
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
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--incognito')

    browser = webdriver.Chrome(executable_path = PATH, chrome_options = options)
    return browser

#sleeps for a random period between min and max in order to stay undected
def rand_wait():
    min_s = 2.0
    max_s = 6.0
    sleep(uniform(min_s, max_s))

#searches jobs on 'keyword' at 'location' and returns the amount of jobs that it found
def searchJobs(keyword, location, browser):
    nPages = 30 #number of pages to search before quitting
    jobCount = 0
    timeOut = 10
    
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
    exclude = string.punctuation.replace("+", "")
    exclude = exclude.replace("#", "")
    outfile = open(filename, "wb")
    
    for i in range(0, nPages):
        try:
            rand_wait()
            jobPostings = browser.find_elements_by_class_name('jl') #get all job listings
            for job in jobPostings:
                job.click() #click the job so that the job description info is available
                rand_wait()
                rand_wait()

                #This try/except block exists to circumvent a popup Glassdoor shows
                #when clicking on a job for the first time
                try:
                    browser.find_element_by_class_name('mfp-close').click()
                except:
                    pass

                #text gets the job description content, encoded to utf-8, and then with the characters in 'exclude' and '\n' removed
                try:
                    myElem = WebDriverWait(browser, timeOut).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobDescriptionContent')))
                    text = myElem.text.encode('utf-8').translate(None, exclude)
                    descList.append(text)
                    descList.append(',')
                    outfile.writelines(descList)
                    jobCount += 1
                except TimeoutException:
                    print TimeoutException
                
                descList = []
            
            browser.find_element_by_class_name('next').click()
        except Exception as e:
            print(e)
            pass
    
    browser.quit()
    #write the description data into one file
    outfile.close()
    print("Write complete.")
    return jobCount

#scans the text for the keywords specified in keyword_dict
def parseData():
    print("Parsing...")
    infile = open(filename, 'r')
    jobs = []

    #Separates jobs on comma
    fullstr = ""
    for line in infile:
        if ',' not in line:
            fullstr += line
        else:
            fullstr += line[:-1]
            jobs.append(fullstr)
            fullstr = ""

    #Iterates through and collects data on jobs
    for job in jobs:
        used_kws = []
        for word in job.split():
            word = ''.join(filter(lambda c: c in string.printable, word)).lower()
            if word in keyword_dict and word not in used_kws:
                keyword_dict[word] += 1
                used_kws.append(word)

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
    kw_map = {}
    df = pd.DataFrame({'keyword': keyword_dict.keys(), 'occurences': keyword_dict.values()})
    df = df.sort_values(by = ['occurences'], ascending = False)
    sns.set_style("whitegrid")
    '''
    ax = sns.barplot(x = 'keyword', y = 'occurences', data = df)
    ax.set_xticklabels(df['keyword'], rotation = 0)
    fig = ax.get_figure()
    fig.savefig('plots/occurrence_bar_plot.png')
    '''
    df.rename(columns = {'occurences': 'percent_occurrence'}, inplace = True)
    #df['percent_occurrence'] = [round((float(x) / float(nJobs)) * 100, 2) for x in df['percent_occurrence']]
    #percs = [round((float(x) / float(nJobs)) * 100, 2) for x in df['percent_occurrence']]
    percs = []
    for item in df['percent_occurrence']:
        percs.append(str(round((float(item) / nJobs) * 100.0, 2)) + "%") 

    ax2 = sns.barplot(x = 'keyword', y = 'percent_occurrence', data = df)
    ax2.set_ylabel('Number of Occurences')
    xlabs = []

    count = 0
    for p in ax2.patches:
        ax2.text(p.get_x()+p.get_width()/2.,
                p.get_height() + 3,
                '{:s}'.format(percs[count]),
                ha="center") 
        count += 1

    for lab in df['keyword']:
        xlabs.append(lab)

    ax2.set_xticklabels(xlabs, rotation = 17)
    fig = ax2.get_figure()
    fig.savefig('plots/occurrence_bar_plot.png')

    plt.show()
    

#Drives the program. Provides logical control
def main():
    url = "https://www.glassdoor.com/index.htm"
    keyword = 'software engineer'
    location = 'Raleigh, NC'
    #browser = initBrowser()
    #browser.get(url)

    #nJobs = searchJobs(keyword, location, browser)
    nJobs = 898
    parseData()
    displayStats(nJobs)

if __name__ == "__main__":
    main()