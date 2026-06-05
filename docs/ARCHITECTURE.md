# Architecture Documentation

## Overview

YT Trend Hunter follows a **modular, event-driven microservices architecture** designed for scalability, extensibility, and production readiness.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │   Web App   │  │   Mobile    │  │    API      │  │  CLI/     │ │
│  │  (Next.js)  │  │  (Future)   │  │  Consumers  │  │  Scripts  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼───────┘
          │                │                │                │
          └────────────────┼────────────────┼────────────────┘
                           │                │
┌──────────────────────────▼────────────────▼────────────────────────┐
│                       API GATEWAY LAYER                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │  Auth    │ │  Rate    │ │  CORS    │ │  Middleware   │   │  │
│  │  │          │ │  Limiter │ │          │ │              │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────────┐
│                      SERVICE LAYER                                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    INTELLIGENCE ENGINES                       │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │  │
│  │  │    Trend     │ │  Competitor  │ │     Comment        │   │  │
│  │  │  Detection   │ │ Intelligence │ │   Intelligence     │   │  │
│  │  └──────────────┘ └──────────────┘ └────────────────────┘   │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │  │
│  │  │   Content    │ │   Channel   │ │      Idea          │   │  │
│  │  │  Gap Detector│ │  Predictor  │ │   Generation       │   │  │
│  │  └──────────────┘ └──────────────┘ └────────────────────┘   │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │              Opportunity Engine                       │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    AI ANALYSIS LAYER                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │ DeepSeek │ │  OpenAI  │ │Anthropic │ │   Ollama     │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    DATA COLLECTORS                            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │ YouTube  │ │  Google  │ │  Reddit  │ │  RSS/News    │   │  │
│  │  │   API    │ │  Trends  │ │          │ │              │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────────────┐
│                      DATA LAYER                                    │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│  │  PostgreSQL  │  │    Redis     │  │    Elasticsearch       │   │
│  │  (Primary)   │  │   (Cache)    │  │    (Search)            │   │
│  └──────────────┘  └──────────────┘  └────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Celery Task Queue                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │  │  Scan    │ │  Report  │ │  Alert   │ │  Analysis    │   │  │
│  │  │  Tasks   │ │  Tasks   │ │  Tasks   │ │  Tasks       │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. API Gateway (FastAPI)

**Purpose**: Entry point for all client requests.

**Features**:
- Request routing
- Authentication & authorization (JWT)
- Rate limiting
- CORS configuration
- Request validation (Pydantic)
- API documentation (Swagger/ReDoc)
- Error handling
- Logging & monitoring

**Key Files**:
- `backend/app/main.py` - Application factory
- `backend/app/api/v1/router.py` - Route registration
- `backend/app/core/security.py` - Auth middleware
- `backend/app/core/config.py` - Configuration

### 2. Intelligence Engines

#### Trend Detection Engine
**Purpose**: Detect emerging trends, exploding topics, and rising keywords.

**Formulas**:
```
Growth Velocity = (current_value - previous_value) / days
Engagement Rate = ((likes + comments) / views) × 100
Trend Strength = w1×GV + w2×EV + w3×SM + w4×VV
Opportunity Score = TS×0.30 + (100-CL)×0.25 + (100-SS)×0.25 + AD×0.20
```

**Key File**: `backend/app/services/engines/trend_detection.py`

#### Comment Intelligence Engine
**Purpose**: Analyze comments at scale to extract demand signals.

**Extracts**:
- Content requests ("Please make a video about X")
- Questions ("Can someone explain Y?")
- Complaints ("Why is nobody talking about Z?")
- Part requests ("Part 2 please")
- Content ideas
- Pain points
- Unmet demand

**Key File**: `backend/app/services/engines/comment_intelligence.py`

#### Opportunity Engine
**Purpose**: Calculate opportunity scores and rank opportunities.

**Scoring**:
```
Opportunity Score = TS×0.30 + (100-CL)×0.25 + (100-SS)×0.25 + AD×0.20
Monetization Score = CPM×0.25 + SA×0.25 + PP×0.25 + APP×0.25
Channel Creation Score = f(competition, demand, gap, monetization)
```

**Key File**: `backend/app/services/engines/opportunity_engine.py`

#### Idea Generation Engine
**Purpose**: Generate channel ideas, video ideas, and content plans.

**Outputs**:
- TOP 10 Channel Ideas
- TOP 25 Video Ideas
- TOP 10 Viral Opportunities
- TOP 10 Underserved Niches
- Content series plans
- Publishing schedules
- Title suggestions
- Thumbnail text

**Key File**: `backend/app/services/engines/idea_generation.py`

### 3. AI Analysis Layer

**Purpose**: Provide interchangeable AI provider support.

**Supported Providers**:
- DeepSeek
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Ollama (local)

**Architecture**:
- Abstract base class `AIProvider`
- Factory pattern `AIFactory`
- Provider-specific implementations
- Easy to add new providers

**Key File**: `backend/app/services/ai/base.py`

### 4. Data Collectors

#### YouTube Collector
**Purpose**: Fetch data from YouTube Data API v3.

**Capabilities**:
- Search videos
- Get channel info
- Get video details
- Get comments
- Get trending videos
- Search channels
- Get video categories

