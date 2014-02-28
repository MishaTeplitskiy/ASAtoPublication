# 
# name: clean_text_files_for_diff.py
# 
# author: misha teplitskiy
# date created: 1-28-2013
# last update: 2/14/2014
#-
# description: given a directory of text files, opens each one and does the following
#	- convert everything to lower case
#	- get rid of numbers
# 	- replaces each newline character with nothing (which makes the entire text file into 1 line).
#	- uses NLTK's sentence tokenizer to partition this one big line into sentences
#	- saves the list of sentences to a pickle
#
#
# uses: NLTK library

import os, string
from nltk.tokenize import sent_tokenize, word_tokenize
from cPickle import dump


def process_file(text):

	# pre-segmentation cleaning
	text = text.lower()
	text = ''.join([w for w in text if w.isalpha() or w in string.punctuation or w == ' ']) # get rid of all weird characters
	
	# tokenize into sentences
	sentences = sent_tokenize(text)
	sents_backup = sentences[:]
	
	# remove punctuation 
	for i in range(len(sentences)):
		sentences[i] = ''.join([l for l in sentences[i] if l not in string.punctuation])
	
# ------------ TO DO: FIGURE OUT WHERE stopwords IS -----------------------
 
	# split the sentence into words
	for i in range(len(sentences)):
          sentences[i] = word_tokenize(sentences[i])
          sentences[i] = [w for w in sentences[i] if w not in stopwords]

	# remove everything that comes after 'references'
	for i in range(len(sentences)):
		if 'references' in sentences[i] and i > len(sentences)/2:
			print 'found references!'
			sentences = sentences[:i]
			break
			
			
	# drop sentences that are less 5 "words" long
	sentences = [s for s in sentences if len(s)>4]
	
	# drop sentences that are less than 10 characters long
	sentences = [s for s in sentences if sum([len(w) for w in s]) > 9]
	
	#sentences = [[[w for w in word if w not in string.punctuation] for word in sent] for sent in sentences]  # get rid of punctuation marks	
	#sentences = [s for s in sentences if mean([len(w) for w in s])>1] # the problem with this last part is that some weird characters (e.g. less than or equals to) take several special characters to produce
	
	return sentences

#---------------------
# main
#---------

directory = 'C:/Users/DJ Ukrainium/Documents/Dropbox/Future of Knowledge/minianalysis - diff approach/corpus/socialforces/plaintext/'
files = [f for f in os.listdir(directory) if f[0].isdigit() and f.endswith('.txt')]  # use all the files that start with a number and are text files
	
for file in files:
	print file
	text = open(directory + file).read()
	sentences = process_file(text)
	fout = open(directory + 'sentences/' + file[:-4] + '_cleaned.txt', 'w')
	fout.writelines([' '.join(s) + '\n' for s in sentences])
     fout.close()
	dump(sentences, open(directory + 'sentences/' + file[:-4] + '.pickle', 'w'))
	
