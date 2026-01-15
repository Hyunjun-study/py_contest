// src/App.jsx
import React, { useState } from "react";
import MainPage from "./components/MainPage";
import RecommendationPage from "./components/RecommendationPage"; // 새로 만든 페이지
import ResultsPage from "./components/ResultsPage";
import LoadingPage from "./components/LoadingPage";
import { searchAPI } from "./services/api";

// --- [가짜 데이터] 백엔드 완성 전까지 사용할 추천 결과 ---
const MOCK_RECOMMENDATIONS = [
  {
    regionName: "강원도 강릉시",
    regionCode: "51150",
    houseCount: 24,
    jobCount: 15,
    score: 95,
  },
  {
    regionName: "강원도 원주시",
    regionCode: "51130", // 원주 코드
    houseCount: 45,
    jobCount: 32,
    score: 88,
  },
  {
    regionName: "충청남도 청양군",
    regionCode: "44790",
    houseCount: 8,
    jobCount: 5,
    score: 82,
  },
  {
    regionName: "전북특별자치도 김제시",
    regionCode: "52210",
    houseCount: 12,
    jobCount: 10,
    score: 79,
  },
  {
    regionName: "강원도 영월군",
    regionCode: "51750",
    houseCount: 6,
    jobCount: 3,
    score: 75,
  },
];

// --- [유틸리티] 직무 텍스트에서 필터 코드 추출 ---
const getJobFiltersFromProfile = (jobString) => {
  if (!jobString) return {};
  const text = jobString.toLowerCase().replace(/\s/g, "");
  const filters = {};

  const jobFields = {
    IT: "R600020",
    개발: "R600020",
    정보통신: "R600020",
    경영: "R600002",
    사무: "R600002",
    회계: "R600002",
    의료: "R600006",
    간호: "R600006",
    병원: "R600006",
    건설: "R600014",
    현장: "R600014",
    생산: "R600015",
    기계: "R600015",
    농업: "R600024",
    농사: "R600024",
    귀농: "R600024",
    연구: "R600025",
  };

  for (const [key, code] of Object.entries(jobFields)) {
    if (text.includes(key)) {
      filters["ncsCdLst"] = code;
      console.log(`💼 직무 필터 적용: ${key} -> ${code}`);
      break;
    }
  }
  return filters;
};

