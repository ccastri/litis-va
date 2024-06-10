import random
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os

load_dotenv()

URL="https://www.aportesenlinea.com/Home/home.aspx?ReturnUrl=%2fPagosMultiples.aspx%3fmaremplsid%3df0mqdlyd11jxbb3pqbquxbpy&maremplsid=f0mqdlyd11jxbb3pqbquxbpy"
username = os.getenv("NIT")
password = os.getenv("PASSWORD")




def random_delay():
    # Agrega una pausa aleatoria entre 1 y 3 segundos
    delay = random.uniform(1, 3)
    time.sleep(delay)


def simulate_human_movement(driver, element):
    # Simula movimientos aleatorios del mouse sobre el elemento
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()

def setup_driver(url:str):
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')  # Ejecutar en modo headless si no necesitas ver la GUI

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # chrome_options = Options()
    # driver=webdriver.Chrome(service)
    # Abre una página para verificar que la sesión está iniciada
    driver.get(url)
    return driver
# def setup_driver(url:str):
#     chrome_options = Options()
#     driver=webdriver.Chrome(service)
#     # Abre una página para verificar que la sesión está iniciada
#     driver.get(url)
#     return driver

def login(username:str, password:str) -> None:
    '''
    Input the login credentials stored on the env variables
    '''
    input_element = driver.find_element(By.ID, "Contenido_tbUsuario").send_keys(username)
    input_element = driver.find_element(By.ID, "Contenido_tbClave").send_keys(password)
    login_button = driver.find_element(By.ID, "Contenido_lbIniciar").click()

def open_employees_search_form():
    # Espera a que el botón "Empleados" esté presente
    empleados_button_xpath = '//a[@class="level1 level1 static" and @href="empleados.aspx"]'
    empleados_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, empleados_button_xpath)))

    # Simula un movimiento del mouse sobre el botón "Empleados"
    simulate_human_movement(driver, empleados_button)

    # Espera a que el menú esté presente y visible
    menu_xpath = '//*[@id="mnuEmpresa:submenu:15"]'
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, menu_xpath)))

    # Encuentra el segundo elemento de la lista y haz clic en él
    third_item_xpath = '//*[@id="mnuEmpresa:submenu:15"]/li[3]/a'
    third_item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, third_item_xpath)))
    third_item.click()

    # Asegúrate de esperar lo necesario después de hacer clic, por ejemplo, esperar a que la nueva página se cargue
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, 'XPATH_DE_UN_ELEMENTO_EN_LA_NUEVA_PAGINA')))

    print("Se hizo clic en el segundo elemento exitosamente.")

def search_employees(employee):
    try:
        # Espera a que el campo de texto de número de identificación esté presente
        identification_field_xpath = '//*[@id="Contenido_NumeroIdentificacion1_txtNumeroIdentificacion"]'
        identification_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, identification_field_xpath)))
        identification_field.clear()  # Clear the identification field
        identification_field.send_keys(str(employee))  # Input the employee ID
        print("Número de cédula introducido exitosamente.")

        # Selecciona la opción de certificado general
        report_type_xpath = '//*[@id="Contenido_rdbCertificadoGeneral"]'
        report_type = driver.find_element(By.XPATH, report_type_xpath)
        report_type.click()
        print("Opción de certificado general seleccionada exitosamente.")

        time.sleep(1)

        # Selecciona el periodo inicial
        dropdown_begginning_period_xpath = '//*[@id="Contenido_PeriodoInicial"]'
        dropdown_begginning_period = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, dropdown_begginning_period_xpath)))
        dropdown_begginning_period.click()
        time.sleep(1)
        second_option_begginning = dropdown_begginning_period.find_element(By.XPATH, './/option[2]')  # Select the second option
        second_option_begginning.click()
        print("Periodo inicial seleccionado exitosamente.")

        time.sleep(2)

        # Selecciona el periodo final
        dropdown_ending_period_xpath = '//*[@id="Contenido_PeriodoFinal"]'
        dropdown_ending_period = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, dropdown_ending_period_xpath)))
        dropdown_ending_period.click()
        time.sleep(1)
        second_option_ending = dropdown_ending_period.find_element(By.XPATH, './/option[2]')  # Select the second option
        second_option_ending.click()
        print("Periodo Final seleccionado exitosamente.")

        time.sleep(1)

        # Presiona el botón de submit para realizar la búsqueda
        submit_button_xpath = '//*[@id="Contenido_Submit1"]'
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
        submit_button.click()
        print("Búsqueda de empleado realizada exitosamente.")

        time.sleep(2)
        download_pdf()

    except Exception as e:
        print(f"Ocurrió un error durante la búsqueda del empleado {employee}: {e}")

def download_pdf():
    # Abre el menú desplegable de selección de formato de reporte

    driver.switch_to.window(driver.window_handles[-1])
    format_dropdown_xpath = '//*[@id="Contenido_ReportViewer1_ctl01_ctl05_ctl00"]'
    format_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, format_dropdown_xpath)))

    # Haz clic en el menú desplegable para abrirlo
    format_dropdown.click()
    time.sleep(1)

    # Espera a que las opciones del menú estén disponibles
    
    format_dropdown_options_xpath = '//*[@id="Contenido_ReportViewer1_ctl01_ctl05_ctl00"]/option'
    format_dropdown_options = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, format_dropdown_options_xpath)))

    # Encuentra y haz clic en la cuarta opción del menú desplegable (PDF)
    pdf_option = format_dropdown_options[3]  # El índice 3 representa la cuarta opción (la primera opción tiene índice 0)
    pdf_option.click()

    print("Opción de formato PDF seleccionada exitosamente.")
    time.sleep(1)

    download_button_xpath = '//*[@id="Contenido_ReportViewer1_ctl01_ctl05_ctl01"]'
    download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
    download_button.click()
    print("Descarga del reporte iniciada exitosamente.")
    driver.switch_to.window(driver.window_handles[0])

def logout() -> None:
    # xpath = '//*[@id="Contenido_NumeroIdentificacion1_txtNumeroIdentificacion"]'
    driver.find_element(By.XPATH, '//*[@id="mnuEmpresa"]/ul/li[10]/a').click()

driver=setup_driver(URL)
    
employees=[1107518873]
try:

    time.sleep(1)
    login(username, password)
    time.sleep(1)
    open_employees_search_form()
    time.sleep(1)
    [search_employees(employee) for employee in employees]
    time.sleep(1)
    logout()
except Exception as e:
    print(f"Ocurrió un error: {e}")
time.sleep(10)
# Cierra el navegador al finalizar
driver.quit()

