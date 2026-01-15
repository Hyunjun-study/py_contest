import os
import sys
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# 기존 서버 코드 가져오기 (API 호출 함수 재사용)
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.realestate_server import call_apt_rent_api

load_dotenv()

# ==========================================
# 1. 사용자 예산 설정 (여기만 수정하세요!)
# ==========================================
USER_BUDGET = 10000     # 예: 2억 (단위: 만원)
USER_RENT_BUDGET = 30   # 예: 50만원 (단위: 만원)
TARGET_DATE = "202506"  # 조회할 기준 년월

# ==========================================
# 2. 지역 데이터 정의
# ==========================================

# 사용자가 제공한 전체 지역 코드 (앞 4자리 기준)
FULL_CITY_MAP = {
    # 서울특별시 (제외)
    "1111": "서울특별시 종로구", "1114": "서울특별시 중구", "1117": "서울특별시 용산구", 
    "1168": "서울특별시 강남구", "1171": "서울특별시 송파구",
    
    # 부산광역시 (기장군 포함)
    "2611": "부산광역시 중구", "2644": "부산광역시 강서구", "2647": "부산광역시 연제구", "2671": "부산광역시 기장군",
    
    # 경기도 (외곽/군 지역 포함)
    "4111": "경기도 수원시", "4113": "경기도 성남시", "4128": "경기도 고양시", "4146": "경기도 용인시",
    "4115": "경기도 의정부시", "4117": "경기도 안양시", "4119": "경기도 부천시", "4121": "경기도 광명시",
    "4122": "경기도 평택시", "4125": "경기도 동두천시", "4127": "경기도 안산시", "4129": "경기도 과천시",
    "4131": "경기도 구리시", "4136": "경기도 남양주시", "4137": "경기도 오산시", "4139": "경기도 시흥시",
    "4141": "경기도 군포시", "4143": "경기도 의왕시", "4145": "경기도 하남시", "4148": "경기도 파주시",
    "4150": "경기도 이천시", "4155": "경기도 안성시", "4157": "경기도 김포시", "4159": "경기도 화성시",
    "4161": "경기도 광주시", "4163": "경기도 양주시", "4165": "경기도 포천시", "4167": "경기도 여주시",
    "4180": "경기도 연천군", "4182": "경기도 가평군", "4183": "경기도 양평군",

    # 충청남도
    "4413": "충청남도 천안시", "4420": "충청남도 아산시", "4425": "충청남도 계룡시", 
    "4480": "충청남도 예산군", "4479": "충청남도 청양군",

    # 경상남도
    "4812": "경상남도 창원시", "4817": "경상남도 진주시", "4824": "경상남도 거제시", "4825": "경상남도 양산시",

    # 강원/충북/전북/전남/경북/제주
    "5111": "강원특별자치도 춘천시", "5113": "강원특별자치도 원주시", "5115": "강원특별자치도 강릉시",
    "5177": "강원특별자치도 정선군", "5175": "강원특별자치도 영월군", # (추가: 이전에 언급하신 곳)
    "4311": "충청북도 청주시", "5211": "전북특별자치도 전주시", "5221": "전북특별자치도 김제시", # (추가)
    "4611": "전라남도 목포시", "4711": "경상북도 포항시", "5011": "제주특별자치도 제주시"
}

# 🚨 [핵심] 지역 소멸 위험 지역 필터 리스트 (행안부 지정 인구감소지역 및 군 단위 위주)
# 여기에 포함된 코드만 실제 API 조회를 수행합니다.
EXTINCTION_RISK_CODES = [
    "2671", # 부산 기장군
    "4125", # 경기 동두천시 (일부 기준 포함)
    "4165", # 경기 포천시
    "4167", # 경기 여주시
    "4180", # 경기 연천군
    "4182", # 경기 가평군
    "4183", # 경기 양평군
    "4480", # 충남 예산군
    "4479", # 충남 청양군
    "5115", # 강원 강릉시 (인구 감소 추세 포함)
    "5177", # 강원 정선군
    "5175", # 강원 영월군
    "5221", # 전북 김제시
    "4611", # 전남 목포시 (구도심 공동화 포함)
    # 필요하면 여기에 코드를 더 추가하거나 빼면 됩니다.
]

