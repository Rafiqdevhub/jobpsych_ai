# JobPsych AI API Routes Report

## 📋 Overview

This document provides a comprehensive report of all API routes in the JobPsych AI backend system, designed specifically for frontend integration. The API is built with FastAPI and provides AI-powered resume analysis capabilities.

**Base URL:** `https://jobpsych-ai.vercel.app/`  
**Version:** 2.0.0  
**Framework:** FastAPI  
**AI Engine:** Google Gemini 2.5 Flash

---

## 🔐 Authentication

### JWT Token Requirements

- **Header:** `Authorization: Bearer <jwt_token>`

- **Token Source:** External authentication service
- **Token Validation:** HS256 algorithm with JWT_SECRET

### Rate Limiting

- **Public Endpoints:** 5 requests per day per IP address
- **Authenticated Endpoints:** 10 files per user account (tracked via external service)

---

## 📚 API Endpoints

### 1. System Endpoints

#### `GET /`

**Purpose:** API information and system overview

**Authentication:** ❌ None required  
**Rate Limit:** None  
**Response Type:** JSON

**Frontend Integration:**

```javascript
// Get API information
const apiInfo = await fetch("https://api.jobpsych.com/");
const data = await apiInfo.json();

// Use in frontend
console.log(data.app_name); // "JobPsych AI - Role Suggestion and HR Intelligence Platform"
console.log(data.core_capabilities); // Available features
```

**Response Structure:**

```json
{
  "app_name": "JobPsych AI - Role Suggestion and HR Intelligence Platform",
  "message": "AI-Powered Resume Analysis & Job Role Recommendation Service",
  "status": "running",
  "version": "2.0.0",
  "core_capabilities": {
    "resume_parsing": {...},
    "ai_analysis": {...},
    "interview_assistance": {...},
    "batch_processing": {...}
  },
  "api_endpoints": {
    "analyze_resume": {
      "endpoint": "/api/analyze-resume",
      "method": "POST",
      "description": "Basic resume analysis with role recommendations",
      "rate_limit": "5 requests per day per IP address",
      "required_params": ["file (PDF/DOCX)"],
      "optional_params": ["target_role", "job_description"]
    }
  }
}

```

#### `GET /health`

**Purpose:** System health check and configuration validation

**Authentication:** ❌ None required  
**Rate Limit:** None  
**Response Type:** JSON

**Frontend Integration:**

```javascript
// Check API health
const health = await fetch("https://api.jobpsych.com/health");
const status = await health.json();

// Use in frontend
if (status.status === "healthy" && status.api_configured) {
  console.log("API is ready for use");
}
```

**Response Structure:**

```json
{
  "status": "healthy",
  "api_configured": true,
  "environment": "production"
}
```

#### `GET /api/cors-test`

**Purpose:** Test CORS configuration

**Authentication:** ❌ None required  
**Rate Limit:** None  
**Response Type:** JSON

**Frontend Integration:**

```javascript
// Test CORS connectivity
const corsTest = await fetch("https://api.jobpsych.com/api/cors-test");
const result = await corsTest.json();
console.log(result.message); // "CORS is working!"
```

---

### 2. Resume Analysis Endpoints

#### `POST /api/analyze-resume`

**Purpose:** Basic resume analysis with role recommendations (Public endpoint)

**Authentication:** ❌ None required  
**Rate Limit:** 5 requests per day per IP address  
**Content-Type:** `multipart/form-data`  
**File Support:** PDF, DOCX, DOC (max 10MB)

**Parameters:**

- `file` (required): Resume file
- `target_role` (optional): Specific job role to analyze fit for
- `job_description` (optional): Job requirements for better analysis

**Frontend Integration:**

```javascript
// Basic resume analysis
async function analyzeResume(file, targetRole = null, jobDescription = null) {
  const formData = new FormData();
  formData.append("file", file);

  if (targetRole) formData.append("target_role", targetRole);
  if (jobDescription) formData.append("job_description", jobDescription);

  try {
    const response = await fetch(
      "https://api.jobpsych.com/api/analyze-resume",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Analysis failed");
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Resume analysis failed:", error);
    throw error;
  }
}

// Usage example
const fileInput = document.getElementById("resume-file");
const file = fileInput.files[0];
const analysis = await analyzeResume(file, "Software Engineer");
console.log("Role recommendations:", analysis.roleRecommendations);
```

**Response Structure:**

