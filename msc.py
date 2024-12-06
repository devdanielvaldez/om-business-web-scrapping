from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import time
import random

# Configurar opciones para el navegador
options = uc.ChromeOptions()

# Configurar el User-Agent (simula un navegador real)
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Evitar la detección de Selenium
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")  # Abrir en tamaño máximo
options.add_argument("--disable-extensions")  # Desactivar extensiones

# Iniciar Chrome con opciones personalizadas
chromedriver_autoinstaller.install()
driver = uc.Chrome(options=options)

# URL de la página principal
MAIN_URL = "https://www.msc.com/en"
LOGIN_URL = "https://mscciam.b2clogin.com/mscciam.onmicrosoft.com/oauth2/v2.0/authorize?p=b2c_1a_signupsignin&client_id=a67f5969-b5a5-4de0-ae50-f611dfa91fee&redirect_uri=https%3A%2F%2Fidentityserver.msc.com%2Fsignin-aad-b2c&response_type=id_token&scope=openid%20profile&response_mode=form_post&nonce=638690298275218679.NzNkMDcyZGYtZjZkMi00MTRmLThiYzktMjliODMyMWNmYTMyMWNiMjkwZDYtZGZmYy00MGVlLTgwNjktMDkwZTI0MTk1NGI2&ui_locales=en&state=CfDJ8JCi0WqCtPVEprDHFnXVEfN8lfQcXYs5Ekz7qq8B5MUIHYzkdCFhDniyAeYV-WqdBDGWWteAL-pDepyTFXkwrpPSEdsqctz5DCRHHcelNj9CeqPtaYWhKu6KUKpPQ4t_vLQAe8thikIKQAWryAj8rVwk1LUNmh0ZOzcwEjC_9joS&x-client-SKU=ID_NETSTANDARD2_0&x-client-ver=6.10.0.0"

USERNAME = "omontero@ombusinesslogistic.com"  # Cambia esto por tu usuario
PASSWORD = "Candhy1986--"  # Cambia esto por tu contraseña

def simulate_human_behavior():
    """Simula el comportamiento humano con un retraso aleatorio entre acciones."""
    time.sleep(random.uniform(2, 4))  # Espera aleatoria entre 2 y 4 segundos
    return

def main():
    try:
        driver.get(MAIN_URL)
        
        # Espera que la política de cookies aparezca y acepta
        wait = WebDriverWait(driver, 60)
        accept_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        accept_button.click()
        simulate_human_behavior()  # Espera después de hacer clic

        # Espera a que el botón de redirección sea visible y haz clic en él
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".msc-header__nav-item.msc-header__nav-item--last[type='submit']")))
        submit_button.click()
        simulate_human_behavior()  # Espera después de hacer clic

        # Redirección a la página de login
        driver.get(LOGIN_URL)

        # Espera que el campo de usuario y contraseña sean visibles
        username_input = wait.until(EC.element_to_be_clickable((By.ID, "signInName")))
        password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))

        # Introduce las credenciales
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)

        # Simula presionar Enter para enviar el formulario
        password_input.send_keys(Keys.RETURN)

        simulate_human_behavior()  # Espera después de enviar el formulario

        # Espera para permitir que el login se procese
        time.sleep(10)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # No cerrar el navegador para depuración
        # driver.quit()
        pass

if __name__ == "__main__":
    main()