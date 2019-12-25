import xml
from nltk.corpus import stopwords

# Text Parsing and Splitting
import re
from nltk.tokenize import word_tokenize
from nltk import stem
from collections import Counter

LEN_INFOBOX  = len('{{Infobox')
LEN_CATEGORY = len('[[Category:')
LEN_EXTERNS  = len('==External Links==')
TAG_RE = re.compile(r'<[^>]+>')
infoBoxRegex = re.compile(r'(\{\{Infobox(.|\n)*?\}\}\n)(?:[^\|])') 
categoryRegex = re.compile(r'\[\[Category:.*\]\]\n')
externalsRegex = re.compile(r'==External [Ll]inks==\n(.|\n)*?\n\n')
refsRegex = re.compile(r'(==References==(.|\n)*?\n)(==|\{\{DEFAULTSORT)')
reftagRegex =  re.compile(r'<ref(.|\n)*?</ref>')
stop_words = set(stopwords.words('english')) 
stemmer = stem.PorterStemmer()
MIN_STOP_LENGTH = 2

def remove_tags(text):
    return TAG_RE.sub('', text)

def remove_stopwords(content):
    cleaned_data = []
    for ele in content:
        if len(ele) <= MIN_STOP_LENGTH:
            continue
        elif ele not in stop_words:
            cleaned_data.append(ele)
    return cleaned_data

def stem_data(content):
    stems = []
    for word in content:
        stems.append(stemmer.stem(word))
    return stems

def getInfoBoxContent(content):
    match = infoBoxRegex.search(content)
    if match is not None: #Found some content
        infoContent = match.group(1)
        output  = infoContent.lower().replace('|','') 
        output = remove_tags(output[LEN_INFOBOX:-2])
        output = word_tokenize(output) #TOKENIZATION
        output = remove_stopwords(output) #STOPWORDREMOVAL
        output = stem_data(output)
        return infoContent, output
    else:
        return -1, -1

def getCategoryContent(content):
    match = categoryRegex.findall(content)
    content_array = []
    if match: #Found some content
        for singleCategory in match:
            output = singleCategory.lower()
            output = remove_tags(output[LEN_CATEGORY:-2])
            output = word_tokenize(output) #TOKENIZATION
            output = remove_stopwords(output) #STOPWORDREMOVAL
            output = stem_data(output)
            content_array += output
        return match, content_array
    else:
            return -1, -1

def getExternalsContent(content):
    match = externalsRegex.search(content)
    if match:
        externContent = match.group()
        output = externContent.lower()
        output = word_tokenize(output[LEN_EXTERNS:]) #TOKENIZATION
        output = remove_stopwords(output) #STOPWORDREMOVAL
        output = stem_data(output)
        return externContent, output
    else:
        return -1, -1
    
def getRefsContent(content):
    match = refsRegex.search(content)
    if match:
        refsContent = match.group(1)
        output = refsContent.lower()
        output = word_tokenize(output) #TOKENIZATION
        output = remove_stopwords(output) #STOPWORDREMOVAL
        output = stem_data(output)
        return refsContent, output
    else:
        return -1, -1
        
def getTitleContent(content):
    if content is not None: #Found some content
        output = word_tokenize(content) #TOKENIZATION
        output = stem_data(output)        
        return output
    else:
        return -1 , -1

def getMainContent(content):
    if content:
        content = re.sub(reftagRegex,'',content)
        content = content.lower()
        content = word_tokenize(content) #TOKENIZATION
        content = remove_stopwords(content) #STOPWORDREMOVAL
        content = stem_data(content)
        return content
    else:
        return -1
        

def splitTextContent(title , content):
    infoBoxText, infoWords = getInfoBoxContent(content)
    categoryText, categoryWords = getCategoryContent(content)
    externalsText, externalWords = getExternalsContent(content)
    refsText, refsWords = getRefsContent(content)
    titleWords = getTitleContent(title)
    if infoBoxText != -1:
        content = content.replace(infoBoxText,'')
    if categoryText!= -1:
        for singleCategory in categoryText:
            content = content.replace(singleCategory,'')
    if externalsText!= -1:
            content = content.replace(externalsText,'')
    if refsText!= -1:
            content = content.replace(refsText,'') 
    mainWords =  getMainContent(content)
    return infoWords, categoryWords, externalWords, refsWords, titleWords, mainWords

def getSinglePageIndex(infoWords, categoryWords, externalWords, refsWords, titleWords, mainWords):
    invertedPageIndex = {}
    cnt_info = Counter(infoWords)
    return invertedPageIndex

file_name = 'enwiki-latest-pages-articles26.xml-p42567204p42663461'

import xml.sax as sax
class WikiHandler(sax.ContentHandler):
    def __init__(self):
        self.inTitle = False
        self.inText = False
        self.inId = False
        self.title = ""
        self.id = ""
        self.text = ""
        self.encounteredId = False
        
    def startElement(self, name, attrs):
        if name == 'id' and self.encounteredId == False: 
            self.inId = True
            self.id = ""
        if name == 'title': 
            self.inTitle = True
            self.title = ""
        if name == 'text': 
            self.inText = True
            self.text = ""
            
    def endElement(self, name):
        if name == 'id' and self.encounteredId == False: 
            self.inId = False
            self.id = int(self.id)
            self.encounteredId = True
        if name == 'title': 
            self.inTitle = False
        if name == 'text': 
            self.inText = False
        if name == 'page':
            self.encounteredId = False #After page is done, encountered id, can be removed 
            self.id = int(self.id)
            i,c,e, r,t,m = splitTextContent(self.title, self.text)
            getSinglePageIndex(i,c,e,r,t,m)

    def characters(self, content):
        if self.inId:
            self.id += content
        if self.inTitle:
            self.title += content
        if self.inText:
            self.text += content

parser = xml.sax.make_parser()
handler = WikiHandler()
parser.setContentHandler(handler)
parser.parse('shortest.xml')