```json
{
  "resumeData": {
    "personalInfo": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "location": "San Francisco, CA"
    },
    "workExperience": [
      {
        "company": "Tech Corp",
        "position": "Senior Developer",
        "duration": "2020-2023",
        "description": "Led development of web applications..."
      }
    ],
    "education": [
      {
        "degree": "Bachelor of Science",
        "field": "Computer Science",
        "institution": "University of Tech",
        "year": "2019"
      }
    ],
    "skills": ["Python", "React", "AWS", "Docker"],
    "highlights": ["Led team of 5 developers", "Improved performance by 40%"]
  },
  "questions": [], // Empty for basic analysis
  "roleRecommendations": [
    {
      "roleName": "Software Engineer",
      "matchPercentage": 85,
      "reasoning": "Strong technical skills match...",
      "requiredSkills": ["Python", "React"],
      "missingSkills": ["Kubernetes"],
      "learningResources": [
        "Kubernetes documentation",
        "Docker containerization courses"
      ]
    }
  ]
}
```

---

#### `POST /api/hiredesk-analyze`

**Purpose:** Advanced HR analysis with complete assessment suite (Authenticated endpoint)

**Authentication:** ✅ JWT token required  
**Rate Limit:** 10 files per user account  
**Content-Type:** `multipart/form-data`  
**File Support:** PDF, DOCX, DOC (max 10MB)

**Parameters:**

- `file` (required): Resume file
- `target_role` (required): Specific job role for detailed analysis
- `job_description` (required): Complete job requirements

**Frontend Integration:**

```javascript
// Advanced HR analysis (requires authentication)
async function advancedAnalyzeResume(
  file,
  targetRole,
  jobDescription,
  jwtToken
) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_role", targetRole);
  formData.append("job_description", jobDescription);

  try {
    const response = await fetch(
      "https://api.jobpsych.com/api/hiredesk-analyze",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwtToken}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail.message || "Analysis failed");
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Advanced analysis failed:", error);
    throw error;
  }
}

// Usage example
const analysis = await advancedAnalyzeResume(
  resumeFile,
  "Product Manager",
  "Lead product development for SaaS platform...",
  userJwtToken
);

// Access comprehensive results
console.log("Resume Score:", analysis.resumeScore.overall_score);
console.log("Interview Questions:", analysis.questions);
console.log("Personality Insights:", analysis.personalityInsights);
```

**Response Structure:**

```json
{
  "success": true,
  "fit_status": "fit",
  "reasoning": "Strong technical background and leadership experience align well with product management requirements",
  "resumeData": {
    "personalInfo": {...},
    "workExperience": [...],
    "education": [...],
    "skills": [...],
    "highlights": [...]
  },
  "roleRecommendations": [
    {
      "roleName": "Product Manager",
      "matchPercentage": 88,
      "reasoning": "Excellent analytical skills and technical background...",
      "requiredSkills": ["Product Strategy", "Data Analysis"],
      "missingSkills": ["Agile Certification"],
      "learningResources": [...]
    }
  ],
  "questions": [
    {
      "question": "Can you describe a time when you led a cross-functional team through a product launch?",
      "type": "behavioral",
      "category": "leadership"
    },
    {
      "question": "How do you prioritize features in your product roadmap?",
      "type": "technical",
      "category": "product_management"
    }
  ],
  "best_fit_role": "Product Manager",
  "resumeScore": {
    "overall_score": 85,
    "technical_score": 82,
    "experience_score": 88,
    "education_score": 90,
    "communication_score": 78,
    "strengths": [
      "Strong leadership experience",
      "Technical background",
      "Data-driven decision making"
    ],
    "weaknesses": [
      "Limited formal product management education",
      "Could benefit from Agile certification"
    ],
    "recommendations": [
      "Consider Agile certification",
      "Focus on product management courses",
      "Build network in product community"
    ]
  },
  "personalityInsights": {
    "work_style": "Analytical and collaborative",
    "leadership_style": "Transformational",
    "communication_style": "Clear and concise",
    "decision_making": "Data-driven approach",
    "strengths": ["Problem-solving", "Team collaboration", "Strategic thinking"],
    "potential_challenges": ["May need to develop more assertive communication"]
  },
  "careerPath": {
    "current_level": "Senior Individual Contributor",
    "next_roles": ["Product Manager", "Engineering Manager"],
    "timeline": "1-2 years",
    "development_areas": [
      "Product management fundamentals",
      "Agile methodologies",
      "Stakeholder management"
    ],
    "growth_path": "Technical → Leadership track",
    "salary_projection": "$120K - $160K",
    "career_advice": "Leverage technical background while building product skills"
  }
}

```

