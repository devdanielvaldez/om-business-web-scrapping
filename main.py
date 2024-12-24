from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import undetected_chromedriver as uc
from fastapi.middleware.cors import CORSMiddleware
import time
import firebase_admin
from firebase_admin import credentials, storage

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
import uuid
import random
import os
from fastapi.responses import JSONResponse
import base64

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import motor.motor_asyncio

cred = credentials.Certificate("om-business-41594-firebase-adminsdk-xrqd5-0a3af07260.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'triptap-dev.appspot.com'
})

app = FastAPI()

# Modelo de datos para recibir los parámetros
class QuoteRequest(BaseModel):
    start_location: str
    end_location: str
    container_type: str
    container_quantity: int
    customer: str
    phone: str
    service_type: str

class BLRequest(BaseModel):
    bl: str


LOGIN_URL = "https://identity.hapag-lloyd.com/hlagwebprod.onmicrosoft.com/b2c_1a_signup_signin/oauth2/v2.0/authorize?client_id=64d7a44b-1c5b-4b52-9ff9-254f7acd8fc0&scope=openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Fwww.hapag-lloyd.com%2Fsolutions%2Fauth"
NEW_QUOTE_URL = "https://www.hapag-lloyd.com/solutions/new-quote/#/simple?language=en"
USERNAME = "omontero@ombusinesslogistic.com"
PASSWORD = "Candhy20241986--"

MONGO_URL = "mongodb+srv://admin:Admin123@ombusinesslogistic.gxrlr.mongodb.net"  # Asegúrate de cambiar a la URL de tu MongoDB
DATABASE_NAME = "Customers"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]
quotes_collection = db["quotes"]
bl_release_collection = db["bl_releases"]

def save_quote_to_db(price: str, company: str, url: str, uuid: str, customer: str, phone: str, service_type: str):
    try:
        uuid_str = str(uuid)
        # Crear una nueva cotización
        new_quote = {
            "price": price,
            "company": company,
            "url": url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "uuid": uuid_str,
            "customer": customer,
            "phone": phone,
            "service_type": service_type
        }
        # Insertar la cotización en MongoDB
        result = quotes_collection.insert_one(new_quote)
        print(f"Quote saved to DB with ID: {result}")
    except Exception as e:
        print(f"Error saving quote to DB: {e}")

def save_bl_release(bl: str):
    try:
        new_bl_release = {
            "bl_number": bl,
            "status": "Pending"
        }
        # Insertar la cotización en MongoDB
        result = bl_release_collection.insert_one(new_bl_release)
        print(f"BL Release saved to DB with ID: {result}")
        return {"success": True}
    except Exception as e:
        print(f"Error saving quote to DB: {e}")
        return {"error": str(e)}
    
def register_bl_release(bl: str):
    try:
        result = save_bl_release(bl)
        return result
    except Exception as e:
        print("Error in save BL Release")
        return {"error": str(e)}

@app.post("/release-bl/")
async def release_bl_endpoint(blRequest: BLRequest):
    result = register_bl_release(blRequest.bl)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

def upload_image_to_firebase(image_path: str) -> str:
    """
    Sube una imagen a Firebase Storage y devuelve su URL pública.
    """
    try:
        # Referencia al bucket de Firebase
        bucket = storage.bucket()
        filename = f"{uuid.uuid4()}.png"  # Nombre único para el archivo

        # Crea un blob (archivo) en el bucket
        blob = bucket.blob(filename)

        # Sube la imagen
        blob.upload_from_filename(image_path)
        print(f"Imagen subida: {filename}")

        # Hacer pública la imagen (opcional)
        blob.make_public()
        print(f"URL pública: {blob.public_url}")

        # Devuelve la URL pública
        return blob.public_url

    except Exception as e:
        raise Exception(f"Error al subir la imagen a Firebase: {e}")

def get_driver():
    chromedriver_autoinstaller.install()
    driver = uc.Chrome()
    return driver

