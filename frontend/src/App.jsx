import { useState } from "react";

import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const initialForm = {
  idea: "",
  target_customer: "",
  region: "한국",
  service_type: "모바일 앱",
  max_results_per_source: 3,
  use_live_collectors: true,
};

const queryLabels = {
  customer_problem: "고객 문제",
  market: "시장/수요",
  competitors: "경쟁자",
  pricing: "가격/수익화",
  implementation: "구현/API",
  alternatives: "대체재",
  pest: "PEST",
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/reports`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setReport(data);
    } catch (requestError) {
      setError("리포트를 생성하지 못했습니다. Backend 실행 상태를 확인해 주세요.");
      console.error(requestError);
    } finally {
      setIsLoading(false);
    }
  }

  function updateField(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">CSE4181-SW-MVP</p>
        <h1>앱 아이디어 검증 리포트</h1>
        <p>
          검색어를 만들고 공개 source를 수집해 근거 중심의 MVP 조사 리포트를
          생성합니다.
        </p>
      </section>

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <div className="field field-wide">
          <label htmlFor="idea">아이디어</label>
          <textarea
            id="idea"
            name="idea"
            rows="5"
            required
            value={form.idea}
            onChange={(event) => updateField("idea", event.target.value)}
            placeholder="예: 자취생 냉장고 재고 관리 앱"
          />
        </div>

        <div className="field">
          <label htmlFor="target_customer">타겟 고객</label>
          <input
            id="target_customer"
            name="target_customer"
            value={form.target_customer}
            onChange={(event) => updateField("target_customer", event.target.value)}
            placeholder="예: 대학생 자취생, 1인 가구"
          />
        </div>

        <div className="field">
          <label htmlFor="region">지역</label>
          <input
            id="region"
            name="region"
            value={form.region}
            onChange={(event) => updateField("region", event.target.value)}
            placeholder="예: 한국"
          />
        </div>

        <div className="field">
          <label htmlFor="service_type">서비스 유형</label>
          <input
            id="service_type"
            name="service_type"
            value={form.service_type}
            onChange={(event) => updateField("service_type", event.target.value)}
            placeholder="예: 모바일 앱"
          />
        </div>

        <div className="field">
          <label htmlFor="max_results_per_source">Source 수</label>
          <input
            id="max_results_per_source"
            name="max_results_per_source"
            type="number"
            min="1"
            max="10"
            value={form.max_results_per_source}
            onChange={(event) =>
              updateField("max_results_per_source", Number(event.target.value))
            }
          />
        </div>

        <label className="toggle field-wide">
          <input
            type="checkbox"
            checked={form.use_live_collectors}
            onChange={(event) => updateField("use_live_collectors", event.target.checked)}
          />
          <span>공개 collector 사용</span>
        </label>

        <div className="actions field-wide">
          <button type="submit" disabled={isLoading}>
            {isLoading ? "생성 중" : "리포트 생성"}
          </button>
          {error ? <p className="error">{error}</p> : null}
        </div>
      </form>

      {report ? <ReportView report={report} /> : <EmptyState />}
    </main>
  );
}

function EmptyState() {
  return (
    <section className="panel muted-panel">
      <h2>대기 중</h2>
      <p>아이디어를 입력하면 검색어, report section, source 목록이 표시됩니다.</p>
    </section>
  );
}

function ReportView({ report }) {
  const { meta, generated_queries: queries, report: body, sources } = report;

  return (
    <section className="results">
      <div className="summary-band">
        <div>
          <span className={`badge confidence-${meta.confidence_level.toLowerCase()}`}>
            Confidence {meta.confidence_level}
          </span>
          <span className="badge">{meta.llm_used ? "LLM 사용" : "Rule 기반"}</span>
        </div>
        <p>{meta.confidence_reasons.join(" · ")}</p>
        <MetaStatus meta={meta} />
      </div>

      <section className="panel">
        <h2>생성된 검색어</h2>
        <div className="query-grid">
          {Object.entries(queries).map(([key, values]) => (
            <div className="query-group" key={key}>
              <h3>{queryLabels[key] || key}</h3>
              <ul>
                {values.map((value) => (
                  <li key={value}>{value}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="report-grid">
        <ReportSection title="고객 문제" section={body.customer_problem} />
        <ReportSection title="시장 신호" section={body.market_signals} />
        <CompetitorSection section={body.competitors} />
        <ReportSection title="가격/수익화" section={body.pricing} />
        <ImplementationSection section={body.implementation} />
        <PestSection section={body.pest} />
      </section>

      <section className="panel">
        <h2>Unknowns</h2>
        <List items={body.unknowns} emptyText="현재 추가 unknown은 없습니다." />
      </section>

      <section className="panel">
        <h2>Sources</h2>
        <SourceList sources={sources} />
      </section>
    </section>
  );
}

function MetaStatus({ meta }) {
  const collectorErrors = Object.entries(meta.collector_errors || {});

  if (!meta.skipped_collectors.length && !meta.failed_collectors.length && !collectorErrors.length) {
    return null;
  }

  return (
    <div className="meta-grid">
      <MetaList title="Skipped" items={meta.skipped_collectors} />
      <MetaList title="Failed" items={meta.failed_collectors} />
      {collectorErrors.length ? (
        <div className="meta-block">
          <h3>Collector errors</h3>
          <ul>
            {collectorErrors.map(([name, message]) => (
              <li key={name}>
                <strong>{name}</strong>: {message}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

function MetaList({ title, items }) {
  if (!items?.length) {
    return null;
  }

  return (
    <div className="meta-block">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function ReportSection({ title, section }) {
  return (
    <article className="panel">
      <h2>{title}</h2>
      <p>{section.summary}</p>
      <Evidence evidence={section.evidence} />
      <List title="Unverified" items={section.unverified} emptyText="" />
    </article>
  );
}

function CompetitorSection({ section }) {
  return (
    <article className="panel">
      <h2>경쟁 앱</h2>
      {section.items.length ? (
        <ul className="source-list">
          {section.items.map((item) => (
            <li key={item.source_id}>
              <a href={item.url} target="_blank" rel="noreferrer">
                {item.app_name}
              </a>
              <span>
                {[item.category, item.price, item.rating && `${item.rating}점`]
                  .filter(Boolean)
                  .join(" · ")}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p>경쟁 앱 후보가 아직 충분하지 않습니다.</p>
      )}
      <Evidence evidence={section.evidence} />
      <List title="Unverified" items={section.unverified} emptyText="" />
    </article>
  );
}

function ImplementationSection({ section }) {
  return (
    <article className="panel">
      <h2>구현/API</h2>
      <List title="API 후보" items={section.apis} emptyText="확인된 API 후보가 없습니다." />
      <List
        title="기술 제약"
        items={section.technical_constraints}
        emptyText="기술 제약이 아직 정리되지 않았습니다."
      />
      <Evidence evidence={section.evidence} />
      <List title="Unverified" items={section.unverified} emptyText="" />
    </article>
  );
}

function PestSection({ section }) {
  return (
    <article className="panel pest-panel">
      <h2>PEST</h2>
      {Object.entries(section).map(([key, value]) => (
        <div className="pest-block" key={key}>
          <h3>{key}</h3>
          <p>{value.summary}</p>
          <List items={value.signals} emptyText="" />
          <Evidence evidence={value.evidence} />
        </div>
      ))}
    </article>
  );
}

function Evidence({ evidence }) {
  if (!evidence?.length) {
    return null;
  }

  return (
    <p className="evidence">
      Evidence: <span>{evidence.join(", ")}</span>
    </p>
  );
}

function List({ title, items, emptyText }) {
  if (!items?.length) {
    return emptyText ? <p className="muted">{emptyText}</p> : null;
  }

  return (
    <div>
      {title ? <h3>{title}</h3> : null}
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function SourceList({ sources }) {
  if (!sources.length) {
    return <p>연결된 source가 없습니다. API key 또는 네트워크 상태를 확인해 주세요.</p>;
  }

  return (
    <ul className="source-list">
      {sources.map((source) => (
        <li key={source.source_id}>
          <a href={source.url} target="_blank" rel="noreferrer">
            {source.title}
          </a>
          <span>
            {source.source_id} · {source.source_type} · {source.category}
          </span>
          {source.snippet ? <p>{source.snippet}</p> : null}
        </li>
      ))}
    </ul>
  );
}

export default App;
