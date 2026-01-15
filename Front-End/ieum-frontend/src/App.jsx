// src/App.jsx
import React, { useState } from "react";
import MainPage from "./components/MainPage";
import RecommendationPage from "./components/RecommendationPage";
import ResultsPage from "./components/ResultsPage";
import LoadingPage from "./components/LoadingPage";
import { searchAPI } from "./services/api";

// --- [가짜 데이터] 6개 지역의 상세 정보를 미리 정의 (나중에 백엔드에서 받아올 구조) ---
const MOCK_FULL_DATA = {
  51150: {
    // 강릉시
    summary: {
      text: "강릉시는 관광과 해양 관련 일자리가 풍부하며, 청년 주거 지원 정책이 활발합니다.",
    },
    jobs: {
      totalCount: 15,
      jobs: [
        {
          title: "[강릉] 관광 데이터 분석가",
          company: "오션뷰테크",
          salary: "연봉 3,200만원",
        },
        { title: "웹 개발자", company: "강릉소프트", salary: "연봉 3,000만원" },
      ],
    },
    realestate: {
      price_analysis: { sample_count: 24 },
      properties: [
        { dealAmount: "전세 1억 8,000", aptNm: "교동택지 아파트" },
        { dealAmount: "보증금 2,000 / 월세 45", aptNm: "포남동 원룸" },
      ],
    },
    policies: {
      totalCount: 5,
      policies: [
        { servNm: "강릉시 청년 월세 지원" },
        { servNm: "청년 창업 보증 대출" },
      ],
    },
  },
  51130: {
    // 원주시
    summary: {
      text: "원주시는 공공기관 이전으로 안정적인 일자리가 많고 교통이 편리합니다.",
    },
    jobs: {
      totalCount: 32,
      jobs: [
        {
          title: "공공데이터 인턴",
          company: "건강보험공단",
          salary: "월 210만원",
        },
      ],
    },
    realestate: {
      price_analysis: { sample_count: 45 },
      properties: [{ dealAmount: "전세 1억 5,000", aptNm: "무실동 아파트" }],
    },
    policies: { totalCount: 8, policies: [{ servNm: "원주 정착 지원금" }] },
  },
  44790: {
    // 청양군
    summary: {
      text: "청양군은 귀농/귀촌 지원이 강력하며 주거 비용이 매우 저렴합니다.",
    },
    jobs: {
      totalCount: 5,
      jobs: [
        {
          title: "스마트팜 관리자",
          company: "청양농협",
          salary: "연봉 3,500만원",
        },
      ],
    },
    realestate: {
      price_analysis: { sample_count: 8 },
      properties: [{ dealAmount: "전세 8,000", aptNm: "읍내리 빌라" }],
    },
    policies: {
      totalCount: 12,
      policies: [{ servNm: "귀농 정착금 지원" }, { servNm: "청년 쉐어하우스" }],
    },
  },
  52210: {
    // 김제시
    summary: {
      text: "김제시는 스마트팜 혁신 밸리가 있어 농업 관련 창업 기회가 많습니다.",
    },
    jobs: {
      totalCount: 10,
      jobs: [
        { title: "농업 연구원", company: "김제센터", salary: "연봉 3,400만원" },
      ],
    },
    realestate: {
      price_analysis: { sample_count: 12 },
      properties: [{ dealAmount: "월세 30", aptNm: "신풍동 주택" }],
    },
    policies: { totalCount: 6, policies: [{ servNm: "청년 농부 지원" }] },
  },
  51750: {
    // 영월군
    summary: {
      text: "영월군은 문화 관광 콘텐츠 기획자와 크리에이터를 위한 지원이 좋습니다.",
    },
    jobs: {
      totalCount: 3,
      jobs: [
        {
          title: "박물관 큐레이터",
          company: "영월문화재단",
          salary: "연봉 2,800만원",
        },
      ],
    },
    realestate: {
      price_analysis: { sample_count: 6 },
      properties: [{ dealAmount: "전세 6,000", aptNm: "영월읍 아파트" }],
    },
    policies: { totalCount: 4, policies: [{ servNm: "문화 예술인 지원" }] },
  },
  44800: {
    // 예산군
    summary: {
      text: "예산군은 백종원 거리 등 요식업 창업과 관광 산업이 성장 중입니다.",
    },
    jobs: {
      totalCount: 7,
      jobs: [
        { title: "매장 관리직", company: "예산시장", salary: "월 250만원" },
      ],
    },
    realestate: {
      price_analysis: { sample_count: 18 },
      properties: [{ dealAmount: "전세 1억", aptNm: "산성리 아파트" }],
    },
    policies: { totalCount: 7, policies: [{ servNm: "청년 상인 대출" }] },
  },
};