def submit_quote(quote_request: QuoteRequest):
    driver = get_driver()

    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 120)

        # Aceptar el modal de políticas de privacidad
        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.ID, "accept-recommended-btn-handler")))
            accept_button.click()
            print("Políticas de privacidad aceptadas.")
        except Exception as e:
            print("No se encontró el modal de políticas de privacidad o ya fue aceptado.")
            driver.get(LOGIN_URL)
            wait = WebDriverWait(driver, 120)
            try:
                accept_button = wait.until(EC.element_to_be_clickable((By.ID, "accept-recommended-btn-handler")))
                accept_button.click()
                print("Políticas de privacidad aceptadas.")
            except Exception as e:
                print("No se encontró el modal de políticas de privacidad o ya fue aceptado.")

        # Ingresar las credenciales
        username_input = wait.until(EC.element_to_be_clickable((By.ID, "signInName")))
        password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)

        # Esperar a que el login sea procesado
        time.sleep(5)

        # Redirigir a la URL de nuevo presupuesto
        driver.get(NEW_QUOTE_URL)
        time.sleep(2)

        # Rellenar los campos con los datos del request
        start_location_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Start Location"]')))
        start_location_input.send_keys(quote_request.start_location)
        time.sleep(2)
        start_location_input.send_keys(Keys.ARROW_DOWN)
        start_location_input.send_keys(Keys.RETURN)

        end_location_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="End Location"]')))
        end_location_input.send_keys(quote_request.end_location)
        time.sleep(2)
        end_location_input.send_keys(Keys.ARROW_DOWN)
        end_location_input.send_keys(Keys.RETURN)

        container_type_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Container Type"]')))
        container_type_input.send_keys(quote_request.container_type)
        container_type_input.send_keys(Keys.RETURN)

        container_quantity_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Container Quantity"]')))
        container_quantity_input.send_keys(Keys.CONTROL + "a")
        container_quantity_input.send_keys(Keys.BACKSPACE)
        container_quantity_input.send_keys(str(quote_request.container_quantity))

        # Verificar si los campos están completos
        start_location_value = start_location_input.get_attribute("value")
        end_location_value = end_location_input.get_attribute("value")
        container_type_value = container_type_input.get_attribute("value")
        container_quantity_value = container_quantity_input.get_attribute("value")

        if not start_location_value or not end_location_value or not container_type_value or not container_quantity_value:
            print("No se han completado todos los campos requeridos.")
            return "Error: Faltan campos."

        # Enviar el formulario
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "q-btn") and @type="submit" and contains(@class, "q-btn--orange")]')))
        submit_button.click()
        print("Formulario enviado.")

        time.sleep(3)

        # Buscar y hacer clic en el primer span que contiene "Select"
        select_span = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Select"]')))
        select_span.click()
        print("Primer 'Select' seleccionado.")

        # Buscar y hacer clic en el span que contiene "Next" en la primera página
        next_span = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Next"]')))
        next_span.click()
        print("Primer 'Next' seleccionado.")

        time.sleep(2)

        # Cambiará de página, buscar nuevamente el span "Next" y hacer clic
        next_span_second_page = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Next"]')))
        next_span_second_page.click()
        print("Segundo 'Next' seleccionado.")

        time.sleep(2)

        # Buscar un h2 con las clases "text-h2 h-ma-none" y que contenga "USD"
        usd_h2 = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//h2[contains(@class, "text-h2 h-ma-none") and contains(text(), "USD")]')
        ))

        # Extraer el texto del h2
        usd_text = usd_h2.text
        price = usd_text.replace("USD", "").replace(" ", "").strip()

        # Convertir a número
        price_number = float(price.replace(",", ""))

        # Calcular el 20% y sumarlo
        result = round(price_number * 1.20)
        print(f"Texto encontrado en h2: {usd_text}")
        current_url = driver.current_url
        print(f"URL: {current_url}")

        uuid_quote = uuid.uuid4()

        save_quote_to_db(result, "HP", current_url, uuid_quote, quote_request.customer, quote_request.phone, quote_request.service_type)

        return {"data": { "price": result, "id": uuid_quote, "url": current_url, "company": "HP" }}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

    finally:
        driver.quit()


