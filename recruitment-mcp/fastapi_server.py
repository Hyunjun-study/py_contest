# fastapi_server.py - 정책만 AI 적용 완전 수정
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.web_api_handler import WebAPIHandler

app = FastAPI(
    title="이음(IEUM) 통합 정보 조회 API",
    description="채용정보 + 부동산 + 청소년정책(AI) 통합 검색 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = WebAPIHandler()

class UserProfile(BaseModel):
    name: str
    gender: Optional[str] = None
    age: Optional[str] = None
    budget: Optional[str] = None      # 예: "2억"
    rent_budget: Optional[str] = None # 예: "50만원"
    job: Optional[str] = None         # 예: "IT 개발자"
    policy: Optional[str] = None      # 예: "청년월세"
    car: Optional[str] = None         # 예: "yes/no"

# === Request/Response 모델들 ===
class SearchRequest(BaseModel):
    query: str
    region_code: str = "44790"
    max_price: Optional[int] = None
    user_profile: Optional[UserProfile] = None

class JobSearchRequest(BaseModel):
    region_code: str
    job_field: Optional[str] = None
    hire_type: Optional[str] = None
    education: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    # 정책만 AI 적용하므로 user_query 제거

class RealestateSearchRequest(BaseModel):
    region_code: str
    deal_ymd: str = "202506"
    max_price: Optional[int] = None
    user_profile: Optional[UserProfile] = None

class PolicySearchRequest(BaseModel):
    region_code: str
    keywords: Optional[str] = None
    user_query: Optional[str] = None  # ⭐ 정책만 AI 적용
    user_profile: Optional[UserProfile] = None

# === API 엔드포인트들 ===
@app.post("/api/search/comprehensive")
async def search_comprehensive(request: SearchRequest):
    """종합 검색 - 기존 방식 (AI 없음)"""
    try:
        print(f" [DEBUG] Comprehensive API 호출: {request.query}")

        if request.user_profile:
            print(f" [DEBUG] 사용자 프로필 수신: {request.user_profile.name}, {request.user_profile.age}세, {request.user_profile.job}")

        result = await handler.search_comprehensive(
            query=request.query,
            region_code=request.region_code,
            max_price=request.max_price,
            user_profile=request.user_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.post("/api/search/jobs")
async def search_jobs(request: JobSearchRequest):
    """일자리 검색 - 기존 방식 (AI 없음)"""
    filters = {}
    if request.job_field:
        filters["ncsCdLst"] = request.job_field
    if request.hire_type:
        filters["hireTypeLst"] = request.hire_type
    if request.education:
        filters["acbgCondLst"] = request.education
    
    try:
        print(f"💼 [DEBUG] Jobs API 호출: {request.region_code}")

        if request.user_profile:
            print(f"👤 [DEBUG] 사용자 프로필 수신: {request.user_profile.name}, {request.user_profile.age}세, {request.user_profile.job}")

        result = await handler.search_jobs_only(
            region_code=request.region_code,
            filters=filters,
            user_profile=request.user_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.post("/api/search/realestate")
async def search_realestate(request: RealestateSearchRequest):
    """부동산 검색 - 기존 방식 (AI 없음)"""
    try:
        print(f"🏠 [DEBUG] Realestate API 호출: {request.region_code}")

        if request.user_profile:
            print(f"👤 [DEBUG] 사용자 프로필 수신: {request.user_profile.name}, {request.user_profile.age}세, {request.user_profile.job}")
        
        result = await handler.search_realestate_only(
            region_code=request.region_code,
            deal_ymd=request.deal_ymd,
            max_price=request.max_price,
            user_profile=request.user_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.post("/api/search/policies")
async def search_policies(request: PolicySearchRequest):
    """정책 검색 - AI 적용 🤖"""
    try:
        print(f"🤖 [DEBUG] Policies API 호출 (AI 모드)")
        print(f"📍 [DEBUG] region_code: {request.region_code}")
        print(f"🔑 [DEBUG] keywords: {request.keywords}")
        print(f"💬 [DEBUG] user_query: {request.user_query}")

        if request.user_profile:
            print(f"👤 [DEBUG] 사용자 프로필 수신: {request.user_profile.name}, {request.user_profile.age}세, {request.user_profile.job}")
        
        # ⭐ AI 분석을 위한 user_query 전달
        result = await handler.search_policies_only(
            region_code=request.region_code,
            keywords=request.keywords,
            user_query=request.user_query,
              user_profile=request.user_profile  # AI 분석용
        )
        
        print(f"🤖 [DEBUG] AI 분석 결과 포함: {bool(result.get('ai_analysis'))}")
        
        return result
    except Exception as e:
        print(f"❌ [DEBUG] Policies API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "message": "이음 API 서버가 정상 동작 중입니다.",
        "ai_features": {
            "policies": "AI 분석 활성화 🤖",
            "jobs": "기본 검색",
            "realestate": "기본 검색", 
            "comprehensive": "기본 검색"
        },
        "supported_regions": {
            "51770": "정선군",
            "51750": "영월군",
            "44790": "청양군",
            "51150": "강릉시",
            "52210": "김제시"
        }
    }

@app.get("/api/regions")
async def get_supported_regions():
    return {
        "regions": {
            "51770": "정선군",
            "51750": "영월군",
            "44790": "청양군", 
            "51150": "강릉시",
            "52210": "김제시"
        }
    }

@app.get("/api/job-fields")
async def get_job_fields():
    return {
        "job_fields": {
            "R600020": "정보통신",
            "R600006": "보건.의료",
            "R600004": "교육.자연.사회과학",
            "R600002": "경영.회계.사무",
            "R600014": "건설",
            "R600025": "연구"
        }
    }

@app.get("/api/ai-status")
async def get_ai_status():
    """AI 기능 상태 확인"""
    return {
        "ai_enabled_services": ["policies"],
        "ai_disabled_services": ["jobs", "realestate", "comprehensive"],
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "message": "정책 검색에만 AI 분석이 적용됩니다."
    }

def run_server():
    uvicorn.run(
        "fastapi_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()