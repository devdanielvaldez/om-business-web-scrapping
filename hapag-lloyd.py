from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import time

LOGIN_URL = "https://identity.hapag-lloyd.com/hlagwebprod.onmicrosoft.com/b2c_1a_signup_signin/oauth2/v2.0/authorize?client_id=64d7a44b-1c5b-4b52-9ff9-254f7acd8fc0&scope=openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Fwww.hapag-lloyd.com%2Fsolutions%2Fauth"
NEW_QUOTE_URL = "https://www.hapag-lloyd.com/solutions/new-quote/#/simple?language=en"

USERNAME = "ingdanielvadez@gmail.com"  # Cambia esto por tu usuario
PASSWORD = "D@niel1901"  # Cambia esto por tu contraseña

def main():
    chromedriver_autoinstaller.install()
    driver = uc.Chrome()

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

        # Espera hasta que el campo de usuario sea visible e interactuable
        username_input = wait.until(EC.element_to_be_clickable((By.ID, "signInName")))
        password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))

        # Introduce las credenciales
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)

        # Enviar el formulario presionando Enter en el campo de contraseña
        password_input.send_keys(Keys.RETURN)

        # Espera 10 segundos para permitir que el sitio procese el login
        time.sleep(10)

        # Redirige a la URL de "New Quote"
        driver.get(NEW_QUOTE_URL)
        print(f"Redirigido a {NEW_QUOTE_URL}")

        time.sleep(5)

        start_location_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Start Location"]')))

        # Escribir DOCAU en el campo "Start Location"
        start_location_input.send_keys("DOCAU")
        time.sleep(2)
        start_location_input.send_keys(Keys.ARROW_DOWN)
        start_location_input.send_keys(Keys.RETURN)
        print("Búsqueda de Start Location completada.")

        # Ahora interactuar con el campo "End Location"
        end_location_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="End Location"]')))

        # Escribir USMIA en el campo "End Location"
        end_location_input.send_keys("USMIA")
        time.sleep(2)
        end_location_input.send_keys(Keys.ARROW_DOWN)
        end_location_input.send_keys(Keys.RETURN)

        print("Búsqueda de End Location completada.")

        # Ahora interactuar con el campo "Container Type"
        container_type_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Container Type"]')))
        container_type_input.send_keys("20' General Purpose")
        container_type_input.send_keys(Keys.RETURN)  # Pulsar Enter para finalizar selección

        # Ahora interactuar con el campo "Container Quantity"
        # Esperar hasta que el campo "Container Quantity" sea visible
        container_quantity_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Container Quantity"]')))

        # Eliminar valor actual en el campo de tipo "number" utilizando BACKSPACE repetidamente
        container_quantity_input.send_keys(Keys.CONTROL + "a")  # Selecciona todo el texto
        container_quantity_input.send_keys(Keys.BACKSPACE)  # Borra el contenido

        # Insertar nuevo valor
        container_quantity_input.send_keys("1")
        # time.sleep(5)


        # Verificar si los campos están completos
        start_location_value = start_location_input.get_attribute("value")
        end_location_value = end_location_input.get_attribute("value")
        container_type_value = container_type_input.get_attribute("value")
        container_quantity_value = container_quantity_input.get_attribute("value")

        if not start_location_value or not end_location_value or not container_type_value or not container_quantity_value:
            print("No se han completado todos los campos requeridos.")
            return  # Detener el proceso si algún campo está vacío

        # # Hacer clic en el botón con las clases especificadas (botón de envío)
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "q-btn") and @type="submit" and contains(@class, "q-btn--orange")]')))
        submit_button.click()
        print("Formulario enviado.")

        time.sleep(5)

        # Buscar y hacer clic en el primer span que contiene "Select"
        select_span = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Select"]')))
        select_span.click()
        print("Primer 'Select' seleccionado.")

        # Buscar y hacer clic en el span que contiene "Next" en la primera página
        next_span = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Next"]')))
        next_span.click()
        print("Primer 'Next' seleccionado.")

        time.sleep(10)

        # Cambiará de página, buscar nuevamente el span "Next" y hacer clic
        next_span_second_page = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Next"]')))
        next_span_second_page.click()
        print("Segundo 'Next' seleccionado.")

        time.sleep(10)

        # Buscar un h2 con las clases "text-h2 h-ma-none" y que contenga "USD"
        usd_h2 = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//h2[contains(@class, "text-h2 h-ma-none") and contains(text(), "USD")]')
        ))

        # Extraer el texto del h2
        usd_text = usd_h2.text
        print(f"Texto encontrado en h2: {usd_text}")
        current_url = driver.current_url
        print(f"URL: {current_url}")

        # # Esperar 30 segundos después de la redirección
        time.sleep(180)
        # print("Esperando 30 segundos después de la redirección.")

    except Exception as e:
        print(f"Error: {e}")

    # No cerrar el navegador para depuración
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    main()
