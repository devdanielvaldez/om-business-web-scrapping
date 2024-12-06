from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
import uuid
import random
import os
import openai
from fastapi.responses import JSONResponse
import base64

openai.api_key = "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"


app = FastAPI()

# Modelo de datos para recibir los parámetros
class QuoteRequest(BaseModel):
    start_location: str
    end_location: str
    container_type: str
    container_quantity: int

LOGIN_URL = "https://identity.hapag-lloyd.com/hlagwebprod.onmicrosoft.com/b2c_1a_signup_signin/oauth2/v2.0/authorize?client_id=64d7a44b-1c5b-4b52-9ff9-254f7acd8fc0&scope=openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Fwww.hapag-lloyd.com%2Fsolutions%2Fauth"
NEW_QUOTE_URL = "https://www.hapag-lloyd.com/solutions/new-quote/#/simple?language=en"
USERNAME = "omontero@ombusinesslogistic.com"  # Cambia esto por tu usuario
PASSWORD = "Dios1986--"  # Cambia esto por tu contraseña

def get_driver():
    chromedriver_autoinstaller.install()
    driver = uc.Chrome()
    return driver

def submit_quote(quote_request: QuoteRequest):
    driver = get_driver()

    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 60)

        # Aceptar el modal de políticas de privacidad
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
        time.sleep(10)

        # Redirigir a la URL de nuevo presupuesto
        driver.get(NEW_QUOTE_URL)
        time.sleep(5)

        # Cerrar el modal si aparece
        try:
            close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "q-dialog__x")))
            close_button.click()
            print("Botón cerrado.")
        except Exception as e:
            print("No se encontró el botón de cerrar modal.")

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

        # Esperar y obtener el precio
        offer_card_actions_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "offer-card__actions")))
        text_caption_div = offer_card_actions_div.find_element(By.CLASS_NAME, "text-caption-1")
        price_span = text_caption_div.find_element(By.CLASS_NAME, "text-h1.h-mr-xs")
        currency_span = text_caption_div.find_element(By.CLASS_NAME, "h-mr-xs")

        price = price_span.text
        currency = currency_span.text

        print(f"Precio: {price}")
        print(f"Moneda: {currency}")

        # Retornar el resultado
        return {"price": price, "currency": currency}

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
        # with open(image_path, "rb") as image_file:
        base64_image = encode_image(image_path)

        # Enviar la imagen a OpenAI para reconocimiento y descripción
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Dame la informacion del tracking, presentalo en formato para enviarselo al cliente como un mensaje. Solo agrega la informacion del tracking y que pueda enviarlo directamente al cliente sin tener que limpiar nada. Nunca agregues nada como esto: Aquí tienes la información de tracking que puedes enviar al cliente.",
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url":  f"data:image/png;base64,{base64_image}"
                    },
                    },
                ],
                }
            ],
        )

        return response['choices'][0]['message']['content']

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")

@app.get("/track/{tracking_number}")
async def track_container(tracking_number: str):
    """Endpoint para capturar y analizar el estado de tracking."""
    try:
        # Capturar la página de tracking y obtener la ruta de la imagen
        image_path = capture_tracking_page(tracking_number)

        # Analizar la imagen con OpenAI
        tracking_description = analyze_image_with_openai(image_path)

        # Retornar la descripción obtenida
        return JSONResponse(content={"tracking_number": tracking_number, "description": tracking_description})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")