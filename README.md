This is a UIC domain specific search engine. 
For web crawling it uses a scrapy spider and for the UI and PageRank implementation Flask framework was used in Python. 

Required Libraries:
scrapy
Flask
os
string
re
math
collections
pandas
nltk
bs4
pandas
numpy

Steps to run:
create a pages folder in the project directory and feed it's value 
a. 'filepath' variable in the 'toscrape.py' script
b. 'file_path_docs' variable in the 'Test.py' script
## Also give an appropiate path to the urlpath variable in the 'toscrape.py' script
## And pass the same path value to 'file_path_urls' variable in 'Test.py' script
In cmd:
1. Run the spider file in the crawler/spiders path of your project using the following command
	scrapy crawl toscrape
Now the 3000 pages crawled by the spider will be in the pages folder.(it stops after crawling 3000 pages) 
2. Run the 'Test.py' file:
	python Test.py
The Flask server will be running on your localhost now.
3. Open the 'http://127.0.0.1/search' on your web browser. (It may take some time to load.)
4. Enter your search query.
5. Click on the submit button.
6. Click on any results to view the page.
