// src/components/RecommendationPage.jsx
import React from "react";
import "./RecommendationPage.css"; // (CSS 파일도 필요하면 만드세요, 없으면 인라인 스타일 사용)
import BackgroundPattern from "../assets/background.svg?react";

function RecommendationPage({
  userName,
  recommendations,
  onSelectRegion,
  onBackToMain,
}) {
  return (
    <div className="recommendation-container">
      <button
        className="back-fab fixed-top-left"
        onClick={onBackToMain}
        title="처음 화면으로 돌아가기"
      >
        ← 조건 다시 입력
      </button>

      <div className="recommendation-header fade-in">
        <h1>🎉 {userName}님에게 딱 맞는 지역 TOP 6</h1>
        <p>
          빅데이터 분석 결과, 거주 가능성과 일자리 매칭률이 가장 높은 곳입니다.
        </p>
      </div>

      <div className="cards-grid fade-in-delay">
        {recommendations.map((item, index) => (
          <div
            key={item.regionCode}
            className="region-card"
            onClick={() => onSelectRegion(item.regionCode)} // 클릭 시 상세 페이지 이동
          >
            <div className="rank-badge">{index + 1}위</div>
            <div className="region-name">
              <h2>{item.regionName}</h2>
              <span className="region-code">({item.regionCode})</span>
            </div>

            <div className="stats-preview">
              <div className="stat-item">
                <span className="label">🏠 예산 내 매물</span>
                <span className="value">{item.houseCount}건</span>
              </div>
              <div className="stat-divider-vertical"></div>{" "}
              {/* 세로 구분선 (선택사항) */}
              <div className="stat-item">
                <span className="label">💼 관련 일자리</span>
                <span className="value">{item.jobCount}개</span>
              </div>
              <div className="stat-divider-vertical"></div>{" "}
              {/* 세로 구분선 (선택사항) */}
              <div className="stat-item">
                <span className="label">📜 관련 정책</span>
                <span className="value">{item.policyCount}개</span>
              </div>
            </div>

            <div className="card-footer">상세 정보 보기 →</div>
          </div>
        ))}
      </div>

      <div className="background-container">
        <BackgroundPattern />
      </div>

      {/* 간단한 스타일 (나중에 CSS 파일로 분리 추천) */}
      <style jsx>{`
        .recommendation-container {
          padding: 40px 20px;
          text-align: center;
          max-width: 1200px;
          margin: 0 auto;
          font-family: "Pretendard", sans-serif;
        }
        .recommendation-header h1 {
          font-size: 2rem;
          color: #333;
          margin-bottom: 10px;
        }
        .cards-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
          margin-top: 40px;
        }
        .region-card {
          background: white;
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
          position: relative;
          overflow: hidden;
          border: 1px solid #eee;
        }
        .region-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
          border-color: #646cff;
        }
        .rank-badge {
          position: absolute;
          top: 0;
          left: 0;
          background: #646cff;
          color: white;
          padding: 8px 16px;
          font-weight: bold;
          border-bottom-right-radius: 16px;
        }
        .region-name {
          margin-top: 20px;
          margin-bottom: 20px;
        }
        .region-name h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #2c3e50;
        }
        .stats-preview {
          display: flex;
          justify-content: space-around;
          background: #f8f9fa;
          padding: 15px;
          border-radius: 12px;
          margin-bottom: 20px;
        }
        .stat-item {
          display: flex;
          flex-direction: column;
        }
        .stat-item .label {
          font-size: 0.85rem;
          color: #666;
        }
        .stat-item .value {
          font-size: 1.2rem;
          font-weight: bold;
          color: #333;
        }
        .stat-item .value.highlight {
          color: #646cff;
        }
        .card-footer {
          font-size: 0.9rem;
          color: #888;
          text-align: right;
        }
      `}</style>
    </div>
  );
}

export default RecommendationPage;
