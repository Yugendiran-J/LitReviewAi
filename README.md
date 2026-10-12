# LitReviewAI

## Run locally on Windows

1. Ensure `backend/.env` has a working `DATABASE_URL`. AI uses local Ollama;
   no external LLM API key is required. `OLLAMA_BASE_URL` defaults to
   `http://127.0.0.1:11434` and `OLLAMA_MODEL` defaults to `qwen3:4b`.
   Ollama requests time out after 300 seconds by default; set
   `OLLAMA_TIMEOUT_SECONDS` in `backend/.env` to override this if needed.
2. Install Ollama and ensure the configured model is downloaded:

   ```powershell
   ollama pull qwen3:4b
   ```

   Ollama usually runs in the background on Windows. If it is already running,
   do not run `ollama serve` again; the "address already in use" message means
   the Ollama port is occupied. Start `ollama serve` only when Ollama is not
   running.
3. Start the backend in PowerShell:

   ```powershell
   Set-Location 'C:\Users\Lenovo\Desktop\LitReviewAI\backend'
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
   ```

4. In a second PowerShell window, start the frontend:

   ```powershell
   Set-Location 'C:\Users\Lenovo\Desktop\LitReviewAI\frontend'
   npm run dev
   ```

5. Open the local URL printed by Vite (usually `http://localhost:5173`).
   Check backend health at `http://127.0.0.1:8001/health` and API docs at
   `http://127.0.0.1:8001/docs`.

If dependencies are not installed, run `pip install -r requirements.txt` in
the backend virtual environment and `npm ci` in `frontend`. Restart the backend
after changing `.env` so it reloads the configured service credentials.

## Base paper assistant

LitReviewAI helps researchers find and assess candidate papers that may serve
as a starting (base) paper. It searches the selected scholarly sources,
deduplicates records, applies year filters, screens a small candidate set
against the research criteria, and provides available metadata and extracted
evidence for the researcher to inspect and select. It is not intended to write
a complete literature review, journal article, website, or book, and it cannot
guarantee that a candidate is the single best paper.

The authenticated `POST /literature/run` endpoint runs discovery and screens
up to three candidates; it returns the results in the response `data` object.
The request can include:

- `year_from` and `year_to` (either may be `null`)
- `restriction` and `limitations`
- `sources`: any combination of `pubmed`, `openalex`, `crossref`, and `arxiv`.
IEEE Xplore is available with `IEEE_XPLORE_API_KEY`; Google Scholar results are
available through SerpApi with `SERPAPI_API_KEY`. Set a valid key, for example
`SERPAPI_API_KEY=<your-rotated-key>`, in `backend/.env` and restart the backend.

To test in `http://127.0.0.1:8001/docs`, authenticate first, then send this
JSON to `POST /literature/run`. Replace `project_id` with an existing project
owned by the authenticated user:

```json
{
  "project_id": 1,
  "keyword": "deep learning diabetic retinopathy screening",
  "domain": "ophthalmology",
  "population": "Adults with diabetes",
  "intervention": "Machine-learning models using retinal images",
  "comparison": "Ophthalmologist assessment",
  "outcome": "Sensitivity, specificity, and AUC",
  "study_type": "Diagnostic accuracy studies",
  "year_from": 2019,
  "year_to": 2025,
  "restriction": "English-language studies",
  "limitations": "Exclude pediatric-only studies",
  "sources": ["pubmed"]
}
```

Screening uses a paper's extracted `full_text` when available and otherwise
uses its abstract. Attach a full-text PDF to enable evidence extraction from
that candidate. A bibliographic record or DOI link alone does not mean the
full text is available; the response identifies papers screened from abstracts
and reports full-text processing errors/skips.

`publication_year` is already part of the `papers` table; these features do not
require a database migration. A configured key must be valid and active;
HTTP 401/403 errors indicate that the provider rejected it. If a provider key
is missing or inactive, deselect that source and choose another available
source such as PubMed, OpenAlex, or Crossref. Google Scholar search uses the
SerpApi `google_scholar` engine and appears in the source picker only when
`SERPAPI_API_KEY` is configured. ResearchGate remains unavailable because no
supported API is configured. All AI pipeline stages and the separate screening,
extraction, and verification endpoints use the configured local Ollama model;
no external AI API key or paid LLM account is required. Research criteria and
paper text sent to AI processing stay on the local Ollama service. Literature
search queries still go to the external provider APIs selected by the user.
When `OLLAMA_BASE_URL` is changed from its localhost default, AI prompts and
paper text are sent to that configured Ollama endpoint instead.

The Research Brief page exports candidate metadata, screening results, and
available evidence notes as Markdown, JSON, and CSV. These exports support
researcher review; they are not a complete review manuscript. Researchers
must verify citations and evidence against the original publication.

If a search source fails, the pipeline reports its error. When another chosen
source succeeds, its results are retained and the Literature page warns that
the search may be incomplete. If all sources fail, broaden the topic or date
range, check connectivity, and retry; use the API docs' `/health` route to
confirm the backend is running. Independent provider searches run with bounded
concurrency (PubMed requests remain serialized), and up to three candidate
screening requests run concurrently. External provider latency and rate limits
can still affect total run time.