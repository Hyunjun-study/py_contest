# test_rent_check.py
import requests
import os
from dotenv import load_dotenv
import xml.dom.minidom

load_dotenv()

def test_rent_api():
    # 1. 환경변수 확인
    api_key = os.getenv("MOLIT_API_KEY")
    base_url = os.getenv("MOLIT_BASE_URL")
    
    print(f"🔗 접속 주소: {base_url}")
    
    if "AptRent" not in base_url:
        print("❌ [오류] .env 파일의 URL이 'AptRent'가 아닙니다! 전월세 주소로 바꿔주세요.")
        return

    # 2. 강릉시(51150), 2025년 6월 데이터 요청 (강릉은 무조건 거래가 있습니다)
    params = {
        "serviceKey": api_key,  # 이미 Decoding된 키라면 그대로 사용
        "LAWD_CD": "51150",     # 강릉시
        "DEAL_YMD": "202506",   # 2025년 6월
        "pageNo": 1,
        "numOfRows": 5
    }

    # API 호출 endpoint 추가
    full_url = f"{base_url}/getRTMSDataSvcAptRent"
    
    print(f"🚀 API 호출 중... (강릉시 202506)")
    
    try:
        response = requests.get(full_url, params=params)
        print(f"📡 응답 코드: {response.status_code}")
        
        # 결과 출력 (보기 좋게 정렬)
        try:
            dom = xml.dom.minidom.parseString(response.text)
            pretty_xml = dom.toprettyxml()
            print(pretty_xml[:1000]) # 앞부분 1000자만 출력
            
            if "<totalCount>0</totalCount>" in response.text:
                print("\n❌ [결과] 데이터가 0건입니다. API 키 권한 문제일 가능성이 높습니다.")
                print("👉 공공데이터포털에서 '국토교통부_아파트전월세 실거래자료' 활용신청을 했는지 확인하세요.")
            elif "<resultCode>00" in response.text:
                print("\n✅ [결과] 성공! 전월세 데이터가 정상적으로 조회됩니다.")
            else:
                print("\n⚠️ [결과] 에러 메시지를 확인하세요.")
                
        except:
            print(response.text)

    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    test_rent_api()