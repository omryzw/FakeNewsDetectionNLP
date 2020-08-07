import itertools
import pandas as pd
import numpy as np
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import pickle

# Import dataset
df = pd.read_csv('data_set/training.csv')


# Isolate the labels / changes are not persistent :)
# df.loc[(df['label'] == 1), ['label']] = 'FAKE'
# df.loc[(df['label'] == 0), ['label']] = 'REAL'

labels = df.label
labels.head()

# Split the dataset
x_train, x_test, y_train, y_test = train_test_split(df['text'].values.astype('str'), labels, test_size=0.2, random_state= 7)
# Initialize a TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)

# Fit & transform train set, transform test set

tfidf_train = tfidf_vectorizer.fit_transform(x_train)


# query text
txt2 = ["We Didnt Even See Comeys Letter Until Jason Chaffetz Tweeted ItDarrell LucusHouse Dem Aide We Didnt Even See Comeys Letter Until Jason Chaffetz Tweeted It By Darrell Lucus on October 30 2016 Subscribe Jason Chaffetz on the stump in American Fork Utah  image courtesy Michael Jolley available under a Creative CommonsBY license With apologies to Keith Olbermann there is no doubt who the Worst Person in The World is this weekFBI Director James Comey But according to a House Democratic aide it looks like we also know who the secondworst person is as well It turns out that when Comey sent his nowinfamous letter"]
txt = ['House Dem Aide: We Didn’t Even See Comey’s Letter'
           ' Until Jason Chaffetz Tweeted It,Darrell Lucus,"House Dem Aide: We Didn’t Even '
           'See Comey’s Letter Until Jason Chaffetz Tweeted It By Darrell Lucus on October '
           '30, 2016 Subscribe Jason Chaffetz on the stump in American Fork, Utah  '
           'image courtesy Michael Jolley, available under a Creative Commons-BY license With '
           'apologies to Keith Olbermann, there is no doubt who the Worst Person in The World'
           ' is this week–FBI Director James Comey. But according to a House Democratic aide, '
           'it looks like we also know who the second-worst person is as well. It turns out that when Comey sent '
           'his now-infamous letter announcing that the FBI was looking'
           ' into emails that may be related to Hillary Clinton’s '
           'email server, the ranking Democrats on the relevant committees didn’t hear '
           'about it from Comey. They found out via a tweet from one of the Republican committee '
           'chairmen. As we now know, Comey notified the Republican chairmen and Democratic ranking '
           'members of the House Intelligence, Judiciary, and Oversight committees that his agency was reviewing '
           'emails it had recently discovered in order to see if they contained classified information. Not long '
           'after this letter went out, Oversight Committee Chairman Jason Chaffetz set the political world '
           'ablaze with this tweet. FBI Dir just informed me, ""The FBI has learned of the existence of emails '
           'that appear to be pertinent ']


tfidf_test = tfidf_vectorizer.transform(txt2)


# Initialize the PassiveAggressiveClassifier and fit training sets
# pa_classifier = PassiveAggressiveClassifier(max_iter=50)
# pa_classifier.fit(tfidf_train, y_train)


# save the model to disk
# save_classifier = open("model.pickle", "wb")
# pickle.dump(pa_classifier,save_classifier)
# save_classifier.close()

# Predict and calculate accuracy
# y_pred = pa_classifier.predict(tfidf_test)
classifier_f = open("model.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()

print(classifier.predict(tfidf_test))


# print(y_pred)
# score = accuracy_score(y_test, y_pred)
# print(f'Accuracy: {round(score*100,2)}%')
# print(confusion_matrix(y_test, y_pred, labels=['FAKE', 'REAL']))

# load the model from disk






