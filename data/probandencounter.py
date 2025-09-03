import os
#basedir is the data directory inside the current directory
basedir = "./data"
counter  =  0
for file in os.listdir(basedir):
    if "Valididitätskontrolle" in str(file):
        #sic!
        counter = counter +1
print(counter)