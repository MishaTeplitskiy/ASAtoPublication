# name: convert_pdfs_to_plaintext.py
#
# created: 1/27/2012
# author: misha teplitskiy
# 
# description: given a directory, converts all the .pdf files that start with a number in that directory to text files and puts them in
#				the /plaintext/ folder.
#
# uses: PDFminer library
#

import os
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

def convert_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = open(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    return str
	
directory = 'C:/Users/DJ Ukrainium/Documents/Dropbox/Future of Knowledge/minianalysis - diff approach/corpus/socialforces/'
files = [f for f in os.listdir(directory) if f[0].isdigit()]

for file in files:
	print file
	#os.system('pdf2txt.py -o plaintext/%s.txt -t text %s' % (dir + file[:-4], dir + file))
	output = convert_pdf(directory + file)
	open(directory + '/plaintext/' + file[:-4] + '.txt', 'w').write(output)
	
	