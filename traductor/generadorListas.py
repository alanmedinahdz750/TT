import json

# Abrir el JSON y cargar los datos
with open('traducido.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Conjuntos para almacenar los valores únicos de cada campo
informacion_set = set()
series_description_set = set()
study_description_set = set()
body_part_examined_set = set()
modality_set = set()

# Recorrer el JSON y almacenar los valores únicos en los conjuntos
for key, value in json_data.items():
    informacion_set.add(value.get("informacion", ""))
    series_description_set.add(value.get("SeriesDescription", ""))
    study_description_set.add(value.get("StudyDescription", ""))
    body_part_examined_set.add(value.get("BodyPartExamined", ""))
    modality_set.add(value.get("Modality", ""))

# Escribir los conjuntos en un archivo de texto
with open('resultados.txt', 'w', encoding='utf-8') as outfile:
    outfile.write("informacion: " + json.dumps(list(informacion_set), indent=4, ensure_ascii=False) + "\n")
    outfile.write("SeriesDescription: " + json.dumps(list(series_description_set), indent=4, ensure_ascii=False) + "\n")
    outfile.write("StudyDescription: " + json.dumps(list(study_description_set), indent=4, ensure_ascii=False) + "\n")
    outfile.write("BodyPartExamined: " + json.dumps(list(body_part_examined_set), indent=4, ensure_ascii=False) + "\n")
    outfile.write("Modality: " + json.dumps(list(modality_set), indent=4, ensure_ascii=False))

print("Conjuntos de valores únicos guardados en 'resultados.txt'.")