# ==========================================
# 3. 로직 구현
# ==========================================

def get_target_regions():
    """전체 맵에서 소멸 위험 지역만 필터링"""
    targets = {}
    for code, name in FULL_CITY_MAP.items():
        # 4자리 코드가 리스트에 있거나, 앞 4자리가 일치하는 경우
        if code in EXTINCTION_RISK_CODES:
            # API는 5자리 코드를 원하므로 뒤에 '0'을 붙여줌 (예: 4479 -> 44790)
            full_code = code + "0"
            targets[full_code] = name
    return targets

def parse_and_count(xml_text, region_name):
    """API 결과 XML을 파싱해서 조건에 맞는 매물 수 카운트"""
    if not xml_text: return 0
    
    try:
        root = ET.fromstring(xml_text)
        items = root.findall(".//item")
        
        valid_count = 0
        
        for item in items:
            # 1. 값 추출 (deposit, monthlyRent 등 가능한 모든 키 확인)
            deposit_raw = (item.findtext("deposit") or item.findtext("보증금액") or item.findtext("depositAmount") or "0")
            rent_raw = (item.findtext("monthlyRent") or item.findtext("월세금액") or "0")
            
            # 2. 전처리 (콤마 제거)
            deposit_val = int(deposit_raw.replace(",", "").strip())
            rent_val = int(rent_raw.replace(",", "").strip())
            
            # 3. 필터링 (사용자 예산 이내인지 확인)
            if deposit_val <= USER_BUDGET and rent_val <= USER_RENT_BUDGET:
                valid_count += 1
                
        return valid_count

    except Exception as e:
        # print(f"⚠️ {region_name} 파싱 중 에러: {e}")
        return 0

def main():
    print(f"\n🚀 [분석 시작] 예산: {USER_BUDGET:,}만원 / 월세: {USER_RENT_BUDGET:,}만원 이하")
    print(f"📅 기준 년월: {TARGET_DATE}")
    
    target_regions = get_target_regions()
    print(f"🎯 분석 대상 지역: {len(target_regions)}곳 (지역 소멸 위험 지역 한정)")
    print("-" * 60)

    results = {}

    # 각 지역별로 순회
    for code, name in target_regions.items():
        print(f"📡 {name} ({code}) 조회 중...", end=" ", flush=True)
        
        # API 호출 (한 번에 100개씩 요청)
        response = call_apt_rent_api(lawdcd=code, deal_ymd=TARGET_DATE, num_rows=100)
        
        if response["status"] == "ok":
            # XML 텍스트 추출
            content = response.get("text")
            if not content and response.get("data"):
                 print("failed (JSON type)")
                 continue

            count = parse_and_count(content, name)
            results[name] = count
            print(f"✅ {count}개 발견")
        else:
            print("❌ API 호출 실패")

    # ==========================================
    # 4. 결과 집계 및 상위 5개 출력
    # ==========================================
    print("-" * 60)
    print(f"🏆 [TOP 5] 내 예산({USER_BUDGET}만원/{USER_RENT_BUDGET}만원)으로 갈 수 있는 지역")
    print("-" * 60)

    # 개수 기준 내림차순 정렬
    sorted_regions = sorted(results.items(), key=lambda x: x[1], reverse=True)

    rank = 1
    has_data = False
    for name, count in sorted_regions[:5]:
        if count > 0:
            print(f"🥇 {rank}위 : {name} (매물 {count}개)")
            rank += 1
            has_data = True
        
    if not has_data:
        print("😢 조건에 맞는 매물이 있는 지역을 찾지 못했습니다.")
        print("   (예산이나 월세 한도를 조금만 올려보세요!)")

if __name__ == "__main__":
    main()