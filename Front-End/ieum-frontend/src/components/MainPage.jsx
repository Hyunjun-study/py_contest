// src/components/MainPage.jsx
import React, { useState, useRef, useEffect } from "react";
import "./MainPage.css";
import Modal from "./Modal";
import logo from "../assets/ieum_logo.svg";
import slogan from "../assets/slogan.svg";
import BackgroundPattern from "../assets/background.svg?react";

function MainPage({ onSubmit, error }) {
  // --- 상태 관리 ---
  // 1. 단계 관리: 'profile' (정보입력) -> 'chat' (검색)
  const [step, setStep] = useState("profile");

  // 2. 사용자 프로필 데이터
  const [profile, setProfile] = useState({
    name: "",
    gender: "",
    age: "",
    budget: "", // 전체 예산 (전세/매매 등)
    rent_budget: "", // 보증금/월세
    job: "",
    policy: "",
    car: "", // 자차 유무
  });

  // --- 기존 Chat 관련 State ---
  const [isInputActive, setIsInputActive] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inputError, setInputError] = useState("");

  const promptWrapperRef = useRef(null);
  const sendButtonRef = useRef(null);
  const textareaRef = useRef(null);

  // --- 모달 상태 ---
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  // --- 핸들러: 프로필 입력 ---
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    // 간단한 유효성 검사 (이름과 나이는 필수)
    if (!profile.name || !profile.age) {
      alert("정확한 추천을 위해 이름과 나이는 꼭 입력해주세요!");
      return;
    }
    // 다음 단계로 전환
    setStep("chat");
  };

  // --- 핸들러: 채팅 검색 (기존 로직 + 프로필 전달) ---
  const handleInputChange = (e) => {
    const value = e.target.value;
    setPrompt(value);
    if (inputError) setInputError("");
  };

  const handleSubmit = async (event) => {
    if (event) event.preventDefault();
    if (isSubmitting) return;

    const cleanPrompt = prompt.trim();
    if (!cleanPrompt) {
      setInputError("검색할 내용을 입력해주세요.");
      return;
    }

    try {
      setIsSubmitting(true);
      setInputError("");
      // ⭐ 여기서 [검색어 + 프로필 정보]를 함께 상위 컴포넌트(App.jsx)로 전달
      await onSubmit(cleanPrompt, profile);
    } catch (err) {
      console.error("제출 오류:", err);
      setInputError(err?.message || "검색 중 오류가 발생했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(null);
    }
  };

  // ... (handleClickOutside, handleInputClick 등 기존 UI 로직 유지) ...
  const handleClickOutside = (event) => {
    if (
      promptWrapperRef.current &&
      !promptWrapperRef.current.contains(event.target)
    ) {
      if (inputError || !prompt.trim()) {
        setIsInputActive(false);
        setInputError("");
        setPrompt("");
      }
    }
  };

  useEffect(() => {
    if (isInputActive) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isInputActive, prompt, inputError]);

  const handleInputClick = () => {
    setIsInputActive(true);
    setInputError("");
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  // --- 렌더링 ---
  // --- 렌더링 ---
  return (
    <div className="main-container">
      {/* 헤더 (유지) */}
      <header className="header">
        <img src={logo} alt="ieum logo" className="logo" />
        <img src={slogan} alt="slogan" className="slogan" />
        <nav className="nav-links">
          <a
            href="#about"
            onClick={(e) => {
              e.preventDefault();
              setIsAboutModalOpen(true);
            }}
          >
            서비스 소개
          </a>
          <a>|</a>
          <a
            href="#help"
            onClick={(e) => {
              e.preventDefault();
              setIsHelpModalOpen(true);
            }}
          >
            도움말
          </a>
        </nav>
      </header>

      {/* 👇 여기서부터 수정됨: main 태그와 center-interaction-area가 추가되어야 합니다 */}
      <main className="content">
        <h1>
          나의 새로운 시작은
          <br />
          어디서?
        </h1>
        <p>이음이 당신에게 꼭 맞는 지역을 찾아드려요</p>

        <div className="center-interaction-area">
          {/* [Step 1] 프로필 입력 카드 */}
          {step === "profile" && (
            <div className="profile-card fade-in">
              <div className="profile-header">
                <h3>👋 맞춤 추천을 위한 기본 정보</h3>
                <p>입력하신 정보는 정착지 추천에만 사용됩니다.</p>
              </div>

              <form
                onSubmit={handleProfileSubmit}
                className="profile-form-vertical"
              >
                <div className="input-group">
                  <label>이름 / 닉네임</label>
                  <input
                    name="name"
                    placeholder="홍길동"
                    value={profile.name}
                    onChange={handleProfileChange}
                    autoFocus
                  />
                </div>

                <div className="input-group-row">
                  <div className="input-half">
                    <label>나이</label>
                    <input
                      name="age"
                      type="number"
                      placeholder="26"
                      value={profile.age}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="input-half">
                    <label>성별</label>
                    <select
                      name="gender"
                      value={profile.gender}
                      onChange={handleProfileChange}
                    >
                      <option value="">선택</option>
                      <option value="male">남성</option>
                      <option value="female">여성</option>
                    </select>
                  </div>
                </div>

                <div className="input-group">
                  <label>희망 직무</label>
                  <input
                    name="job"
                    placeholder="예: IT 개발자, 간호사, 마케터"
                    value={profile.job}
                    onChange={handleProfileChange}
                  />
                </div>

                <div className="input-group-row">
                  <div className="input-half">
                    <label>총 주거 예산</label>
                    <input
                      name="budget"
                      placeholder="예: 2억"
                      value={profile.budget}
                      onChange={handleProfileChange}
                    />
                  </div>
                  <div className="input-half">
                    <label>월세 희망액</label>
                    <input
                      name="rent_budget"
                      placeholder="예: 50만원"
                      value={profile.rent_budget}
                      onChange={handleProfileChange}
                    />
                  </div>
                </div>

                <div className="input-group">
                  <label>관심 정책 키워드</label>
                  <input
                    name="policy"
                    placeholder="예: 청년월세지원, 창업대출"
                    value={profile.policy}
                    onChange={handleProfileChange}
                  />
                </div>

                <div className="input-group">
                  <label>자차 보유 여부</label>
                  <select
                    name="car"
                    value={profile.car}
                    onChange={handleProfileChange}
                  >
                    <option value="">선택해주세요</option>
                    <option value="yes">있음</option>
                    <option value="no">없음</option>
                  </select>
                </div>

                <button type="submit" className="profile-submit-btn-large">
                  입력 완료
                </button>
              </form>
            </div>
          )}

          {/* [Step 2] 채팅 입력창 */}
          {step === "chat" && (
            <div className="prompt-wrapper fade-in" ref={promptWrapperRef}>
              {!isInputActive ? (
                <button
                  className="prompt-placeholder"
                  onClick={handleInputClick}
                  disabled={isSubmitting}
                >
                  나에게 맞는 조건 입력하기
                  <span className="enter-icon">↵</span>
                </button>
              ) : (
                <form onSubmit={handleSubmit} className="prompt-form">
                  <div className="input-shell">
                    <textarea
                      ref={textareaRef}
                      className={`prompt-input ${inputError ? "error" : ""} ${
                        isSubmitting ? "submitting" : ""
                      }`}
                      placeholder={`안녕하세요 ${profile.name}님!\n원하는 지역이나 구체적인 조건을 자유롭게 이야기해주세요.`}
                      value={prompt}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      autoFocus
                      disabled={isSubmitting}
                      maxLength={500}
                    />
                    <button
                      type="submit"
                      className={`send-button ${isSubmitting ? "loading" : ""}`}
                      ref={sendButtonRef}
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? "검색 중..." : "Send"}
                    </button>
                    <div className="input-counter">{prompt.length}/500</div>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>
        {/* 👆 여기까지 center-interaction-area 닫힘 */}

        {(inputError || error) && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {inputError || error}
          </div>
        )}

        <div className="background-container">
          <BackgroundPattern />
        </div>
      </main>
      {/* 👆 여기서 main 태그 닫힘 */}

      <Modal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
        title="서비스 소개"
      >
        <p>
          <strong>'이음'은 새로운 시작을 꿈꾸는 당신을 위한 다리입니다.</strong>
        </p>
        <p>
          낯선 지역으로의 이주를 고민할 때, 가장 큰 막막함은 정보의 부족입니다.
          어디에 어떤 일자리가 있는지, 내가 받을 수 있는 혜택은 무엇인지, 집은
          어디에 구해야 할지... '이음'은 흩어져 있는 정보들을 한데 모아 당신의
          합리적인 의사결정을 돕습니다.
        </p>
        <p>
          단순한 정보 제공을 넘어, 당신의 조건과 희망에 꼭 맞는 '새로운 삶의
          터전'을 찾아주는 것. 그것이 바로 '이음'이 존재하는 이유입니다.
        </p>
      </Modal>

      <Modal
        isOpen={isHelpModalOpen}
        onClose={() => setIsHelpModalOpen(false)}
        title="도움말"
      >
        <p>
          <strong>'이음' 서비스는 어떻게 사용하나요?</strong>
        </p>
        <p>
          '이음'은 당신의 새로운 시작을 위한 최적의 지역을 찾아주는
          서비스입니다. 아래 입력창에 원하는 직업, 필요한 정부 지원 정책, 그리고
          예상 주거 예산 등을 자유롭게 입력해보세요.
        </p>
        <p>
          <strong>예시:</strong>
          <br />
          "강릉시에서 IT 프론트엔드 개발자로 일하고 싶어. 청년 버팀목 대출이
          가능한 전세 2억 이하의 집이었으면 좋겠어."
        </p>
        <p>
          입력된 정보를 바탕으로, 'ieum'이 일자리 정보, 주거 정보, 관련 정책을
          종합하여 가장 적합한 지역을 추천해 드립니다.
        </p>
      </Modal>
    </div>
  );
}

export default MainPage;
