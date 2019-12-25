import sys
import pickle
from datetime import datetime
import re
import os

MIN_STOP_LENGTH = 2

from nltk import stem
stemmer = stem.PorterStemmer() 
with open('stopwords.pkl','rb') as f:
    stop_words = pickle.load(f)
    
def remove_stopwords(content):
    cleaned_data = []
    for ele in content:
        if len(ele) <= MIN_STOP_LENGTH:
            continue
        elif ele not in stop_words:
            cleaned_data.append(stemmer.stem(ele))
    return cleaned_data

def read_file(query_file):
    '''Read query_file and return a list of queries'''
    with open(query_file, 'r') as file:
        queries = file.readlines()
    return queries

def write_file(outputs, output_file):
    '''outputs should be a list of lists.
        len(outputs) = number of queries
        Each element in outputs should be a list of titles corresponding to a particular query.'''
    with open(output_file, 'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')

def str_to_dict(query):
    dict_ = {}
    query_list = query.split('|')[:-1]
    for ele in query_list:
        splite = ele.split('-', 1)
        dict_[int(splite[0])] = splite[1]
    return dict_

def getfieldPieces(query):
    pieces = []
    query = query.strip()#Remove /n
    while ':' in query:
        query_str = query.rsplit(':',1)[1] #Query str has 
        query = query.rsplit(':',1)[0]
        if ' ' not in query: #Reached the last word 
            loc = query
            query = ''
        else:
            loc = query.rsplit(' ',1)[1]
            query = query.rsplit(' ',1)[0]
        pieces.append([loc.strip(), query_str.strip()])
    return pieces

def NormalSearch(query,data,titlemap):
    query = query.strip()
    splitted_words = query.lower().split(' ')
    splitted_words = remove_stopwords(splitted_words)
    flag = False
    output = []
    main_strim = {}
    for ele in splitted_words:
        if data[ele] != '': #Check if data has some files
            strim = str_to_dict(data[ele])
            if flag ==  False: #First query
                flag = True
                main_strim = strim.keys()
                if len(main_strim) == 0:
                    flag = False #Havent found a nonzero init array yet
            else:
                temp = main_strim & strim.keys()
                if len(temp) == 0:
                    continue #No intersections
                else:
                    main_strim = temp
    for ele in main_strim:
        output.append(titlemap[ele])
    if(len(output)) > 10:
        output = output[:10]
    return output #All the valid files

field_map = {'title':'t',
             'body':'b',
             'infobox':'i',
             'ref':'r',
             'category':'c',
             'external':'x'
            }

def str_to_dict_with_field(query, letter):
    dict_ = {}
    query_list = query.split('|')[:-1]
    for ele in query_list:
        if letter in ele:
            splite = ele.split('-', 1)
            dict_[int(splite[0])] = splite[1]
    return dict_
    
def FieldSearch(queryList,data,titlemap):
    lofields = getfieldPieces(queryList)
    main_strim = {}
    output = []
    flag = False
    for ele in lofields:
        field_char = field_map[ele[0]]
        query = ele[1]
        splitted_words = query.lower().split(' ')
        splitted_words = remove_stopwords(splitted_words)
        for jele in splitted_words:
            if data[jele] != '': #Check if data has some files
                strim = str_to_dict_with_field(data[jele],field_char)
                if flag ==  False: #First query
                    flag = True
                    main_strim = strim.keys()
                    if len(main_strim) == 0:
                        flag = False #Havent found a nonzero init array yet
                else:
                    temp = main_strim & strim.keys()
                    if len(temp) == 0:
                        continue #No intersections
                    else:
                        main_strim = temp
    for ele in main_strim:
        output.append(titlemap[ele])
    if(len(output)) > 10:
        output = output[:10]
    return output #All the valid files

def search(path_to_index_folder, queries,data,titlemap):
    output = []
    for query in queries:
        if ':' in query:
            output.append(FieldSearch(query,data,titlemap))
        else:
            output.append(NormalSearch(query,data,titlemap))
    return output

def main():
    path_to_index_folder = sys.argv[1]
    query_file = sys.argv[2]
    output_file = sys.argv[3]
    path = os.path.join(path_to_index_folder,'dump.pkl') 
    with open(path,'rb') as f:
        data = pickle.load(f)
        titlemap = pickle.load(f)
    queries = read_file(query_file)
    outputs = search(path, queries, data, titlemap)
    write_file(outputs, output_file)


if __name__ == '__main__':
    main()
