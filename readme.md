# 🏢 OrgLens: Organizational Intelligence Platform

**AI-powered organizational analysis using communication data (Slack, Gmail) combined with employee records to uncover hidden power structures, trust gaps, decision velocity bottlenecks, and cultural contradictions.**

---

## 🎯 Why OrgLens Exists

Most organizational problems are invisible in org charts and KPIs.
Teams rarely fail because of strategy alone. They fail because of:

- hidden influence networks,
- decision bottlenecks,
- trust erosion,
- siloed communication,
- leadership misalignment,
- contradictions between stated values and actual behavior.

OrgLens was built to surface those invisible organizational dynamics using communication intelligence, NLP, graph analysis, and machine learning.
Instead of relying only on surveys or intuition, OrgLens analyzes communication patterns from Slack, Gmail, employee records, and uploaded organizational data to generate a deep organizational diagnostic dashboard.

---

## 🎯 What OrgLens Does

OrgLens is a **CHRO (Chief Human Resources Officer) intelligence tool** that analyzes raw organizational communication to answer questions HR teams actually need answered:

- **Who really makes decisions?** (vs. who's formally supposed to)
- **Where are the bottlenecks?** (approval chains, gatekeepers, silos)
- **Are we practicing what we preach?** (claims vs. reality gaps)
- **Who's at risk of leaving?** (flight risk prediction)
- **What's actually broken?** (system diagnosis with root causes)
- **How healthy is our org?** (10-card diagnostic dashboard)

### 📊 The 10-Card Dashboard

```
1. ORG HEALTH CARD          → Overall health score + breakdown (trust, resilience, velocity, quality, alignment, info flow)
2. TRUST GAP CARD           → Claims vs. reality contradictions (meritocracy, transparency, work-life balance, etc.)
3. POWER STRUCTURE          → Who actually influences decisions (formal vs. hidden power, gatekeepers, ignored authorities)
4. TOP INFLUENCERS          → People with highest influence scores + authority gaps
5. GATEKEEPERS              → Information & decision blockers (domains they control, blocks_count)
6. RESILIENCE               → Single points of failure, knowledge silos, flight risk people
7. DECISION VELOCITY        → How long decisions take + bottleneck persons
8. SYSTEM DIAGNOSIS         → Root causes (governance/culture/structure), who profits from gaps, dysfunction cost
9. PREDICTIONS              → Attrition risk, decision reversal risks, org health in 6 months
10. RECOMMENDATIONS         → Prioritized actions with ROI, confidence scores, quick wins
```

**Plus**: Contradictions detected, positive signals, org archetype classification, confidence metrics, and deep political intelligence (CEO briefing).

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND (React/Vite)              │
│  • Dashboard with 10 cards                              │
│  • Data upload UI (ZIP, CSV, Slack JSON, Gmail export)  │
│  • Deep-dive drill-downs                                │
│  • Demo org (public access, no auth needed)             │
└────────────────────┬────────────────────────────────────┘
                     │ axios + Bearer token
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND (Python)               │
│  • REST API endpoints                                   │
│  • OAuth2 (Slack, Gmail optional)                       │
│  • File ingestion (ZIP parser, CSV, mbox, Slack JSON)   │
│  • Async processing (SQLAlchemy ORM)                    │
│  • Token encryption (Fernet AES)                        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌─────────────┐
    │ NLP    │  │ ML     │  │ Diagnostics │
    │Pipeline│  │Models  │  │ & Confidence│
    └────────┘  └────────┘  └─────────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
    ┌─────────────────────────────────────┐
    │  GROQ LLM Interface                 │
    │  • Narrative generation             │
    │  • Deep political intelligence      │
    │  • Recommendations synthesis        │
    └─────────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  PostgreSQL (Analysis Results)      │
    │  • AnalysisReport model             │
    │  • Cached scores (Redis optional)   │
    └─────────────────────────────────────┘
```

---

## 🔧 Core Components

### **1. Data Ingestion (`services/ingestion/`)**

Accepts multiple input formats:

| Format | Source | How It Works |
|--------|--------|--------------|
| **ZIP** | User upload | Extracts all files inside (CSV, Slack JSON, Gmail mbox, narrative.txt) |
| **CSV** | Employee roster | Columns: name, email, title, department, level, tenure_months, flight_risk, collaboration, performance_rating |
| **Slack JSON** | Slack export | Per-channel JSON files (each message object with ts, user, text) |
| **Gmail mbox** | Gmail Takeout | Standard mbox format (extracts subject, from, date, body) |
| **Narrative TXT** | User-provided | Company mission, values, claims (for trust gap analysis) |

**Key Classes**:
- `ZipParser`: Routes files by extension, deduplicates employees
- `ParsedEmployee`, `ParsedMessage`, `ParsedNarrative`: Normalized data structures
- `IngestionResult`: Structured output with errors, file_summary, parsed records

### **2. NLP Pipeline (`services/nlp/`)**

Extracts decision moments, objections, sentiment from text.

**Decision Extractor** (`decision_extractor.py`):
```python
# Finds decision keywords (approved, rejected, decided, object, stall, pivot)
# Extracts objections (concern, problem, risk, against)
# Detects domains (hiring, budget, product, process, strategy, org)
decisions = extractor.extract_decisions(text)
objections = extractor.extract_objections(text)
```

**Influence Scorer** (`influence_scorer.py`):
```python
# Message-level influence: conviction phrases, veto phrases, formal authority, reception
message_influence = scorer.score_message_influence(text, formal_authority, responses, decision_followed)

# Person-level influence: activity, quality, responses, objection credibility, decision outcomes
person_influence = scorer.score_person_influence(msg_count, avg_influence, response_rate, ...)

# Identifies power type: hidden_power, formal_leader, ignored_authority, gatekeeper, neutral
power_type = scorer.identify_influence_type(formal_authority, actual_influence, tone, outcomes)
```

**Sentiment Analyzer** (`sentiment_analyzer.py`):
```python
# Uses TextBlob for polarity + subjectivity
sentiment = analyzer.analyze_sentiment(text)  # {sentiment_score: -1 to 1, label: pos/neg/neutral}

# Urgency signals: ASAP, urgent, critical, etc.
urgency = analyzer.analyze_urgency(text)  # {urgency_score: 0-1, level: low/medium/high/critical}

# Tone: blocking, exploratory, collaborative, formal
tone = analyzer.analyze_tone(text)

# Confidence + specificity scoring
```

### **3. ML Models (`services/ml/`)**

**Influence Model** (`influence_model.py`):
- **Decision Reversal Prediction**: Uses objector influence scores + conviction levels
  - Trains GradientBoostingClassifier on historical reversals
  - Outputs probability (0-1) that decision will be reversed
- **Influence Score Prediction**: RandomForestRegressor predicting hidden authority
  - Features: message count, message quality, response rate, objection credibility, proposal success, formal authority
  - Outputs predicted influence (0-10)

**Network Analyzer** (`network_analyzer.py`):
- Builds directed communication graph (who mentions whom)
- Detects gatekeepers (high betweenness centrality, low clustering)
- Identifies isolated experts (high in-degree, low out-degree)
- Detects alliances (community detection on undirected graph)

**Predictor** (`predictor.py`):
- **Attrition Risk**: Authority gap, objection acceptance ratio, tenure window (18-36 months = high risk), dept turnover
- **Decision Velocity Trend**: Polyfit on historical decision times, forecast 3 months ahead
- **Org Health Forecast**: 6-month projection based on metric trends

### **4. ML Signal Extractor (`services/ai_analysis/ml_signals.py`)**

Core feature engineering. Produces objective, quantifiable signals fed to Groq.

**Returns**:
```python
{
    "person_signals": {
        "Alice Chen": {
            "influence_score": 8.5,
            "formal_authority": 5.0,
            "authority_gap": 3.5,  # hidden power
            "message_count": 142,
            "conviction_count": 23,
            "escalation_count": 8,
            "objection_count": 12,
            "burnout_signal": 3,
            "flight_risk_score": 0.15,  # from HR data
            "channels_active": ["slack-engineering", "slack-general", "email-thread-123"]
        }
    },
    "trust_signals": {
        "trust_gap_score": 4.2,  # out of 10
        "meritocracy_violations": 3,
        "transparency_violations": 5,
        "comp_inversion_evidence": [{"sender": "Bob", "snippet": "new hires paid more"}],
        "escalation_rate": 0.08
    },
    "network_signals": {
        "bypass_count": 7,  # people bypassing authority
        "gatekeeper_signals": {"Alice": 5, "Charlie": 3},
        "isolated_count": 2,
        "network_density": 0.0512
    },
    "decision_signals": {
        "decision_count": 14,
        "block_count": 3,
        "reversal_count": 2,
        "reversal_rate": 0.143,
        "estimated_avg_days": 21
    },
    "resilience_signals": {
        "high_flight_risk_count": 2,
        "ownership_gap_count": 3,
        "departure_mention_count": 1
    },
    "sentiment_signals": {
        "negative_ratio": 0.12,
        "urgency_ratio": 0.08
    },
    "conflict_signals": {
        "conflict_ratio": 0.05,
        "conflict_messages": [...]
    },
    "velocity_signals": {
        "delay_message_count": 6,
        "domain_delays": {"budget": 3, "hiring": 2}
    }
}
```

**Key Metrics Computed**:
- `health_score`: 10 - (trust_gap*0.25) - (resilience_score*0.20) - (velocity_score*0.20) - ... (weighted blend)
- `resilience_score`: 10 - (high_risk*1.0) - (ownership_gaps*0.5) - (departures*0.8)
- `velocity_score`: Based on avg_days (≤5d = 9.0, ≤10d = 7.5, ≤20d = 6.0, ≤30d = 4.5, >30d = 2.5)
- `trust_gap_score`: (meritocracy_violations*0.8) + (transparency_violations*0.6) + ... (capped at 8.5)

### **5. Groq AI Narrator (`services/ai_analysis/groq_narrator.py`)**

Calls Claude 3.3 (via Groq API) with locked ML scores to generate narratives.

**Three-step approach**:

1. **Call 1: Core Analysis** (`_call_groq_core`)
   - Input: ML signals + locked computed scores
   - Output: org_health, trust_gap, power_structure, top_influencers, gatekeepers, resilience, decision_velocity, system_diagnosis, predictions
   - **Critical**: Groq is forced to use exact scores (trust_gap_score=4.2, not 3.8)
   - Names real people, quotes real messages

2. **Call 2: Recommendations** (`_call_groq_recommendations`)
   - Input: Core findings + root causes
   - Output: 8-10 specific, actionable recommendations
   - Each has: id, title, description, impact, effort, timeline_weeks, cost_estimate, expected_roi, confidence, priority_rank

3. **Call 3: Deep Political Intelligence** (`_call_groq_deep_intel`)
   - Input: Person signals, conflict messages, person-to-person relationships
   - Output: political_map (factions, alliances, upcoming conflicts), culture_toxins, between_the_lines, alert_signals, CEO briefing
   - **Most brutally honest card** — tells CEO what's actually happening

### **6. Confidence & Quality (`services/confidence/`)**

Multi-step enrichment pipeline:

**ClaimExtractor** → **ContradictionDetector** → **PositiveSignalDetector** → **ArchetypeClassifier** → **ConfidenceCalculator**

- Extracts org claims from mission statement
- Finds contradictions between claims and observed behavior
- Detects positive signals (collaboration, alignment wins, successful initiatives)
- Classifies org archetype (Chaotic, Siloed, Aligned, Thriving, Declining, etc.)
- Calculates overall confidence % (30-100%) based on data coverage

---

## ⚙️ Analysis Pipeline (`services/ai_analysis/pipeline.py`)

**Main orchestration** (`_async_analysis_pipeline`):

```python
# Step 1: Load org data (employees, messages)
org, employees, messages = await _load_org_data(session, org_id)

# Step 2: NLP enrichment
decisions, _ = await _nlp_pipeline(session, org_id, messages)
# → Populates: contains_decision, contains_objection, sentiment_score, urgency_score, influence_signal

# Step 3: ML signal extraction
ml_signals = extractor.extract_all_signals(employees, messages, org_context)
# → 8 signal groups + 4 computed scores

# Step 4: Groq AI narration
ai_result = narrator.generate_analysis(ml_signals)
# → Full dashboard output + recommendations + deep intel

# Step 5: Save everything to DB
await _save_ai_analysis_results(session, analysis_id, org_id, ai_result, ml_signals, messages)
```

**No Celery**: Processing is async (FastAPI native) but runs in-request without background task queuing. For large orgs (500+ messages), expect 3-8 minutes.

---

## 📊 Database Schema (`models/`)

### **AnalysisReport**
- `id`, `org_id`, `status` (PENDING/PROCESSING/COMPLETED/FAILED)
- `org_health_score`, `health_breakdown` (JSON)
- `trust_gap_score`, `trust_gap_details` (JSON)
- `power_structure`, `top_influencers`, `gatekeepers` (JSON)
- `resilience_score`, `resilience_details` (JSON)
- `decision_velocity`, `system_diagnosis`, `predictions` (JSON)
- `contradictions`, `positive_signals`, `archetype`, `confidence_metrics` (JSON)
- `recommendations` (JSON array)
- `messages_analyzed`, `decisions_extracted`, `date_range_start/end`
- `created_at`, `completed_at`, `progress` (0-100)

### **Organization**
- `id`, `name`, `industry`, `size_estimate`, `mission_statement`
- `slack_connected`, `gmail_connected`
- `slack_access_token`, `gmail_access_token` (encrypted with Fernet AES)
- `stated_values`, `leadership_claims` (JSON for trust gap comparison)
- Relationships: `employees`, `messages`, `decisions`, `analyses`

### **Employee**
- `id`, `org_id`, `name`, `email`, `title`, `department`, `level`, `tenure_months`
- `influence_score`, `formal_authority_score`, `credibility_score` (computed)
- `resilience_impact_score`, `information_control_score`

### **Message**
- `id`, `org_id`, `source` (slack/gmail/upload), `external_id`
- `sender_id`, `sender_raw`, `channel_or_thread`, `content`, `timestamp`
- `contains_decision`, `contains_objection`, `sentiment_score`, `urgency_score`
- `decision_keywords`, `topics`, `influence_signal` (all JSON/float)

### **Decision**
- `id`, `org_id`, `title`, `domain`, `status` (PROPOSED/APPROVED/REJECTED/REVERSED/STALLED)
- `proposed_at`, `resolved_at`, `resolution_days`
- `proposer_id`, `supporters`, `objectors`, `deciders` (JSON)
- `followed_objector`, `power_play_score`
- `source_message_ids` (which messages led to this decision)

---

## 🔐 Security

### **Token Encryption** (`services/security/token_encryption.py`)
- All OAuth tokens (Slack, Gmail) are encrypted at rest using Fernet (AES-128)
- Encryption key stored in `TOKEN_ENCRYPTION_KEY` environment variable
- Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### **OAuth2 Flow**
- Slack OAuth 2.0 with scopes: `chat:read`, `channels:history`, `users:read`
- Gmail OAuth 2.0 with scopes: `gmail.readonly`
- Tokens stored encrypted; never logged or exposed in responses

### **Rate Limiting** (`services/security/rate_limiter.py`)
- 100 requests/hour per user
- 1000 requests/hour per IP
- Analysis trigger: max 5/hour (to prevent abuse)

### **CORS & Headers**
- CORS allowed for frontend domain (configurable)
- Security headers: X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security

---

## 🛠️ Setup & Deployment

### **Prerequisites**
- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (optional, for score caching)
- Groq API key (free tier available)
- Slack OAuth app (for live sync, optional)
- Gmail OAuth app (for live sync, optional)

### **Backend Setup**

```bash
# Clone repo
git clone https://github.com/GuruRamya/ORGLENS.git
cd orglens/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate token encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Create .env
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/orglens
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key
TOKEN_ENCRYPTION_KEY=your-generated-fernet-key
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
FRONTEND_URL=http://localhost:5173
EOF

# Create database
createdb orglens
alembic upgrade head

# Run migrations (if using Alembic)
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head

# Run dev server
uvicorn app.main:app --reload --port 8000
```

### **Frontend Setup**

```bash
cd orglens/frontend

# Install dependencies
npm install

# Create .env
cat > .env << EOF
VITE_API_BASE=http://localhost:8000
VITE_DEMO_ORG_ID=<uuid-from-demo-seed>
VITE_DEMO_ANALYSIS_ID=<uuid-from-demo-seed>
EOF

# Run dev server
npm run dev  # http://localhost:5173
```

### **Seed Demo Organization**

OrgLens includes a pre-seeded demo organization that allows users to explore the full dashboard experience without uploading real company data.

The demo contains:
- synthetic employee records,
- simulated Slack/Gmail communication,
- organizational narratives,
- decision history,
- and pre-generated analysis outputs.

This allows:
- recruiters,
- developers,
- HR professionals,
- and evaluators

to immediately experience the platform’s organizational intelligence capabilities.

The frontend includes public demo access with predefined organization and analysis IDs.


```bash
python scripts/seed_demo.py \
  --zip path/to/demo_data.zip \
  --api http://localhost:8000 \
  --email demo@orglens.app \
  --password DemoOrgLens2024! \
  --org-name "OrgLens Corp (Demo)" \
  --out demo_config.json
```

---

## 🚨 Known Limitations & Trade-offs

### **1. No Celery (Background Task Queue)**

**Why Removed**:
- Render's free tier doesn't support long-running worker processes
- Celery + Redis adds deployment complexity for hobby projects
- FastAPI's native async/await is sufficient for mid-size orgs

**Impact**:
- Analysis requests block the API endpoint for 3-8 minutes (depending on org size)
- Large orgs (500+ messages) may timeout (if API timeout < 10min)
- No job queuing; concurrent analyses are serialized

**Workaround**:
- For larger-scale deployments, restore Celery: create `analysis_tasks.py`, update `pipeline.py` to enqueue instead of await
- Use Cloud Tasks (GCP) or SQS (AWS) instead of Redis

**Code skeleton ready**:
```python
# Commented in analysis_tasks.py
# @shared_task(bind=True, max_retries=3)
# def analyze_organization(self, org_id: str, analysis_id: str):
#     result = asyncio.run(_async_analysis_pipeline(org_id, analysis_id))
#     return result
```

---

### **2. Slack Integration (Optional, Not Required)**

**Current State**:
- `SlackClient` class (`services/ingestion/slack_client.py`) is **fully implemented**
- Can fetch messages from public channels in real-time
- Requires Slack OAuth token (user must authorize)

**Limitations**:
- **No private channel access** (requires additional OAuth scopes + enterprise plan)
- **No thread replies** (Groq only analyzes main channel messages)
- **Rate-limited to 100 messages/hour** by Slack API
- **User upload (ZIP + Slack JSON export) is faster** and preferred for analysis

**Why Not Enforced**:
- Slack OAuth adds setup friction for SMBs
- CSV + ZIP file upload covers 90% of use cases
- Slack auth token storage requires hardened infrastructure

**To Enable Live Sync**:
1. Create Slack app at https://api.slack.com/apps
2. Set scopes: `channels:history`, `chat:read`, `users:read`
3. Set OAuth redirect URI: `https://yourdomain.com/api/auth/callback/slack`
4. Add `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET` to `.env`
5. Endpoint `/api/auth/slack/authorize` becomes functional

---

### **3. Gmail Integration (Optional, Not Required)**

**Current State**:
- `GmailClient` class (`services/ingestion/gmail_client.py`) is **fully implemented**
- Can fetch important emails (by default)
- Requires Gmail OAuth token + Google Cloud project

**Limitations**:
- **Gmail API query limited to 1000 emails** (free tier cap)
- **Only "important" emails** by default (can change query)
- **No thread reconstruction** (each email treated separately)
- **2-step OAuth process** (user must authorize Google account)

**Why Not Enforced**:
- Gmail OAuth requires Google Cloud setup (project, credentials, verification)
- Email patterns are less predictive than Slack (async, less context)
- User upload (mbox from Gmail Takeout) is simpler

**To Enable Live Sync**:
1. Create Google Cloud project: https://console.cloud.google.com
2. Enable Gmail API
3. Create OAuth 2.0 credentials (type: Web application)
4. Set redirect URI: `https://yourdomain.com/api/auth/callback/gmail`
5. Download JSON and add `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET` to `.env`
6. Endpoint `/api/auth/gmail/authorize` becomes functional

---

### **4. Groq API Dependency**

**Current**:
- All narrative generation uses Groq (free tier: 14,400 requests/month)
- No fallback if Groq fails

**Limitations**:
- **Rate-limited** (if org > 5000 messages, may hit quotas)
- **Requires internet connection** (can't work offline)
- **Cost escalates** with volume (at scale: ~$0.01/analysis)

**To Add Fallback**:
```python
# Wrap Groq call in try/except, use spacy + rule-based analysis as fallback
try:
    ai_result = narrator.generate_analysis(ml_signals)
except Exception:
    ai_result = fallback_rule_based_analysis(ml_signals)  # ← Implement
```

---

### **5. Redis Optional (Score Caching)**

**Current**:
- Score caching enabled if Redis available
- Gracefully disables if Redis unavailable (no error)
- TL DR: Not required, but speeds up repeat analyses

**If Redis Unavailable**:
- Every analysis recalculates ML scores from scratch
- No performance degradation, just slower for large orgs
- To enable: `REDIS_URL=redis://localhost:6379/0`

---

### **6. Analysis Timeout (No Streaming)**

**Current**:
- Request waits for full analysis (3-8 minutes for typical org)
- No WebSocket or Server-Sent Events for progress streaming

**Limitation**:
- Frontend shows "loading..." spinner for entire duration
- Browser may timeout if infrastructure timeout > 30 minutes
- User can't see intermediate results

**To Add Progress Streaming**:
1. Modify pipeline to emit progress events
2. Frontend opens WebSocket to `/api/analysis/stream/{analysisId}`
3. Backend emits JSON: `{"step": 2, "progress": 40, "message": "Running ML models..."}`

---

### **7. Data Privacy & Retention**

**Current**:
- All data (messages, employee records) stored in PostgreSQL
- No automatic deletion or anonymization
- No compliance with GDPR/CCPA built-in

**Recommendations**:
```python
# Add to Organization model
data_retention_days: int = 90  # Auto-delete after 90 days
is_pii_anonymized: bool = False  # Anonymize names/emails

# Implement cleanup job
async def cleanup_old_analyses():
    cutoff = datetime.utcnow() - timedelta(days=90)
    await session.execute(delete(AnalysisReport).where(AnalysisReport.created_at < cutoff))
```

---

### **8. Accuracy Caveats**

**Power Structure Detection**:
- Assumes active communicators are influential (may miss silent strategists)
- Slack is more transparent than in-person hallway conversations
- Text-based influence ≠ actual decision-making power

**Trust Gap Analysis**:
- Only detects contradictions explicitly mentioned in messages
- Subtle cultural issues (microaggressions, bias) not detected
- Requires >30 days of data for reliability

**Flight Risk**:
- Uses tenure + influence gap + formal authority
- Missing signals: external job offers, family circumstances, personal ambitions

**Recommendation**:
> Treat OrgLens as **"data-informed intuition boost"**, not absolute truth. Always validate findings with HR interviews & 1:1s.

---

## 📈 Performance Notes

### **Typical Analysis Times**
| Org Size | Messages | Time |
|----------|----------|------|
| 10 people | 50 | 30s |
| 20 people | 200 | 1.5m |
| 50 people | 500 | 3-4m |
| 100 people | 1000 | 6-8m |
| 200+ people | 2000+ | 10-15m+ |

### **Bottlenecks**
1. **Groq API call** (1-2 min): Most time-consuming step
2. **ML signal extraction** (30-60s): Feature engineering across all messages
3. **NLP pipeline** (20-30s): Decision extraction, sentiment analysis
4. **Database commits** (10-20s): Saving results to PostgreSQL

### **Optimization Ideas**
- Cache Groq responses by message hash (implemented via Redis)
- Batch process messages in chunks
- Use async Groq client (currently blocking)
- Reduce message analysis to last 90 days (configurable)

---

## 🧠 CHRO Use Cases

### **1. Annual Talent Review**
- Identify hidden influencers to promote/retain
- Spot attrition risks before they quit
- Validate decision-making health vs. stated goals

### **2. Org Restructuring**
- Understand existing power dynamics before reshuffle
- Identify gatekeepers who might resist change
- Spot collaboration gaps to fix with new structure

### **3. Leadership Coaching**
- Show executive blind spots (authority gap data)
- Provide evidence for credibility/trust issues
- Suggest specific changes with predicted ROI

### **4. Culture Audit**
- Quantify gaps between stated values & reality
- Identify toxic patterns (escalation culture, blame, silos)
- Track culture metrics over time (multiple analyses)

### **5. M&A Due Diligence**
- Assess target company's organizational health
- Identify integration risks (incompatible cultures)
- Benchmark decision velocity vs. parent org

---

## 🎯 Roadmap

### **Planned** (Not Yet Implemented)
- [ ] Multi-language support (currently English-only)
- [ ] Custom org archetypes (user-defined classifications)
- [ ] Trend analysis (compare multiple analyses over time)
- [ ] Export to PDF/PowerPoint (currently JSON only)
- [ ] Slack app (in-app recommendations)
- [ ] Predictive modeling (ML model for churn, promotion success)
- [ ] Real-time dashboard (WebSocket streaming)

### **Out of Scope** (Will Not Build)
- Employee surveillance or covert monitoring
- Automated firing recommendations
- Integration with ATS/HRIS systems (data privacy risk)
- Competitor benchmarking database

---

## 🤝 Contributing

**Development Stack**:
- Backend: FastAPI, SQLAlchemy, Pydantic, scikit-learn, NetworkX, TextBlob
- Frontend: React 18, Vite, Tailwind CSS, Lucide icons
- Infra: PostgreSQL, Redis (optional), Groq API

**To Add a Feature**:
1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow code style: Black (backend), Prettier (frontend)
3. Add tests: `pytest tests/` for backend
4. Submit PR with description of changes

**Bug Reports**: Open GitHub issue with:
- OrgLens version
- Steps to reproduce
- Expected vs. actual behavior
- Screenshot (if UI bug)

---

## 👤 Built By - 
                  M.Guru Ramya

**AI/ML Student & Aspiring CHRO** — Created as a learning project to understand organizational psychology through data.

**Key Insights from Building This**:
- Communication patterns reveal truth that org charts hide
- Trust is measurable (claims vs. reality gap)
- Decision velocity is the #1 org health indicator
- Hidden influencers are more powerful than titles suggest

---

## 🙏 Acknowledgments

- **Groq** for free API tier access
- **FastAPI** & SQLAlchemy teams for excellent documentation
- **scikit-learn** & **NetworkX** for ML/graph algorithms
- **TextBlob** for sentiment analysis
- Org psychology inspiration: Organizational Politics, Power Dynamics, Trust literature

---

**TL;DR**: OrgLens is a CHRO intelligence tool that analyzes Slack/Gmail/CSV data to uncover hidden power structures, trust gaps, and decision bottlenecks. It's async, secure, and runs without Celery (trade-off for free deployment). Start with demo → upload your data → get 10-card diagnostic in 3-8 minutes. 🚀