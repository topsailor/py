from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import sys
import os
import requests
from urllib.parse import unquote, urljoin, urlparse

def extract_content(element, depth=0, is_first_level=True, base_indent=2, base_url='https://durumee.notion.site', image_folder='extracted_content'):
    result = []
    if isinstance(element, str):
        return []
    
    os.makedirs(image_folder, exist_ok=True)
    
    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        heading_level = int(element.name[1])
        heading_text = element.get_text(strip=True)
        result.append(('#' * heading_level) + ' ' + heading_text)
    elif element.name == 'div' and element.has_attr('contenteditable') and element['contenteditable'] == 'false':
        placeholder = element.get('placeholder', '').lower()
        text = element.get_text(strip=True)
        link = element.find('a', class_='notion-link-mention-token')
        img = element.find('img')
        
        if is_first_level:
            indent = ' ' * base_indent
        else:
            indent = ' ' * (base_indent + (depth - 1) * 2)
        prefix = '- ' if placeholder == '리스트' else ''
        
        content = []
        
        if img:
            src = img.get('src', '')
            if src:
                src = unquote(src)
                if src.startswith('/'):
                    src = urljoin(base_url, src)
                
                try:
                    parsed_url = urlparse(src)
                    if parsed_url.netloc == 'durumee.notion.site':
                        query_params = parsed_url.query.split('&')
                        for param in query_params:
                            if param.startswith('id='):
                                image_id = param.split('=')[1]
                                break
                        else:
                            image_id = 'unknown'
                        filename = f"notion_image_{image_id}.png"
                    else:
                        filename = os.path.basename(parsed_url.path)
                    
                    local_path = os.path.join(image_folder, filename)
                    
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        content.append(f"![{filename}]({local_path})")
                    else:
                        print(f"Failed to download image: {src}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image {src}: {e}")
        
        if link:
            link_text = link.get_text(strip=True)
            link_url = link.get('href', '')
            content.append(f"[{link_text}]({link_url})")
        elif text:
            content.append(text)
        
        result.append(indent + prefix + ' '.join(content))
    elif element.name == 'div' and 'notion-code-block' in element.get('class', []):
        code_content = element.find('div', class_='line-numbers')
        if code_content:
            code_text = code_content.get_text()
            language = element.find('div', {'role': 'button', 'aria-disabled': 'true'})
            language = language.get_text(strip=True) if language else 'plaintext'
            code_text = '\n'.join([line for line in code_text.split('\n') if not line.strip() in ['Python복사', 'ALT']])
            result.append(f"```{language}\n{code_text.strip()}\n```")

    for child in element.children:
        if isinstance(child, str):
            continue
        if child.name:
            if child.name == 'div' and 'notion-bulleted_list-block' in child.get('class', []):
                child_result = extract_content(child, depth + 1, False, base_indent, base_url, image_folder)
            else:
                child_result = extract_content(child, depth, False, base_indent, base_url, image_folder)
            result.extend(child_result)
    
    return result

def main(url):
    # ChromeDriver 경로 설정
    try:
        service = Service('C:\\cdw\\chromedriver.exe')
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        sys.exit(1)

    # Webdriver 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저를 열지 않고 백그라운드에서 실행

    # Webdriver 초기화
    driver = webdriver.Chrome(service=service, options=options)

    # 웹페이지 접속
    # url = "https://durumee.notion.site/14a4b7a3564f4f74967cd9e8f27a0c4c"
    
  
    driver.get(url)

    # 페이지가 완전히 로드될 때까지 대기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "notion-page-content")))

    # 추가적인 대기 시간 (JavaScript가 모든 내용을 렌더링할 시간을 줌)
    time.sleep(5)

    # 페이지 소스 가져오기
    page_source = driver.page_source

    # # 원본 HTML 저장
    # with open('original_html.html', 'w', encoding='utf-8') as f:
    #     f.write(page_source)

    # print("원본 HTML이 'original_html.html' 파일로 저장되었습니다.")

    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(page_source, 'html.parser')

    # # 파싱된 HTML 저장
    # with open('parsed_html.html', 'w', encoding='utf-8') as f:
    #     f.write(soup.prettify())

    # print("파싱된 HTML이 'parsed_html.html' 파일로 저장되었습니다.")

    # 메인 컨텐츠 영역 찾기
    main_content = soup.find('main', class_='notion-frame')

    # 결과를 저장할 리스트
    extracted_text = []

    if main_content:
        layout_contents = main_content.find_all('div', class_='layout-content')
        for layout in layout_contents:
            extracted_text.extend(extract_content(layout))

    # 추출된 텍스트를 하나의 문자열로 연결
    final_text = '\n'.join(extracted_text)

    # 연속된 빈 줄 제거
    final_text = re.sub(r'\n{3,}', '\n\n', final_text)

    # 결과 출력
    print(final_text)

    # 결과를 파일로 저장
    with open('extracted_content.md', 'w', encoding='utf-8') as f:
        f.write(final_text)

    print("추출된 내용이 'extracted_content.md' 파일로 저장되었습니다.")

    # Webdriver 종료
    driver.quit()

    # # 텍스트 파일로 저장
    # with open('notion_crawling_result.txt', 'w', encoding='utf-8') as f:
    #     f.writelines(content_to_save)

    # print("크롤링 결과가 'notion_crawling_result.txt' 파일로 저장되었습니다.")

if __name__ == "__main__":
    url = "https://durumee.notion.site/fa9a32255e2f4297ab5b5dfd632bb6cb"
    main(url)
