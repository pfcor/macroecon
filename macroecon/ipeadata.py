"""
Interface for retrieving data from IPEA's portal: http://www.ipeadata.gov.br

@author: Pedro Correia
"""

### importing dependencies
# web scraping
import requests
from bs4 import BeautifulSoup

# data manipulation
import pandas as pd

# db connection
import pymongo

# auxlibs
import datetime as dt
import re


### aux data (put this in a conf file perhaps?)

pt2en = {
    'fonte': 'source',
    'frequência': 'frequency',
    'atualizado_em': 'last_updated',
    'unidade': 'unit',
    'comentário': 'comment'
}

periodicity_code = {
    'Anual': 'A',
    'Mensal': 'M',
    'Diário': 'D',
    'Diária': 'D',
    'Quadrienal': 'Q',
    'Trimestral': 'T'
}

db_connection_string = "mongodb://user:ieG3hWVxMsWNME3P@macroecon-shard-00-00-ee0yx.mongodb.net:27017,macroecon-shard-00-01-ee0yx.mongodb.net:27017,macroecon-shard-00-02-ee0yx.mongodb.net:27017/admin?replicaSet=Macroecon-shard-0&ssl=true"


### functions

# aux functions

def get_page(series_id):
    """
    Returns soup object referring to the page of the series 
    especified by its id
    """

    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?serid={}".format(series_id)
   
    try:
        r = requests.get(url)    
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print('Unable to parse page:', e)
        raise

    return soup

def extract_source(value):
    """
    Source field info extraction from value 
    """

    if 'href' in value:
        m = re.search(r"href=\"(.+?)\">(.+?)<", value)
        link = m.group(1)
        full_source = m.group(2)
    else:
        link = None
        full_source = value


    source_name = full_source.split(' (')[0]    
    if ',' in full_source:
        source_name = full_source.split(',')[0]
        
    try:
        m = re.search(r"\((.+?)\)", full_source)
        # sometimes, the source short name is accompanied by
        # by the initials of the research group separated by
        # a '/'. thus the split below.
        short_name = m.group(1).split('/')[0].strip() 
    except:
        short_name = None
    value = {
        'link': link,
        'full_source': full_source,
        'source_name': source_name,
        'short_name': short_name
    }

    return value


# main funtions

def get_series_info(series_id):
    """
    Returns dictionary with the info from the series determined by its id, 
    such as its name, its source, its frequency and the last time it was
    updated.
    """

    try:
        series_id = int(series_id)
    except Exception as e:
        print('Invalid series_id format.')
        raise
    
    # get page html
    soup = get_page(series_id)

    # getting the header on the series page, where the metadata can be found
    # the '<br/>' tag separates the lines, so we get a list of metadata lines
    header = str(soup.find('table').find_all('td')[-1]).split('<br/>') # parsing the page and extracting 

    series_info = {'series_id': series_id}
    for i, h in enumerate(header):
        try:
            if i == 0:
                # the first line of the header is the title
                m = re.search(r'<b>(.+?)</b>', h)
                series_info['series_name'] = m.group(1)
            else:
                m = re.search(r'<b>(.+?): </b>(.+)', h)
                field = m.group(1).lower().replace(' ', '_')
                value = m.group(2)

                # check for links 
                if field == 'fonte': # if it's the source field, it's dealt with differently
                    value = extract_source(value)
                
                elif field == 'atualizado_em':
                    try:
                        value = dt.datetime.strptime(value, "%d/%m/%Y")
                    except:
                        pass

                elif field == 'frequência':
                    periodicity, rang = value.split(' ', 1)
                    m = re.search('de(.+?)até(.+)', rang)
                    rang = (m.group(1).strip(), m.group(2).strip())
                    series_info['periodicity'] = periodicity_code[periodicity]
                    series_info['date_range'] = rang
                    continue

                else:
                    if 'href' in value:
                        m = re.search("(.+?)<a href=\"(.+?)\">(.+?)</a>(.+)", value)
                        value = m.group(1) + m.group(3) + m.group(4) + ' link: ' + m.group(2)

                series_info[pt2en.get(field, field)] = value

        except Exception as e:
            pass
    
    #TODO > think of way to determine series health using the line below plus the 'last_updated' field
    # series_info['interrupted'] = 'série interrompida' in series_info['comentário'].lower()
    if 'série interrompida' in series_info['comment'].lower():
        series_info['interrupted'] = True

    return series_info

def get_series_data(series_id, date_as_index=False):
    """
    Returns a pd.DataFrame with the data from the requested series, which is 
    determined by its id.

    If a problem happens in the parsing, e.g. the date column, None is returned 
    """

    # TODO: use this periodicity to correctly parse the dates
    periodicity = get_series_info(series_id)['periodicity']

    soup = get_page(series_id)
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

def search(query, n=10, full_source=False, comment=False, periodicity=False, last_updated=False):
    client = pymongo.MongoClient(db_connection_string)
    ipea_series = client["ipeadata"]["series_info"]

    # text search
    match = {
        '$match': {
            '$text': {'$search': query}
        }
    }

    # scoring, sorting and limiting returns by "relevance" of text matching
    text_score = {
        '$addFields': {
            'score': {'$meta': 'textScore'}
        }
    }
    sort_by_score = {
        '$sort': {
            'score': -1
        }
    }
    series_returned = {
        '$limit': n
    }

    # fields returned for each series
    project = {
        '_id': 0,
        'id': '$series_id',
        'name': '$series_name'
    }
    if full_source:
        project.update({'source': 1})
    else:
        project.update({'source': '$source.source_name'})
    if comment:
        project.update({'comment': 1})
    if periodicity:
        project.update({'periodicity': 1})
    if last_updated:
        project.update({'last_updated': 1})

    
    project = {
        '$project': project
    }

    # aggregation pipeline
    series = ipea_series.aggregate([
        match,
        text_score,
        sort_by_score,
        series_returned,
        project
    ])

    return list(series)


if __name__ == '__main__':
    import pprint

    for s in search('ipca'):
        pprint.pprint(s)
        print()
