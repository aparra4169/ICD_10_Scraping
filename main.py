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
    name: Optional[str] = None
    introduction: Optional[str] = None
    notes: Optional[str] = None
    blocks: List[Block] = field(default_factory=list)



def create_database(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id_chapter INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            introduction TEXT,
            notes TEXT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            id_chapter INTEGER,
            id_block INTEGER,
            name TEXT,
            description TEXT,
            inclusion TEXT,
            exclusion TEXT,
            href TEXT,
            PRIMARY KEY (id_chapter, id_block)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            id_chapter INTEGER,
            id_block INTEGER,
            id_code INTEGER,
            name TEXT,
            description TEXT,
            inclusion TEXT,
            exclusion TEXT,
            PRIMARY KEY (id_chapter, id_block, id_code)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sub_codes (
            id_chapter INTEGER,
            id_block INTEGER,
            id_code INTEGER,
            id_sub_code INTEGER,
            name TEXT,
            description TEXT,
            inclusion TEXT,
            exclusion TEXT,
            PRIMARY KEY (id_chapter, id_block, id_code, id_sub_code)
        );
    ''')

def insert_chapter_db(chapter: Chapter, cursor_db):

    # Insert into DB
    cursor_db.execute("INSERT OR IGNORE INTO chapters (id_chapter, name, introduction, notes) VALUES (?,?,?,?)", (chapter.id_chapter, chapter.name, chapter.introduction, chapter.notes))
    for block in chapter.blocks:
        cursor_db.execute("INSERT OR IGNORE INTO blocks (id_chapter, id_block, name, description, inclusion, exclusion, href) VALUES (?,?,?,?,?,?,?)", 
                          (chapter.id_chapter, block.id_block, block.name, block.description, block.inclusion, block.exclusion, block.href))
        for code in block.codes:
            cursor_db.execute("INSERT OR IGNORE INTO codes (id_chapter, id_block, id_code, name, description, inclusion, exclusion) VALUES (?,?,?,?,?,?,?)", 
                          (chapter.id_chapter, block.id_block, code.id_code, code.name, code.description, code.inclusion, code.exclusion))
            for sub_code in code.sub_codes:
                cursor_db.execute("INSERT OR IGNORE INTO sub_codes (id_chapter, id_block, id_code, id_sub_code, name, description, inclusion, exclusion) VALUES (?,?,?,?,?,?,?,?)", 
                          (chapter.id_chapter, block.id_block, code.id_code, sub_code.id_subcode, sub_code.name, sub_code.description, sub_code.inclusion, sub_code.exclusion))




def scrape_block_incl_excl(driver):
    
    # exclusions
    exclusions = driver.find_elements(By.XPATH, "//div[@class='Block']/dl[@class='Rubric-exclusion']/dd")
    exclusion_texts = [exclusion.text.strip() for exclusion in exclusions]
    exclusion_texts_combined = ";".join(exclusion_texts)

    # inclusions
    inclusions = driver.find_elements(By.XPATH, "//div[@class='Block']/dl[@class='Rubric-inclusion']/dd")
    inclusions_texts = [inclusions.text.strip() for inclusions in inclusions]
    inclusions_texts_combined = ";".join(inclusions_texts)

    return inclusions_texts_combined, exclusion_texts_combined

def extract_inclusions(element_parent, type="inclusion"):
    # Search <dd>
    dd_elements = element_parent.find_elements(By.XPATH, f".//dl[contains(@class, 'Rubric-{type}')]/dd")

    result_list = []
    # Iterate <dd>
    for dd in dd_elements:
        # Get text inside <dd>
        main_text = dd.text.split("\n")[0].replace(":", "").strip()

        # Check if there is <ul> inside this <dd>
        list_items = dd.find_elements(By.XPATH, ".//ul/li")

        if list_items:
            list_texts = [li.text.strip() for li in list_items]
            list_text = f"{','.join(list_texts)}"
            full_text = f"{main_text}[{list_text}]"
        else:
            full_text = main_text

        # Add results
        result_list.append(full_text)


    # Join results in one variable
    result = ";".join(result_list)

    return result

def scrape_subcode_data(sub_category_html):
    return extract_inclusions(sub_category_html, "inclusion"), extract_inclusions(sub_category_html, "exclusion")

def scrape_codes(driver) -> List[Code]:

    # Encontrar todos los elementos de categoría
    categories_html = driver.find_elements(By.XPATH, "//div[@class='Category1' or @class='Category2']")

    list_codes = []
    current_code = None
    id_code = -1
    # Iterar a través de todos los elementos de categoría
    for category_html in categories_html:
        if 'Category1' in category_html.get_attribute("class"):
            # Reset subcode id
            id_code += 1
            id_subcode = 0
            # Si hay una categoría actual, añadirla al resultado antes de empezar una nueva
            if current_code:
                list_codes.append(current_code)
            
            # Crear una nueva categoría
            current_code = Code()
            current_code.id_code = id_code
            current_code.name = category_html.find_element(By.TAG_NAME, 'a').text.strip()
            current_code.description = category_html.find_element(By.TAG_NAME, 'span').text.strip()
            print(f"--- Caegory1: {current_code.name}")
            current_code.inclusion = extract_inclusions(category_html, "inclusion")
            current_code.exclusion = extract_inclusions(category_html, "exclusion")

        elif 'Category2' in category_html.get_attribute("class") and current_code is not None:
            # Añadir subcategoría a la categoría actual
            current_sub_code = SubCode()
            current_sub_code.id_subcode = id_subcode
            current_sub_code.name = category_html.find_element(By.TAG_NAME, 'a').text.strip()
            current_sub_code.description = category_html.find_element(By.TAG_NAME, 'span').text.strip()
            print(f"--- Caegory2: {current_sub_code.name}")
            current_sub_code.inclusion = extract_inclusions(category_html, "inclusion")
            current_sub_code.exclusion = extract_inclusions(category_html, "exclusion")
            current_code.sub_codes.append(current_sub_code)
            # increment id_subcode
            id_subcode += 1

    # Asegurarse de añadir la última categoría después de salir del bucle
    if current_code:
        list_codes.append(current_code)
    
    return list_codes

## BLOCKS
def scrape_block(driver, id_chapter) -> List[Block]:
    # Get blocks
    html_blocks = driver.find_elements(By.XPATH, "//dl[@class='BlockList' or @class='ListClassesWithUsage']//li")
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
        # Update block inclusions and exclusion. At the beginning of the page
        inclusion, exclusion = scrape_block_incl_excl(driver)
        block.inclusion = inclusion
        block.exclusion = exclusion
        block.codes = scrape_codes(driver)
        list_blocks.append(block)

    return list_blocks


    
## CHAPTERS
def scrape_chapter(driver, cursor_db, filters: List[str]) -> List[Chapter]:
    # Get the chapters
    chapters = driver.find_elements(By.XPATH, "//*[@id='ygtvc1']/div[@id[starts-with(., 'ygtv')]]/table//a[@class='ygtvlabel  ']")

    list_chapters = []
    for id_chapter, chapter in enumerate(chapters):
       # Get elements
       current_chapter = Chapter()
       current_chapter.id_chapter = id_chapter
       current_chapter.name = chapter.text.strip()
       print(f"- Chapter: {current_chapter.name}")
       
       if filters is None or current_chapter.name in filters:
         # Go to link
         chapter.click()
         time.sleep(0.5)
         current_chapter.introduction = '\n'.join([node.text.strip() for node in driver.find_elements(By.XPATH, "//dl[@class='Rubric-text']//p")])  
         current_chapter.notes = '\n'.join([node.text.strip() for node in driver.find_elements(By.XPATH, "//dl[@class='Rubric-introduction']//p")])
         current_chapter.blocks = scrape_block(driver, id_chapter)
         list_chapters.append(current_chapter)
         insert_chapter_db(current_chapter, cursor_db)

    return list_chapters

def scrape_icd10_data():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get('https://icd.who.int/browse10/2016/en')

    # Wait for the page to load and elements to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ygtvitem']//div[@class='ygtvitem']//div[@class='ygtvitem']")))

    # Create the database and tables
    conn = sqlite3.connect('icd10.db')
    cursor = conn.cursor()
    create_database(cursor)

    data = scrape_chapter(driver, cursor, None)

    # print
    # chapters_dict = [asdict(chapter) for chapter in data]
    # chapters_json = json.dumps(chapters_dict, indent=4)
    # print(chapters_json)


    conn.commit()
    conn.close()

    driver.quit()

if __name__ == "__main__":
    scrape_icd10_data()