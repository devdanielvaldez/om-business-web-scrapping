from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
from io import BytesIO
import uuid  # Para generar nombres únicos aleatorios

# URL de la página
URL = "https://www.searates.com/container/tracking/?number=LMM0496953"

# Lista de proxies (puedes agregar más proxies)
proxies = [
    'http://190.61.84.166:9812'
]

def get_random_proxy():
    import random
    return random.choice(proxies)

def generate_random_filename(extension="png"):
    """Genera un nombre de archivo aleatorio con una extensión especificada."""
    return f"screenshot_{uuid.uuid4().hex}.{extension}"

def main():
    # Instalar y configurar el controlador de Chrome con las opciones de proxy
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Abrir la página
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

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cerrar el navegador
        driver.quit()

if __name__ == "__main__":
    main()