#!/usr/env/python
import math

from bs4 import BeautifulSoup
from services import *

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

	googleSERP = getGoogleHTMLPage(query)
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

	googleAdsAndTlds = retrieveAdTldDict(soup)
	f4_adsRatio = getAdRatio(googleAdsAndTlds)

	linksFromGooglePage = retrieveLinksFromGooglePage(soup)
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

	featuresDict = getFeaturesDictForQuery(query)

	googleEntityFeature = 1
	if( featuresDict['f1_googleEntity'] == True ):
		# weka switches polarity during substitution
		googleEntityFeature = 0

	googleImageFeature = 1
	if( featuresDict['f2_googleImageFlag'] == True ):
		# weka switches polarity during substitution
		googleImageFeature = 0

	googleScholarFeature = 1
	if( featuresDict['f3_googleScholarFlag'] == True ):
		# weka switches polarity during substitution
		googleScholarFeature =  0

	adsRatioFeature = featuresDict['f4_adsRatio']
	nonHTMLRateFeature = getMimeTypeFeature(featuresDict['linksFromGooglePage'])

	# rank8PNFeature - start
	rank8P23Feature = getRank8PNFeature(featuresDict['googleBarsPermutation'])
	#rank8P2Feature = rank8P23Feature[0]
	verticalPermutationFeature = rank8P23Feature[1]
	# rank8PNFeature - end

	wikipediaFeature = 1
	if( getWikipediaFeature(featuresDict['linksFromGooglePage']) == True ):
		# weka switches polarity during substitution
		wikipediaFeature =  0

	comRateFeature = getTldFeature(featuresDict['linksFromGooglePage'])
	maxDissimilarityFeature = getMaxRelatedness(featuresDict['query'], featuresDict['allTitles'], 'similarity')
	maxOverlapFeature = getMaxRelatedness(featuresDict['query'], featuresDict['allTitles'], 'exactness')
	
	classProbability = 0
	classProbability = coeffsDict['Intercept'] + (coeffsDict['entity'] * googleEntityFeature) + (coeffsDict['image'] * googleImageFeature) + (coeffsDict['googleScholar'] * googleScholarFeature) + (coeffsDict['adRatio'] * adsRatioFeature) + (coeffsDict['mime'] * nonHTMLRateFeature) + (coeffsDict['rank8P3'] * verticalPermutationFeature) + (coeffsDict['wikipedia'] * wikipediaFeature) + (coeffsDict['tld'] * comRateFeature) + (coeffsDict['maxSimilarityScore'] * maxDissimilarityFeature) + (coeffsDict['maxIntersection'] * maxOverlapFeature)
	classProbability = math.exp(classProbability) / (1 + math.exp(classProbability))

	queryClass = ''
	if( classProbability >= 0.5 ):
		queryClass = 'scholar'
	else:
		queryClass = 'non-scholar'

	return ('class: ' + queryClass + ', classProbability: ' + str(classProbability))

if( len(sys.argv) == 2 ):
	print 'Classification result for:', sys.argv[1]
	print
	print classifyQueryScholarOrNonScholar(sys.argv[1])
else:
	print 'Usage:'
	print '\t', sys.argv[0], 'query'
	print '\tE.g.', sys.argv[0], '"fluid dynamics"'