// 추천 리스트 데이터 (요약본)
const MOCK_RECOMMENDATIONS_LIST = [
  {
    regionName: "강원도 강릉시",
    regionCode: "51150",
    houseCount: 24,
    jobCount: 15,
    policyCount: 12,
    score: 95,
  },
  {
    regionName: "강원도 원주시",
    regionCode: "51130",
    houseCount: 45,
    jobCount: 32,
    policyCount: 12,
    score: 88,
  },
  {
    regionName: "충청남도 청양군",
    regionCode: "44790",
    houseCount: 8,
    jobCount: 5,
    policyCount: 12,
    score: 82,
  },
  {
    regionName: "전북특별자치도 김제시",
    regionCode: "52210",
    houseCount: 12,
    jobCount: 10,
    policyCount: 12,
    score: 79,
  },
  {
    regionName: "강원도 영월군",
    regionCode: "51750",
    houseCount: 6,
    jobCount: 3,
    policyCount: 12,
    score: 75,
  },
  {
    regionName: "충청남도 예산군",
    regionCode: "44800",
    houseCount: 18,
    jobCount: 7,
    policyCount: 12,
    score: 72,
  },
];

function App() {
  // --- 상태 관리 ---
  // 단계: 'main'(입력) -> 'analyzing'(로딩:여기서 다 가져옴) -> 'recommendation'(결과6개) -> 'results'(상세:즉시이동)
  const [currentPage, setCurrentPage] = useState("main");

  const [userProfile, setUserProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  // 모든 지역의 상세 데이터를 미리 저장해두는 곳
  const [allRegionsData, setAllRegionsData] = useState({});

  const [searchData, setSearchData] = useState(null);
  const [resultData, setResultData] = useState(null);

  // --- [Step 1] 메인 페이지: 프로필 입력 완료 ---
  const handleProfileSubmit = (profileData) => {
    console.log("👤 프로필 입력 완료:", profileData);
    setUserProfile(profileData);

    // 1. 분석 로딩 화면으로 전환 (여기서 백엔드 연결)
    setCurrentPage("analyzing");

    // ============================================================
    // 🚀 [핵심] 여기서 백엔드 API를 호출하여 6개 지역 데이터를 싹 다 가져와야 함
    // 지금은 가짜 데이터(MOCK)로 시뮬레이션하지만, 나중에 여기서 API 호출
    // ============================================================

    setTimeout(() => {
      // 1. 추천 리스트 생성 (서버 응답 가정)
      setRecommendations(MOCK_RECOMMENDATIONS_LIST);

      // 2. 각 지역별 상세 데이터 미리 저장 (서버 응답 가정)
      setAllRegionsData(MOCK_FULL_DATA);

      // 3. 분석 완료 -> 추천 페이지로 이동
      setCurrentPage("recommendation");
    }, 3000); // 3초 분석 시뮬레이션
  };

  // --- [Step 2] 추천 페이지: 지역 선택 (로딩 없이 즉시 이동!) ---
  const handleSelectRegion = (regionCode) => {
    // 1. 선택한 지역 이름 찾기
    const selectedRegion = recommendations.find(
      (r) => r.regionCode === regionCode
    );
    const regionName = selectedRegion
      ? selectedRegion.regionName
      : "선택한 지역";

    console.log(`🎯 지역 선택됨: ${regionName} (${regionCode})`);
    console.log("🚀 저장된 데이터로 즉시 상세 페이지 이동!");

    // 2. 미리 받아둔 데이터(allRegionsData)에서 꺼내기
    const preloadedData = allRegionsData[regionCode];

    if (preloadedData) {
      // 데이터 셋팅
      setSearchData({ prompt: regionName, regionCode: regionCode });
      setResultData(preloadedData);

      // 3. 로딩 화면 없이 바로 결과 페이지로!
      setCurrentPage("results");
    } else {
      alert("데이터를 불러오는 중 오류가 발생했습니다.");
    }
  };

  const handleBackToRecommendations = () => {
    console.log("🔙 추천 목록으로 돌아갑니다.");
    setCurrentPage("recommendation");
    // userProfile과 recommendations는 유지해야 함!
    // searchData만 초기화 (선택 취소)
    setSearchData(null);
  };

  const handleBackToMain = () => {
    setCurrentPage("main");
    setSearchData(null);
    setUserProfile(null);
    setRecommendations([]);
    setAllRegionsData({});
  };

  // --- 렌더링 ---
  return (
    <div className="App">
      {/* 1. 입력 화면 */}
      {currentPage === "main" && <MainPage onSubmit={handleProfileSubmit} />}

      {/* 2. 분석 로딩 화면 (백엔드 통신 구간) */}
      {currentPage === "analyzing" && (
        <LoadingPage
          searchPrompt="전국 소멸 위험 지역 데이터 정밀 분석 중..."
          loadingStatus={{}}
          customMessage={`${userProfile?.name}님의 조건(예산, 직무)에 맞는 최적의 지역 6곳을 선별하고 있습니다.`}
        />
      )}

      {/* 3. 6개 지역 추천 화면 */}
      {currentPage === "recommendation" && (
        <RecommendationPage
          userName={userProfile?.name}
          recommendations={recommendations}
          onSelectRegion={handleSelectRegion}
          onBackToMain={handleBackToMain}
        />
      )}

      {/* 4. 최종 상세 결과 화면 (로딩 없이 즉시 뜸) */}
      {currentPage === "results" && searchData && resultData && (
        <ResultsPage
          searchData={searchData}
          resultData={resultData}
          onBackToMain={handleBackToMain}
          onBackToRecommendations={handleBackToRecommendations}
        />
      )}
    </div>
  );
}

export default App;
