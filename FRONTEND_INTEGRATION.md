# JobPsych Resume Analysis API - Frontend Integration Guide

This document provides instructions for integrating your frontend application with the JobPsych Resume Analysis API featuring a **two-tier rate limiting system**.

## System Overview

JobPsych is a resume analysis and interview question generation system with a **two-tier rate limiting approach**:

### Anonymous Users (No Authentication Required)

- **2 free resume uploads per IP address** (lifetime limit)
- When limit is reached → prompted to create an account

### Authenticated Users

- **Free tier**: 2 additional resume uploads after signup
- **Premium tier**: Unlimited resume uploads after payment
- Can track upload history and access from any device

### Rate Limiting Flow

1. **Anonymous user uploads** → IP-based tracking (2 uploads max)
2. **Limit exceeded** → Show signup prompt
3. **User authenticates** → User-based tracking (2 more uploads)
4. **User limit exceeded** → Show upgrade to premium
5. **Premium user** → Unlimited uploads

### Monetization Strategy

- Free users get total of 4 uploads (2 anonymous + 2 authenticated)
- Natural conversion funnel: Anonymous → Authenticated → Premium
- Clear value proposition at each step

## API Endpoints

### Base URL

- **Production**: `https://jobpsych.vercel.app`
- **Local Development**: `http://localhost:8001`

### Main Endpoints

1. **API Information**

   - `GET /`
   - Returns API info including rate limit policies for both tiers

2. **Health Check**

   - `GET /health`
   - Returns API health status and environment info

3. **Resume Analysis**

   - `POST /api/analyze-resume`
   - Upload and analyze a resume
   - **Rate limited based on authentication status**

4. **Rate Limit Status**

   - `GET /api/rate-limit-status`
   - Check current rate limit status for IP or authenticated user

5. **Signup Required Info**

   - `GET /api/auth/signup-required`
   - Information shown when anonymous users hit their limit

6. **Upgrade Plan Info**
   - `GET /api/upgrade-plan`
   - Information about premium subscription plans

## Frontend Integration Examples

### 1. Check Rate Limit Status

