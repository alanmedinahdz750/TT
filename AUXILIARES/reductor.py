import json

# Cargar el JSON traducido
with open('traducido.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Diccionarios para almacenar las descripciones organizadas
series_description_dict = {}
study_description_dict = {}

# Organizar los datos por Series Description y Study Description
for key, value in json_data.items():
    series_description = value.get("SeriesDescription")
    study_description = value.get("StudyDescription")
    
    # Organizar por Series Description
    if series_description:
        if series_description not in series_description_dict:
            series_description_dict[series_description] = []
        series_description_dict[series_description].append(key)
    
    # Organizar por Study Description
    if study_description:
        if study_description not in study_description_dict:
            study_description_dict[study_description] = []
        study_description_dict[study_description].append(key)

# Crear un nuevo diccionario organizado
organized_data = {
    "Series Description": series_description_dict,
    "Study Description": study_description_dict
}

# Guardar el JSON organizado en un nuevo archivo
with open('resumen.json', 'w', encoding='utf-8') as outfile:
    json.dump(organized_data, outfile, indent=4, ensure_ascii=False)

print("JSON organizado y guardado en 'organizado.json'.")
