# Scrape ICD10CM codes from websites

1. Import needed packages

```
import requests as re
from bs4 import BeautifulSoup
import csv
import pandas as pd

```

2. As usual, we define a main function to run everything in a chunk.
```
def main():
   #the main codes that we need to write.

```

3. Now we define the main function to scrape the data from the website. we need to get information for our request header.

```
def scrape_icd10_codes(url,data):
    response = re.get(url,headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Content-Type': 'text/html; charset=utf-8'})
    soup = BeautifulSoup(response.content, 'html.parser')
    # Selecting the ul element
    ul = soup.select_one('body > div.container.vp > div > div.col-sm-8 > div > ul')
    if not ul:
        return data

    for li in ul.find_all('li'):
        # Extracting the code from the 'a' element and the definition from the 'span' element
        code = li.find('a').get_text(strip=True) if li.find('a') else ''
        definition = li.find('span').get_text(strip=True) if li.find('span') else ''
        #print(code, definition)
        data.append((code, definition))

    return data
```

4. Now, also define the function to write out the data. There are many ways to write out the data, and this is just one way.

```
def save_to_csv(codes, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Code', 'Definition'])
        for code, definition in codes:
            writer.writerow([code, definition])

```
5. Now we add the content to the main() function
```
def main():
 # scrape female diagnosis codes
    url = "https://www.icd10data.com/ICD10CM/Codes/Rules/Female_Diagnosis_Codes/"
    female_code = list()
    for i in range(1,36):
        url_s = url + str(i)
        print("scrapping from " + url_s )
        female_code = scrape_icd10_codes(url_s,female_code)
    #male diagnosis codes
    url = "https://www.icd10data.com/ICD10CM/Codes/Rules/Male_Diagnosis_Codes/"
    male_code = list()
    for i in range(1,7):
        url_s = url + str(i)
        print("scrapping from " + url_s )
        male_code = scrape_icd10_codes(url_s,male_code)    
    
    #turn dictionary into data frame
    #female
    save_to_csv(female_code, 'female_icd10_codes.csv')
    print("saved to csv: female icd10 codes.")
    save_to_csv(male_code, 'male_icd10_codes.csv')
    print("saved to csv: male icd10 codes.")
```

6 Lastly, run the main function:

```
if __name__ == '__main__':
    main()


```


and we got the data perfectly!

## END
