#!/usr/env/python
import time
import os, sys
import requests
import unicodedata
from random import randint

import urlparse
import itertools
from urlparse import urlparse


#methods for extracting features - start

	#from collectStatsFromGoogle import getGoogleKnowledgeEntityPresent
	#from collectStatsFromGoogle import getGoogleImageFlag
	#from collectStatsFromGoogle import getGoogleScholarFlag
	#from collectStatsFromGoogle import retrieveAdTldDict
	#from collectStatsFromGoogle import getAdRatio
	#from collectStatsFromGoogle import retrieveLinksFromGooglePage
	#from collectStatsFromGoogle import getPermutationOfBars
	#from collectStatsFromGoogle import getTitles

	#from generateVis import getMimeTypeFeature
	#from generateVis import getRank8PNFeature
	#from generateVis import getTldFeature
	#from generateVis import getMaxRelatedness
	#from generateVis import getWikipediaFeature

#methods for extracting features - end

def getGoogleKnowledgeEntityPresent(googleHTMLSoup):
	if( len(googleHTMLSoup) == 0 ):
		return False

	knowledgeGraphEntity = googleHTMLSoup.find('div', {'class': 'kno-ecr-pt kno-fb-ctx'})

	if( knowledgeGraphEntity is None ):
		return False
	else:
		#return knowledgeGraphEntity.text
		return True

def getGoogleImageFlag(googleHTMLSoup):

	if( len(googleHTMLSoup) == 0 ):
		return False

	googleImageHeading = googleHTMLSoup.find('span', {'class': '_SKb bl'})

	if( googleImageHeading is None ):
		return False
	else:
		return True

def getGoogleScholarFlag(googleHTMLSoup):

	if( len(googleHTMLSoup) ==  0 ):
		return False

	results = googleHTMLSoup.findAll('div', {'class': 'srg'})
	titles = []
	for result in results:

		liOrDiv = result.findAll('li', {'class': 'g'})
		if( len(liOrDiv) == 0 ):
			liOrDiv = result.findAll('div', {'class': 'g'})

		for resultInstance in result:
			
			googleScholarFlag = resultInstance.find('div', {'class': 'f slp'})
			if( googleScholarFlag is not None ):
				googleScholarFlag = googleScholarFlag.findAll('a', {'class': 'fl'})

				if( len(googleScholarFlag) != 0 ):
					for item in googleScholarFlag:
						googleScholarFlag = item.text.lower()

						if( googleScholarFlag.find('by') != -1 or googleScholarFlag.find('cited by') != -1 or googleScholarFlag.find('related articles') != -1 ):
							return True

	return False

def retrieveAdTldDict_obsolete(googleHTMLSoup):

	if( len(googleHTMLSoup) == 0 ):
		return {}

	mainWindow = googleHTMLSoup.findAll('div', {'class': 'mw'})
	allLinksDict = {}

	if( mainWindow is None ):
		return {}
	else:
		if( len(mainWindow) > 1 ):

			linkHeaders = []
			try:
				linkHeaders = mainWindow[1].findAll('h3')
			except:
				return {}

			for i in range(0, len(linkHeaders)):
				
				try:
					#used to check if item is junk, since junk does not have .a or 'href'
					#try was used instead of explicit check due to problems checking if key exists
					link = linkHeaders[i].a['href']
					
					#special case - start
					if( link.find('http') != 0 ):
						#link to ad search on google
						continue
					#special case - end

					allLinksDict[i] = {}
					allLinksDict[i]['tld'] = ''

					parsedLink = urlparse(link)
					try:
						print('ad here'*5)
						#non add has link and class
						allLinksDict[i]['class'] = linkHeaders[i]['class'][0]
						
						if( len(parsedLink.netloc) != 0 ):
							#reference: domain.tld:port
							allLinksDict[i]['tld'] = parsedLink.netloc.split('.')[-1].split(':')[0]
	
					except:
						#ad has link but no class
						allLinksDict[i]['class'] = 'AD'
						
						#for ads links are relative to google domain
						if( len(parsedLink.query) != 0 ):
							indexOfAdurl = parsedLink.query.find('&adurl')

							if( indexOfAdurl != -1 ):
								adurl = parsedLink.query[indexOfAdurl+7:]
								adurl = urllib.unquote(adurl)
								parsedLink = urlparse(adurl)

								if( len(parsedLink.netloc) != 0 ):
									#reference: domain.tld:port
									allLinksDict[i]['tld'] = parsedLink.netloc.split('.')[-1].split(':')[0]

				except:
					pass

	return allLinksDict

def getAdRatio(googleHTMLSoup, linksCount):

	if( len(googleHTMLSoup) == 0 ):
		return 0

	liOrDiv = googleHTMLSoup.findAll('li', {'class': 'ads-ad'})
	if( len(liOrDiv) == 0 ):
		liOrDiv = googleHTMLSoup.findAll('div', {'class': 'ads-ad'})
	
	adCount = len(liOrDiv)
	if( linksCount == 0 ):
		linksCount = 1

	return adCount/float(adCount+linksCount)

