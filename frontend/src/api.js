const API_BASE_URL = "http://127.0.0.1:8001";


export function saveToken(token) {
  localStorage.setItem(
    "access_token",
    token
  );
}


export function getToken() {
  return localStorage.getItem(
    "access_token"
  );
}


export function removeToken() {
  localStorage.removeItem(
    "access_token"
  );
}


async function apiRequest(
  endpoint,
  options = {}
) {

  const token = getToken();

  const headers = {
    ...(options.headers || {})
  };

  if (token) {
    headers["Authorization"] =
      `Bearer ${token}`;
  }

  if (
    options.body &&
    !(options.body instanceof FormData)
  ) {
    headers["Content-Type"] =
      "application/json";
  }

  let response;
  try {
    response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        ...options,
        headers
      }
    );
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

  if (response.status === 401) {
    throw new Error(
      "Authentication failed. Please login again."
    );
  }

  if (!response.ok) {

    let message =
      "API request failed.";

    try {

      const errorData =
        await response.json();

      message =
        errorData.detail ||
        message;

    } catch {
      // ignore
    }

    throw new Error(message);
  }

  return await response.json();
}


export async function createProject(
  projectData
) {

  return await apiRequest(
    "/projects/",
    {
      method: "POST",
      body: JSON.stringify(
        projectData
      )
    }
  );
}


export async function getProjects() {

  return await apiRequest(
    "/projects/"
  );
}


export async function getDashboard(
  projectId
) {

  return await apiRequest(
    `/projects/${projectId}/dashboard`
  );
}


export async function getProjectPapers(
  projectId
) {

  return await apiRequest(
    `/projects/${projectId}/papers/list`
  );
}


export async function getScreeningStatistics(
  projectId
) {

  return await apiRequest(
    `/projects/${projectId}/screening/statistics`
  );
}


export async function getScreeningResults(
  projectId
) {

  return await apiRequest(
    `/projects/${projectId}/screening/results`
  );
}


export async function getExtractionStatistics(
  projectId
) {

  return await apiRequest(
    `/projects/${projectId}/extraction/statistics`
  );
}


export async function getFeedbackStatistics(
  projectId
) {

  return await apiRequest(
    `/projects/${projectId}/feedback/statistics`
  );
}


export async function getDashboardStats(
  projectId
) {

  const [
    dashboard,
    papers,
    screening,
    extraction,
    feedback
  ] = await Promise.all([

    getDashboard(projectId),

    getProjectPapers(projectId),

    getScreeningStatistics(
      projectId
    ),

    getExtractionStatistics(
      projectId
    ),

    getFeedbackStatistics(
      projectId
    )

  ]);

  return {
    dashboard,
    papers,
    screening,
    extraction,
    feedback
  };
}

export async function runLiteratureReview(
  researchData
) {

  return await apiRequest(
    "/literature/run",
    {
      method: "POST",
      body: JSON.stringify(
        researchData
      )
    }
  );
}