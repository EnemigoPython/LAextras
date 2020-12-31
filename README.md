# LAextras
Takes the list of top comedy shows from IMDB and creates a data set from the actors. (from the top 150 titles)

# ORIGIN
I like to watch sit-coms on Netflix and I notice a lot of similar faces in different sitcoms, from main cast and also background characters/extras. I thought it would be fun and interesting to make a program that automatically gathers the actors from the top comedy shows on Netflix and compares their overlapping roles.

# REQUIREMENTS
-Python 3(.6+)
-Selenium
-Computer space

# USE
The Selenium driver and PATH needs to be configured to your computer. The program creates three files: a text file to keep track of which titles have already been added to the data set, a text file of titles which are from outside of the US and thus excluded from the search, and a CSV file (which can be imported into Excel).

# EXPANSION
The program currently generates a long list and doesn't exclude anyone credited on the IMDB page of each title. Perhaps this could be specified further for, say, only main cast actors or actors that appear in more than one episode. It also currently takes a long time to run to completion and the resulting file will be extremely large. I'm sure some optimisations could be made in this regard.
