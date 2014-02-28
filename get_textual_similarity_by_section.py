# name: get_textual_similarity_by_section.py
#
# created: 1/27/2013
# updated: 2/27/2014
#
# author: misha teplitskiy
# 
# description: This program does the bulk of the analysis. Splits papers into sections/sentences/words
#              and computes similarity measures. 
# 
#----------------------------------------------- 
# approach:
#	outcome: the sentences of a given section of the ASA paper tend to be replicated with X similarity in the final paper
#	
# 0. make sure all the labels have been written correctly, etc.
#
# 1. (manually) split ASA paper into sections by labelling the beginning of each section as "[[[ __label__ ]]]"
# 2. for each section 
# 2.1. for each sentence in the section
# 2.1.1. find the similarity (Jaccard of the sets of words) of this sentence's with every sentence in same section of the published paper
# 2.1.2. take the highest of these similarities (this is the best match)
# 2.2. take the average of these jaccards for all sentences in the section
# 

import os, re, string, copy
from random import choice
from cPickle import load, dump
from nltk.tokenize import sent_tokenize, word_tokenize


def verifyLabels():
	'''
	#----------------------------------------------- Coding verification
	# * go through all the files and get the set of labels to see if there are any unexpected (bad) ones
	# 
	'''
	asrPlaintext = 'C:/Users/DJ Ukrainium/Documents/Dropbox/Future of Knowledge/corpus_latest/asr/plaintext/'
	asrFilesPlaintext = [f for f in os.listdir(asrPlaintext) if f.endswith('.txt')]  
	sfPlaintext = 'C:/Users/DJ Ukrainium/Documents/Dropbox/Future of Knowledge/corpus_latest/socialforces/plaintext/'
	sfFilesPlaintext = [f for f in os.listdir(sfPlaintext) if f.endswith('.txt')]  

	# set of labels, used for quality control to see if there are any "bad" labels
	setOfLabels = set()
	
	# get all labels from asr articles
	for file in asrFilesPlaintext:
		print file
		text = open(asrPlaintext + file).read()
		for match in re.findall(r'\[{3}.*?\]{3}', text):
			setOfLabels.add(match[4:-4])		
	
	# do all labels from social forces articles
	for file in sfFilesPlaintext:
		print file
		text = open(sfPlaintext + file).read()
		for match in re.findall(r'\[{3}.*?\]{3}', text):
			setOfLabels.add(match[4:-4])

	print setOfLabels

# the function below has been put into clean_text_files_for_diff.py
def cleanAndSplitIntoSents(text):

	# pre-segmentation cleaning
	text = text.lower()
	text = ''.join([w for w in text if w.isalpha() or w in string.punctuation or w == ' ']) # get rid of all weird (non-alphanum, non-punct) characters
	
	# tokenize into sentences
	sentences = sent_tokenize(text)
	sents_backup = sentences[:]
	
	# remove punctuation 
	for i in range(len(sentences)):
		sentences[i] = ''.join([l for l in sentences[i] if l not in string.punctuation])
	
	# split the sentence into words
	for i in range(len(sentences)):
		#sentences[i] = sentences[i].split(' ')
          sentences[i] = word_tokenize(sentences[i])
          sentences[i] = [w for w in sentences[i] if w not in stopwords]
          
          #***************
          # ^ find stopwords collection!!!
          
          
	# drop sentences that are less 5 "words" long
	sentences = [s for s in sentences if len(s)>4]
	
	# drop sentences that are less than 10 characters long
	sentences = [s for s in sentences if sum([len(w) for w in s]) > 9]
	
	#sentences = [[[w for w in word if w not in string.punctuation] for word in sent] for sent in sentences]  # get rid of punctuation marks	
	#sentences = [s for s in sentences if mean([len(w) for w in s])>1] # the problem with this last part is that some weird characters (e.g. less than or equals to) take several special characters to produce
	
	return sentences

