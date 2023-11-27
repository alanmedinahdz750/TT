textos = [
    "Resonancia magnética coronal con técnica de Fast Spin Echo que permite obtener imágenes rápidamente, al ser PD,  resalta los tejidos basándose en la densidad de protones",
    "Resonancia magnética con técnica de Fast Recovery Fast Spin Echo que permite obtener imágenes con un tiempo relativamente corto, al ser PD, resalta los tejidos basándose en la densidad de protones y al ser FS,  suprime la señal de los tejidos grasos en las imágenes",
    "No hay informacion",
    "Tomografía por Emisión de Positrones de Cuerpo Completo que no ha sido corregido o ajustado para ciertos artefactos o irregularidades",
    "Resonancia magnética coronal con técnica de Fast Spin Echo que permite obtener imágenes rápidamente, al ser T1, los tejidos grasos suelen aparecer brillantes y los tejidos cerebrales y musculares aparecen en tonos de gris",
    "Tomografía por Emisión de Positrones de Cuerpo Completo",
    "Tomografía Computarizada se realizó del cuello",
    "Tomografía Computarizada de Cuerpo Completo con Contraste"
]

textos_en_mayusculas = [texto.upper() for texto in textos]

for texto in textos_en_mayusculas:
    print(texto)
