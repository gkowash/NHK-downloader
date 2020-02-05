from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import time
import os



'___user parameters___'
directory = r''
startDate = datetime.date.today() #datetime.date(2019, 9, 5)   #to set manually, use datetime.date(year, month, day)
numDays = 7
combineByDay = True
combineAll = False

if directory == '':
    directory = str.join('\\', __file__.split('\\')[:-1])
if startDate == 'today':
    startDate = datetime.date.today()





class Article:
    def __init__(self, idNum, date):
        self.idNum = idNum
        self.date = date



def goBackBy(date, numDays, businessDays=True):
    currentDate = date
    oneDay = datetime.timedelta(days=1)
    while numDays > 0:
            if businessDays:
                    currentDate -= oneDay
                    if currentDate.weekday() not in [4,5]: #NHK doesn't post on Saturday or Sunday (but the sidebar is off by one day)
                            numDays -= 1
            else:
                    currentDate -= oneDay
                    numDays -= 1
    return currentDate



def getDateFromString(dateString, year):
    monthIndex = dateString.index('月')
    dayIndex = dateString.index('日')
    date = datetime.date(year, int(dateString[0:monthIndex]), int(dateString[monthIndex+1:dayIndex]))
    return date



def getSidebarArticles(browser):
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    articleElements = soup.findAll('a', {'class':'side-news-list__item side-news-item'})
    dateString = soup.find('p', {'class': 'archives-pager__date'}).string

    articles = []
    for article in articleElements:
        idNum = article['href'][2:17]
        date = getDateFromString(dateString, startDate.year)
        articles.append(Article(idNum=idNum, date=date))

    return articles



def getFrontpageArticles(browser):
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    articleElements = soup.findAll('h1', {'class': 'news-list-item__title'})

    articles = []
    for article in articleElements:
        idNum = article.a['href'][2:17]
        date = getDateFromString(article.a.time.string, startDate.year)
        articles.append(Article(idNum=idNum, date=date))
    
    return articles



def getSidebarDate(browser, html=None):
    if html == None:
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
    dateString = soup.find('p', {'class': 'archives-pager__date'}).string
    date = getDateFromString(dateString, startDate.year) #this might cause problems in the few weeks after the new year
    
    return date



def downloadArticles(articles):
    print('\nDownloading articles from ', articles[0].date) #in certain cases this date may not be accurate
    filenames = []
    for j,article in enumerate(articles):
        print('\tfile {}/{}'.format(j+1,len(articles)))
        date = article.date
        idNum = article.idNum
        fileURL = 'https://nhks-vh.akamaihd.net/i/news/easy/{}.mp4/master.m3u8'.format(idNum)
        filename = r'\NHK__{}-{}.mp3'.format(date.strftime('%Y-%m-%d'), j)
        filenames.append("file '{}'\n".format(filename[1:]))
        os.system('ffmpeg -i "{}" -f mp3 "{}"'.format(fileURL, directory+filename))
    if combineByDay:
        print('\tCombining {} files...'.format(len(filenames)))
        fileList = open('fileList.txt', 'w')
        fileList.writelines(filenames)
        fileList.close()
        os.system('ffmpeg -safe 0 -f concat -i fileList.txt -c copy {}.mp3'.format(filename[1:-6]))
        os.remove('fileList.txt')
        for j, article in enumerate(articles): #cleanup
            date = article.date
            filename = 'NHK__{}-{}.mp3'.format(date.strftime('%Y-%m-%d'), j)
            os.remove(filename)
            
    return filenames
        









        
if __name__ == '__main__':
    '___initiate browser___'
    print('Initializing browser')
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
    sidebarDate = getSidebarDate()
    while sidebarDate > startDate: #this loop doesn't run if the start date is 'today'
        prevDayButton.click()
        sidebarDate = getSidebarDate()
        


    '___download and convert audio files___'
    oneDay = datetime.timedelta(days=1)
    today = datetime.date.today()
    endDate = goBackBy(startDate, numDays) + oneDay #adding one day prevents overcounting

    articles = []
    filenames = []

    ##if startDate == today:
    ##    frontpageArticles = getFrontpageArticles()
    ##    frontpageFilenames = downloadArticles(frontpageArticles)
    ##    articles.extend(frontpageArticles)
    ##    filenames.extend(frontpageFilenames)

    while sidebarDate != endDate:
        sidebarArticles = getSidebarArticles()
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

