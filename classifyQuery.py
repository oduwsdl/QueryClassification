#!/usr/env/python
import math

from bs4 import BeautifulSoup
from services import *

reload(sys)
sys.setdefaultencoding('utf8')

def getGoogleHTMLPage(query):

	print 'getGoogleHTMLPage():'
	query = query.strip()
	if( len(query) == 0 ):
		return ''

	query = query.split(' ')

	searchQueryFragment = 'as_q='
	for token in query:
		searchQueryFragment = searchQueryFragment + token + '+'

	searchQueryFragment = searchQueryFragment[:-1]
	searchQuery = 'https://www.google.com/search?' + searchQueryFragment
	
	return dereferenceURI(searchQuery)

def getFeaturesDictForQuery(query):

	print 'getFeaturesDictForQuery():'

	#MOD
	googleSERP = getGoogleHTMLPage(query)
	outfile = open('output.html', 'w')
	outfile.write(googleSERP)
	outfile.close()
	

	#MOD
	'''
	print(' CAUTION, NOT LIVE' * 3)
	googleSERP = ''
	infile = open('output.html', 'r')
	googleSERP = infile.read()
	infile.close()
	'''

	soup = BeautifulSoup(googleSERP)

	f1_googleEntity = getGoogleKnowledgeEntityPresent(soup)
	f2_googleImageFlag = getGoogleImageFlag(soup)
	f3_googleScholarFlag = getGoogleScholarFlag(soup)

	linksFromGooglePage = retrieveLinksFromGooglePage(soup)
	f4_adsRatio = getAdRatio(soup, len(linksFromGooglePage))

	
	googleVerticalPermutation = getPermutationOfBars(soup)

	# maxdissim and max overlap - storing not required since titles are stored
	allTitles = getTitles(soup)

	query = query.encode('ascii', 'ignore')

	f1_googleEntity = f1_googleEntity
	f2_googleImageFlag = f2_googleImageFlag
	f3_googleScholarFlag = f3_googleScholarFlag
	f4_adsRatio = f4_adsRatio

	featuresDict = {}
	featuresDict['query'] = sanitizeString(query)

	featuresDict['f1_googleEntity'] = f1_googleEntity
	featuresDict['f2_googleImageFlag'] = f2_googleImageFlag
	featuresDict['f3_googleScholarFlag'] = f3_googleScholarFlag
	featuresDict['f4_adsRatio'] = f4_adsRatio
	
	featuresDict['linksFromGooglePage'] = linksFromGooglePage
	featuresDict['googleBarsPermutation'] = googleVerticalPermutation
	featuresDict['allTitles'] = allTitles

	return featuresDict

'''
	This module checks if the Google SERP DOM has changed with some predefined by testing predefined queries against
	expected output. If some features do not fire a signal, this could indicate that the DOM has changed, therefore the classifier cannot perform as expected.
'''
def test_hasGoogleDOMChanged():

	print 'test_hasGoogleDOMChanged():'
	'''
	query: "albert einstein" tests
		f1_googleEntity
	
	query: "cheap bicycle" tests
		f4_adsRatio

	query: "genetically engineered mice" tests
		f2_googleImageFlag
		f3_googleScholarFlag
		f5_nonHTMLRate
		f6_VerticalPermutation
		f7_wikipedia
		f8_comRate
	'''

	passFlag = True

	#stage 1 test - start
	featuresDict = getFeaturesDictForQuery('albert einstein')
	if( featuresDict['f1_googleEntity'] == True ):
		print '\tf1_googleEntity: Pass'
	else:
		passFlag = False
		print '\tf1_googleEntity: Fail'
	#stage 1 test - end

	#stage 2 test - start
	featuresDict = getFeaturesDictForQuery('cheap bicycle')
	if( featuresDict['f4_adsRatio'] > 0 ):
		print '\tf4_adsRatio: Pass'
	else:
		passFlag = False
		print '\tf4_adsRatio: Fail'
	#stage 2 test - end

	#stage 3 test - start
	featuresDict = getFeaturesDictForQuery('genetically engineered mice')
	if( featuresDict['f2_googleImageFlag'] == True ):
		print '\tf2_googleImageFlag: Pass'
	else:
		passFlag = False
		print '\tf2_googleImageFlag: Fail'

	if( featuresDict['f3_googleScholarFlag'] == True ):
		print '\tf3_googleScholarFlag: Pass'
	else:
		passFlag = False
		print '\tf3_googleScholarFlag: Fail'

	if( getMimeTypeFeature(featuresDict['linksFromGooglePage']) > 0 ):
		print '\tf5_nonHTMLRate: Pass'
	else:
		passFlag = False
		print '\tf5_nonHTMLRate: Fail'

	rank8P23Feature = getRank8PNFeature(featuresDict['googleBarsPermutation'])
	if( rank8P23Feature[1] != 999 ):
		print '\tf6_VerticalPermutation: Pass'
	else:
		passFlag = False
		print '\tf6_VerticalPermutation: Fail'

	if( getWikipediaFeature(featuresDict['linksFromGooglePage']) == True ):
		print '\tf7_wikipedia: Pass'
	else:
		passFlag = False
		print '\tf7_wikipedia: Fail'

	if( getTldFeature(featuresDict['linksFromGooglePage']) > 0 ):
		print '\tf8_comRate: Pass'
	else:
		passFlag = False
		print '\tf8_comRate: Fail'
	#stage 3 test - end

	print 
	if( passFlag ):
		print '\tTest passed'
	else:
		print '\tTest failed; 1 or multiple DOM search keys in services.py might have changed, investigate by checking the DOM for whatever feature key is faulty.'