def retrieveLinksFromGooglePage(googleHTMLSoup):

	#print '...getLinksFromGooglePage() - start'
	if( len(googleHTMLSoup) ==  0 ):
		return []

	listOfSearchTuples = []
	results = googleHTMLSoup.findAll('div', {'class': 'srg'})
	for result in results:

		liOrDiv = result.findAll('li', {'class': 'g'})
		if( len(liOrDiv) == 0 ):
			liOrDiv = result.findAll('div', {'class': 'g'})
		

		for resultInstance in liOrDiv:
			title = resultInstance.h3.a.text
			titleLink = resultInstance.h3.a['href']

			title = title.encode('ascii', 'ignore')

			#searchTuple = (title, titleLink)
			#listOfSearchTuples.append(searchTuple)
			listOfSearchTuples.append(titleLink.strip())

	#print '...getLinksFromGooglePage() - end'
	return listOfSearchTuples

def getPermutationOfBars(googleHTMLSoup):
	if( len(googleHTMLSoup) == 0 ):
		return ''

	googleButtons = googleHTMLSoup.findAll('div', {'class': 'hdtb-mitem hdtb-imb'})

	buttons = ''
	if( googleButtons is None ):
		return ''
	else:
		for button in googleButtons:
			buttons += ', ' + button.text

	if( len(buttons) > 1 ):
		buttons = buttons[2:]
		return buttons
	
	return ''

def getTitles(googleHTMLSoup):

	if( len(googleHTMLSoup) ==  0 ):
		return []

	results = googleHTMLSoup.findAll('div', {'class': 'srg'})
	titles = []
	for result in results:

		liOrDiv = result.findAll('li', {'class': 'g'})
		if( len(liOrDiv) == 0 ):
			liOrDiv = result.findAll('div', {'class': 'g'})

		for resultInstance in result:
			title = resultInstance.h3.a.text

			title = title.encode('ascii', 'ignore')
			title = sanitizeString(title.strip())
			titles.append(title)

	return titles

#**

def getTypeFromURL(URL):
	'''
		Using heuristics in order to avoid making slow request to server
	'''

	URL = URL.strip()
	if( len(URL) == 0 ):
		return ''

	parsed = urlparse(URL)

	extension = 'html'
	if( len(parsed.path) != 1 ):
		parsed = parsed.path.split('.')
		if( len(parsed) > 1 ):
			extension = parsed[-1].lower()

	return extension

def getListOfTypesFromURLs(arrayOfURLs):

	if( len(arrayOfURLs) == 0 ):
		return []

	extensions = []
	for url in arrayOfURLs:
		extensions.append(getTypeFromURL(url))

	return extensions

def getMimeTypeFeature(linksFromGooglePage):

	if( len(linksFromGooglePage) == 0 ):
		return 0.0

	mimeTypeFeature = 0.0
	pdfpptCount = 0
	listOfTypes = getListOfTypesFromURLs(linksFromGooglePage)
	listOfKnownTypes = ['pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt', 'dot', 'dox', 'dotx', 'rtf', 'pps', 'dotm', 'pdfx']
	for docType in listOfTypes:
		docType = docType.lower()
		if( docType in listOfKnownTypes ):
			pdfpptCount += 1

	if( len(listOfTypes) != 0 ):
		mimeTypeFeature = pdfpptCount/float(len(listOfTypes))
	else:
		mimeTypeFeature = 0

	return mimeTypeFeature

def getRankFor8PN(tup, n):

	if(n < 1):
		return 999

	lexPermList = list(itertools.permutations([0, 1, 2, 3, 4, 5, 6, 7], n))
	try:
		return lexPermList.index(tup)
	except:
		return 999

def getResultPermutationEncoding(commaDelPerm):

	if( len(commaDelPerm) == 0 ):
		return ''

	googlePermutationDict = {}

	googlePermutationDict['Apps'] = '0'
	googlePermutationDict['Books'] = '1'
	googlePermutationDict['Flights'] = '2'
	googlePermutationDict['Images'] = '3'
	googlePermutationDict['Maps'] = '4'
	googlePermutationDict['News'] = '5'
	googlePermutationDict['Shopping'] = '6'
	googlePermutationDict['Videos'] = '7'

	tokensArray = commaDelPerm.split(', ')

	encoding = ''
	for t in tokensArray:
		if t in googlePermutationDict:
			encoding += ', ' + googlePermutationDict[t]
		else:
			encoding += ', ' + '*'

	if len(encoding) > 1:
		encoding = encoding[2:]

	return encoding

