# Wiki-Search-Engine
As a part of Information Retrieval and Extraction Course, I built a scalable search engine for searching Wikipedia XML dump. The search engine is designed to be scalable and retrieve search results for long words in a few seconds
Index.py makes the inverted index. Merge.py merges the indices , which is then accessed by search.py for querying.

## Phase-1 
* environment.yml - Python environment file
* index.py - Makes the index
* index.sh - Bash script to run the index
* search.py - Search engine
* search.sh - Bash script to run the index
* shortest.xml - An example XML file
* stopwords.pkl - Stopwords file (nltk)

## Final phase of the project (Uses code from Phase-1)
* index.py - Builds the index
* mergeIndices - Merges all index files into a single file
* search.py - Searches in an infinite loop, waiting for queries