def splitIntoSections(text):
	''' takes text of an article where I've manually inserted section titles and splits it into sections'''
	
	textBySection = {}
	
	indStart = text.find('[[[ ')
	while indStart != -1:
		sectionNameStartInd = indStart+4
		sectionNameEndInd = text.find(' ]]]', indStart)
		sectionName = text[sectionNameStartInd : sectionNameEndInd]
		indStart = text.find('[[[ ', sectionNameEndInd) # index of start of next section
		
		sectionStartInd = sectionNameEndInd + 4
		sectionEndInd = len(text) # assume the current section is the last one
		if indStart != -1: sectionEndInd = indStart # if there is actually another section to follow, change sectionEndIndex to right before this next section
	
		# if have NOT encountered this section before	
		if sectionName not in textBySection:
			textBySection[sectionName] = text[sectionStartInd : sectionEndInd]

		else:
			textBySection[sectionName] = textBySection[sectionName] + ' ' + text[sectionStartInd : sectionEndInd]
	
	return textBySection
	
'''	
for file in files:
	print file
	text = open(directory + file).read()
	sentences = process_file(text)
	fout = open(directory + 'sentences/' + file[:-4] + '_cleaned.txt', 'w')
	fout.writelines([' '.join(s) + '\n' for s in sentences]); fout.close()
	dump(sentences, open(directory + 'sentences/' + file[:-4] + '.pickle', 'w'))
'''	

def jaccardSimilarity(list1, list2):
	return float(len(set(list1).intersection(list2)))/len(set(list1).union(list2))

def getMeanJaccards(sectionsOfInterest, allJaccardsForCorpus):
	''' This section takes a dictionary of file:jaccards by section and plots the results
	'''
	meanJaccardsForCorpus = {}  # (section : mean jaccards from all files with that section)
	
	for section in sectionsOfInterest: # for each section I want to plot
		sectionMeans = []
		for file in allJaccardsForCorpus: # for each ASA paper
			if section in allJaccardsForCorpus[file]: # if the section of interest is in that paper (and it'll have to be in the published version too), use the paper in calculating the average
				sectionMeans.append( mean( allJaccardsForCorpus[file][section] )) # for the file, calculate the mean of all sentences in the section and add it to the list 
		print section, 'Number of files used in average:', len(sectionMeans)
		meanJaccardsForCorpus[section] = mean(sectionMeans)
	
	return meanJaccardsForCorpus

	
