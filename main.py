'''

THIS SCRIPT AND INSTRUCTIONS HAVE ONLY BEEN USED DURING
2022 PUNJAB ELECTIONS RESULT DECLARATION DAY.
ECI MIGHT CHANGE THEIR WEBSITE, MAKING THIS SCRIPT USELESS.
USE WITH CAUTION

'''
import pandas as pd
from time import sleep
import re
from pathlib import Path

# prepared this txt file manually by copying from 
# # eci website's by 'viewing source'
# this is only for punjab. extract similar for up/goa/uk
vals = Path('punjab_constituency_value.txt').read_text()
print(vals[:100])
vals_ls = vals.split('\n')

link = "https://results.eci.gov.in/ResultAcGenMar2022/RoundwiseS19"
# preparing a dict in {"constituency_name:(value,link)"} format
d = {}
for val in vals_ls[:]:
    # extracting 'value' 
    v = re.search('\\d+',val)
    # extracting constituency name
    n = re.search('>(.*?)<',val)
    if v: d = d | {n.group(1) : (v.group(0),
                                 link + v.group(0) + ".htm?ac=" + v.group(0))} 
    #extracted this link creation using string concatenation from eci website


def get_roundwise_votes(link:str) -> tuple[pd.DataFrame,pd.DataFrame]:
    '''
    Get roundwise votes at each constituency from ECI website 
    
    '''
    # extracting tables from webpage having 'o.s.n' string 
    # as I found table which has the data we require has this string
    df_ls = pd.read_html(link,match='O.S.N.*')
    df =  df_ls[1].copy()
    # the extracted table has multi indexed colnames, treating it
    state_city = df.columns[0][0]
    df.columns = [col for _,_,col in df.columns]
    
    df['state_city'] = state_city
    # one column with name 'unnamed' with only null values was getting pulled. removing it
    if un := df.columns[df.columns.str.startswith("Un")].tolist():
        df = df.drop(columns=un)
    # asserting if the table extracted has correct columns
    assert pd.Series(df.columns).isin(['Candidate','Party','R-1','R-2']).sum() == 4
    return df,df_ls[1]

a,b = get_roundwise_votes("https://results.eci.gov.in/ResultAcGenMar2022/RoundwiseS1981.htm?ac=81")

for item in d:
    df,_ = get_roundwise_votes(d[item][1])
    df['constituency_from_link'] = item
    df.to_csv(f'out/roundwise/pb/{item}.csv',index=False)
    print(item)
    sleep(10)