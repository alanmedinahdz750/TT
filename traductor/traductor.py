import json

# Abrir el archivo JSON y cargar los datos
with open('raw.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

def SeriesDescription(texto):
    with open('SeriesDescription.json', 'r', encoding='utf-8') as file:
        banco = json.load(file)
        return banco.get(texto, texto)

def BodyPartExamined(texto):
    with open('BodyPartExamined.json', 'r', encoding='utf-8') as file:
        banco = json.load(file)
        return banco.get(texto, texto)
    
def StudyDescription(texto):
    with open('StudyDescription.json', 'r', encoding='utf-8') as file:
        banco = json.load(file)
        return banco.get(texto, texto)
    
def Modality(texto):
    with open('Modality.json', 'r', encoding='utf-8') as file:
        banco = json.load(file)
        return banco.get(texto, texto)
    
def concatenador(texto):
    with open('informacion.json', 'r', encoding='utf-8') as file:
        banco = json.load(file)
        return banco.get(texto, "")

# Función para agregar información y traducción a un nuevo diccionario
def procesar_datos(original_data):
    nuevo_data = {}
    for key, value in original_data.items():
        nuevo_value = {}
        nuevo_value['informacion'] = ""

        for campo, texto in value.items():

            dato_traducido = ""
            if campo == 'SeriesDescription':
                dato_traducido = SeriesDescription(texto)

            elif campo == 'StudyDescription': 
                dato_traducido = StudyDescription(texto)
            
            elif campo == 'BodyPartExamined':
                dato_traducido = BodyPartExamined(texto)

            elif campo == 'Modality':
                dato_traducido = Modality(texto)
            
            nuevo_value[campo] = dato_traducido
            nuevo_value['informacion'] += concatenador(dato_traducido)  # Agrega tu lógica para concatenar la información
        
        #Manejo de vacios
        if nuevo_value['informacion'] == "":
            nuevo_value['informacion'] = "No hay informacion"

        if nuevo_value['BodyPartExamined'] == "":
            nuevo_value['BodyPartExamined'] = BodyPartExamined(nuevo_value['StudyDescription'])
            if nuevo_value['BodyPartExamined'] == "":
                nuevo_value['BodyPartExamined'] = "No se conoce la parte del cuerpo"

        nuevo_data[key] = nuevo_value
    return nuevo_data

# Llama a la función para procesar los datos
json_traducido = procesar_datos(json_data)

# Guardar el JSON traducido y procesado en un nuevo archivo
with open('traducido.json', 'w', encoding='utf-8') as outfile:
    json.dump(json_traducido, outfile, indent=4, ensure_ascii=False)

print("JSON modificado guardado en 'traducido.json'.")