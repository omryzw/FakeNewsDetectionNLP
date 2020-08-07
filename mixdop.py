# this module checks if the article already exists
import math
import string
import pymysql
import re
from datetime import date
import random

mydb = pymysql.connect(
    host="35.224.191.214",
    user="omrizw",
    password="omoomo97",
    database="edith"
)

mycursor = mydb.cursor(pymysql.cursors.DictCursor)
# translation table is a global variable
# mapping upper case to lower case and
# punctuation to spaces
translation_table = str.maketrans(string.punctuation + string.ascii_uppercase,
                                  " " * len(string.punctuation) + string.ascii_lowercase)

# returns a list of the words


def get_words_from_line_list(text):
    text = text.translate(translation_table)
    word_list = text.split()
    return word_list
# counts frequency of each word
# returns a dictionary which maps
# the words to their frequency.


def count_frequency(word_list):
    D = {}
    for new_word in word_list:
        if new_word in D:
            D[new_word] = D[new_word] + 1
        else:
            D[new_word] = 1
    return D

# returns dictionary of (word, frequency)
# pairs from the previous dictionary.


def word_frequencies_for_file(filename):
    # line_list = read_file(filename)
    line_list = filename
    word_list = get_words_from_line_list(line_list)
    freq_mapping = count_frequency(word_list)
    return freq_mapping

# returns the dot product of two documents


def dotProduct(D1, D2):
    Sum = 0.0
    for key in D1:
        if key in D2:
            Sum += (D1[key] * D2[key])
    return Sum


def vector_angle(D1, D2):
    numerator = dotProduct(D1, D2)
    denominator = math.sqrt(dotProduct(D1, D1) * dotProduct(D2, D2))
    return math.acos(numerator / denominator)


def documentSimilarity(filename_1, filename_2):
    sorted_word_list_1 = word_frequencies_for_file(filename_1)
    sorted_word_list_2 = word_frequencies_for_file(filename_2)
    distance = vector_angle(sorted_word_list_1, sorted_word_list_2)
    return distance
    # print("The distance between the documents is: % 0.2f " % distance)


def checkDocSimilarity(qdoc):
    mycursor.execute("SELECT * FROM articles")
    myresult = mycursor.fetchall()
    minscore = documentSimilarity(qdoc, myresult[0]['article'])
    minID = myresult[0]['sourceid']
    articleid = myresult[0]['articleid']
    i = 0
    while i < len(myresult):
        #     # check if the text exists partially
        if myresult[i]['article'].find(qdoc) != -1:
            minID = 0
            minscore = 1000
            minID = myresult[i]['sourceid']
            articleid = myresult[i]['articleid']
        else:
            distance = documentSimilarity(qdoc, myresult[i]['article'])
            if distance < minscore:
                minscore = distance
                minID = myresult[i]['sourceid']
                articleid = myresult[i]['articleid']
        i += 1
    return finalizeSimilarity(qdoc, minscore, minID, articleid)


def checkDocSimilarity(qdoc):
    mycursor.execute("SELECT * FROM articles")
    myresult = mycursor.fetchall()
    minscore = documentSimilarity(qdoc, myresult[0]['article'])
    minID = myresult[0]['sourceid']
    articleid = myresult[0]['articleid']
    i = 0
    while i < len(myresult):
        #     # check if the text exists partially
        if myresult[i]['article'].find(qdoc) != -1:
            minscore = 1000
            minID = myresult[i]['sourceid']
            articleid = myresult[i]['articleid']
            break
        else:
            distance = documentSimilarity(qdoc, myresult[i]['article'])
            if distance < minscore:
                minscore = distance
                minID = myresult[i]['sourceid']
                articleid = myresult[i]['articleid']
        i += 1
    return finalizeSimilarity(qdoc, minscore, minID, articleid)



def finalizeSimilarity(qdoc, minscore, minID, articleid):
    # if min score is 1000 then it partially exists at minid
    # if less than 0.8 return full article with label
    if((minscore < 0.8) or (minscore == 1000)):
        # article already exist so send back full article and label
        sql = "SELECT article,atype FROM articles WHERE articleid = %s"
        query = (articleid,)
        mycursor.execute(sql, query)
        myresult = mycursor.fetchall()
        mydb.commit()
        final = []
        for x in myresult:
            final.append(x['article'])
            final.append(x['atype'])
        return formatforMessage('similar', final)
    else:
        return scanforLinks(qdoc)


def normalizeRate(score):
    OldMax = 100
    OldMin = 0
    NewMax = 5
    NewMin = 0
    OldValue = score

    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return math.floor(NewValue)


# print(math.floor(NewValue))

