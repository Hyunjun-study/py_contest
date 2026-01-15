// src/App.jsx - 정책만 AI 적용 완전 수정 버전
import React, { useState } from "react";
import MainPage from "./components/MainPage";
import ResultsPage from "./components/ResultsPage";
import LoadingPage from "./components/LoadingPage";
import { searchAPI } from "./services/api";

const parsePrice = (text) => {
  if (
    !text ||
    !["이하", "까지", "안으로", "아래"].some((keyword) =>
      text.includes(keyword)
    )
  ) {
    return null;
  }

  const eokMatch = text.match(/(\d+)억/);
  if (eokMatch) {
    return parseInt(eokMatch[1]) * 10000;
  }

  const manMatch = text.match(/(\d+)만/);
  if (manMatch) {
    return parseInt(manMatch[1]);
  }

  return null;
};

const analyzePromptForJobFilters = (prompt) => {
  const text = prompt.toLowerCase().replace(/\s/g, "");
  const filters = {};

  const jobFields = {
    사업관리: "R600001",
    "경영.회계.사무": "R600002",
    "금융.보험": "R600003",
    "교육.자연.사회과학": "R600004",
    "법률.경찰.소방.교도.국방": "R600005",
    "보건.의료": "R600006",
    "사회복지.종교": "R600007",
    "문화.예술.디자인.방송": "R600008",
    "운전.운송": "R600009",
    영업판매: "R600010",
    "경비.청소": "R600011",
    "이용.숙박.여행.오락.스포츠": "R600012",
    음식서비스: "R600013",
    건설: "R600014",
    기계: "R600015",
    재료: "R600016",
    화학: "R600017",
    "섬유.의복": "R600018",
    "전기.전자": "R600019",
    정보통신: "R600020",
    식품가공: "R600021",
    "인쇄.목재.가구.공예": "R600022",
    "환경.에너지.안전": "R600023",
    농림어업: "R600024",
    연구: "R600025",
  };

  for (const [fieldName, code] of Object.entries(jobFields)) {
    if (text.includes(fieldName.toLowerCase().replace(/\./g, ""))) {
      filters["ncsCdLst"] = code;
      console.log(`💼 직무 분야 "${fieldName}" 발견 -> 필터 코드: ${code}`);
      return filters;
    }
  }

  return filters;
};

