#THIS SCRIPT BASICALLY UPLOADS THE SYLLABUS IN MONGO DB


import pymongo
import csv
import random



def getNonLinear(wm,h):
    H = h
    hard_week = [0]*wm
    
    end = wm
    total = 0
    while h > 0:
        if(h%2!=0 and h!=1):
            h += 1
        h = round(h/2)

        if h==1:
            break;
        
        if(end==0):
            break
        que = round(h/end)
        if(que== 0):
            que=1
        for x in range(0,end):
            hard_week[x] += que
            if(sum(hard_week) == H ):
                break
        end = round(end/2)
        if(sum(hard_week) == H ):
            break
           
        total += h

    while sum(hard_week) < H:
        for x in range(wm):
            if sum(hard_week) > H:
                break
            hard_week[x] += 1
    if(sum(hard_week) > H):
        hard_week[wm-1] -= 1
    else:
        hard_week[0] +=1

    print("total weeks: ", wm)
    print("total topics: ",H)
    print("distributed topics: ", sum(hard_week))
    return hard_week




client = pymongo.MongoClient("mongodb://aniket:Aniketsprx077@cluster0-shard-00-00-uugt8.mongodb.net:27017,cluster0-shard-00-01-uugt8.mongodb.net:27017,cluster0-shard-00-02-uugt8.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.main


def sendCsvToMongo(filename):
    data = []
    csv_file = open(filename, mode='r')
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        row[2] = random.choice(['h','m','e'])
        row[0] += row[2]
        data.append(row)
    csv_file.close()


    subjects = []
    document = {}
    for rec in data:
        subject = rec[0][3:5]
        if subject not in subjects:
            subjects.append(subject)
            document[subject] = []
        

    print(subjects)


    for rec in data:
        subject = rec[0][3:5]
        document[subject].append(rec)

    syllabus = db['syllabus']
    x = syllabus.insert_one({ "GME" : document })
    print(x)

#sendCsvToMongo('./syllabus/gateme.csv')


