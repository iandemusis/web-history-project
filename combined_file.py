from pathlib import Path
import os
import mailbox
import email
import pandas as pd
from bs4 import BeautifulSoup
import requests 
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import email_reply_parser

def process_message(message):
    subject = message['Subject']
    sender = message['From']
    date = message['Date']
    recipient = message['To']
    
    name, email_address = email.utils.parseaddr(sender)
    
    #extract the first line of the email body
    content = message.get_payload()  #get the email content
    if isinstance(content, list):
        content = content[0].as_string()  #convert list to string
    first_line = content.split('\n', 1)[0] if content else ''          
    
    return {
        'Subject': subject,
        'Author Name': name,
        'Author Email': email_address,
        'Date': date,
        'Recipient': recipient,
        'First Line': first_line
    }


def analyse_data(df):
    author_counts = df['Author Name'].value_counts()
    top_10_names = author_counts.head(10)
    
    if not top_10_names.empty:  #check if there are names to print
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
    
    #the clusters represent groups of email subjects that share similar characteristics.
    #It groups together subjects that have similar word usage, language patterns, or thematic similarities. 
    #The algorithm does this by calculating the TF-IDF (Term Frequency-Inverse Document Frequency) #
    #representation of the subjects and using the K-means algorithm to partition them into distinct clusters.
    
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
    
def merge_text_files(directory_path, output_file):
    directory = Path(directory_path)
    
    with open(output_file, "w") as outfile:
        for file_path in directory.glob("*.txt"):
            with open(file_path, "r", encoding='latin-1') as infile:
                outfile.write(infile.read())
    print("Files merged successfully.") 
    
    return output_file
    
def process_emails():
    list_for_dataframe = []
    
    directory = Path("/Users/iandemusis/Desktop/html_zinoviev")
    files = directory.glob("www-talk.199[1-6]q[1-4].txt")
    
    input_directory = str(directory) #make the directory into a str object
    message_details_csv_file = os.path.join(input_directory, "message_details.csv")
    
    for f_path in files:
        mbox = mailbox.mbox(str(f_path))
        for message in mbox:
            data_row = process_message(message)
            list_for_dataframe.append(data_row)
                  
    df = pd.DataFrame(list_for_dataframe, columns=[
        'Subject', 'Author Name', 'Author Email', 'Date', 'Recipient', 'First Line'])
    
    df['Date'] = df['Date'].str.replace(r'est$', 'EST', regex=True).replace("MET", "", regex = True)
    
    df.to_csv(message_details_csv_file, index=False)
    
    return df

def main():
    merge_text_files("/Users/iandemusis/Desktop/html_zinoviev", "/Users/iandemusis/Desktop/html_zinoviev/merged_output.txt")
    df = process_emails()
    #email_clustering(df)
    #scrape_data()
    #count_replies(df)
    
    
if __name__ == "__main__":
    main()
    
    #SAVE INFO IN ONE BIG CSV FILE 
    #FIND MODULE THAT SEPARATES NAMES FROM EMAILS (MIGHT BE EMAIL MODULE ITSELF)
    #use standards and create a dataframe
