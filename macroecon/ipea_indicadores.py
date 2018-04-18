# indicadores de interesse
# TODO colocar isso em arquivo ou base de dados separada
# com mais informaÃ§Ãµes sobre cada indicador
ipea_indicadores = {
    "ICC": 40080,
    "ICEA": 40081,
    "INEC": 40872,
    "INPC": 36473,
    "INPC_ab": 36485,
    "IPCA": 38513,
    "IPCA_ab": 39861,
    "RendimentoMedio": 1347352654,
    "SelicMes": 32241,
    "TaxaDesocupacao": 1347352645,
    'test': 1319263849
}

### imports
# web scraping
import requests
from bs4 import BeautifulSoup

# data manipulation
import pandas as pd

# auxlibs
import datetime as dt

### funcs
def get_header(indicador):
    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?serid={}&module=M".format(indicador)

    r = requests.get(url)
    if r.status_code != 200:
        print('data extraction error - status code {}'.format(r.status_code))
        return
    soup = BeautifulSoup(r.text, 'html.parser')

    header = soup.find('table').find_all('td')[-1]
    bs = [b.string for b in header.find_all('b')]
    head = header.text
    return head

def get_series(indicador):
    
    # montando url
    if isinstance(indicador, str):
        try:
            indicador = ipea_indicadores[indicador] #db connection
        except KeyError:
            print('indicador nao encontrado.\n\nindicadores disponiveis:')
            for ind in ipea_indicadores:
                print('  - {}'.format(ind))      
            return

    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?serid={}&module=M".format(indicador)
    
    # obtendo os dados
    r = requests.get(url)
    if r.status_code != 200:
        print('data extraction error - status code {}'.format(r.status_code))
        return
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find(id="grd")
    rows = table.find('tr').find_all('tr')[3:] # os tres primeiros 'tr's sÃ£o de cabecalho    
    
    data = {
        'Data': [],
        indicador: []
    }

    for row in rows:
        datum = tuple(r.text for r in row.find_all('td'))
        if not datum[0]:
            break
        try:    
            data['Data'].append(dt.datetime.strptime(datum[0], '%Y.%m'))
            try:
                data[indicador].append(float(datum[1].replace('.', '').replace(',', '.')))
            except:
                data[indicador].append(None)
        except Exception as e:
            print(e)
            print(indicador, datum)
            return
        
    return pd.DataFrame(data[indicador], index=data['Data'], columns=[indicador])


def ipea_dataset(indicadores):
    dataset = pd.DataFrame()
    print('Iniciando coleta de dados')
    for indicador in indicadores:
        print('  - {}:'.format(indicador), end=' ')
        try:
            ind_data = get_series(indicador)
            dataset = pd.concat([dataset, ind_data], axis=1)
            print('OK')
        except Exception as e:
            print('NOK', e)
    dataset = dataset.loc[dt.datetime(1980,1,1):]
    dataset['Ano'] = dataset.index.year
    dataset['Mes'] = dataset.index.month
    dataset.reset_index(drop=True, inplace=True)
    dataset.rename(index=str, columns={'RendimentoMedio':'RedimentoMedio'}, inplace=True)
    return dataset

if __name__ == '__main__':
    pass

    print(get_series('ICC'))

    """
    print('Gerando base de dados - indicadores IPEA')
    try:
        dataset = ipea_dataset(indicadores.keys())
        dataset.to_csv('IndicesMacroEconomicos.csv', index=False, sep=';')
    except Exception as e:
        print('dataset nÃ£o criado:', e)
    """