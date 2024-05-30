# Importing necessary libraries and modules
import re
import os
import csv
import requests
import pandas as pd
import json

# Function to read CSV file
def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df
    
# Function to write content to CSV file    
def csv_write(content,filename):
    with open(filename, 'a+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(content)
            
# Function to make HTTP GET request to fetch detailed response            
def get_detail_response(url, main_url):

    """
    Makes an HTTP GET request to fetch detailed response from a given URL.
    
    Args:
    url (str): The URL to make the request to.
    main_url (str): The main URL of the website.
    
    Returns:
    requests.Response: Response object containing the HTTP response.
    """
    session=requests.session()
    
    print(url)
    Detail_resp=session.get(url, headers={'Accept':'*/*','Referer':main_url,'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36','X-Nextjs-Data':'1'})
    
    print("Detail response::",Detail_resp.status_code)
    
    return Detail_resp
    
# Function to extract details from the response and write to CSV   
def detail_extract(Con,Input,filename):

    """
    Extracts book details from the JSON response and writes them to a CSV file.
    
    Args:
        content (dict): Dictionary containing book data.
        input_data (str): The input ISBN.
        filename (str): The path to the CSV file.
    """

    Block=Con
    Isbn= Input
    
    try:
        Title = Block['displayName']
        Subtitle  = Block['subtitle']
        
        # Check if Subtitle is not None
        if Subtitle != None:
            # If Subtitle is not None, concatenate Title and Subtitle with a space in between and assign to Book_Title
            Book_Title = f"{Title} {Subtitle}"
        else:
            # If Subtitle is None, assign Title to Book_Title
            Book_Title=Title
    except:
        Book_Title=""
    
    try:
        # Attempt to retrieve the 'contributors' key from the Block dictionary
        Contributors = Block['contributors']
        
        # Create a string of author names and roles. If the role is "Author", only the name is included;
        # otherwise, the name is followed by the role in parentheses.
        Author_Names = ", ".join([f"{contributor['name']} ({contributor['role']})" if contributor['role'] != "Author" else contributor['name'] for contributor in Contributors])
    except:
        Author_Names=""

    Book_type = Block.get('bindingFormat') or ""
    
    Retail_Price = Block.get('retailPrice') or ""
    
    Sale_Price = Block.get('salePrice',) or ""
    
    Isbn_10 = Block.get('isbn10') or ""
    
    Publication_Date = Block.get('publicationDate') or "" #YYYY-MM-DD Format
    
    Publisher = Block.get('publisher') or ""
    
    Pages = Block.get('numberOfPages') or ""
    
    Pages = Pages if Pages not in (None, 0) else "" 

    # Formatting output list
    Ouput=[str(Isbn),Book_Title,Author_Names,Book_type,Retail_Price,Sale_Price,Isbn_10,str(Publication_Date),Publisher,Pages]
    # Writing to CSV file
    csv_write(Ouput,filename)
    
    
#Main function to manage the process of fetching book details from an API and writing them to a CSV file.
def main(): 
        
    Meta_Path='Meta_Output/'
    if not os.path.exists(Meta_Path):
        os.makedirs(Meta_Path)
        
    filename=Meta_Path+'Booktopia_Output.csv'    
    OP_Headers = ['ISBN','Title','Author','Book Type','Original Price','Discount Price','ISBN-10','Published Date','Publisher','Number Of Pages']
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(OP_Headers)  
    
    dir_path = os.path.dirname(os.path.realpath(__file__))+"\\"
    
    file_path = dir_path+'input_list.csv'
    Input_Codes=read_csv(file_path)
    
    Main_Url="https://www.booktopia.com.au/"
    
    for isbn in Input_Codes['ISBN13']:
        print(isbn)
        
        Api_Url="https://www.booktopia.com.au/_next/data/BiLaGwnyd3BPwc2WwI_bZ/search.json?keywords="+str(isbn)+"&productType=&pn="
        
        Api_resp=get_detail_response(Api_Url,Main_Url)
        
        Api_response=Api_resp.text

        Match=re.search("\{\"\_\_N_REDIRECT\"\:\"\s*([^>]*?)\s*\"\,",Api_response)
        if Match:
            Detail_Api=Match.group(1)
            Detail_Api=re.sub(r'^//', '/', Detail_Api)
        else:
            Detail_Api=""
            
        if Detail_Api:
        
            Detail_Url="https://www.booktopia.com.au/_next/data/BiLaGwnyd3BPwc2WwI_bZ"+Detail_Api+".json?productName=&type="
            
            Detail_resp=get_detail_response(Detail_Url,Main_Url)
            
            Detail_response=Detail_resp.json()
            
            try:
                Block=Detail_response['pageProps']['product']                
                detail_extract(Block,isbn,filename)
            except: 
                
                Detail_resp_text = Detail_resp.text
                
                Match=re.search("\{\"\_\_N_REDIRECT\"\:\"\s*([^>]*?)\s*\"\,",Detail_resp_text)
                if Match:
                    Inner_Detail_Api=Match.group(1)
                    Inner_Detail_Api=re.sub(r'^//', '/', Inner_Detail_Api)
                else:
                    Inner_Detail_Api=""
                
                Inner_Detail_Url="https://www.booktopia.com.au/_next/data/BiLaGwnyd3BPwc2WwI_bZ"+Inner_Detail_Api+".json?productName=&type="
                
                Inner_Detail_resp=get_detail_response(Inner_Detail_Url,Main_Url)    
                
                Inner_Detail_response=Inner_Detail_resp.json()

                Block=Inner_Detail_response['pageProps']['product']                
                detail_extract(Block,isbn,filename)
        else:
            Ouput=[str(isbn),"Book not found","","","","","","","",""]
            csv_write(Ouput,filename)
                
                
if __name__ == "__main__":
    main()