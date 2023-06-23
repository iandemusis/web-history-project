#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 14:47:20 2023

@author: iandemusis
"""
from pathlib import Path
import mailbox
import email
import pandas as pd
from bs4 import BeautifulSoup
import requests 
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def process_message(message):
    subject = message['Subject']
    sender = message['From']
    date = message['Date']
    recipient = message['To']
    
    name, email_address = email.utils.parseaddr(sender)
    
    return {
        'Subject': subject,
        'Author Name': name,
        'Author Email': email_address,
        'Date': date,
        'Recipient': recipient
        }

def analyse_data(df):
    author_counts = df['Author Name'].value_counts()
    top_10_names = author_counts.head(10)
    
    print("\nTop 10 Most Popular Names:\n")
    for name, count in top_10_names.items():
        print(f"{name:<50} {count}")
    
def scrape_data():
    data = []

    for page in range(3):
        #this is only scraping 1993-1995, the 1991 and 1992 are differently formatted
            
        url = f"http://1997.webhistory.org/www.lists/www-talk.199{page+3}q1/"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all('a', {'href': re.compile(r'[0-9]+\.html')})
                #get the b from link, the i in other, store the info in data
            #names = soup.find_all('a', {'name': re.compile(r'[0-9]+')})

        b = links[0].find_all('b')
        data.append(b[0].get_text())

    print(data)
    
def email_clustering(df, subjects_per_cluster=5, top_clusters = 10):
    #to drop rows with no subject:
    df = df.dropna(subset=['Subject']) 
    
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df['Subject'])
    
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(X)
    
    df['Cluster'] = kmeans.labels_
    
    cluster_counts = df['Cluster'].value_counts()
    top_clusters = cluster_counts.head(top_clusters).index
    
    print("\nEmail Clustering Results:")
    for cluster_id in top_clusters:
        cluster_emails = df[df['Cluster'] == cluster_id]
        cluster_subjects = cluster_emails['Subject'].head(subjects_per_cluster).tolist()
        
        print(f"\nCluster {cluster_id}:")
        for subject in cluster_subjects:
            print(f"- {subject}")
            
    #the clusters represent groups of email subjects that share similar characteristics.
    #It groups together subjects that have similar word usage, language patterns, or thematic similarities. 
    #The algorithm does this by calculating the TF-IDF (Term Frequency-Inverse Document Frequency) #
    #representation of the subjects and using the K-means algorithm to partition them into distinct clusters.
    
def count_replies(df):
    reply_counts = {}

    for subject in df['Subject']:
        if subject is not None:
            # code below extracts the subject prefix before "Re:"
            match = re.match(r'^(Re: )*(.*)', subject)
            prefix = match.group(2)
    
            # this part increments the count for the subject prefix ,
            #if it already exists
            if prefix in reply_counts:
                reply_counts[prefix] += 1
            # otherwise it creates a new entry with starting value 1
            else:
                reply_counts[prefix] = 1

    # sorts the reply counts in descending order
    sorted_counts = sorted(reply_counts.items(), key=lambda x: x[1], reverse=True)

    #this part prints the subjects with the 10 highest reply counts
    print("\nTop 10 Subjects with the Most Replies:\n")
    for i, (subject, count) in enumerate(sorted_counts[:10], start=1):
        print(f"{i}. {subject:<50} {count} replies\n")

    
def process_emails():
    list_for_dataframe = []
    
    directory = Path("/Users/iandemusis/Desktop/html_zinoviev")
    files = directory.glob("www-talk.199[1-5]q[1-4]")
    message_details_csv_file = "message_details.csv"
        
    for f_path in files:
        mbox = mailbox.mbox(str(f_path))
        for message in mbox:
            data_row = process_message(message)
            list_for_dataframe.append(data_row)
                  
    df = pd.DataFrame(list_for_dataframe,columns = ['Subject', 'Author Name', 'Author Email', 'Date', 'Recipient'])

    analyse_data(df)
    
    df.to_csv(message_details_csv_file, index=False)
    
    return df
    
def main():
    df = process_emails()
    email_clustering(df)
    scrape_data()
    count_replies(df)
    
if __name__ == "__main__":
    main()
    
    
    #added a main function to get ability to compartimentalize the code.
    
    #pathlib over glob for a more convenient way to handle file paths. (how is it better?)
    #explanation for pathlib over glob:
        #Regarding why pathlib is recommended over glob, here are a few advantages:
        #Object-oriented approach: pathlib provides a clean and intuitive object-oriented 
        #interface to work with paths, making it easier to perform common file system operations.
        #Platform-independent code: pathlib handles paths in a platform-independent manner. 
        #It automatically handles path separators (/ or \) based on the operating system, 
        #allowing your code to be portable.
        #Enhanced functionality: pathlib offers more functionality for working with paths, 
        #such as joining paths, resolving relative paths, extracting file components, and much more.
        #By using pathlib, your code becomes more readable, maintainable, and flexible. 
        #It provides a consistent and powerful way to handle file system paths in Python.

    
    
    #who sends the most emails? 
    #(is most_popular_name the most popular email sender in general, 
    #or does it only count originals, originals and replies, repeats, etc...)
    #stuff to do with date!
    #average number of emails a day? most popular day to communicate?
    
    #Email Network Analysis: Build a network graph using the email addresses as nodes 
    #and analyze the network structure to identify influential senders, 
    #common communication patterns, and potential clusters of people.

    #Email Topic Modeling: Apply topic modeling techniques (e.g., Latent Dirichlet Allocation) 
    #to identify common topics or themes within your email dataset. This can help in understanding 
    #the main discussion areas or recurring subjects in your emails.
    
    # when emails are responses to a thread, the recipient on the csv file reads 
    # as " multiple recipients". 
    # We need to figure out a way to order and separate these emailers, both the senders
    # and recipients in order. 
    
    #need to fix the combined file, so all the files are included!!!
    #convert the dates all to the same format, so there are no headaches in the future
    
    
    
    #USE THE MAILBOX AND EMAIL MODULES
    #SAVE INFO IN ONE BIG CSV FILE 
    #FIND MODULE THAT SEPARATES NAMES FROM EMAILS (MIGHT BE EMAIL MODULE ITSELF)
    #use standards and create a dataframe
    #USE THE MAILBOX AND EMAIL MODULES
    #SAVE INFO IN ONE BIG CSV FILE 
    #FIND MODULE THAT SEPARATES NAMES FROM EMAILS (MIGHT BE EMAIL MODULE ITSELF)
    #use standards and create a dataframe
