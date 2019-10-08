import sys

import xml
from nltk.corpus import stopwords
from datetime import datetime
import os
import pickle
import xml.sax as sax
import re
from nltk import stem
from collections import Counter
from collections import defaultdict

LEN_INFOBOX  = len('{{infobox')
LEN_CATEGORY = len('[[category:')
LEN_EXTERNS  = len('==external links==')

TAG_RE = re.compile(r'<[^>]+>')
infoBoxRegex = re.compile(r'(\{\{infobox(.|\n)*?\}\}\n)(?:[^\|])') 
categoryRegex = re.compile(r'\[\[category:.*\]\]\n')
externalsRegex = re.compile(r'==external links==\n(.|\n)*?\n\n')
reftagRegex =  re.compile(r'<ref(.|\n)*?</ref>')
refsRegex = re.compile(r'(==references==(.|\n)*?\n)(==|\{\{DEFAULTSORT)')
stemmer = stem.PorterStemmer() 
MIN_STOP_LENGTH = 2
punctuation='!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
remove_punctuation_map = dict((ord(char), 32) for char in punctuation)
EACH_FILE_HAS = 1000
stemmer_dict = {}

with open('stopwords.pkl','rb') as f:
    stop_words = pickle.load(f)
def remove_tags(text):
    return TAG_RE.sub('', text)
def word_tokenize(text):
    return text.split()

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
        if word in stemmer_dict:
            stems.append(stemmer_dict[word])
        else:
            new_stem = stemmer.stem(word)
            stemmer_dict[word] = new_stem
            stems.append(new_stem)
    return stems
        
import xml.sax as sax
class WikiHandler(sax.ContentHandler):
    def __init__(self):
        self.inTitle = False
        self.inText = False
        self.inId = False
        self.title = ""
        self.id = ""
        self.count = 0
        self.text = ""
        self.ids = []
        self.fileId = 0
        self.file_counter = EACH_FILE_HAS
        self.isIndexed = 0
        self.encounteredId = False
        self.miniIndex = defaultdict(str)
        self.indexmap = defaultdict(str)
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
            self.content = self.text.lower()
            self.count +=1 
            self.splitTextContent()
            self.id = ""
            self.title = ""
            self.text = ""

    def characters(self, content):
        if self.inId:
            self.id += content
        if self.inTitle:
            self.title += content
        if self.inText:
            self.text += content
            
    def splitTextContent(self):
        title = self.title
        origcontent = self.content
        Words1 = []
        Words2 = []
        Words3 = []
        Words4 = []
        minpos = len(origcontent)
        pos = origcontent.find('{{infobox')
        if pos != -1:
#             self.isIndexed+=1
            content = origcontent[pos:]
            match = infoBoxRegex.search(content)
            if match is not None: #Found some content
                Text = match.group(1)
                Words1 = Text.replace('|','') 
                Words1 = remove_tags(Words1[LEN_INFOBOX:-2])
                Words1 = word_tokenize(Words1.translate(remove_punctuation_map)) #TOKENIZATION
                Words1 = remove_stopwords(Words1) #STOPWORDREMOVAL
                Words1 = stem_data(Words1)
        #---------------------------
        pos = origcontent.find('[[category')
        if pos != -1:
            minpos = min(minpos,pos)
            content = origcontent[pos:]
            match = categoryRegex.findall(content)
            Words2 = []
            if match: #Found some content
                for singleCategory in match:
                    output = singleCategory
                    output = remove_tags(output[LEN_CATEGORY:-2])
                    output = word_tokenize(output.translate(remove_punctuation_map)) #TOKENIZATION
                    output = remove_stopwords(output) #STOPWORDREMOVAL
                    output = stem_data(output)
                    Words2 += output
                    Text = match
            #---------------------------
        pos = origcontent.find('==external')
        if pos != -1:
            minpos = min(minpos,pos)
            content = origcontent[pos:]
            match = externalsRegex.search(content)
            if match:
                content = origcontent[pos:]
                Text = match.group()
                Words3 = Text
                Words3 = word_tokenize(Words3[LEN_EXTERNS:].translate(remove_punctuation_map)) #TOKENIZATION
                Words3 = remove_stopwords(Words3) #STOPWORDREMOVAL
                Words3 = stem_data(Words3)
            #---------------------------
        pos = origcontent.find('==references==')
        if pos != -1:
            minpos = min(minpos,pos)
            content = origcontent[pos:]
            match = refsRegex.search(content)
            if match:
                minpos = min(minpos,pos)
                Text = match.group(1)
                Words4 = Text 
                Words4 = word_tokenize(Words4.translate(remove_punctuation_map)) #TOKENIZATION
                Words4 = remove_stopwords(Words4) #STOPWORDREMOVAL
                Words4 = stem_data(Words4)
            #---------------------------
        if title is not None: #Found some content
            titleWords = word_tokenize(title.translate(remove_punctuation_map)) #TOKENIZATION
            titleWords = stem_data(titleWords)        
        else:
            titleWords = []
            #---------------------------
        content = origcontent[:minpos]
        if content:
            content = re.sub(reftagRegex,'',content)
            content = word_tokenize(content.translate(remove_punctuation_map)) #TOKENIZATION
            content = remove_stopwords(content) #STOPWORDREMOVAL
            content = stem_data(content)
        else:
            content = []
        
        cnt_info = Counter(Words1)
        cnt_cat  = Counter(Words2)
        cnt_ext  = Counter(Words3)
        cnt_ref  = Counter(Words4)
        cnt_title  = Counter(titleWords)
        cnt_main = Counter(content)
        all_tokens = set(cnt_main.keys())
        all_tokens = all_tokens.union(cnt_info.keys(),cnt_cat.keys(), cnt_ext.keys(), cnt_ref.keys() , cnt_title.keys() , cnt_main.keys())
        all_tokens_arr = list(all_tokens)
        all_tokens_arr.sort()
        for word in all_tokens_arr:
            string = ""
            string += str(self.count)
            if word in cnt_main:
                string+= '-b'+str(cnt_main.get(word))
            if word in cnt_title:
                string+= '-t'+str(cnt_title.get(word))
            if word in cnt_info:
                string+= '-i'+str(cnt_info.get(word))
            if word in cnt_ref:
                string+= '-r'+str(cnt_ref.get(word))
            if word in cnt_ext:
                string+= '-x'+str(cnt_ext.get(word))
            if word in cnt_cat:
                string+= '-c'+str(cnt_cat.get(word))
            string+='|' #EOF  of info for this word, for this file
            self.miniIndex[word] +=string
        self.indexmap[self.count] = self.title

def main():
    path_to_data_dump = sys.argv[1]
    path_to_index_folder = sys.argv[2]
    parser = xml.sax.make_parser()
    handler = WikiHandler()
    parser.setContentHandler(handler)
    parser.parse(path_to_data_dump)
    path = os.path.join(path_to_index_folder, 'dump.pkl')
    with open(path,"wb") as f:
        pickle.dump(handler.miniIndex,f)
        pickle.dump(handler.indexmap,f)

if __name__ == '__main__':
    main()
