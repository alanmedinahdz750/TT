import json

# Abrir el archivo JSON y cargar los datos
with open('raw.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

def traducir(texto):
    banco = {"Neck^1HEAD_NECK_PETCT" : "CABEZA_CUELLO_PET-TAC", "NECK" : "CUELLO", "CT HEAD/NK 5.0 B30s" : "TOMOGRAFIA COMPUTARIZADA CABEZA/CUELLO 5.0 B30s", "CT" : "TOMOGRAFIA COMPUTARIZADA", "PT" : "TOMOGRAFIA POR EMISION DE POSITRONES (PET).", "PET WB": "TOMOGRAFIA POR EMISION DE POSITRONES DE CUERPO COMPLETO", "PET WB-uncorrected" : "TOMOGRAFIA POR EMISION DE POSITRONES DE CUERPO COMPLETO SIN CORREGIR", "CT WB w/contrast 5.0 B30s" : "TOMOGRAFIA COMPUTARIZADA DE CUERPO COMPLETO CON CONTRASTE 5.0 B30s", "Cor FSE PD": "RESONANCIA MAGNETICA CORONAL CON TECNICA 'FAST SPIN ECHO' Y 'PROTON DENSITY'", "Cor FSE T1" : "RESONANCIA MAGNETICA CORONAL CON TECNICA 'FAST SPIN ECHO' Y 'T1'", "AX.  FSE PD" : "RESONANCIA MAGNETICA AXIAL CON TECNICA 'FAST SPIN ECHO' Y 'DENSIDAD DE PROTONES'", "Sag FRSE PD FS" : "RESONANCIA MAGNETICA SAGITAL CON TECNICA 'FAS RECOVERY FAST SPIN ECHO', 'PROTON DENSITY' y SUPRECIÓN DE LA GRASA", "Sag FSE T2" : "RESONANCIA MAGNETICA SAGITAL SAGITAL CON  TECNICA 'FAST SPIN ECHO' Y 'T2'"}
    return banco.get(texto, texto)

def concatenador(texto):
    info = {"TOMOGRAFIA POR EMISION DE POSITRONES DE CUERPO COMPLETO" : "Tomografía por Emisión de Positrones de Cuerpo Completo", "TOMOGRAFIA COMPUTARIZADA CABEZA/CUELLO 5.0 B30s" : "Tomografía Computarizada", "CABEZA_CUELLO_PET-TAC" : " es  PET-TAC (Tomografía por Emisión de Positrones con Tomografía Computarizada)", "CUELLO" : " se realizó del cuello", "TOMOGRAFIA POR EMISION DE POSITRONES DE CUERPO COMPLETO SIN CORREGIR" : "Tomografía por Emisión de Positrones de Cuerpo Completo que no ha sido corregido o ajustado para ciertos artefactos o irregularidades", "TOMOGRAFIA COMPUTARIZADA DE CUERPO COMPLETO CON CONTRASTE 5.0 B30s" : "Tomografía Computarizada de Cuerpo Completo con Contraste", "RESONANCIA MAGNETICA CORONAL CON TECNICA 'FAST SPIN ECHO' Y 'PROTON DENSITY'" : "Resonancia magnética coronal con técnica de Fast Spin Echo que permite obtener imágenes rápidamente, al ser PD,  resalta los tejidos basándose en la densidad de protones", "RESONANCIA MAGNETICA CORONAL CON TECNICA 'FAST SPIN ECHO' Y 'T1'" : "Resonancia magnética coronal con técnica de Fast Spin Echo que permite obtener imágenes rápidamente, al ser T1, los tejidos grasos suelen aparecer brillantes y los tejidos cerebrales y musculares aparecen en tonos de gris", "RESONANCIA MAGNETICA AXIAL CON TECNICA 'FAST SPIN ECHO' Y 'DENSIDAD DE PROTONES'" : "Resonancia magnética coronal con técnica de Fast Spin Echo que permite obtener imágenes rápidamente, al ser PD,  resalta los tejidos basándose en la densidad de protones", "RESONANCIA MAGNETICA SAGITAL CON TECNICA 'FAS RECOVERY FAST SPIN ECHO', 'PROTON DENSITY' y SUPRECIÓN DE LA GRASA" : "Resonancia magnética con técnica de Fast Recovery Fast Spin Echo que permite obtener imágenes con un tiempo relativamente corto, al ser PD, resalta los tejidos basándose en la densidad de protones y al ser FS,  suprime la señal de los tejidos grasos en las imágenes", "RESONANCIA MAGNETICA SAGITAL SAGITAL CON  TECNICA 'FAST SPIN ECHO' Y 'T2'" : "Resonancia magnética sagital con técnica de Fast Spin Echo que permite e obtener imágenes más rápidamente, al ser T2, los líquidos y los tejidos patológicos suelen aparecer brillantes"}
    return info.get(texto, "")

def parte_del_cuerpo(texto):
    banco = {"CABEZA_CUELLO_PET-TAC" : "CUELLO"}
    return banco.get(texto, "")

# Función para agregar información y traducción a un nuevo diccionario
def procesar_datos(original_data):
    nuevo_data = {}
    for key, value in original_data.items():
        nuevo_value = {}
        nuevo_value['informacion'] = ""
        for campo, texto in value.items():
            dato_traducido = traducir(texto)
            nuevo_value[campo] = dato_traducido
            nuevo_value['informacion'] += concatenador(dato_traducido)  # Agrega tu lógica para concatenar la información
        
        #Manejo de vacios
        if nuevo_value['informacion'] == "":
            nuevo_value['informacion'] = "No hay informacion"

        if nuevo_value['BodyPartExamined'] == "":
            nuevo_value['BodyPartExamined'] = parte_del_cuerpo(nuevo_value['StudyDescription'])
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