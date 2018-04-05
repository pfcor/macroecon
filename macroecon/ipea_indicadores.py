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
    "TaxaDesocupacao": 1347352645
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
def ipeadata(indicador):
    
    # montando url
    try:
        ind = indicadores[indicador]
    except KeyError:
        print('indicador nao encontrado.\n\nindicadores disponiveis:')
        for ind in indicadores:
            print('  - {}'.format(ind))      
        return
    url = "http://www.ipeadata.gov.br/ExibeSerie.aspx?serid={}&module=M".format(ind)
    
    # obtendo os dados
    r = requests.get(url)
    if r.status_code != 200:
        print('erro na extraÃ§Ã£o dos dados - status code {}'.format(r.status_code))
        return
    soup = BeautifulSoup(r.text,  'lxml')
    table = soup.find(id="grd")
    rows = table.find('tr').find_all('tr')[3:] # os tres primeiros 'tr's sÃ£o de cabecalho    
    
    data = {
        'Data': [],
        indicador: []
    }

    for row in rows:
        datum = tuple(row.find_all('td')[i].text for i in [0,1])
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
            ind_data = ipeadata(indicador)
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

    """
    print('Gerando base de dados - indicadores IPEA')
    try:
        dataset = ipea_dataset(indicadores.keys())
        dataset.to_csv('IndicesMacroEconomicos.csv', index=False, sep=';')
    except Exception as e:
        print('dataset nÃ£o criado:', e)
    """