```javascript
async function checkRateLimitStatus(authToken = null) {
  try {
    const headers = {};
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`;
    }

    const response = await fetch("/api/rate-limit-status", { headers });
    const status = await response.json();

    return status;
  } catch (error) {
    console.error("Rate limit status error:", error);
    throw error;
  }
}
```

### 2. Upload Resume with Two-Tier Handling

```javascript
async function uploadResume(file, authToken = null) {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const headers = {};
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`;
    }

    const response = await fetch("/api/analyze-resume", {
      method: "POST",
      headers,
      body: formData,
    });

    if (response.status === 429) {
      const errorData = await response.json();

      if (errorData.detail.requires_auth) {
        // Anonymous user hit IP limit - show signup
        showSignupPrompt(errorData.detail);
      } else if (errorData.detail.requires_payment) {
        // Authenticated user hit free limit - show upgrade
        showUpgradePrompt(errorData.detail);
      }
      return null;
    }

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Upload error:", error);
    throw error;
  }
}
```

### 3. Handle Different Rate Limit Scenarios

```javascript
function showSignupPrompt(errorDetail) {
  // Show modal encouraging signup
  const modal = document.getElementById("signup-modal");
  modal.querySelector(".message").textContent = errorDetail.message;
  modal.querySelector(".auth-message").textContent = errorDetail.auth_message;

  // Add click handler for signup button
  modal.querySelector(".signup-btn").onclick = () => {
    window.location.href = errorDetail.signup_url || "/auth/signup";
  };

  // Show the modal
  modal.style.display = "block";
}

function showUpgradePrompt(errorDetail) {
  // Show modal encouraging premium upgrade
  const modal = document.getElementById("upgrade-modal");
  modal.querySelector(".message").textContent = errorDetail.message;

  // Add click handler for upgrade button
  modal.querySelector(".upgrade-btn").onclick = () => {
    window.location.href = errorDetail.upgrade_url || "/api/upgrade-plan";
  };

  // Show the modal
  modal.style.display = "block";
}
```

### 4. Dynamic UI Updates Based on Status

```javascript
async function updateUIBasedOnStatus(authToken = null) {
  try {
    const status = await checkRateLimitStatus(authToken);

    // Update rate limit display
    const rateLimitEl = document.getElementById("rate-limit-info");

    if (status.is_development) {
      rateLimitEl.innerHTML = "Development mode: Unlimited uploads";
      return;
    }

    if (status.authenticated) {
      // Authenticated user
      if (status.tier === "premium") {
        rateLimitEl.innerHTML = "Premium: Unlimited uploads available";
      } else {
        rateLimitEl.innerHTML = `Free account: ${status.remaining_uploads} uploads remaining`;
      }
    } else {
      // Anonymous user
      rateLimitEl.innerHTML = `Free trial: ${status.remaining_uploads} of ${status.limit} uploads remaining from this location`;
    }

    // Update upload button state
    const uploadBtn = document.getElementById("upload-button");
    if (status.remaining_uploads <= 0 && status.tier !== "premium") {
      uploadBtn.disabled = true;
      uploadBtn.textContent = status.authenticated
        ? "Upgrade to Continue"
        : "Sign Up to Continue";
    } else {
      uploadBtn.disabled = false;
      uploadBtn.textContent = "Analyze Resume";
    }

    // Show appropriate call-to-action
    if (status.remaining_uploads <= 0) {
      if (status.authenticated) {
        document.getElementById("upgrade-cta").style.display = "block";
      } else {
        document.getElementById("signup-cta").style.display = "block";
      }
    }
  } catch (error) {
    console.error("Failed to update UI:", error);
  }
}
```

### 5. Complete Integration Example

```javascript
class JobPsychIntegration {
  constructor() {
    this.authToken = localStorage.getItem("authToken");
    this.init();
  }

  async init() {
    await this.updateUI();
    this.setupEventHandlers();
  }

  async updateUI() {
    await updateUIBasedOnStatus(this.authToken);
  }

  setupEventHandlers() {
    // Resume upload form
    document
      .getElementById("resume-form")
      .addEventListener("submit", async (e) => {
        e.preventDefault();

        const fileInput = e.target.querySelector('input[type="file"]');
        const file = fileInput.files[0];

        if (!file) {
          alert("Please select a file to upload");
          return;
        }

        try {
          const result = await uploadResume(file, this.authToken);
          if (result) {
            this.displayResults(result);
            await this.updateUI(); // Refresh UI after successful upload
          }
        } catch (error) {
          alert(`Upload failed: ${error.message}`);
        }
      });

    // Auth state changes
    window.addEventListener("authStateChanged", (e) => {
      this.authToken = e.detail.token;
      this.updateUI();
    });
  }

  displayResults(data) {
    // Display resume analysis results
    const resultsEl = document.getElementById("results");
    // ... (same as before)
  }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  new JobPsychIntegration();
});
```

## Error Handling

### Rate Limit Error Responses

1. **Anonymous User Limit Exceeded (429)**

   ```json
   {
     "detail": {
       "error": "Free limit exceeded",
       "message": "You have used all 2 free resume analyses from this location. Sign up to continue with more analyses!",
       "requires_auth": true,
       "auth_message": "Create an account to unlock more resume analyses",
       "signup_url": "/auth/signup"
     }
   }
   ```

2. **Authenticated User Limit Exceeded (429)**
   ```json
   {
     "detail": {
       "error": "Free tier limit exceeded",
       "message": "You have used all 2 free analyses in your account. Upgrade to premium for unlimited access!",
       "requires_payment": true,
       "tier": "free",
       "upgrade_url": "/api/upgrade-plan"
     }
   }
   ```

## Rate Limit Status Response Examples

### Anonymous User

```json
{
  "ip": "192.168.1.100",
  "user_id": null,
  "authenticated": false,
  "limit": 2,
  "limit_type": "ip_based",
  "remaining_uploads": 1,
  "uploads_used": 1,
  "tier": "anonymous",
  "signup_url": "/auth/signup"
}
```

### Authenticated Free User

```json
{
  "ip": "192.168.1.100",
  "user_id": "user123",
  "authenticated": true,
  "limit": 2,
  "limit_type": "user_based",
  "remaining_uploads": 0,
  "uploads_used": 2,
  "tier": "free",
  "upgrade_url": "/api/upgrade-plan"
}
```

### Premium User

```json
{
  "ip": "192.168.1.100",
  "user_id": "user123",
  "authenticated": true,
  "limit": "unlimited",
  "limit_type": "user_based",
  "remaining_uploads": "unlimited",
  "uploads_used": 15,
  "tier": "premium"
}
```

## Best Practices

### 1. User Experience

- **Clear Communication**: Always explain the limits and benefits of upgrading
- **Progressive Disclosure**: Show signup benefits when IP limit is reached
- **Smooth Transitions**: Make auth and payment flows seamless

### 2. Rate Limit Management

- Check status before allowing uploads
- Cache status for better performance
- Handle all rate limit scenarios gracefully

### 3. Authentication Integration

- Store auth tokens securely
- Handle token expiration
- Update UI immediately when auth state changes

### 4. Conversion Optimization

- Highlight value proposition at each limit
- Make signup and upgrade processes clear
- Show progress through the funnel

---

This two-tier system provides a natural progression from anonymous usage to paid subscription while preventing abuse and maximizing conversion opportunities.