def getRank8PNFeature(rank):

	permutation = getResultPermutationEncoding(rank)
	listOfPermTokes = permutation.split(', ')

	rank8P2Feature = 999
	rank8P3Feature = 999

	if( len(listOfPermTokes) > 1 ):
		perm = ( int(listOfPermTokes[0]), int(listOfPermTokes[1]) )
		rank8P2Feature = getRankFor8PN(perm, 2)
		
		perm = ( int(listOfPermTokes[0]), int(listOfPermTokes[1]), int(listOfPermTokes[2]) )
		rank8P3Feature = getRankFor8PN(perm, 3)

	return (rank8P2Feature, rank8P3Feature)

def getTldFeature(linksFromGooglePage):
	comCount = 0
	restCount = 0
	for link in linksFromGooglePage:
		url = urlparse(link)
		tld = url.netloc.split('.')[-1].split(':')[0].lower()
		url = url.netloc.lower()
		
		if( tld == 'com' ):
			comCount += 1
		else:
			restCount += 1

	tldFeature = 0
	if( comCount + restCount != 0 ):
		tldFeature = comCount / float(comCount + restCount)

	return tldFeature

# credit to: http://rosettacode.org/wiki/Levenshtein_distance
def LevenshteinDistance(s1,s2):
	if len(s1) > len(s2):
		s1,s2 = s2,s1

	distances = range(len(s1) + 1)
	for index2,char2 in enumerate(s2):

		newDistances = [index2+1]
		for index1,char1 in enumerate(s1):

			if char1 == char2:
				newDistances.append(distances[index1])
			else:
				newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
		
		distances = newDistances
	return distances[-1]

def relatednessMeasure(query, title, similarityOrExactness):

    query = query.strip().lower()
    title = title.strip().lower()
    similarityOrExactness = similarityOrExactness.strip()

    if( len(query) == 0 or len(title) == 0 or len(similarityOrExactness) == 0 ):
        return 0

    maxLength = len(title)
    if( len(query) > maxLength ):
        maxLength = len(query)

    distance = LevenshteinDistance(query, title)
    similarityScore = distance/float(maxLength)

    set1 = set(query.split(' '))
    set2 = set(title.split(' '))
    exactnessScore = len(set1 & set2)

    if( similarityOrExactness == 'similarity' ):
    	return similarityScore
    else:
    	return exactnessScore

def getMaxRelatedness(query, titlesArray, similarityOrExactness):

	#print '\t', similarityOrExactness
	query = query.strip().lower()
	similarityOrExactness = similarityOrExactness.strip()
	if( len(query) == 0 or len(titlesArray) == 0 or len(similarityOrExactness) == 0 ):
		return 0

	maxRelatedness = -1
	maxRelatedTitle = ''
	for title in titlesArray:
		relatedness = relatednessMeasure(query, title, similarityOrExactness)
		#print '\t\t', title, relatedness

		if( relatedness > maxRelatedness ):
			maxRelatedness = relatedness
			maxRelatedTitle = title
	
	#print '\t', maxRelatedness, maxRelatedTitle
	if( maxRelatedness == -1 ):
		return 0
	
	return maxRelatedness

def getWikipediaFeature(linksFromGooglePage):

	wikipediaFeature = False
	for link in linksFromGooglePage:
		url = link
		url = urlparse(url)

		url = url.netloc.lower()
		if( url.find('wikipedia') != -1 ):
			wikipediaFeature = True
			break

	return wikipediaFeature
#**

def remove_control_characters(s):
	if s is None:
		return ''

	s = unicode(s, "utf-8")
	return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def sanitizeString(myStr):
	myStr = remove_control_characters(myStr)

	myStr = myStr.replace('"', '')
	myStr = myStr.replace('\\','')
	myStr = myStr.replace('/','')

	return myStr

def genericErrorInfo():
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(fname, exc_tb.tb_lineno, sys.exc_info() )

def randSleep(maxSleepInSeconds=8):
	
	print 'randSleep():'
	if( maxSleepInSeconds < 1 ):
		maxSleepInSeconds = 5

	sleepSeconds = randint(1, 5)
	print '\tsleep:', sleepSeconds
	time.sleep(sleepSeconds)

def getCustomHeaderDict():
	#MOD get header from file
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:38.0) Gecko/20100101 Firefox/38.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate',
		'Connnection': 'keep-alive',
		'Cache-Control':'max-age=0'	
		}

	return headers

def mimicBrowser(uri, requestType='GET'):

	try:
		headers = getCustomHeaderDict()

		if( requestType == 'HEAD' ):
			co = 'curl -I --silent'

			for key, value in headers.items():
				co = co + ' -H "' + key + ': ' + value + '"'
			co = co + ' "' + uri + '"'

			return commands.getoutput(co)
		else:
			response = requests.get(uri, headers=headers)
			return response.text
	except:
		genericErrorInfo()

def dereferenceURI(URI):
	
	print 'dereferenceURI():', URI
	URI = URI.strip()
	if( len(URI) == 0 ):
		return ''
	
	htmlPage = ''
	try:
		randSleep()
		htmlPage = mimicBrowser(URI)
	except:
		genericErrorInfo()
	
	return htmlPage