from turtle import textinput
import tweepy
import configparser
import pandas as pd 
import re
from textblob import TextBlob
import matplotlib.pyplot as plt
import streamlit as st

def cleantt(tw):
    tw = re.sub('#bitcoin','bitcoin',tw)
    tw = re.sub('#Bitcoin','Bitcoin',tw)
    tw = re.sub('#[A-Za-z0-9]+', '', tw)
    tw = re.sub('\\n', '',tw)
    tw = re.sub('https?:\/\/\S+','',tw)
    tw = re.sub('[@#]','',tw)
    
    return tw



def re_emotions(tw):
    #text = u'This dog \U0001f602'
    #print(text) # with emoji
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

    print(emoji_pattern.sub(r'', tw)) # no emoji

#import re
#re_emotions()



def subjectivity(tw):
    return TextBlob(tw).sentiment.subjectivity

def polarity(tw):
    return TextBlob(tw).sentiment.polarity


def Gsentiment(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

st.title('Twitter sentimental Analysis')

usr_inp = st.text_input('Enter a hastag','#Bitcoin')
global use_inp

num = st.number_input('Enter a number',value = 50, max_value=1000, min_value=1)

st.write('You Have Entered:', usr_inp)
clicked = st.button("Submit")


if clicked:

    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['twitter']['api_key']
    api_key_secret = config['twitter']['api_key_secret']
    access_token = config['twitter']['access_token']
    access_token_secret = config['twitter']['access_token_secret']

    auth = tweepy.OAuthHandler(api_key,api_key_secret)
    auth.set_access_token(access_token,access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    print('Auth done')

    #HERE CHANGE NUMBER .ITEMS(NUMBER) MAX = 1000  MIN = 10
    #MAKE CHANGES IN SEARCH_QUERY TO CUSTOMIZE THE INPUT

    search_query = str(usr_inp) + '-filter:retweets'
    tweets = tweepy.Cursor(api.search_tweets, q=search_query, lang='en', tweet_mode='extended').items(num)

    all_tweets = [tweet.full_text for tweet in tweets]
    df = pd.DataFrame(all_tweets,columns=['Tweets'])

    df['Cleaned_Tweets'] = df['Tweets'].apply(cleantt)
    df['Cleaned_Tweets_emoji'] = df['Tweets'].apply(re_emotions)


    df['Subjectivity'] = df['Cleaned_Tweets'].apply(subjectivity)
    df['Polarity'] = df['Cleaned_Tweets'].apply(polarity)

    df['Sentiment'] = df['Polarity'].apply(Gsentiment)

    print(df)

    st.subheader('Figures')
    fig = plt.figure(figsize=(8,6))
    for i in range(0,df.shape[0]):
        plt.scatter(df['Polarity'][i],df['Subjectivity'][i],color='Red')
    plt.title('Analysis')
    plt.xlabel('Polarity')
    plt.ylabel('Subjectivity')
    st.pyplot(fig)

    st.subheader('Figures #2')
    fig1 = plt.figure(figsize=(8,6))
    df['Sentiment'].value_counts().plot(kind='bar')
    plt.title('Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    st.pyplot(fig1)