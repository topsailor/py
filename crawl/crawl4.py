from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os

"""
결제 비밀번호 입력이 완성되지 않음
"""


def save_image(image, filename):
    print("save images")

    if not os.path.exists("keyboard_images"):
        os.makedirs("keyboard_images")
    full_path = os.path.join("keyboard_images", filename)

    if isinstance(image, bytes):  # 원본 스크린샷 (PNG 바이트)
        with open(full_path, "wb") as file:
            file.write(image)
    elif isinstance(image, Image.Image):  # PIL Image
        image.save(full_path)
    elif isinstance(image, np.ndarray):  # NumPy 배열 (OpenCV 이미지)
        cv2.imwrite(full_path, image)

    print(f"Saved {filename}")


# OpenCV 설치 시 numpy 포함, pip install opencv-python
# Pytesseract 설치 pip install pytesseract
# Pillow (PIL) 설치 pip install Pillow
def login_and_order(username, password, product_url):
    driver = webdriver.Chrome()

    try:
        # 11번가 로그인 페이지로 이동
        driver.get("https://login.11st.co.kr/auth/front/login.tmall")

        # 로그인
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "memId"))
        )
        driver.find_element(By.ID, "memId").send_keys(username)
        driver.find_element(By.ID, "memPwd").send_keys(password)
        driver.find_element(By.ID, "loginButton").click()

        # 인라인 레이어 로그인 유지여부 확인
        btn_not_to_keep_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-log-actionid-area="login_keep_layer"]')
            )
        )

        btn_not_to_keep_login.click()

        # 로그인 성공 확인
        WebDriverWait(driver, 10).until(EC.url_contains("11st.co.kr/main"))

        # 상품 페이지로 이동
        driver.get(product_url)

        # 주문하기 버튼 클릭
        btn_buy = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-log-actionid-label="purchase"]')
            )
        )
        btn_buy.click()

        # 휴대전화번호 입력
        btn_process_account = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnAccount"))
        )

        driver.find_element(By.ID, "poptel21").send_keys("3535")
        driver.find_element(By.ID, "poptel31").send_keys("3590")

        btn_process_account.click()

        # 스크린 키보드 이미지 캡처 및 처리
        keyboard_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@id, 'keypad11pay')]")
            )
            # EC.presence_of_element_located((By.ID, "keypad11pay-container"))
        )

        print("진행중")
        keyboard_image = keyboard_element.screenshot_as_png
        save_image(keyboard_image, "1_original.png")
        keyboard_image = Image.open(io.BytesIO(keyboard_image))
        save_image(keyboard_image, "2_pil_image.png")
        keyboard_image = np.array(keyboard_image)
        save_image(keyboard_image, "3_numpy_array.png")
        keyboard_image = cv2.cvtColor(keyboard_image, cv2.COLOR_RGB2BGR)
        save_image(keyboard_image, "4_bgr_image.png")

        # 이미지에서 숫자 인식
        gray = cv2.cvtColor(keyboard_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # pytesseract를 사용하여 숫자 인식
        custom_config = r"--oem 3 --psm 6 outputbase digits"
        numbers = pytesseract.image_to_boxes(thresh, config=custom_config)

        # 숫자와 위치 정보 저장
        number_positions = {}
        for box in numbers.splitlines():
            box = box.split()
            number = box[0]
            x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
            center_x = (x + w) // 2
            center_y = keyboard_image.shape[0] - (y + h) // 2  # y 좌표 변환
            number_positions[number] = (center_x, center_y)

        print(number_positions)

        # 비밀번호 입력 (예: '1234')
        password = "1234"
        for digit in password:
            if digit in number_positions:
                x, y = number_positions[digit]
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(keyboard_element, x, y)
                actions.click()
                actions.perform()
                time.sleep(0.5)  # 각 클릭 사이에 짧은 대기 시간

        time.sleep(50)

    except Exception as e:
        print(f"오류 발생: {e}")

    finally:
        # 브라우저 종료
        # driver.quit()
        pass


# 사용 예
username = "아이디"
password = "비번"
product_url = "https://www.11st.co.kr/products/4620621521"

print(username)

login_and_order(username, password, product_url)
