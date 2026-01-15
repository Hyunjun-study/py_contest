# src/web_api_handler.py - 수정된 버전
from typing import Dict, Any, Optional, List
from datetime import datetime

# 상대 import 방식으로 변경
from .enhanced_orchestrator import EnhancedOrchestrator
from .final_chatbot import PerfectChatbot

class WebAPIHandler:
    def __init__(self):
        self.orchestrator = EnhancedOrchestrator()
        self.chatbot = PerfectChatbot()
        
        # 🗺️ 지역코드 → 광역(도)명 매핑 (표시용)
        self.PROVINCE_BY_CODE = {
            "51150": "강원",  # 강릉 → 강원
            "51770": "강원",  # 정선 → 강원
            "51750": "강원",  # 영월 → 강원
            "52210": "전북",  # 김제 → 전북
            "44790": "충남",  # 청양 → 충남
        }
        
        # 🔧 학력 코드 매핑 테이블 (클래스 속성으로 이동)
        self.EDUCATION_CODE_MAPPING = {
            "R7010": "학력무관",
            "R7020": "고등학교졸업",
            "R7030": "고등학교졸업 이상", 
            "R7040": "전문대학졸업",
            "R7050": "대학교졸업",
            "R7060": "대학원 석사졸업", 
            "R7070": "대학원 박사졸업",
            "R7080": "기타"
        }

        # 🔧 고용형태 코드 매핑 (클래스 속성으로 이동)
        self.HIRE_TYPE_CODE_MAPPING = {
            "R1010": "정규직",
            "R1020": "무기계약직",
            "R1030": "기간제계약직",
            "R1040": "비정규직",
            "R1050": "청년인턴(체험형)",
            "R1060": "청년인턴(채용형)",
            "R1070": "기타"
        }

        # 🆕 채용구분 코드 매핑 추가
        self.RECRUIT_TYPE_CODE_MAPPING = {
            "R2010": "신입",
            "R2020": "경력", 
            "R2030": "신입+경력",
            "R2040": "외국인 전형"
        }
    
    def _format_user_profile_to_text(self, profile) -> str:
        if not profile:
            return ""
        
        return f"""
        [사용자 프로필 정보]
        - 이름: {profile.name}
        - 나이: {profile.age if profile.age else '미입력'}
        - 성별: {profile.gender if profile.gender else '미입력'}
        - 희망 직무: {profile.job if profile.job else '미입력'}
        - 주거 예산: {profile.budget if profile.budget else '미입력'} (월세 희망: {profile.rent_budget if profile.rent_budget else '미입력'})
        - 관심 정책: {profile.policy if profile.policy else '없음'}
        - 자차 보유: {'있음' if profile.car == 'yes' else '없음'}
        """

    def format_education_requirement(self, code_str):
        """학력 코드를 한글로 변환 - 개선된 로직"""
        if not code_str:
            return "정보 없음"
        
        codes = [code.strip() for code in code_str.split(',') if code.strip()]
        
        # 🎯 학력무관이 포함되어 있으면 학력무관만 표시
        if "R7010" in codes:
            return "학력무관"
        
        # 🎯 학력 순서 정의 (낮은 순부터)
        education_order = {
            "R7020": 1,  # 고등학교졸업
            "R7030": 2,  # 고등학교졸업 이상  
            "R7040": 3,  # 전문대학졸업
            "R7050": 4,  # 대학교졸업
            "R7060": 5,  # 대학원 석사졸업
            "R7070": 6,  # 대학원 박사졸업
            "R7080": 7   # 기타
        }
        
        # 코드를 학력 순서대로 정렬
        valid_codes = [code for code in codes if code in education_order]
        
        if not valid_codes:
            # 매핑되지 않은 코드들
            return ', '.join([self.EDUCATION_CODE_MAPPING.get(code, code) for code in codes])
        
        # 가장 낮은 학력과 가장 높은 학력 찾기
        sorted_codes = sorted(valid_codes, key=lambda x: education_order[x])
        
        if len(sorted_codes) == 1:
            return self.EDUCATION_CODE_MAPPING.get(sorted_codes[0], sorted_codes[0])
        
        # 연속된 범위인 경우 "X 이상" 형태로 표시
        min_code = sorted_codes[0]
        max_code = sorted_codes[-1]
        
        # 🎯 범위로 표시하는 경우
        if len(sorted_codes) >= 3:  # 3개 이상이면 범위로
            min_education = self.EDUCATION_CODE_MAPPING.get(min_code, min_code)
            return f"{min_education} 이상"
        
        # 🎯 개별 표시하는 경우 (2개 정도)
        formatted_codes = [self.EDUCATION_CODE_MAPPING.get(code, code) for code in sorted_codes]
        return ', '.join(formatted_codes)

    def format_hire_type(self, code_str):
        """고용형태 코드를 한글로 변환 - 개선된 로직"""
        if not code_str:
            return "정보 없음"
        
        codes = [code.strip() for code in code_str.split(',') if code.strip()]
        
        # 🎯 중복 제거 및 우선순위 정렬
        hire_type_priority = {
            "R1010": 1,  # 정규직 (최우선)
            "R1020": 2,  # 무기계약직
            "R1040": 3,  # 비정규직
            "R1030": 4,  # 기간제계약직
            "R1060": 5,  # 청년인턴(채용형)
            "R1050": 6,  # 청년인턴(체험형)
            "R1070": 7   # 기타
        }
        
        # 우선순위에 따라 정렬
        valid_codes = [code for code in codes if code in hire_type_priority]
        sorted_codes = sorted(valid_codes, key=lambda x: hire_type_priority.get(x, 999))
        
        # 🎯 최대 2개까지만 표시 (너무 길어지지 않게)
        display_codes = sorted_codes[:2]
        
        formatted_codes = [self.HIRE_TYPE_CODE_MAPPING.get(code, code) for code in display_codes]
        result = ', '.join(formatted_codes)
        
        # 더 많은 타입이 있으면 "외 N개" 추가
        if len(sorted_codes) > 2:
            additional_count = len(sorted_codes) - 2
            result += f" 외 {additional_count}개"
        
        return result

    def format_category_display(self, policy: Dict) -> str:
        """
        정책 카테고리를 깔끔하게 표시 (중복 제거 강화)
        """
        large_category = policy.get("lclsfNm", "")  # 대분류
        medium_category = policy.get("mclsfNm", "")  # 중분류
        
        # 🔥 강화된 중복 제거 로직
        if large_category and medium_category:
            # 1. 완전히 같은 경우
            if large_category.strip() == medium_category.strip():
                return large_category.strip()
            
            # 2. 콤마로 구분된 여러 값이 있는 경우 처리
            large_parts = [part.strip() for part in large_category.split(',') if part.strip()]
            medium_parts = [part.strip() for part in medium_category.split(',') if part.strip()]
            
            # 3. 대분류와 중분류에서 중복되는 부분 제거
            unique_parts = []
            
            # 대분류 먼저 추가 (중복 제거)
            for part in large_parts:
                if part and part not in unique_parts:
                    unique_parts.append(part)
            
            # 중분류에서 대분류와 중복되지 않는 것만 추가
            for part in medium_parts:
                if part and part not in unique_parts:
                    unique_parts.append(part)
            
            # 4. 결과 반환
            if len(unique_parts) == 1:
                return unique_parts[0]
            elif len(unique_parts) > 1:
                return " > ".join(unique_parts)
            else:
                return large_category or medium_category or "기타"
        
        elif large_category:
            # 대분류만 있는 경우, 콤마 분리된 중복 제거
            parts = list(dict.fromkeys([part.strip() for part in large_category.split(',') if part.strip()]))
            return parts[0] if len(parts) == 1 else ", ".join(parts)
        
        elif medium_category:
            # 중분류만 있는 경우, 콤마 분리된 중복 제거  
            parts = list(dict.fromkeys([part.strip() for part in medium_category.split(',') if part.strip()]))
            return parts[0] if len(parts) == 1 else ", ".join(parts)
        
        else:
            return "기타"
    
    async def search_comprehensive(self, query: str, region_code: str = "44790", max_price: Optional[int] = None, user_profile: Any = None) -> Dict[str, Any]:
        """요약 페이지용 - 전체 데이터 통합"""
        try:
            # 자연어 의도 분석
            intent = self.chatbot.analyze_user_intent(query)
            if region_code:
                intent["region_mentioned"] = region_code

            parsed_price = self.chatbot._parse_price_from_text(query)
            print(f"🔍 검색어: {query}")
            print(f"🔍 파싱된 가격: {parsed_price}")
            print(f"🔍 전달받은 max_price: {max_price}")

            if max_price:
                intent["max_price"] = max_price
            else:
                # 자연어에서 파싱된 가격이 없으면 직접 전달된 가격 사용
                parsed_price = self.chatbot._parse_price_from_text(query)
                if parsed_price:
                    intent["max_price"] = parsed_price

            print(f"🔍 최종 intent[max_price]: {intent.get('max_price')}")
            
            # 모든 타입 검색 강제
            intent["search_jobs"] = True
            intent["search_realestate"] = True
            intent["search_policies"] = True
            
            # 각 영역별 데이터 수집
            raw_data = await self._get_raw_data(intent)
            
            # 요약 정보 생성
            summary = self._generate_summary(raw_data, region_code)
            
            return {
                "success": True,
                "summary": summary,
                "preview_data": {
                    "jobs": raw_data["jobs"][:3],
                    "realestate": raw_data["realestate"][:3],
                    "policies": raw_data["policies"][:3]
                },
                "region_info": {
                    "code": region_code,
                    "name": self.chatbot.get_region_name(region_code)
                },
                "search_metadata": {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "intent_type": intent.get("type", "comprehensive")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_jobs_only(self, region_code: str, filters: Dict = None, user_profile: Any = None) -> Dict[str, Any]:
        """일자리 페이지용 - final_chatbot.py와 동일한 로직 사용"""
        try:
            # 🎯 final_chatbot.py와 정확히 같은 방식으로 채용정보 검색
            job_result = self.orchestrator.call_recruitment_tool(
                'listRecruitments',
                {
                    'pageNo': 1,
                    'numOfRows': 50,  # final_chatbot.py와 동일
                    'filters': {**filters} if filters else {}
                }
            )
            
            jobs = []
            if job_result["status"] == "success":
                raw_jobs = job_result["result"].get("data", {}).get("result", [])
                
                # 🎯 final_chatbot.py와 동일한 지역 필터링 및 정렬 적용
                filtered_jobs = raw_jobs
                if filters and "ncsCdLst" in filters:
                    requested_code = filters["ncsCdLst"]
                    filtered_jobs = [
                        job for job in raw_jobs
                        if requested_code in job.get("ncsCdLst", "")
                    ]
                jobs = self.chatbot.filter_and_sort_jobs_by_region(filtered_jobs, region_code)
            
            # 🎯 final_chatbot.py의 format_job_results 함수와 동일한 포맷팅을 JSON으로 변환
            formatted_jobs = []
            region_name = self.chatbot.get_region_name(region_code)
            
            # ✅ 표시용 광역명 (강원/전북/충남 고정)
            province_name = self.PROVINCE_BY_CODE.get(region_code, self.chatbot.get_region_name(region_code))

            for i, job in enumerate(jobs[:20], 1):  # 상위 20개
                title = job.get("recrutPbancTtl", "제목 없음")
                company = job.get("instNm", "기관명 없음")
                hire_type = job.get("hireTypeNmLst", "")
                region = job.get("workRgnNmLst", "")
                deadline = job.get("pbancEndYmd", "")
                ncs_field = job.get("ncsCdNmLst", "")

                # 🎯 학력요건 포맷팅 (개선된 로직 사용)
                education_code = job.get("acbgCondLst", "")
                formatted_education = self.format_education_requirement(education_code)
                
                # 🎯 고용형태 포맷팅 (개선된 로직 사용)
                hire_type_code = job.get("hireTypeNmLst", "")
                formatted_hire_type_detailed = self.format_hire_type(hire_type_code)
                
                # 🎯 기본 고용형태 (제목용, 간단하게)
                basic_hire_type = hire_type.split(',')[0] if hire_type else ""
                
                # 마감일 포맷팅 (final_chatbot.py와 동일)
                formatted_deadline = ""
                if deadline and len(deadline) == 8:
                    formatted_deadline = f"{deadline[:4]}.{deadline[4:6]}.{deadline[6:]}"
                
                # ✅ 표시 규칙: 항상 광역명 기준으로 요약
                region_display = province_name
                if region:
                    region_count = region.count(',') + 1
                    if region_count > 1:
                        region_display = f"{province_name} 외 {region_count-1}개 지역"
                    else:
                        region_display = province_name
                
                # final_chatbot.py와 동일한 구조로 포맷팅
                formatted_job = {
                    **job,  # 원본 데이터 유지

                    # final_chatbot.py에서 표시하는 추가 정보들
                    "display_number": i,
                    "display_title": f"{i}. {company} ({hire_type})",
                    "formatted_title": title,
                    "formatted_company": company,
                    "formatted_hire_type": hire_type,
                    "formatted_region": region_display,
                    "formatted_deadline": formatted_deadline if formatted_deadline else "미정",
                    "formatted_ncs_field": ncs_field,
                    "formatted_education": formatted_education,
                    "formatted_hire_type_detailed": formatted_hire_type_detailed if formatted_hire_type_detailed != basic_hire_type else None,
                    "education_code_original": education_code,  # 원본 코드 보존
                    "hire_type_code_original": hire_type_code,   # 원본 코드 보존
                                        
                    # 추가 필드들
                    "acbg_cond": job.get("acbgCondLst", ""),
                    "career_cond": job.get("creerCondLst", ""),
                    "major_field": job.get("mjrfldNmLst", ""),
                    "recruit_count": job.get("rcritNmprCo", ""),
                    "work_type": job.get("workTypeNmLst", ""),
                    "salary_type": job.get("salaryTypeNmLst", ""),
                    "contact_info": job.get("cntctNo", ""),
                    "recruit_start_date": job.get("pbancBgngYmd", ""),
                    "application_method": job.get("aplyMthdNmLst", ""),
                    
                    # 🆕 채용구분 추가 - 올바른 필드명 사용
                    "recruit_type_code": job.get("recrutSe", ""),
                    "formatted_recruit_type": job.get("recrutSeNm", "") or "미정"  # 빈 값일 때 "미정"
                }
                
                formatted_jobs.append(formatted_job)
            
            # 통계 계산 (final_chatbot.py의 _calculate_job_stats와 동일)
            statistics = self._calculate_job_stats_detailed(jobs)
            
            return {
                "success": True,
                "jobs": formatted_jobs,
                "statistics": statistics,
                "total_count": len(jobs),
                "filters_applied": filters,
                "region_info": {
                    "code": region_code,
                    "name": region_name
                },
                # final_chatbot.py 스타일 메시지 추가
                "summary_message": f"📋 **{region_name} 지역의 채용정보를 찾을 수 없습니다.**" if not jobs else f"📋 **채용정보** (총 {len(jobs)}건, 지역 관련성 순)"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_job_stats_detailed(self, jobs: List[Dict]) -> Dict[str, Any]:
        """상세 채용 통계 계산 (final_chatbot.py 스타일)"""
        if not jobs:
            return {
                "total": 0, 
                "by_category": {}, 
                "by_type": {},
                "by_education": {},
                "by_region": {},
                "by_deadline": {}
            }
        
        categories = {}
        types = {}
        education = {}
        regions = {}
        deadlines = {}
        
        for job in jobs:
            # 직무분야별 통계
            ncs_field = job.get("ncsCdNmLst", "기타")
            if ncs_field:
                main_category = ncs_field.split(",")[0] if "," in ncs_field else ncs_field
                categories[main_category] = categories.get(main_category, 0) + 1
            
            # 고용형태별 통계
            hire_type = job.get("hireTypeNmLst", "기타")
            types[hire_type] = types.get(hire_type, 0) + 1
            
            # 학력조건별 통계
            acbg_cond = job.get("acbgCondLst", "기타")
            education[acbg_cond] = education.get(acbg_cond, 0) + 1
            
            # 마감일별 통계
            deadline = job.get("pbancEndYmd", "")
            if deadline and len(deadline) == 8:
                month = f"{deadline[:4]}-{deadline[4:6]}"
                deadlines[month] = deadlines.get(month, 0) + 1
        
        return {
            "total": len(jobs),
            "by_category": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            "by_type": dict(sorted(types.items(), key=lambda x: x[1], reverse=True)),
            "by_education": dict(sorted(education.items(), key=lambda x: x[1], reverse=True)),
            "by_deadline": dict(sorted(deadlines.items()))
        }
    
    async def search_realestate_only(self, region_code: str, deal_ymd: str = "202506", max_price: Optional[int] = None, user_profile: Any = None) -> Dict[str, Any]:
        """부동산 페이지용 - 실거래가 전문"""
        try:
            apt_result = self.orchestrator.call_realestate_tool(
                'getApartmentTrades',
                {
                    'lawdcd': region_code,
                    'deal_ymd': deal_ymd,
                    'pageNo': 1,
                    'numOfRows': 30
                }
            )
            
            properties = []
            if apt_result["status"] == "success":
                apt_text = apt_result["result"].get("text", "")
                properties = self.chatbot.parse_apartment_xml(apt_text)

                # 가격 필터링 로직
                if max_price and max_price > 0:
                    properties = [
                        prop for prop in properties
                        if int(prop.get("dealAmount", "0").replace(",", "")) <= max_price
                    ]
            
            # 🗺️ 지역명으로 좌표 변환 (간단히 매핑 추가)
            REGION_COORDS = {
                "51150": (37.7519, 128.8761),  # 강릉
                "52210": (35.8032, 126.8800),  # 김제
                "44790": (36.4595, 126.8028),  # 청양
                "51770": (37.3802, 128.6631),  # 정선
                "51750": (37.1833, 128.4619),  # 영월
            }
            lat, lng = REGION_COORDS.get(region_code, (37.5665, 126.9780))  # 기본값 서울
            
            return {
                "success": True,
                "properties": properties,
                "price_analysis": self._analyze_price_trends(properties),
                "deal_period": deal_ymd,
                "region_info": {
                    "code": region_code,
                    "name": self.chatbot.get_region_name(region_code),
                    "lat": lat,
                    "lng": lng
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    
    # ✅ [수정] search_policies_only 함수
    async def search_policies_only(self, region_code: str, keywords: str = None, user_query: str = None, user_profile: Any = None) -> Dict[str, Any]:
        
        print(f"🤖 [DEBUG] search_policies_only 호출")
        print(f"📍 [DEBUG] region_code: {region_code}")
        print(f"💬 [DEBUG] user_query: {user_query}")

        # 1. 프로필 정보를 텍스트로 변환
        profile_context = self._format_user_profile_to_text(user_profile)
        
        # 2. 사용자 질문에 프로필 정보를 합침 (AI에게 전달할 최종 프롬프트)
        augmented_query = user_query
        if user_profile:
            augmented_query = f"{profile_context}\n\n[사용자 질문]: {user_query}\n\n(위 프로필 정보를 최우선으로 고려해서 답변해줘)"
            print(f"🧠 [DEBUG] AI 프롬프트 보강됨:\n{augmented_query}")

        policies = []
        ai_analysis = None
        ai_insights = None

        target_category = None
        if user_profile and user_profile.policy:
            # 사용자가 입력한 관심사가 있으면 그걸 카테고리 필터로 씀
            # (참고: API가 정확한 카테고리명(일자리, 주거, 교육 등)을 요구할 수 있으니 
            #  사용자가 '교육'이라고 입력하면 더 정확함)
            target_category = user_profile.policy

        try:
            # 🎯 오케스트레이터 호출 (여기서 user_query 대신 augmented_query를 전달!)
            policy_result = self.orchestrator.call_youth_policy_tool(
                'searchPoliciesByRegion',
                {
                    'regionCode': region_code,
                    'pageNum': 1,
                    'pageSize': 30,
                    'categories': target_category,
                    'user_query': augmented_query  # 👈 핵심 변경 사항
                }
            )
            
            if policy_result["status"] == "success":
                all_policies = policy_result["result"].get("policies", [])

                ai_analysis = policy_result["result"].get("ai_analysis")
                ai_insights = policy_result["result"].get("ai_insights")
                
                # 디버깅 로그
                if ai_analysis:
                    print(f"🤖 [DEBUG] AI 분석 결과 포함됨")
                if ai_insights:
                    print(f"🤖 [DEBUG] AI 인사이트 포함됨")

                # 필터링 및 정렬
                active_policies = self.chatbot.filter_active_policies(all_policies)
                policies = self.chatbot.filter_and_sort_policies_by_region(active_policies, region_code)
            
            # 포맷팅 로직 (기존 유지)
            formatted_policies = []
            for i, policy in enumerate(policies[:30], 1):  # 상위 30개
                
                # --- 날짜 포맷팅 함수 ---
                def format_date(date_str):
                    if date_str and len(date_str) == 8 and date_str.isdigit():
                        return f"{date_str[:4]}년 {date_str[4:6]}월 {date_str[6:]}일"
                    return date_str

                def format_apply_period(apply_str):
                    if not apply_str: return ""
                    if " ~ " in apply_str:
                        dates = apply_str.split(" ~ ")
                        if len(dates) == 2:
                            start = format_date(dates[0].strip())
                            end = format_date(dates[1].strip())
                            return f"{start} ~ {end}"
                    return format_date(apply_str)

                # --- 데이터 가공 ---
                business_start = policy.get("bizPrdBgngYmd", "")
                business_end = policy.get("bizPrdEndYmd", "")
                business_period = ""
                if business_start and business_end:
                    # 값이 유효한지 체크
                    if "0000" not in business_start and "0000" not in business_end:
                        business_period = f"{format_date(business_start)} ~ {format_date(business_end)}"
                
                # 적용 범위
                zip_codes = policy.get('zipCd', '')
                if zip_codes:
                    cnt = len(zip_codes.split(',')) if ',' in zip_codes else 1
                    scope_display = f"전국 ({cnt}개 지역)" if cnt >= 50 else (f"광역 ({cnt}개 지역)" if cnt > 10 else "지역특화")
                else:
                    scope_display = "범위미상"

                # 신청 기간
                apply_period = policy.get("aplyYmd", "")
                formatted_apply_period = format_apply_period(apply_period) if apply_period else ""
                
                # 상세 링크
                policy_no = policy.get("plcyNo", "")
                detail_url = f"https://www.youthcenter.go.kr/youthPolicy/ythPlcyTotalSearch/ythPlcyDetail/{policy_no}" if policy_no else ""

                # 카테고리
                category_display = self.format_category_display(policy)

                # 최종 객체 생성
                formatted_policy = {
                    **policy,
                    "display_title": f"{i}. {policy.get('plcyNm', '정책명 없음')}",
                    "formatted_explanation": policy.get('plcyExplnCn', '설명 없음'),
                    "category_display": category_display,
                    "scope_display": scope_display,
                    "keywords_display": policy.get('plcyKywdNm', ''),
                    "institution_display": policy.get('sprvsnInstCdNm', ''),
                    "support_content_display": policy.get('plcySprtCn', ''),
                    "business_period_display": business_period,
                    "apply_period_display": formatted_apply_period if formatted_apply_period else "상시접수",
                    "support_scale_display": f"{policy.get('sprtSclCnt', '0')}명" if policy.get('sprtSclCnt') != "0" else "",
                    "apply_method_display": policy.get('plcyAplyMthdCn', ''),
                    "additional_conditions_display": policy.get('addAplyQlfcCndCn', ''),
                    "participation_target_display": policy.get('ptcpPrpTrgtCn', ''),
                    "detail_url": detail_url
                }
                
                formatted_policies.append(formatted_policy)
            
            return {
                "success": True,
                "policies": formatted_policies,
                "categories": self._group_policies_by_category(policies),
                "total_count": len(policies),
                "keywords_used": keywords,
                "region_info": {
                    "code": region_code,
                    "name": self.chatbot.get_region_name(region_code)
                },
                "ai_analysis": ai_analysis if ai_analysis else None,
                "ai_insights": ai_insights if ai_insights else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_raw_data(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """원시 데이터 수집"""
        region_code = intent.get("region_mentioned", "44790")
        max_price = intent.get("max_price")
        results = {"jobs": [], "realestate": [], "policies": []}
        
        # 채용정보
        if intent["search_jobs"]:
            job_result = self.orchestrator.call_recruitment_tool(
                'listRecruitments',
                {'pageNo': 1, 'numOfRows': 50, 'filters': intent.get("filters", {})} #rows : 종합 분석 란에 보일 개수
            )
            if job_result["status"] == "success":
                raw_jobs = job_result["result"].get("data", {}).get("result", [])

                filtered_jobs = raw_jobs
                job_filters = intent.get("filters", {})
                if job_filters and "ncsCdLst" in job_filters:
                    requested_code = job_filters["ncsCdLst"]
                    filtered_jobs = [
                        job for job in raw_jobs
                        if requested_code in job.get("ncsCdLst", "")
                    ]

                results["jobs"] = self.chatbot.filter_and_sort_jobs_by_region(filtered_jobs, region_code)
        
        # 부동산
        if intent["search_realestate"]:
            apt_result = self.orchestrator.call_realestate_tool(
                'getApartmentTrades',
                {'lawdcd': region_code, 'deal_ymd': "202506", 'pageNo': 1, 'numOfRows': 15}
            )
            if apt_result["status"] == "success":
                apt_text = apt_result["result"].get("text", "")
                properties = self.chatbot.parse_apartment_xml(apt_text)

                print(f"🏠 필터링 전 매물 수: {len(properties)}")  # 추가
                print(f"🏠 필터링할 최대가격: {max_price}")  # 추가

                # 🆕 가격 필터링 로직 추가
                intent_max_price = intent.get("max_price")  # 변수명 변경
                if intent_max_price and intent_max_price > 0:  # 변수명 변경
                    original_count = len(properties)
                    properties = [
                        prop for prop in properties
                        if int(prop.get("dealAmount", "0").replace(",", "")) <= intent_max_price
                    ]
                    print(f"🏠 필터링 후 매물 수: {len(properties)}")
                results["realestate"] = properties
        
        # 정책
        if intent["search_policies"]:
            policy_result = self.orchestrator.call_youth_policy_tool(
                'searchPoliciesByRegion',
                {'regionCode': region_code, 'pageNum': 1, 'pageSize': 20}
            )
            if policy_result["status"] == "success":
                policies = policy_result["result"].get("policies", [])
                active_policies = self.chatbot.filter_active_policies(policies)
                results["policies"] = self.chatbot.filter_and_sort_policies_by_region(active_policies, region_code)
        
        return results
    
    def _generate_summary(self, raw_data: Dict[str, Any], region_code: str) -> Dict[str, Any]:
        """요약 페이지용 통계 생성"""
        return {
            "region_name": self.chatbot.get_region_name(region_code),
            "total_jobs": len(raw_data["jobs"]),
            "total_properties": len(raw_data["realestate"]),
            "total_policies": len(raw_data["policies"]),
            "avg_property_price": self._calculate_avg_price(raw_data["realestate"]),
            "top_job_categories": self._get_top_job_categories(raw_data["jobs"]),
            "urgent_policies": len([p for p in raw_data["policies"][:5] if self._is_urgent_policy(p)])
        }
    
    def _calculate_avg_price(self, properties: List[Dict]) -> str:
        """평균 매매가 계산"""
        if not properties:
            return "데이터 없음"
        
        prices = []
        for prop in properties:
            price_str = prop.get("dealAmount", "").replace(",", "")
            if price_str.isdigit():
                prices.append(int(price_str))
        
        if prices:
            avg = sum(prices) // len(prices)
            if avg >= 10000:
                return f"{avg//10000}억 {(avg%10000):,}만원"
            else:
                return f"{avg:,}만원"
        return "계산 불가"
    
    def _get_top_job_categories(self, jobs: List[Dict]) -> List[str]:
        """상위 직무분야 추출"""
        categories = {}
        for job in jobs:
            category = job.get("ncsCdNmLst", "").split(",")[0] if job.get("ncsCdNmLst") else "기타"
            categories[category] = categories.get(category, 0) + 1
        
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return [cat[0] for cat in sorted_categories[:3]]
    
    def _analyze_price_trends(self, properties: List[Dict]) -> Dict[str, Any]:
        """가격 트렌드 분석"""
        if not properties:
            return {"trend": "데이터 부족", "price_range": "확인 불가"}
        
        prices = []
        for prop in properties:
            price_str = prop.get("dealAmount", "").replace(",", "")
            if price_str.isdigit():
                prices.append(int(price_str))
        
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            return {
                "trend": "안정세",
                "price_range": f"{min_price:,}만원 ~ {max_price:,}만원",
                "sample_count": len(prices)
            }
        
        return {"trend": "데이터 부족", "price_range": "확인 불가"}
    
    def _group_policies_by_category(self, policies: List[Dict]) -> Dict[str, int]:
        """정책 카테고리별 그룹핑"""
        categories = {}
        for policy in policies:
            category = policy.get("lclsfNm", "기타")
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _is_urgent_policy(self, policy: Dict) -> bool:
        """긴급 정책 여부 판단 (마감 임박)"""
        apply_period = policy.get("aplyYmd", "")
        return "마감" in apply_period or "긴급" in policy.get("plcyNm", "")