function App() {
  // --- 상태 관리 ---
  // 단계: 'main'(입력) -> 'analyzing'(분석중) -> 'recommendation'(추천결과) -> 'loading_details'(상세로딩) -> 'results'(최종결과)
  const [currentPage, setCurrentPage] = useState("main");

  const [userProfile, setUserProfile] = useState(null); // 사용자 입력 정보 저장
  const [recommendations, setRecommendations] = useState([]); // 추천 지역 리스트

  const [searchData, setSearchData] = useState(null);
  const [error, setError] = useState(null);

  // 로딩바 상태
  const [loadingStatus, setLoadingStatus] = useState({
    summary: { loading: false, completed: false, error: null },
    jobs: { loading: false, completed: false, error: null },
    realestate: { loading: false, completed: false, error: null },
    policies: { loading: false, completed: false, error: null },
  });

  // 최종 결과 데이터
  const [resultData, setResultData] = useState({
    summary: null,
    jobs: null,
    realestate: null,
    policies: null,
  });

  // --- [Step 1] 메인 페이지: 프로필 입력 완료 핸들러 ---
  const handleProfileSubmit = (profileData) => {
    console.log("👤 프로필 입력 완료:", profileData);
    setUserProfile(profileData);

    // 1. 분석 로딩 화면으로 전환
    setCurrentPage("analyzing");

    // 2. (가짜) 서버 분석 시뮬레이션 (2.5초 후 추천 페이지로 이동)
    setTimeout(() => {
      setRecommendations(MOCK_RECOMMENDATIONS);
      setCurrentPage("recommendation");
    }, 2500);
  };

  // --- [Step 2] 추천 페이지: 지역 선택 핸들러 ---
  const handleSelectRegion = async (regionCode) => {
    // 선택한 지역 이름 찾기 (목록에서)
    const selectedRegion = recommendations.find(
      (r) => r.regionCode === regionCode
    );
    const regionName = selectedRegion
      ? selectedRegion.regionName
      : "선택한 지역";

    console.log(`🎯 지역 선택됨: ${regionName} (${regionCode})`);
    console.log("🚀 상세 정보 로딩 시작...");

    // 1. 상세 로딩 화면으로 전환
    setCurrentPage("loading_details");
    setError(null);

    const newSearchData = {
      prompt: regionName, // 결과 페이지 표시용
      regionCode: regionCode,
    };
    setSearchData(newSearchData);

    // 2. 직무 필터 준비
    const jobFilters = getJobFiltersFromProfile(userProfile.job);

    // 3. 실제 API 호출 시작
    await loadAllAPIData(regionCode, jobFilters, userProfile, regionName);
  };

  // --- [Step 3] 실제 데이터 로딩 (기존 로직 재사용) ---
  const updateApiStatus = (apiName, status) => {
    setLoadingStatus((prev) => ({ ...prev, [apiName]: status }));
  };

  const updateApiResult = (apiName, data) => {
    setResultData((prev) => ({ ...prev, [apiName]: data }));
  };

  const loadAllAPIData = async (
    regionCode,
    jobFilters,
    profile,
    regionName
  ) => {
    // 초기화
    const tempResults = {
      summary: null,
      jobs: null,
      realestate: null,
      policies: null,
    };
    const apiNames = ["summary", "jobs", "realestate", "policies"];

    // 상태 초기화
    apiNames.forEach((name) =>
      updateApiStatus(name, { loading: false, completed: false, error: null })
    );
    setResultData(tempResults);

    // 개별 API 호출 정의
    const apiCalls = [
      {
        name: "summary",
        fn: () => {
          console.log(" [DEBUG] Summary API 호출");
          // AI에게 "OOO 지역에 대해 알려줘" 라고 요청
          return searchAPI.comprehensive(regionName, regionCode);
        },
      },
      {
        name: "jobs",
        fn: () => {
          console.log(" [DEBUG] Jobs API 호출");
          return searchAPI.jobs(regionCode, jobFilters);
        },
      },
      {
        name: "realestate",
        fn: () => {
          console.log(" [DEBUG] Realestate API 호출 (프로필 포함)");
          // ✅ 여기서 userProfile을 넘겨주므로 필터링이 작동합니다!
          // 예산 문자열(예: "2억")은 백엔드에서 파싱하므로 그대로 넘겨도 됨 (maxPrice는 null로)
          return searchAPI.realestate(regionCode, "202506", null, profile);
        },
      },
      {
        name: "policies",
        fn: () => {
          console.log("🤖 [DEBUG] Policies API 호출");
          // 정책 검색도 프로필 기반 AI 분석 요청
          return searchAPI.policies(regionCode, regionName, null, profile);
        },
      },
    ];

    // 병렬 실행 및 개별 상태 업데이트
    const promises = apiCalls.map(async ({ name, fn }) => {
      updateApiStatus(name, { loading: true, completed: false, error: null });
      try {
        const result = await fn();
        updateApiResult(name, result);
        updateApiStatus(name, { loading: false, completed: true, error: null });
        return result;
      } catch (err) {
        console.error(`❌ ${name} 실패:`, err);
        updateApiStatus(name, {
          loading: false,
          completed: false,
          error: err.message,
        });
        return null;
      }
    });

    await Promise.allSettled(promises);

    // 로딩 완료 후 결과 페이지로 이동 (1초 지연)
    setTimeout(() => {
      setCurrentPage("results");
    }, 1000);
  };

  // 메인으로 돌아가기
  const handleBackToMain = () => {
    setCurrentPage("main");
    setSearchData(null);
    setUserProfile(null);
    setRecommendations([]);
  };

  // --- 렌더링 ---
  return (
    <div className="App">
      {/* 1. 메인 페이지 (프로필 입력) */}
      {currentPage === "main" && <MainPage onSubmit={handleProfileSubmit} />}

      {/* 2. 분석 중 로딩 화면 */}
      {currentPage === "analyzing" && (
        <LoadingPage
          searchPrompt="전국 소멸 위험 지역 데이터 분석 중..."
          loadingStatus={{}} // 빈 상태 (단순 로딩 애니메이션)
          customMessage={`${userProfile?.name}님에게 딱 맞는 지역을 찾고 있어요!`}
        />
      )}

      {/* 3. 추천 결과 페이지 (TOP 5 선택) */}
      {currentPage === "recommendation" && (
        <RecommendationPage
          userName={userProfile?.name}
          recommendations={recommendations}
          onSelectRegion={handleSelectRegion}
        />
      )}

      {/* 4. 상세 정보 로딩 화면 */}
      {currentPage === "loading_details" && (
        <LoadingPage
          searchPrompt={`${searchData?.prompt} 상세 정보 조회 중`}
          loadingStatus={loadingStatus}
        />
      )}

      {/* 5. 최종 결과 페이지 */}
      {currentPage === "results" && searchData && (
        <ResultsPage
          searchData={searchData}
          resultData={resultData}
          onBackToMain={handleBackToMain}
        />
      )}
    </div>
  );
}

export default App;