def scanforLinks(article):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, article)
    links = [x[0] for x in url]

    if len(links) != 0:
        # get score
        sql = "SELECT score,sourceid FROM sources WHERE source = %s"
        query = (links[0],)
        mycursor.execute(sql, query)
        myresult = mycursor.fetchall()
        if mycursor.rowcount != 0:
            # meaning that the link exists in the database
            final = []
            for x in myresult:
                final.append(x['score'])
                final.append(x['sourceid'])
            # send score & article to NLP
            mydb.commit()
            return nlpCheck(final[0], final[1], article)
        else:
            # link exists but not in database so it is an unknown source
            return scanforMediaMention(article)

    elif len(links) == 0:
        # if no links scan for media mention else return score
        return scanforMediaMention(article)


def scanforMediaMention(article):
    # compare authors from database to aricle
    sql = "SELECT score,source FROM sources WHERE stype = 0"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mydb.commit()
    final = []
    for row in myresult:
        if row['source'] in article:
            final.append(row['score'])
            final.append(row['source']) 
        else:
            pass
    if (len(final) != 0):
        # author exists
        return nlpCheck(final[0], final[1], article)
    else:
        # unknown are given a rating of 40%
        return nlpCheck(0.4, 'aaa222', article)


def finalscore(article,sscore, nscore, source):
    # get weights from file
    finalscore = math.floor(((sscore*75) + nscore))
    nomScore = normalizeRate(finalscore)
    if (addRate(source, nomScore) == 1):
        adjustSourceScore(source, finalscore)
    final = []
    final.append(finalscore)

    if finalscore >=79:
        addToExistingDataSet(source,article,1)
    else:
        addToExistingDataSet(source, article, 0)
    return formatforMessage('nlp', final)


def addRate(source, nomScore):
    sql = "INSERT INTO rates(source,score) VALUES (%s,%s)"
    query = (source, nomScore)
    mycursor.execute(sql, query)
    mydb.commit()
    return 1


def adjustSourceScore(source, finalscore):
    f1 = 0
    f2 = 0
    f3 = 0
    f4 = 0
    f5 = 0
    sql = "SELECT score FROM rates WHERE source = %s"
    query = (source,)
    mycursor.execute(sql, query)
    if mycursor.rowcount > 100:
        myresult = mycursor.fetchall()
        mydb.commit()
        for x in myresult:
            if x['score'] == 1:
                f1 = f1 + 1
            elif x['score'] == 2:
                f2 = f2 + 1
            elif x['score'] == 3:
                f3 = f3 + 1
            elif x['score'] == 4:
                f4 = f4 + 1
            elif x['score'] == 5:
                f5 = f5 + 1

        ftotal = f1 + f2 + f3 + f4 + f5

        sum_score = (f1*1) + (f2*2) + (f3*3) + (f4*4) + (f5*5)

        new_score = sum_score/ftotal

        normalizedScore = normalizeUpdatedScore(new_score)

        sql2 = "UPDATE sources SET score = %s WHERE source = %s"
        query2 = (normalizedScore, source,)
        mycursor.execute(sql2, query2)
        mydb.commit()
        return 1
    else:
        return 0


def normalizeUpdatedScore(score):
    OldMax = 5
    OldMin = 0
    NewMax = 1
    NewMin = 0
    OldValue = score
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue


def formatforMessage(mtype, result):
    #mtype tells us how the array is arranged and where it is coming from
    status = ''
    if mtype == 'similar':
        if result[1] == 0:
            status = 'Fake'
        elif result[1] == 1:
            status = 'Real'
        message = 'This article matches an article has been already been classified as ' + status + ' News Please view the full article here : ' + str(result[0])
    elif mtype == 'nlp':
        if(result[0] >= 80):
            message = 'This article has been classified as ' + str(result[0]) + ' percent Real news. This means the article came from a trustworthy source.'
        elif(result[0] <= 79 and result[0] >= 70):
            message = 'This article has been classified at ' + str(result[0]) + ' percent. This means the article might contain bits of false information, please take caution when sharing such articles.'
        elif(result[0] <= 69):
            message = 'This article has been classified as Fake News! at ' + str(result[0]) + ' percent.Please do not further share this article'
    else:
        message = 'We have encounterd an error'
    return message


def nlpCheck(sscore, source, article):
    nscore = 24.4
    return finalscore(article,sscore, nscore, source)

def addToExistingDataSet(source,article,atype):
    # generate random article id 
    N = 6
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    articleid = str(res)
    #get date
    today = str(date.today())
    #default username is customer
    uname = 'customer'
    sql = "INSERT INTO articles (articleid,article,atype,adate,sourceid,uname) VALUES(%s,%s,%s,%s,%s,%s)"
    query = (articleid,article,atype,today,source,uname,)
    mycursor.execute(sql, query)
    mydb.commit()
    return 1
