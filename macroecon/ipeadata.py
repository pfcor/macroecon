"""
Functions for retrieving data from IPEA's portal: http://www.ipeadata.gov.br

@author: Pedro Correia
"""

### importing dependencies
# web scraping
import requests
from bs4 import BeautifulSoup

# data manipulation
import pandas as pd

# auxlibs
import datetime as dt
import re


### functions

def get_series_info(series_id):
    """
    Returns dictionary with the info from the series determined by its id, 
    such as its name, its source, its frequency and the last time it was
    updated.
    """

    # point of connection with ipeadata's portal
    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?serid={}".format(series_id)

    r = requests.get(url)
    if r.status_code != 200:
        print('data extraction error - status code {}'.format(r.status_code))
        return
    try:
        soup = BeautifulSoup(r.text, 'html.parser')    
        header = str(soup.find('table').find_all('td')[-1]).split('<br/>') # parsing the page and extracting 
    except Exception as e:
        print('Unable to parse page:', e)

    series_info = {}
    for i, h in enumerate(header):
        try:
            if i == 0:
                # the first line of the header is the title
                m = re.search('<b>(.+?)</b>', h)
                series_info['title'] = m.group(1)
            else:
                m = re.search('<b>(.+?): </b>(.+)', h)
                field = m.group(1).lower().replace(' ', '_')
                value = m.group(2)

                # check for links 
                if field == 'fonte': # if it's the source field, it's dealt with differently
                    if 'href' in value:
                        m = re.search("href=\"(.+?)\">(.+?)<", value)
                        value = {
                            'link': m.group(1),
                            'name': m.group(2)
                        }
                    else:
                        value = {
                            'link': None,
                            'name': value
                        }
                else:
                    if 'href' in value:
                        m = re.search("(.+?)<a href=\"(.+?)\">(.+?)</a>(.+)", value)
                        value = m.group(1) + m.group(3) + m.group(4) + ' link: ' + m.group(2)

                # if it is a date it should be parsed
                try:
                    value = dt.datetime.strptime(value, "%d/%m/%Y")
                except:
                    pass

                series_info[field] = value

        except Exception as e:
            pass
    
    #TODO > think of way to determine series health using the line below plus the 'last_updated' field
    # series_info['interrupted'] = 'série interrompida' in series_info['comentário'].lower()

    return series_info


def get_series_data(series_id, date_as_index=False):
    """
    Returns a pd.DataFrame with the data from the requested series, which is 
    determined by its id.

    If a problem happens in the parsing, e.g. the date column, None is returned 
    """

    # point of connection with ipeadata's portal
    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?serid={}".format(series_id)
    
    r = requests.get(url)
    if r.status_code != 200:
        print('data extraction error - status code {}'.format(r.status_code))
        return
    
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find(id="grd") # finding the table which contains the data
    rows = table.find('tr').find_all('tr')[3:] # the first three '<tr>'s are headers    
    
    data = {
        'date': [],
        series_id: []
    }

    for row in rows:
        datum = tuple(r.text for r in row.find_all('td'))
        if not datum[0]:
            # the last line of the table always contains an empty field.
            #TODO a more robust stop method
            break 
        try:    
            #TODO Implement support for different frequencies. The following only applies
            # to monthly data
            try:
                data['date'].append(dt.datetime.strptime(datum[0], '%Y.%m'))
            except ValueError as e:
                print('Unable to parse date:', e)
                return
            try:
                data[series_id].append(float(datum[1].replace('.', '').replace(',', '.')))
            except:
                data[series_id].append(None)
        except Exception as e:
            print(e)
            print(series_id, datum)
            return

    if date_as_index:   
        return pd.DataFrame(data[series_id], index=data['date'], columns=[series_id])
    return pd.DataFrame(data)



if __name__ == '__main__':
    import pprint
    series_id = 40080
    series_info = get_series_info(series_id)
    pprint.pprint(series_info)
    series_data = get_series_data(series_id)
    print(series_data)