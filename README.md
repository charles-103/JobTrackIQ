# JobTrackIQ

**JobTrackIQ** is a personal **Job Tracking & Job Ingestion system** designed for individual job seekers to centrally manage applications, hiring pipeline events (interviews / rejections / offers), and to gradually build a scalable **Job Inbox** (job data pool).

## Project Goals
- Improve control and efficiency in personal job search workflows  
- Structure job and application data for future **analysis, automation, and intelligent matching**

---

## ✨ Current Features (Implemented)

### 1. Applications (Application Management)
- Create / list / delete applications  
- Status & stage management (`active / rejected / offer / closed`)  
- Timeline-based event system:
  - `applied`
  - `interview`
  - `follow-up`
  - `offer`
  - `rejection`
- Event-driven updates of `current_stage`  
- UI support for:
  - Quick event creation  
  - Event deletion  

---

### 2. Job Inbox (Job Pool)
- Manually add job postings:
  - Company  
  - Position  
  - Location  
  - Link  
  - Job Description (JD)  
- Job deduplication using **fingerprint hashing**  
- One-click conversion from **Job Posting → Application**
  - Automatically creates an `applied` event  
  - Removes the job from the Inbox after conversion  

---

### 3. External Job Ingestion
- Integration with **Greenhouse public job boards**  
- One-click import via UI (no manual API calls required)  
- Optional full Job Description fetching  
- Automatically feeds data back into the **Company Index**

---

### 4. Company Index
- Centralized company name management:
  - User input  
  - Crawler ingestion  
  - Manual normalization  
- Autocomplete support (e.g. Add Application page)  
- Ranking based on:
  - Usage frequency  
  - Recent activity  
- Acts as a unified entry point for:
  - Crawling  
  - Search  
  - Future recommendation systems  

---

### 5. Metrics (Basic)
- Total number of applications  
- Aggregated statistics by application status  

---

## 🧱 Tech Stack
- **Backend**: FastAPI  
- **ORM**: SQLAlchemy  
- **Database**: SQLite / PostgreSQL (managed via Alembic)  
- **Templates**: Jinja2  
- **HTTP Client**: httpx  
- **Ingestion**: Greenhouse Public API  
- **Migrations**: Alembic  

---

## 🚀 Run Locally

```bash
uvicorn app.main:app --reload
