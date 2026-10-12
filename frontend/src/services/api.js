const API_BASE_URL = "http://127.0.0.1:8001";

// =====================================================
// TOKEN MANAGEMENT
// =====================================================

export function saveToken(token) {
  localStorage.setItem("access_token", token);
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function removeToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_name");
}

// =====================================================
// COMMON API REQUEST
// =====================================================

async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `Cannot reach the LitReviewAI backend at ${API_BASE_URL}. ` +
          "Start the backend with `python -m uvicorn app.main:app --reload " +
          "--host 127.0.0.1 --port 8001` from the backend folder. " +
          "Do not run `ollama serve` again if Ollama is already running."
      );
    }
    throw error;
  }

  // Authentication error
  if (response.status === 401) {
    if (!endpoint.startsWith("/auth/") && token) {
      removeToken();
      localStorage.removeItem("active_project_id");
      localStorage.removeItem("research_setup");
      window.dispatchEvent(new Event("auth:expired"));
    }
    throw new Error(
      endpoint === "/auth/login"
        ? "Invalid email or password."
        : "Authentication failed. Please login again."
    );
  }

  // Other API errors
  if (!response.ok) {
    let message = "API request failed.";
    try {
      const errorData = await response.json();
      const detail = errorData.detail;
      if (typeof detail === "string") {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail.map((item) => item.msg).filter(Boolean).join(". ") || message;
      }
    } catch {
      // Ignore JSON parsing error
    }
    throw new Error(message);
  }

  return await response.json();
}

// =====================================================
// AUTH APIs
// =====================================================

export async function login(email, password) {
  const result = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  if (!result.access_token) {
    throw new Error("Login succeeded but the server did not return an access token.");
  }

  saveToken(result.access_token);

  if (result.user?.name) {
    localStorage.setItem("user_name", result.user.name);
  } else {
    localStorage.removeItem("user_name");
  }

  return result;
}

export async function register(name, email, password) {
  return await apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

// =====================================================
// PROJECT APIs
// =====================================================

export async function createProject(projectData) {
  return await apiRequest("/projects/", {
    method: "POST",
    body: JSON.stringify(projectData),
  });
}

export async function getProjects() {
  return await apiRequest("/projects/");
}

export async function getDashboard(projectId) {
  return await apiRequest(`/projects/${projectId}/dashboard`);
}

export async function getProjectPapers(projectId) {
  return await apiRequest(`/projects/${projectId}/papers/list`);
}

export async function searchPubMed(projectId, query, maxResults = 10) {
  return await apiRequest(`/projects/${projectId}/search/pubmed`, {
    method: "POST",
    body: JSON.stringify({ query, max_results: maxResults }),
  });
}

export async function getLiteratureSources() {
  return await apiRequest("/literature/sources");
}

// =====================================================
// SCREENING APIs
// =====================================================

export async function getScreeningStatistics(projectId) {
  return await apiRequest(`/projects/${projectId}/screening/statistics`);
}

export async function getScreeningResults(projectId) {
  return await apiRequest(`/projects/${projectId}/screening/results`);
}

export async function submitHumanFeedback(projectId, paperId, decision, comment = "") {
  return await apiRequest(`/projects/${projectId}/screening/${paperId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ decision, comment }),
  });
}

// =====================================================
// EXTRACTION APIs
// =====================================================

export async function getExtractionStatistics(projectId) {
  return await apiRequest(`/projects/${projectId}/extraction/statistics`);
}

// =====================================================
// FEEDBACK APIs
// =====================================================

export async function getFeedbackStatistics(projectId) {
  return await apiRequest(`/projects/${projectId}/feedback/statistics`);
}

// =====================================================
// LITERATURE REVIEW API
// =====================================================

export async function runLiteratureReview(researchData) {
  return await apiRequest("/literature/run", {
    method: "POST",
    body: JSON.stringify(researchData),
  });
}

// =====================================================
// DASHBOARD AGGREGATE
// =====================================================

export async function getDashboardStats(projectId) {
  const [dashboard, papers, screening, extraction, feedback] = await Promise.all([
    getDashboard(projectId),
    getProjectPapers(projectId),
    getScreeningStatistics(projectId),
    getExtractionStatistics(projectId),
    getFeedbackStatistics(projectId),
  ]);

  return { dashboard, papers, screening, extraction, feedback };
}

// =====================================================
// API HEALTH CHECK
// =====================================================

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      signal: AbortSignal.timeout(4000),
    });
    return response.ok || response.status < 500;
  } catch {
    return false;
  }
}