---

#### `POST /api/batch-analyze`

**Purpose:** Process multiple resumes simultaneously for bulk analysis

**Authentication:** ❌ None required  
**Rate Limit:** None (reasonable usage expected)  
**Content-Type:** `multipart/form-data`  
**File Support:** PDF, DOCX, DOC (max 10MB each)  
**Batch Limit:** 2-10 files per request

**Parameters:**

- `files` (required): Array of resume files (2-10 files)
- `target_role` (optional): Analyze all resumes against this role
- `job_description` (optional): Job requirements for focused analysis

**Frontend Integration:**

```javascript
// Batch analysis for multiple resumes
async function batchAnalyzeResumes(
  files,
  targetRole = null,
  jobDescription = null
) {
  const formData = new FormData();

  // Add all files to form data
  files.forEach((file, index) => {
    formData.append("files", file);
  });

  if (targetRole) formData.append("target_role", targetRole);
  if (jobDescription) formData.append("job_description", jobDescription);

  try {
    const response = await fetch("https://api.jobpsych.com/api/batch-analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Batch analysis failed");
    }

    const results = await response.json();
    return results;
  } catch (error) {
    console.error("Batch analysis failed:", error);
    throw error;
  }
}

// Usage example
const resumeFiles = Array.from(document.getElementById("resume-files").files);
const batchResults = await batchAnalyzeResumes(
  resumeFiles,
  "Frontend Developer",
  "Build responsive web applications using React..."
);

// Process results for each candidate
batchResults.forEach((result, index) => {
  console.log(`Candidate ${index + 1}:`, result.resumeData.personalInfo.name);
  console.log("Score:", result.resumeScore?.overall_score || "N/A");
});
```

**Response Structure:**

```json
[
  {
    "resumeData": {
      "personalInfo": {...},
      "workExperience": [...],
      "education": [...],
      "skills": [...],
      "highlights": [...]
    },
    "questions": [
      {
        "question": "Describe your experience with React development",
        "type": "technical",
        "category": "frontend"
      }
    ],
    "roleRecommendations": [...],
    "resumeScore": {
      "overall_score": 82,
      "technical_score": 85,
      "experience_score": 80,
      "education_score": 90,
      "communication_score": 75,
      "strengths": [...],
      "weaknesses": [...],
      "recommendations": [...]
    },
    "personalityInsights": {
      "work_style": "Collaborative and detail-oriented",
      "leadership_style": "Supportive",
      "communication_style": "Clear and methodical",
      "decision_making": "Analytical approach"
    },
    "careerPath": {
      "current_level": "Mid-level Developer",
      "next_roles": ["Senior Frontend Developer", "Frontend Team Lead"],
      "timeline": "1-2 years",
      "development_areas": [...]
    }
  }
]

```

---

#### `POST /api/compare-resumes`

**Purpose:** Compare and rank multiple candidates for the same position

**Authentication:** ❌ None required  
**Rate Limit:** None (reasonable usage expected)  
**Content-Type:** `multipart/form-data`  
**File Support:** PDF, DOCX, DOC (max 10MB each)  
**Comparison Limit:** 2-5 files per request

**Parameters:**

- `files` (required): Array of resume files (2-5 files)

**Frontend Integration:**

```javascript
// Compare and rank multiple candidates
async function compareResumes(files) {
  const formData = new FormData();

  files.forEach((file, index) => {
    formData.append("files", file);
  });

  try {
    const response = await fetch(
      "https://api.jobpsych.com/api/compare-resumes",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Comparison failed");
    }

    const comparison = await response.json();
    return comparison;
  } catch (error) {
    console.error("Resume comparison failed:", error);
    throw error;
  }
}

// Usage example
const candidateFiles = Array.from(
  document.getElementById("candidate-files").files
);
const comparisonResult = await compareResumes(candidateFiles);

// Display ranking results
console.log(
  "Total candidates:",
  comparisonResult.comparison_summary.total_candidates
);
console.log(
  "Highest score:",
  comparisonResult.comparison_summary.highest_score
);

comparisonResult.ranked_candidates.forEach((candidate, index) => {
  console.log(`${index + 1}. ${candidate.filename}: ${candidate.score} points`);
  console.log(`   Strengths: ${candidate.strengths?.join(", ")}`);
});
```