# Endpoint POST para recibir los datos y enviar el presupuesto
@app.post("/submit-quote/")
async def submit_quote_endpoint(quote_request: QuoteRequest):
    result = submit_quote(quote_request)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# Directorio donde se guardarán las capturas de pantalla
SCREENSHOTS_DIR = "screenshots"

proxies = [
    "http://171.237.120.129:4003",
    "http://200.49.99.78:9991",
    "http://36.92.132.116:1010",
    "http://101.51.54.236:8080",
    "http://124.106.173.56:8082",
    "http://185.166.39.29:3128",
    "http://207.154.229.255:10023",
    "http://157.20.36.149:1111",
    "http://42.116.214.29:8080",
    "http://185.204.0.94:8080",
    "http://59.98.4.70:8080",
    "http://167.249.29.218:9999",
    "http://58.120.36.163:3128",
    "http://119.95.235.6:8082",
    "http://114.134.95.222:8080",
    "http://122.54.105.109:8082",
    "http://189.164.188.186:8080",
    "http://181.204.83.115:41890",
    "http://49.146.178.162:8080"
]

# Crear el directorio si no existe
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)
    
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_random_proxy():
    """Selecciona un proxy aleatorio."""
    return random.choice(proxies)

def generate_random_filename(extension="png"):
    """Genera un nombre de archivo aleatorio con una extensión especificada."""
    return f"{SCREENSHOTS_DIR}/screenshot_{uuid.uuid4().hex}.{extension}"

def capture_tracking_page(tracking_number: str):
    """Captura la página de tracking y devuelve la ruta de la imagen."""
    URL = f"https://www.searates.com/container/tracking/?number={tracking_number}"
    chrome_options = Options()
    proxy = random.choice(proxies)  # Elige un proxy aleatorio
    chrome_options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    screenshot_filename = generate_random_filename()

    try:
        driver.get(URL)
        print("Página cargada...")

        # Maximizar la ventana del navegador (pantalla completa)
        driver.maximize_window()
        print("Pantalla maximizada...")

        # Esperar 120 segundos antes de tomar la captura de pantalla
        print("Esperando 20 segundos antes de tomar la captura...")
        time.sleep(20)

        # Tomar una captura de pantalla completa de la página
        screenshot = driver.get_screenshot_as_png()

        # Usar PIL para abrir la captura de pantalla
        image = Image.open(BytesIO(screenshot))

        # Recortar 350px desde la parte superior y 70px desde la parte inferior
        width, height = image.size
        cropped_image = image.crop((0, 300, width, height - 50))  # Recorta desde la parte superior y la parte inferior

        # Generar un nombre de archivo aleatorio
        cropped_image_path = generate_random_filename()

        # Guardar la nueva imagen recortada
        cropped_image.save(cropped_image_path)
        print(f"Captura de pantalla guardada como {cropped_image_path}")
        return cropped_image_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al capturar la página: {e}")
    
    finally:
        driver.quit()

def analyze_image_with_openai(image_path: str):
    """Analiza una imagen con OpenAI y devuelve la descripción del contenido."""
    try:
        return image_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")

@app.get("/track/{tracking_number}")
async def track_container(tracking_number: str):
    """Endpoint para capturar y analizar el estado de tracking."""
    try:
        # Capturar la página de tracking y obtener la ruta de la imagen
        image_path = capture_tracking_page(tracking_number)
        url = upload_image_to_firebase(image_path)

        # Retornar la descripción obtenida
        return JSONResponse(content={"tracking_number": tracking_number, "url": url })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")