'___setup___'
from bs4 import BeautifulSoup
from NHK_helper import *
from selenium import webdriver
import datetime
import time
import os


directory = r''
combineByDay = True
combineAll = False

if directory == '':
    directory = str.join('\\', __file__.split('\\')[:-1])



'___get user input___'
validInput = False
while not validInput:
    validInput = True
    startInput = input("Enter start date (dd/mm/yyyy or 'today'): ")
    endInput = input("Input end date or number of days: ")

    if '/' in startInput:
        day, month, year = startInput.split('/')
        startDate = datetime.date(int(year), int(month), int(day))
    elif startInput == 'today':
        startDate = datetime.date.today()
    else:
        print('Invalid input.\n')
        validInput = False
    

    if '/' in endInput:
        day, month, year = endInput.split('/')
        endDate = datetime.date(int(year), int(month), int(day))
    elif endInput == 'today':
        endDate = datetime.date.today()
    else:
        numDays = int(endInput)
        endDate = goBackBy(startDate, numDays, businessDays=False)

raise SystemExit






'___initiate browser___'
print('\nDownloading articles from {} to {}\n\n'.format(str(startDate), str(endDate)))
time.sleep(1)
print('Initializing browser')
time.sleep(0.5)
options = webdriver.ChromeOptions()
#options.add_argument('headless') #hides browser window
browser = webdriver.Chrome(options=options)



'___load NHK webpage___'
print('Loading NHK Web Easy page')
url = 'https://www3.nhk.or.jp/news/easy/'
browser.get(url)
prevDayButton = browser.find_element_by_xpath('//*[@id="easy-wrapper"]/div[2]/aside/section[2]/div[1]/a[2]')
nextDayButton = browser.find_element_by_xpath('//*[@id="easy-wrapper"]/div[2]/aside/section[2]/div[1]/a[1]')



'___navigate sidebar to start date___'
nextDayButton.click() #NHK sidebar defaults to previous day, so we click '次の日' to start on the current day
sidebarDate = getSidebarDate(browser)
while sidebarDate > startDate: #this loop doesn't run if the start date is 'today'
    prevDayButton.click()
    sidebarDate = getSidebarDate(browser)
    


'___download and convert audio files___'
oneDay = datetime.timedelta(days=1)
today = datetime.date.today()
endDate = goBackBy(startDate, numDays) #+ oneDay #adding one day prevents overcounting

articles = []
filenames = []

##if startDate == today:
##    frontpageArticles = getFrontpageArticles()
##    frontpageFilenames = downloadArticles(frontpageArticles)
##    articles.extend(frontpageArticles)
##    filenames.extend(frontpageFilenames)

while sidebarDate != endDate:
    sidebarArticles = getSidebarArticles(browser)
    newFilenames = downloadArticles(sidebarArticles)
    filenames.extend(newFilenames)
    prevDayButton.click()

if combineAll:
    print('\nCombining all files...')
    fileList = open('fileList.txt', 'w')
    fileList.writelines(filenames)
    fileList.close()
    os.system('ffmpeg -safe 0 -f concat -i fileList.txt -c copy NHK__{}_to_{}.mp3'.format(endDate.strftime('%Y-%m-%d'), startDate.strftime('%Y-%m-%d')))
    os.remove('fileList.txt')

print('Download complete')
browser.quit()