**Response Structure:**

```json
{
  "comparison_summary": {
    "total_candidates": 4,
    "highest_score": 88,
    "average_score": 76.5,
    "score_range": "65-88"
  },
  "ranked_candidates": [
    {
      "filename": "john_doe_resume.pdf",
      "resumeData": {
        "personalInfo": {
          "name": "John Doe",
          "email": "john@example.com"
        },
        "workExperience": [...],
        "education": [...],
        "skills": [...],
        "highlights": [...]
      },
      "score": 88,
      "strengths": [
        "Exceptional technical skills",
        "Strong leadership experience",
        "Excellent communication"
      ],
      "weaknesses": [
        "Limited experience with specific technologies",
        "Could benefit from advanced certifications"
      ]
    },
    {
      "filename": "jane_smith_resume.pdf",
      "resumeData": {...},
      "score": 82,
      "strengths": [...],
      "weaknesses": [...]
    }
  ],
  "recommendations": [
    "Consider top 3 candidates for interviews",
    "Review candidates with scores > 80 for immediate consideration",
    "Candidates with scores < 60 may need additional training",
    "Schedule technical interviews for top 2 candidates"
  ]
}

```

---

## 🔄 Complete Frontend Integration Workflow

### 1. Initial Setup

```javascript
// API Configuration
const API_BASE_URL = "https://api.jobpsych.com";
const API_ENDPOINTS = {
  ANALYZE_RESUME: "/api/analyze-resume",
  HIREDESK_ANALYZE: "/api/hiredesk-analyze",
  BATCH_ANALYZE: "/api/batch-analyze",
  COMPARE_RESUMES: "/api/compare-resumes",
};

// Utility function for API calls
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail?.message || data.message || "API call failed"
      );
    }

    return data;
  } catch (error) {
    console.error(`API call to ${endpoint} failed:`, error);
    throw error;
  }
}
```

### 2. Authentication Handling

```javascript
// JWT Token Management
class AuthManager {
  static getToken() {
    return localStorage.getItem("jwt_token");
  }

  static setToken(token) {
    localStorage.setItem("jwt_token", token);
  }

  static clearToken() {
    localStorage.removeItem("jwt_token");
  }

  static isAuthenticated() {
    const token = this.getToken();
    return token && !this.isTokenExpired(token);
  }

  static isTokenExpired(token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
}
```

### 3. Resume Analysis Service

```javascript
// Resume Analysis Service
class ResumeAnalysisService {
  static async analyzeBasic(file, targetRole = null, jobDescription = null) {
    const formData = new FormData();
    formData.append("file", file);
    if (targetRole) formData.append("target_role", targetRole);
    if (jobDescription) formData.append("job_description", jobDescription);

    return await apiCall(API_ENDPOINTS.ANALYZE_RESUME, {
      method: "POST",
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  }

  static async analyzeAdvanced(file, targetRole, jobDescription) {
    const token = AuthManager.getToken();
    if (!token) {
      throw new Error("Authentication required for advanced analysis");
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_role", targetRole);
    formData.append("job_description", jobDescription);

    return await apiCall(API_ENDPOINTS.HIREDESK_ANALYZE, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });
  }

  static async analyzeBatch(files, targetRole = null, jobDescription = null) {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    if (targetRole) formData.append("target_role", targetRole);
    if (jobDescription) formData.append("job_description", jobDescription);

    return await apiCall(API_ENDPOINTS.BATCH_ANALYZE, {
      method: "POST",
      body: formData,
    });
  }

  static async compareResumes(files) {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    return await apiCall(API_ENDPOINTS.COMPARE_RESUMES, {
      method: "POST",
      body: formData,
    });
  }
}
```

### 4. Error Handling

```javascript
// Error Handling
class APIErrorHandler {
  static handleError(error) {
    if (error.message.includes("RATE_LIMIT_EXCEEDED")) {
      return {
        type: "RATE_LIMIT",
        message: "Upload limit reached. Please try again later.",
        details: error.details,
      };
    }

    if (error.message.includes("VALIDATION_ERROR")) {
      return {
        type: "VALIDATION",
        message: "Invalid file or parameters.",
        details: error.details,
      };
    }

    if (error.message.includes("AUTHENTICATION_ERROR")) {
      AuthManager.clearToken();
      return {
        type: "AUTHENTICATION",
        message: "Please log in again.",
        action: "redirect_to_login",
      };
    }

    return {
      type: "UNKNOWN",
      message: "An unexpected error occurred.",
      details: error.message,
    };
  }
}
```

