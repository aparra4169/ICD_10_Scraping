from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Optional
from dataclasses import dataclass, field
import json
from dataclasses import asdict
import sqlite3
import time
import re


# define classes
@dataclass
class SubCode:
    id_subcode:  Optional[int] = None
    name:  Optional[str] = None
    description:  Optional[str] = None
    inclusion: Optional[str] = None
    exclusion: Optional[str] = None

@dataclass
class Code:
    id_code: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    inclusion: Optional[str] = None
    exclusion: Optional[str] = None
    sub_codes: List[SubCode] = field(default_factory=list)

@dataclass
class Block:
    id_block: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    inclusion: Optional[str] = None
    exclusion: Optional[str] = None
    href: Optional[str] = None
    codes: List[Code] = field(default_factory=list)

@dataclass
class Chapter:
    id_chapter: Optional[int] = None
    data_id: Optional[str] = None
    name: Optional[str] = None
    introduction: Optional[str] = None
    notes: Optional[str] = None
    blocks: List[Block] = field(default_factory=list)



###### REPLACE LINKS

# Rango de ejemplos
ranges = ["A00-A09","A15-A19","A20-A28","A30-A49","A50-A64","A65-A69","A70-A74","A75-A79","A80-A89","A92-A99","B00-B09","B15-B19","B20-B24","B25-B34","B35-B49","B50-B64","B65-B83","B85-B89","B90-B94","B95-B98","B99-B99","C00-C97","C00-C75","C00-C14","C15-C26","C30-C39","C40-C41","C43-C44","C45-C49","C50-C50","C51-C58","C60-C63","C64-C68","C69-C72","C73-C75","C76-C80","C81-C96","C97-C97","D00-D09","D10-D36","D37-D48","D50-D53","D55-D59","D60-D64","D65-D69","D70-D77","D80-D89","E00-E07","E10-E14","E15-E16","E20-E35","E40-E46","E50-E64","E65-E68","E70-E90","F00-F09","F10-F19","F20-F29","F30-F39","F40-F48","F50-F59","F60-F69","F70-F79","F80-F89","F90-F98","F99-F99","G00-G09","G10-G14","G20-G26","G30-G32","G35-G37","G40-G47","G50-G59","G60-G64","G70-G73","G80-G83","G90-G99","H00-H06","H10-H13","H15-H22","H25-H28","H30-H36","H40-H42","H43-H45","H46-H48","H49-H52","H53-H54","H55-H59","H60-H62","H65-H75","H80-H83","H90-H95","I00-I02","I05-I09","I10-I15","I20-I25","I26-I28","I30-I52","I60-I69","I70-I79","I80-I89","I95-I99","J00-J06","J09-J18","J20-J22","J30-J39","J40-J47","J60-J70","J80-J84","J85-J86","J90-J94","J95-J99","K00-K14","K20-K31","K35-K38","K40-K46","K50-K52","K55-K64","K65-K67","K70-K77","K80-K87","K90-K93","L00-L08","L10-L14","L20-L30","L40-L45","L50-L54","L55-L59","L60-L75","L80-L99","M00-M25","M00-M03","M05-M14","M15-M19","M20-M25","M30-M36","M40-M54","M40-M43","M45-M49","M50-M54","M60-M79","M60-M63","M65-M68","M70-M79","M80-M94","M80-M85","M86-M90","M91-M94","M95-M99","N00-N08","N10-N16","N17-N19","N20-N23","N25-N29","N30-N39","N40-N51","N60-N64","N70-N77","N80-N98","N99-N99","O00-O08","O10-O16","O20-O29","O30-O48","O60-O75","O80-O84","O85-O92","O94-O99","P00-P04","P05-P08","P10-P15","P20-P29","P35-P39","P50-P61","P70-P74","P75-P78","P80-P83","P90-P96","Q00-Q07","Q10-Q18","Q20-Q28","Q30-Q34","Q35-Q37","Q38-Q45","Q50-Q56","Q60-Q64","Q65-Q79","Q80-Q89","Q90-Q99","R00-R09","R10-R19","R20-R23","R25-R29","R30-R39","R40-R46","R47-R49","R50-R69","R70-R79","R80-R82","R83-R89","R90-R94","R95-R99","S00-S09","S10-S19","S20-S29","S30-S39","S40-S49","S50-S59","S60-S69","S70-S79","S80-S89","S90-S99","T00-T07","T08-T14","T15-T19","T20-T32","T20-T25","T26-T28","T29-T32","T33-T35","T36-T50","T51-T65","T66-T78","T79-T79","T80-T88","T90-T98","V01-X59","V01-V99","V01-V09","V10-V19","V20-V29","V30-V39","V40-V49","V50-V59","V60-V69","V70-V79","V80-V89","V90-V94","V95-V97","V98-V99","W00-X59","W00-W19","W20-W49","W50-W64","W65-W74","W75-W84","W85-W99","X00-X09","X10-X19","X20-X29","X30-X39","X40-X49","X50-X57","X58-X59","X60-X84","X85-Y09","Y10-Y34","Y35-Y36","Y40-Y84","Y40-Y59","Y60-Y69","Y70-Y82","Y83-Y84","Y85-Y89","Y90-Y98","Z00-Z13","Z20-Z29","Z30-Z39","Z40-Z54","Z55-Z65","Z70-Z76","Z80-Z99","U00-U49","U82-U85"]

