"""
Combina en un solo .html los ficheros descargados con el script combinar_offline.py.
Añade además el buscador de contenido
"""
import os
from bs4 import BeautifulSoup
import re

def modificar_enlaces(contenido):
    # Función para modificar los enlaces según los patrones requeridos
    # Cambia los enlaces del tipo href="P75-P78.html#P78.3" a href="#P78.3"
    contenido = re.sub(r'href="([^"#]+)#([^"]+)"', r'href="#\2"', contenido)
    
    # Cambia los enlaces del tipo href="V10-V19.html" a href="#V10-V19"
    contenido = re.sub(r'href="([^"#]+)"', r'href="#\1"', contenido)
    
    # Quita .html de enlaces que empiezan con #
    contenido = re.sub(r'href="#([^"]+)\.html"', r'href="#\1"', contenido)

    return contenido

def combinar_archivos(directorio):
    contenido_total = ""

    # Recorrer todos los archivos HTML en el directorio
    for nombre_archivo in os.listdir(directorio):
        if nombre_archivo.endswith('.html'):
            ruta_archivo = os.path.join(directorio, nombre_archivo)

            # Leer el contenido del archivo HTML
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()

                # Modificar los enlaces
                contenido = modificar_enlaces(contenido)

                # Usar BeautifulSoup para extraer el div con id="classicont"
                soup = BeautifulSoup(contenido, 'html.parser')
                div_clasicont = soup.find('div', id='classicont')

                if div_clasicont:
                    # Cambiar el id del div por el nombre del archivo (sin extensión)
                    nuevo_id = os.path.splitext(nombre_archivo)[0]
                    div_clasicont['id'] = nuevo_id
                    
                    # Añadir el div modificado al contenido total
                    contenido_total += str(div_clasicont) + "\n"
                elif nombre_archivo == "00_Menu.html":
                    contenido_total+=str(soup)

    return contenido_total

def generar_html(contenido):
    # Crear un nuevo archivo HTML con el contenido combinado y el buscador
    with open('main_offline_website.html', 'w', encoding='utf-8') as archivo:
        archivo.write('<html>\n')
        archivo.write('<head>\n')
        archivo.write('<title>Buscador de Contenido</title>\n')
        archivo.write('<link rel="stylesheet" type="text/css" href="main_offline_website.css">\n')  # Enlace al CSS
        archivo.write('<script>\n')
        archivo.write('function buscarContenido() {\n')
        archivo.write('  const input = document.getElementById("buscador").value.toLowerCase();\n')
        archivo.write('  const divs = document.querySelectorAll("div[id]");\n')
        archivo.write('  const resultados = document.getElementById("resultados");\n')
        archivo.write('  resultados.innerHTML = "";  // Limpiar resultados\n')
        archivo.write('  divs.forEach(div => {\n')
        archivo.write('    const texto = div.innerText.toLowerCase();\n')
        archivo.write('    if (texto.includes(input) && input.length > 0) {\n')
        archivo.write('      const fragmento = encontrarFragmento(div.innerText, input);\n')
        archivo.write('      const resultadoDiv = document.createElement("div");\n')
        archivo.write('      resultadoDiv.className = "result";\n')
        archivo.write('      resultadoDiv.innerHTML = `<a href="#${div.id}">${div.id}</a>: ${fragmento}`;\n')
        archivo.write('      resultados.appendChild(resultadoDiv);\n')
        archivo.write('    }\n')
        archivo.write('  });\n')
        archivo.write('}\n')
        archivo.write('function encontrarFragmento(texto, busqueda) {\n')
        archivo.write('  const regex = new RegExp(`(.*?)(${busqueda})(.*)`, "i");\n')
        archivo.write('  const match = texto.match(regex);\n')
        archivo.write('  return match ? `${match[1]}<strong>${match[2]}</strong>${match[3]}` : texto;\n')
        archivo.write('}\n')
        archivo.write('</script>\n')
        archivo.write('</head>\n')
        archivo.write('<body>\n')
        
        # Añadir el buscador
        archivo.write('<div id="search-bar">\n')
        archivo.write('<h1>Buscador de Contenido</h1>\n')
        archivo.write('<input type="text" id="buscador" onkeyup="buscarContenido()" placeholder="Buscar...">\n')
        archivo.write('<div id="resultados"></div>\n')
        archivo.write('</div>\n')

        # Contenido combinado
        archivo.write(contenido)
        archivo.write('</body>\n')
        archivo.write('</html>\n')

def main():
    directorio = './offline_website'  # Cambia esto por la ruta de tu carpeta
    contenido = combinar_archivos(directorio)  # Combinar archivos
    generar_html(contenido)  # Generar el archivo HTML combinado

    print("Se ha generado 'resultado_combinado.html' con el contenido de los archivos.")

if __name__ == "__main__":
    main()