### 5. Complete Usage Example

```javascript
// Complete integration example
async function handleResumeUpload(files, analysisType = "basic") {
  try {
    let results;

    switch (analysisType) {
      case "basic":
        results = await ResumeAnalysisService.analyzeBasic(files[0]);
        break;

      case "advanced":
        if (!AuthManager.isAuthenticated()) {
          throw new Error("Authentication required");
        }
        results = await ResumeAnalysisService.analyzeAdvanced(
          files[0],
          "Software Engineer",
          "Develop and maintain web applications..."
        );
        break;

      case "batch":
        results = await ResumeAnalysisService.analyzeBatch(files);
        break;

      case "compare":
        results = await ResumeAnalysisService.compareResumes(files);
        break;
    }

    // Process results
    updateUI(results);
    return results;
  } catch (error) {
    const errorInfo = APIErrorHandler.handleError(error);
    showErrorMessage(errorInfo);
    throw error;
  }
}
```

---

## 📊 Rate Limiting & Usage Guidelines

### Public Endpoints

- **`/api/analyze-resume`**: 5 requests per day per IP address
- **`/api/batch-analyze`**: No specific limit (reasonable usage expected)
- **`/api/compare-resumes`**: No specific limit (reasonable usage expected)

### Authenticated Endpoints

- **`/api/hiredesk-analyze`**: 10 files per user account (tracked via external service)

### File Upload Limits

- **Maximum file size**: 10MB per file
- **Supported formats**: PDF, DOCX, DOC
- **Batch limits**: 2-10 files for batch analysis, 2-5 files for comparison

### Error Response Codes

- **400 Bad Request**: Invalid parameters or file format
- **401 Unauthorized**: Missing or invalid JWT token
- **422 Unprocessable Entity**: Validation errors or file processing issues
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side processing errors

---

## 🔧 Environment Configuration

### Required Environment Variables

```javascript
// Frontend configuration
const CONFIG = {
  API_BASE_URL:
    process.env.REACT_APP_API_BASE_URL || "https://api.jobpsych.com",
  AUTH_SERVICE_URL:
    process.env.REACT_APP_AUTH_SERVICE_URL || "https://auth.jobpsych.com",
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_FORMATS: [".pdf", ".docx", ".doc"],
  BATCH_LIMITS: {
    ANALYZE: 10,
    COMPARE: 5,
  },
};
```

## Best Practices for Frontend Integration

### 1. File Upload Handling

```javascript
// File validation before upload
function validateFile(file) {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ];

  if (file.size > maxSize) {
    throw new Error("File size exceeds 10MB limit");
  }

  if (!allowedTypes.includes(file.type)) {
    throw new Error("Only PDF and DOCX files are supported");
  }

  return true;
}
```

### 2. Loading States & Progress

```javascript
// Show loading during analysis
async function analyzeWithLoading(file) {
  setLoading(true);
  setProgress(0);

  try {
    setProgress(25); // File upload started
    const result = await ResumeAnalysisService.analyzeBasic(file);
    setProgress(100); // Complete
    return result;
  } catch (error) {
    setProgress(0);
    throw error;
  } finally {
    setLoading(false);
  }
}
```

### 3. Error Recovery

```javascript
// Implement retry logic for failed requests
async function retryAnalysis(file, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await ResumeAnalysisService.analyzeBasic(file);
    } catch (error) {
      if (attempt === maxRetries) throw error;

      // Wait before retry (exponential backoff)
      await new Promise((resolve) =>
        setTimeout(resolve, Math.pow(2, attempt) * 1000)
      );
    }
  }
}
```

### 4. Caching Strategy

```javascript
// Cache analysis results
class AnalysisCache {
  static cache = new Map();

  static get(fileHash) {
    return this.cache.get(fileHash);
  }

  static set(fileHash, result) {
    this.cache.set(fileHash, {
      result,
      timestamp: Date.now(),
    });
  }

  static isExpired(fileHash, maxAge = 3600000) {
    // 1 hour
    const cached = this.cache.get(fileHash);
    return !cached || Date.now() - cached.timestamp > maxAge;
  }
}
```

---