def find_range(value, ranges):
    # Determinar a qué rango pertenece el valor
    for r in ranges:
        start, end = r.split('-')
        # Verificar si el valor está dentro del rango
        if start <= value <= end:
            return r
    return "JOSE"  # Si no pertenece a ningún rango

def extract_and_replace_links(html_string, ranges):
    # Patrón de la expresión regular para capturar los valores detrás de las letras
    pattern = r'NOT_FOUND\.html#([A-Z0-9]+(?:\.[0-9]+)?)'
    
    # Encontrar todas las coincidencias en el string
    matches = re.findall(pattern, html_string)
    
    for match in matches:
        # Obtener el valor sin la parte decimal
        value = match.split('.')[0]
        
        # Buscar el rango correspondiente
        replacement = find_range(value, ranges)
        
        if replacement:
            # Reemplazar "NOT_FOUND" por el rango correspondiente en el enlace original
            html_string = html_string.replace(f"NOT_FOUND.html#{match}", f"{replacement}.html#{match}")

    return html_string

def replace_links(html_content):

    # Reemplazar enlaces del tipo "#/X.Y" por "NOT_FOUND.html#X.Y"
    html_content = re.sub(r'href="#/([A-Z0-9\.]+)"', r'href="NOT_FOUND.html#\1"', html_content)
    
    # Reemplazar enlaces del tipo "#/X-Y" por "X-Y.html"
    html_content = re.sub(r'href="#/([A-Z0-9\-]+)"', r'href="\1.html"', html_content)

    html_content = extract_and_replace_links(html_content, ranges)

    return html_content

## BLOCKS
def scrape_block(driver, id_chapter) -> List[Block]:
    # Get blocks
    # html_blocks = driver.find_elements(By.XPATH, "//dl[@class='BlockList' or @class='ListClassesWithUsage']//li")
    html_blocks = driver.find_elements(By.XPATH, "//dl[@class='BlockList']//li")
    list_blocks_temp = []
    for id_block, html_block in enumerate(html_blocks):
        # Get elements
        ## link
        link_element = html_block.find_element(By.TAG_NAME, 'a')
        href = link_element.get_attribute('href')
        code_text = link_element.text.strip()
        ## block code
        span_element = html_block.find_element(By.TAG_NAME, 'span')
        label_text = span_element.text.strip()

        current_block = Block()
        current_block.id_block = id_block
        current_block.href = href
        current_block.name = code_text
        current_block.description = label_text

        print(f"-- Block: {current_block.name}-{current_block.description}")

        list_blocks_temp.append(current_block)

        
    # Go to blocks links
    list_blocks = []
    for block in list_blocks_temp:
        ## Go to link
        driver.get(block.href)
        time.sleep(0.5)
        html_content = driver.find_element(By.XPATH, "//*[@id='classicont']").get_attribute('outerHTML')

        # Replace links with offline format
        html_content_modified = replace_links(html_content)

        with open(f"./offline_website/{block.name}.html", "w", encoding="utf-8") as file:
            file.write(html_content_modified)

        # Update block inclusions and exclusion. At the beginning of the page
        # inclusion, exclusion = scrape_block_incl_excl(driver)
        # block.inclusion = inclusion
        # block.exclusion = exclusion
        # block.codes = scrape_codes(driver)
        list_blocks.append(block)

    return list_blocks


    
