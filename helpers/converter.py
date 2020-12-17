from os import listdir
from os.path import isfile, join

from .Project import Project
from .Test import Test

dir = input("Enter the project folder path:\n")
dir = os.path.abspath(dir)
# this is a list of the files int he dir
files = [f for f in listdir(dir) if isfile(join(dir, f))]
csvfiles = [f for f in files if f[:-4] == '.csv' and not 'alldata' in f]

# the previous expressions are list comprehensions
# the latter could be written as
# csvfiles = []
# for f in files:
#   if f[:-4] == '.csv':
#       if not 'alldata' in f:
#           csvfiles.append(f)

# make a new Project using the name of the dir
    # newProject = Project()
    # set the project name to the directory name
    # newProject.name.set(dir.split('/')[-1])
    # (most of the project details can be left blank for now)

# for each csv file
    # make a new Test object
    # this = Test()
    # chop off the directory 
    # csvpath = filepath.split('/')[-1] 
    # chop off the .csv part of the path
    # test.name.set(csvpath[:-4])
    # if 'blank' in csv file name
        # call Test.isBlank.set(True)
    
    # use the following schema for organizing readings
        # reading = {
        #     "elapsedMin": x.xx,
        #     "pump 1": psi1,
        #     "pump 2": psi2,
        #     "average": round((psi1 + psi2)/2)
        # }

    # put whole csv content into pandas dataframe
    # can't expect pressure cols to have always been at a certain index, need to find by name
    # look for a 'PSI 1' and 'PSI 2' col on row 0
    # not all versions of the test handler recorded an average PSI, so calculate your own
    # there is little consistency in the way timestamps have been handled
    # the scoring algo doesn't really care so just guess
    # if len(rows) >= 5399:
        # interval is 1, elapsedMin will be (1/60)*row index, rounded to 2 decimal places
    # if len(rows) >= 1799  and len(rows) <= 5399:
        # inteval is 3, elapsedMin will be (3/60)* row index, rounded to 2 decimal places
    # for each row in the csv:
        # convert into reading dict
        # see above for schema
        # then add to the Test's readings list
    
    # finally
    # newProj.tests.append(this)

# save the project