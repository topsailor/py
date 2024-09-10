import requests
import json
import secret

def get_github_api(username, token, use_spec=True, endpoint=""):
    # GitHub API 엔드포인트
    if use_spec:
        url = f"https://api.github.com/users/{username}/{endpoint}"
    else:
        url = f"https://api.github.com/users/{endpoint}"

    # 인증 헤더 설정
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        # GET 요청 보내기
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 발생

        # JSON 응답 파싱
        api_ret = response.json()
        print(api_ret)
        print(json.dumps(api_ret, indent=2, ensure_ascii=False))

        # 정보 출력
        print(f"{username}의 GitHub 리포지토리 목록:")
        for a_ret in api_ret:
            print(f"- {a_ret['name']}: {a_ret['html_url']}: {a_ret['language']}")

        return api_ret

    except requests.exceptions.RequestException as e:
        print(f"GitHub API 호출 중 오류 발생: {e}")
        
        # return None


# 사용 예시
username = "topsailor"
token = secret.Github_PAT

get_github_api(username, token, False,'emojis')