## CHAPTERS
def scrape_chapter(driver, filters: List[str]) -> List[Chapter]:
    # Get the chapters
    chapters = driver.find_elements(By.XPATH, "//*[@id='ygtvc1']/div[@id[starts-with(., 'ygtv')]]/table//a[@class='ygtvlabel  ']")

    list_chapters = []
    for id_chapter, chapter in enumerate(chapters):
       # Get elements
       current_chapter = Chapter()
       current_chapter.id_chapter = id_chapter
       current_chapter.name = chapter.text.strip()
       current_chapter.data_id = chapter.get_attribute("data-id")
       print(f"- Chapter: {current_chapter.name} Data ID: {current_chapter.data_id}")
       
       if filters is None or current_chapter.name in filters:
            # Go to link
            chapter.click()
            time.sleep(0.5)
            html_content = driver.find_element(By.XPATH, "//*[@id='classicont']").get_attribute('outerHTML')

            # Replace links with offline format
            html_content_modified = replace_links(html_content)

            # Save HTML content
            with open(f"./offline_website/{current_chapter.data_id}.html", "w", encoding="utf-8") as file:
                file.write(html_content_modified)
            
            # current_chapter.introduction = '\n'.join([node.text.strip() for node in driver.find_elements(By.XPATH, "//dl[@class='Rubric-text']//p")])  
            # current_chapter.notes = '\n'.join([node.text.strip() for node in driver.find_elements(By.XPATH, "//dl[@class='Rubric-introduction']//p")])
            current_chapter.blocks = scrape_block(driver, id_chapter)
            list_chapters.append(current_chapter)
            # insert_chapter_db(current_chapter, cursor_db)

    return list_chapters

def generate_menu(data: List[Chapter]):
    # Comenzar el HTML del menú
    html_menu = '<ul>\n'
    
    for chapter in data:
        # Añadir el nombre del capítulo
        html_menu += f'    <li>{chapter.name}\n'
        
        # Comenzar la lista de bloques
        html_menu += '        <ul>\n'
        
        for block in chapter.blocks:
            # Crear el enlace del bloque
            block_link = f'{block.name}.html'
            # Añadir el bloque con su descripción dentro del enlace
            html_menu += f'            <li><a href="{block_link}">{block.name} {block.description}</a></li>\n'
        
        # Cerrar la lista de bloques
        html_menu += '        </ul>\n'
        
        # Cerrar el capítulo
        html_menu += '    </li>\n'
    
    # Cerrar el menú
    html_menu += '</ul>'
    
    # Save HTML content
    with open(f"./offline_website/menu.html", "w", encoding="utf-8") as file:
        file.write(html_menu)

def scrape_icd10_data():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get('https://icd.who.int/browse10/2016/en')

    # Wait for the page to load and elements to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ygtvitem']//div[@class='ygtvitem']//div[@class='ygtvitem']")))

    # Create the database and tables
    # conn = sqlite3.connect('icd10.db')
    # cursor = conn.cursor()
    # create_database(cursor)

    data = scrape_chapter(driver, None)
    generate_menu(data)

    # print
    # chapters_dict = [asdict(chapter) for chapter in data]
    # chapters_json = json.dumps(chapters_dict, indent=4)
    # print(chapters_json)


    # conn.commit()
    # conn.close()

    driver.quit()

if __name__ == "__main__":
    scrape_icd10_data()