#----------------------------------------
# main
#-----------
if __name__== "__main__":	
	
	
	#---global variables ---------------
	uniqueSectionNames = ['abstract', 'introduction', 'context', 'theoretical framing', 'data and methods',
							'results', 'conclusion', 'notes', 'references', 'tables', 'appendices']			
	allJaccardsForCorpus = {} # this dict is (file name : dictionary of all jaccards by section)

	pathASRPlaintext = 'C:/Users/DJ Ukrainium/Documents/Dropbox/Future of Knowledge/corpus_latest/asr/plaintext/'
	filesASRPlaintext = [f for f in os.listdir(pathASRPlaintext) if f.endswith('pre.txt')] 

	pathSFPlaintext = 'C:/Users/DJ Ukrainium/Documents/Dropbox/Future of Knowledge/corpus_latest/socialforces/plaintext/'
	filesSFPlaintext = [f for f in os.listdir(pathSFPlaintext) if f.endswith('pre.txt')] 

	filePaths = [pathASRPlaintext, pathSFPlaintext]
	fileNames = [filesASRPlaintext, filesSFPlaintext]
	
     # the variable below determines whether I use ASR files or SF. 
	# ASR = 0, SF = 1
	asrOrSf = 0
	
	for filename in fileNames[asrOrSf]:
		print filename

		# open the file and the companion published version
		text = open(filePaths[asrOrSf] + filename).read()
		publishedText = open(filePaths[asrOrSf] + filename[:-7] + 'post.txt').read()
		
		# !!!! BASELINE !!!!!: use the following publishedText definition to match a file up with a random file in order to get the baseline measure of similarity
		#publishedText = open(filePaths[asrOrSf] + choice([f for f in fileNames[asrOrSf] if f is not file])[:-7] + 'post.txt').read()
		
  
          # --- TO DO: THE SPLITTING INTO SECTIONS/SENTENCES/WORD CAN BE DONE JUST ONCE AND PICKLED
  
		# split into sections. output of function splitIntoSections is a dict (section name : text in that section)
		textBySection = splitIntoSections(text)
		publishedTextBySection = splitIntoSections(publishedText)
				
		# product dictionary with (section name : sentences (as lists of words) in that section)
		sentsBySection = {}
		publishedSentsBySection = {}
		for sect in textBySection:
			sentsBySection[sect] = cleanAndSplitIntoSents(textBySection[sect])
		for sect in publishedTextBySection:
			publishedSentsBySection[sect] = cleanAndSplitIntoSents(publishedTextBySection[sect])
				
		# for given section, calculate best matches for each sentence (highest jaccard)
		allJaccardsForSection = {}
		for sect in sentsBySection: # for each section
			
			# this approach only looks for matches in the corresponding section (not the entire published article)!!!
			# if sect is not in both versions, this section is not added to allJaccardsForSection[section].. so that dict contains
			# only sections that exist in both versions
			if sect in publishedSentsBySection: # if the published version has this section too, then
			
				allJaccardsForSection[sect] = [] # start with an empty list

				for asaSent in sentsBySection[sect]: # for each sentence in the ASA section	
					# calculate all jaccards and take the highest one
					tempJaccards = [jaccardSimilarity(asaSent, publishedSent) for publishedSent in publishedSentsBySection[sect]]
					allJaccardsForSection[sect].append( max(tempJaccards) )
				
		
		allJaccardsForCorpus[filename] = copy.deepcopy(allJaccardsForSection) # do I need to make a deep copy here, because allJaccardsForSection gets redefined later?
	
	
	# ----- ANALYZE and PLOT JACCARDS ------------------------------
	sectionsOfInterest = ['abstract', 'introduction', 'theoretical framing', 'data and methods', 'results', 'conclusion']
	meanJaccards = getMeanJaccards(sectionsOfInterest, allJaccardsForCorpus)  # this is a dict of (section : mean jaccard)
	
	#fig = plt.figure(figsize=(10,10))
	xticks(xrange(len(sectionsOfInterest)), sectionsOfInterest, rotation='vertical')
	orderedMeans = [meanJaccards[sect] for sect in sectionsOfInterest]
	plot(orderedMeans, 'b-', linewidth=3, label='Observed similarity')
	#plot(orderedMeans, 'r--', linewidth=3, label='Baseline similarity')
	fig.subplots_adjust(bottom=0.3)
	title('Similarity of text by section: ASR')
	ylabel('Jaccard similarity of sentences in section')
	legend()
	show()			
			
			
	# 2/6/2013 -- the effects are smaller than before and i don't know why

		
	'''
	if max(jaccards) > 0.7:
		print sent
		print tosents[jaccards.index(max(jaccards))]
	'''
		
		
		
		
	'''
	fromsents = load(open(path + file))
	tosents = load(open(path + file[:-10] + 'post.pickle'))

	sequences = zeros((len(files), 10))

	jaccards_seq = []	
	for sent in fromsents: # for each sentence in the original file that is at least 5 words long
		
		# find best match (max jaccard)
		jaccards = []
		for tosent in tosents:
			jaccard = float(len(set(sent).intersection(tosent))) / len(set(sent).union(tosent))
			jaccards.append(jaccard)
		jaccards_seq.append( max(jaccards) )

		
		if max(jaccards) > 0.5:
			print sent
			print tosents[jaccards.index(max(jaccards))]
		
	'''


	'''
	seqlen = len(jaccards_seq)
	for i in range(10):
		sequences[index][i] = mean( jaccards_seq[ seqlen/10*i : seqlen/10*(i+1) ]  )
	'''
