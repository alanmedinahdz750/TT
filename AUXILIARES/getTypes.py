import requests
import json
from concurrent.futures import ThreadPoolExecutor

# URL del servidor Orthanc
url = "https://demo.orthanc-server.com/instances/"

# Realizamos una solicitud HTTP para obtener la lista de IDs
response = requests.get(url)
if response.status_code != 200:
    print('Error al obtener la lista de IDs')
    exit()

# Convertimos la respuesta a una lista de IDs y seleccionamos los primeros 5
ids = response.json()

# Diccionario para contar las modalidades
series = {}
studies = {}
bodypart = {}
modality = {}

raw = {}

def process_file(id):
    response = requests.get(url + id + "/simplified-tags")

    if response.status_code == 200:
        simplified_tags = response.json()
        
        for key, value in simplified_tags.items():
            
            if key == 'SeriesDescription':
                if value in series:
                    series[value].append(id)
                else:
                    series[value] = [id]
            
            elif key == 'StudyDescription':
                if value in studies:
                    studies[value].append(id)
                else:
                    studies[value] = [id]

            elif key == 'BodyPartExamined':
                if value in bodypart:
                    bodypart[value].append(id)
                else:
                    bodypart[value] = [id]
            
            elif key == 'Modality':
                if value in modality:
                    modality[value].append(id)
                else:
                    modality[value] = [id]
            
            # Crear el diccionario 'raw'
            raw[id] = {
                'SeriesDescription': simplified_tags.get('SeriesDescription', ''),
                'StudyDescription': simplified_tags.get('StudyDescription', ''),
                'BodyPartExamined': simplified_tags.get('BodyPartExamined', ''),
                'Modality': simplified_tags.get('Modality', '')
            }

    else:
        print(f'Error al descargar el archivo {id}')

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(process_file, ids)

resume = {
    'Series Description' : series,
    'Study Description' : studies,
    'Body Part' : bodypart,
    'Modality' : modality
}

# Guardar el diccionario 'raw' en un archivo JSON llamado 'raw.json'
with open('raw.json', 'w') as json_file:
    json.dump(raw, json_file, indent=4)

with open('resumen.json', 'w') as json_file:
    json.dump(resume, json_file, indent=2)

print("\nLISTOOO!!")
#print(f'\n\n\tSeries Description: {series} \n\tStudy Description: {studies} \n\n\tBody Part: {bodypart} \n\n\tModality: {modality}')
#print(f"\n\n\n {raw}")
