import "./styles.css";

const reportSections = [
  "아이디어 요약",
  "타깃 사용자",
  "관련 키워드",
  "검색 수요 분석",
  "경쟁 앱 분석",
  "리뷰 기반 사용자 불만",
  "수익화 구조",
  "1인 MVP 구현 범위",
  "리스크 요약",
  "추천 방향",
  "데이터 신뢰도",
];

function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">CSE4181-SW-MVP</p>
        <h1>앱 아이디어 검증 리포트 플랫폼</h1>
        <p>
          이 화면은 MVP 구현을 위한 frontend skeleton입니다. 실제 데이터 수집,
          LLM 분석, report generation 기능은 이후 단계에서 연결합니다.
        </p>
      </section>

      <section className="panel" aria-labelledby="idea-form-title">
        <h2 id="idea-form-title">아이디어 입력</h2>
        <label htmlFor="idea">App idea</label>
        <textarea
          id="idea"
          name="idea"
          rows="6"
          placeholder="예: 혼자 사는 직장인을 위한 냉장고 재료 기반 식단 추천 앱"
        />
        <button type="button">리포트 생성 준비 중</button>
      </section>

      <section className="panel" aria-labelledby="report-section-title">
        <h2 id="report-section-title">예상 리포트 섹션</h2>
        <ol className="section-list">
          {reportSections.map((section) => (
            <li key={section}>{section}</li>
          ))}
        </ol>
      </section>
    </main>
  );
}

export default App;