def classifyQueryScholarOrNonScholar(query):

	print 'classifyQueryScholarOrNonScholar():'
	query = query.strip()
	if( len(query) == 0 ):
		return ''

	coeffs = ''
	try:
		#MOD rename coeffs file
		coeffs = open('nasaCoeffs.txt', 'r').readlines()
	except:
		genericErrorInfo()
		return ''

	coeffsDict = {}
	# gen coeffsDict - start
	for featureCoeff in coeffs:
		featureCoeff = featureCoeff.strip().split(' ')
		coeffsDict[featureCoeff[0]] = float(featureCoeff[-1])
	# gen coeffsDict - end

	if( len(coeffsDict) == 0 ):
		print '\tEmpty Classifier Coeffs, exiting'
		return ''

	trueFalseArray = ['True', 'False']
	featuresDict = getFeaturesDictForQuery(query)
	print
	print 'Features:'
	googleEntityFeature = 1
	if( featuresDict['f1_googleEntity'] == True ):
		# weka switches polarity during substitution
		googleEntityFeature = 0
	print '\tf1_googleEntity:', trueFalseArray[googleEntityFeature]

	googleImageFeature = 1
	if( featuresDict['f2_googleImageFlag'] == True ):
		# weka switches polarity during substitution
		googleImageFeature = 0
	print '\tf2_googleImageFlag:', trueFalseArray[googleImageFeature]

	googleScholarFeature = 1
	if( featuresDict['f3_googleScholarFlag'] == True ):
		# weka switches polarity during substitution
		googleScholarFeature =  0
	print '\tf3_googleScholarFlag:', trueFalseArray[googleScholarFeature]

	adsRatioFeature = featuresDict['f4_adsRatio']
	print '\tf4_adsRatio:', adsRatioFeature
	nonHTMLRateFeature = getMimeTypeFeature(featuresDict['linksFromGooglePage'])
	print '\tf5_nonHTMLRate:', nonHTMLRateFeature

	# rank8PNFeature - start
	rank8P23Feature = getRank8PNFeature(featuresDict['googleBarsPermutation'])
	#rank8P2Feature = rank8P23Feature[0]
	verticalPermutationFeature = rank8P23Feature[1]
	print '\tf6_VerticalPermutation:', verticalPermutationFeature
	# rank8PNFeature - end

	wikipediaFeature = 1
	if( getWikipediaFeature(featuresDict['linksFromGooglePage']) == True ):
		# weka switches polarity during substitution
		wikipediaFeature =  0
	print '\tf7_wikipedia:', trueFalseArray[wikipediaFeature]

	comRateFeature = getTldFeature(featuresDict['linksFromGooglePage'])
	print '\tf8_comRate:', comRateFeature
	maxDissimilarityFeature = getMaxRelatedness(featuresDict['query'], featuresDict['allTitles'], 'similarity')
	print '\tf9_maxDissimilarity:', maxDissimilarityFeature
	maxOverlapFeature = getMaxRelatedness(featuresDict['query'], featuresDict['allTitles'], 'exactness')
	print '\tf10_maxOverlap:', maxOverlapFeature
	
	classProbability = 0
	classProbability = coeffsDict['Intercept'] + (coeffsDict['entity'] * googleEntityFeature) + (coeffsDict['image'] * googleImageFeature) + (coeffsDict['googleScholar'] * googleScholarFeature) + (coeffsDict['adRatio'] * adsRatioFeature) + (coeffsDict['mime'] * nonHTMLRateFeature) + (coeffsDict['rank8P3'] * verticalPermutationFeature) + (coeffsDict['wikipedia'] * wikipediaFeature) + (coeffsDict['tld'] * comRateFeature) + (coeffsDict['maxSimilarityScore'] * maxDissimilarityFeature) + (coeffsDict['maxIntersection'] * maxOverlapFeature)
	classProbability = math.exp(classProbability) / (1 + math.exp(classProbability))

	queryClass = ''
	if( classProbability >= 0.5 ):
		queryClass = 'scholar'
	else:
		queryClass = 'non-scholar'

	print
	return ('class: ' + queryClass + ', classProbability: ' + str(classProbability))

if( len(sys.argv) == 2 ):
	print 'Classification result for:', sys.argv[1]
	print
	print classifyQueryScholarOrNonScholar(sys.argv[1])

	print
	print('*'*100)
	print 'Running test to see if DOM has changed'
	test_hasGoogleDOMChanged()
else:
	print 'Usage:'
	print '\t', sys.argv[0], 'query'
	print '\tE.g.', sys.argv[0], '"fluid dynamics"'