**Key File**: `backend/app/services/collectors/youtube.py`

#### Google Trends Collector
**Purpose**: Fetch trending search data.

**Capabilities**:
- Daily trends
- Interest over time
- Related queries

**Key File**: `backend/app/services/collectors/google_trends.py`

#### Reddit Collector
**Purpose**: Fetch trending topics and discussions.

**Capabilities**:
- Trending topics
- Subreddit search
- Subreddit info

**Key File**: `backend/app/services/collectors/reddit.py`

### 5. Data Layer

#### PostgreSQL
**Purpose**: Primary database for all persistent data.

**Tables**:
- `channels` - YouTube channel data
- `videos` - Video metadata and statistics
- `comments` - Comment data
- `trends` - Detected trends
- `opportunities` - Ranked opportunities
- `analyses` - Analysis results
- `reports` - Generated reports
- `alerts` - User alerts
- `users` - User accounts
- `niches` - Niche definitions

#### Redis
**Purpose**: Caching and task queue backend.

**Usage**:
- API response caching
- Session storage
- Rate limiting counters
- Celery message broker

#### Elasticsearch
**Purpose**: Full-text search and analytics.

**Usage**:
- Search videos, channels, comments
- Trend analysis aggregation
- Content gap analysis

### 6. Task Queue (Celery)

**Purpose**: Async task processing.

**Tasks**:
- `scan_global` - Global YouTube scan
- `scan_niche` - Niche-specific scan
- `analyze_comments` - Comment intelligence
- `generate_report` - Report generation
- `send_alert` - Alert notifications
- `update_trends` - Trend data refresh

---

## Data Flow

### Global Discovery Flow
```
1. User requests global discovery
2. API Gateway validates request
3. Service layer checks Redis cache
4. If cached, return cached results
5. If not cached:
   a. YouTube Collector scans multiple categories
   b. Trend Detection Engine analyzes data
   c. Comment Intelligence Engine processes comments
   d. Opportunity Engine calculates scores
   e. Idea Generation Engine creates recommendations
   f. Results cached in Redis
   g. Results stored in PostgreSQL
6. Return ranked opportunities
```

### Niche Analysis Flow
```
1. User requests niche analysis
2. API Gateway validates niche parameter
3. YouTube Collector searches niche-specific content
4. Trend Detection Engine calculates niche trends
5. Competitor Intelligence analyzes top channels
6. Comment Intelligence extracts demand signals
7. Content Gap Detector finds underserved topics
8. Channel Creation Predictor estimates success
9. Opportunity Engine ranks all findings
10. Results cached and returned
```

---

## Scoring Methodology

### Trend Strength (0-100)
```
TS = w1 × GV_norm + w2 × EV_norm + w3 × SM_norm + w4 × VV_norm

Where:
- GV = Growth Velocity (subscriber growth rate)
- EV = Engagement Velocity (engagement rate change)
- SM = Search Momentum (search volume trend)
- VV = Video Velocity (video upload rate)
- w1 = 0.30, w2 = 0.25, w3 = 0.25, w4 = 0.20
```

### Opportunity Score (0-100)
```
OS = TS × 0.30 + (100 - CL) × 0.25 + (100 - SS) × 0.25 + AD × 0.20

Where:
- TS = Trend Strength
- CL = Competition Level
- SS = Saturation Score
- AD = Audience Demand
```

### Content Gap Score (0-100)
```
GAP = demand_score × 0.50 + supply_gap × 0.30 + demand_momentum × 0.20

Where:
- demand_score = Audience request frequency
- supply_gap = (demand - supply) / demand
- demand_momentum = Growth rate of demand
```

### Channel Creation Score (0-100)
```
CCS = (100 - CL) × 0.35 + AD × 0.30 + GAP × 0.20 + MS × 0.15

Where:
- CL = Competition Level
- AD = Audience Demand
- GAP = Content Gap Score
- MS = Monetization Score
```

---

## Security Architecture

### Authentication
- JWT-based authentication
- Token refresh mechanism
- Password hashing with bcrypt
- API key validation for external access

### Authorization
- Role-based access control (RBAC)
- User roles: admin, analyst, basic
- Rate limiting per user/IP
- API quota management

### Data Protection
- Environment variables for secrets
- CORS whitelist
- SQL injection prevention (SQLAlchemy)
- XSS protection
- HTTPS enforcement

---

## Scalability Design

### Horizontal Scaling
- Stateless API servers (add more instances)
- Redis Cluster for distributed caching
- PostgreSQL read replicas
- Celery worker pool expansion

### Vertical Scaling
- Increase instance resources
- Database connection pooling
- Query optimization
- Index optimization

### Caching Strategy
- Redis: API responses, session data
- Database: Materialized views for reports
- Application: LRU cache for frequent queries

---

## Monitoring & Observability

### Logging
- Structured logging with Loguru
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request ID tracking
- Service-specific loggers

### Metrics
- API response times
- Error rates
- Cache hit rates
- Task queue lengths
- Database query performance

### Health Checks
- `/health` endpoint
- Database connectivity
- Redis connectivity
- Celery worker status
- External API availability