function App() {
  const [currentPage, setCurrentPage] = useState("main");
  const [searchData, setSearchData] = useState(null);
  const [error, setError] = useState(null);

  const [loadingStatus, setLoadingStatus] = useState({
    summary: { loading: false, completed: false, error: null },
    jobs: { loading: false, completed: false, error: null },
    realestate: { loading: false, completed: false, error: null },
    policies: { loading: false, completed: false, error: null },
  });

  const [resultData, setResultData] = useState({
    summary: null,
    jobs: null,
    realestate: null,
    policies: null,
  });

  // 지역 분석 함수
  const analyzePromptForRegion = (prompt) => {
    const regionMapping = {
      정선군: "51770",
      정선: "51770",
      영월군: "51750",
      영월: "51750",
      청양군: "44790",
      청양: "44790",
      강릉시: "51150",
      강릉: "51150",
      김제시: "52210",
      김제: "52210",
    };

    const text = prompt.toLowerCase().replace(/\s/g, "");
    const sortedKeys = Object.keys(regionMapping).sort(
      (a, b) => b.length - a.length
    );

    for (const regionName of sortedKeys) {
      if (text.includes(regionName.toLowerCase())) {
        console.log(
          `🎯 지역 매칭 성공: "${regionName}" -> ${regionMapping[regionName]}`
        );
        return regionMapping[regionName];
      }
    }

    console.log("🎯 기본 지역 적용: 청양군 (44790)");
    return "44790";
  };

  // 입력 검증 함수
  const validateInput = (prompt) => {
    const cleanPrompt = prompt.trim();

    if (!cleanPrompt) {
      throw new Error("검색할 내용을 입력해주세요.");
    }

    if (cleanPrompt.length < 2) {
      throw new Error("검색어는 최소 2글자 이상 입력해주세요.");
    }

    if (cleanPrompt.length > 500) {
      throw new Error("검색어는 최대 500자까지 입력 가능합니다.");
    }

    const sanitizedPrompt = cleanPrompt
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
      .replace(/javascript:/gi, "")
      .replace(/on\w+\s*=/gi, "");

    if (sanitizedPrompt !== cleanPrompt) {
      console.warn("⚠️ 입력에서 위험한 스크립트가 제거되었습니다.");
    }

    return sanitizedPrompt;
  };

  const updateApiStatus = (apiName, status) => {
    setLoadingStatus((prev) => ({
      ...prev,
      [apiName]: status,
    }));
  };

  const updateApiResult = (apiName, data) => {
    setResultData((prev) => ({
      ...prev,
      [apiName]: data,
    }));
  };

  // 검색 실행 함수
  const handleSearch = async (prompt, userProfile) => {
    try {
      const validatedPrompt = validateInput(prompt);
      const regionCode = analyzePromptForRegion(validatedPrompt);
      const jobFilters = analyzePromptForJobFilters(validatedPrompt);

      console.log(`🚀 검색 시작: "${validatedPrompt}" -> 지역: ${regionCode}`);

      setCurrentPage("loading");
      setError(null);

      const newSearchData = {
        prompt: validatedPrompt,
        regionCode,
      };
      setSearchData(newSearchData);

      // 초기 상태 설정
      const initialLoadingStatus = {
        summary: { loading: false, completed: false, error: null },
        jobs: { loading: false, completed: false, error: null },
        realestate: { loading: false, completed: false, error: null },
        policies: { loading: false, completed: false, error: null },
      };
      setLoadingStatus(initialLoadingStatus);
      setResultData({
        summary: null,
        jobs: null,
        realestate: null,
        policies: null,
      });

      console.log("[DEBUG] 사용자 프로필 수신:", userProfile);

      // 🚀 개별 추적이 가능한 병렬 API 호출
      await loadAllAPIDataWithIndividualTracking(
        validatedPrompt,
        regionCode,
        jobFilters,
        userProfile
      );
    } catch (err) {
      console.error("❌ 검색 실행 오류:", err);
      setError(err.message);
      setCurrentPage("main");
    }
  };

  // 🚀 개별 추적 가능한 병렬 API 호출
  const loadAllAPIDataWithIndividualTracking = async (
    prompt,
    regionCode,
    jobFilters,
    userProfile
  ) => {
    console.log(" [DEBUG] API 호출 시작");
    console.log(" [DEBUG] 원본 사용자 입력:", prompt);
    console.log(" [DEBUG] 지역 코드:", regionCode);
    console.log(" [DEBUG] 직무 필터:", jobFilters);
    console.log(" [DEBUG] 프로필 데이터:", userProfile);

    const tempResults = {
      summary: null,
      jobs: null,
      realestate: null,
      policies: null,
    };

    const apiCalls = [
      {
        name: "summary",
        promise: handleIndividualAPI(
          "summary",
          () => {
            console.log(" [DEBUG] Summary API 호출");
            return searchAPI.comprehensive(prompt, regionCode);
          },
          tempResults
        ),
      },
      {
        name: "jobs",
        promise: handleIndividualAPI(
          "jobs",
          () => {
            console.log(" [DEBUG] Jobs API 호출 ");
            return searchAPI.jobs(regionCode, jobFilters);
          },
          tempResults
        ),
      },
      {
        name: "realestate",
        promise: handleIndividualAPI(
          "realestate",
          () => {
            const parsedPrice = parsePrice(prompt);
            console.log(" [DEBUG] Realestate API 호출");
            return searchAPI.realestate(regionCode, "202506", parsedPrice);
          },
          tempResults
        ),
      },
      {
        name: "policies",
        promise: handleIndividualAPI(
          "policies",
          () => {
            console.log("🤖 [DEBUG] Policies API 호출 (AI 모드):", {
              regionCode,
              userQuery: prompt,
              userProfile,
            });
            // ⭐ 정책만 AI 적용 - userQuery 전달
            return searchAPI.policies(regionCode, prompt, null, userProfile);
          },
          tempResults
        ),
      },
    ];

    //  모든 API를 병렬로 시작
    apiCalls.forEach(({ name }) => {
      updateApiStatus(name, { loading: true, completed: false, error: null });
    });

    //  모든 API 완료 대기
    const results = await Promise.allSettled(
      apiCalls.map((api) => api.promise)
    );

    //  성공한 API 개수 확인 (tempResults 기준)
    const successfulResults = Object.values(tempResults).filter(
      (data) => data !== null
    );
    const hasAnySuccess = successfulResults.length > 0;

    console.log(` API 결과 요약: 성공 ${successfulResults.length}개`);
    await new Promise((resolve) => setTimeout(resolve, 1000));

    if (hasAnySuccess) {
      console.log("✅ 결과 페이지로 이동");
      setCurrentPage("results");
    } else {
      console.log(" 모든 API 실패");
      setError("모든 데이터를 가져오는데 실패했습니다.");
      setCurrentPage("main");
    }
  };

  // 🎯 개별 API 처리 함수
  const handleIndividualAPI = async (apiName, apiCall, tempResults) => {
    try {
      console.log(`🚀 ${apiName} API 시작`);

      // 🎯 API 호출 실행
      const result = await apiCall();

      // 🎯 성공 시 즉시 상태 업데이트
      updateApiStatus(apiName, {
        loading: false,
        completed: true,
        error: null,
      });
      updateApiResult(apiName, result);

      // 🎯 임시 결과에도 저장
      tempResults[apiName] = result;

      console.log(`✅ ${apiName} API 성공`);

      // 🤖 정책 API 성공 시 AI 결과 확인
      if (apiName === "policies" && result?.ai_analysis) {
        console.log("🤖 🎉 정책 AI 분석 결과 발견!");
      }

      return result;
    } catch (error) {
      console.error(`❌ ${apiName} API 실패:`, error);

      // 🎯 실패 시 즉시 상태 업데이트
      const errorMessage = error.message || `${apiName} API 호출 실패`;
      updateApiStatus(apiName, {
        loading: false,
        completed: false,
        error: errorMessage,
      });
      updateApiResult(apiName, null);

      // 🎯 임시 결과는 null 유지
      tempResults[apiName] = null;

      throw error;
    }
  };

  // 메인 페이지로 돌아가기
  const handleBackToMain = () => {
    setCurrentPage("main");
    setSearchData(null);
    setError(null);
    setLoadingStatus({
      summary: { loading: false, completed: false, error: null },
      jobs: { loading: false, completed: false, error: null },
      realestate: { loading: false, completed: false, error: null },
      policies: { loading: false, completed: false, error: null },
    });
    setResultData({
      summary: null,
      jobs: null,
      realestate: null,
      policies: null,
    });
  };

  return (
    <div className="App">
      {currentPage === "main" && (
        <MainPage onSubmit={handleSearch} error={error} />
      )}

      {currentPage === "loading" && (
        <LoadingPage
          searchPrompt={searchData?.prompt}
          loadingStatus={loadingStatus}
        />
      )}

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
