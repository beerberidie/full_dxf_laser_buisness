# Mobile Integration Quick Start Guide
## Getting Started with Laser Sync Flow Integration

**Last Updated:** 2025-10-27

---

## Prerequisites

### Backend Requirements
- Python 3.9 or higher
- pip (Python package manager)
- SQLite 3
- Existing Laser OS installation

### Frontend Requirements
- Node.js 18+ and npm
- Git
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Development Tools (Recommended)
- VS Code or PyCharm
- Postman or Thunder Client (API testing)
- React DevTools browser extension

---

## Phase 1: Backend API Setup (Week 1-2)

### Step 1: Install Dependencies

```bash
# Navigate to Laser OS root directory
cd /path/to/laser-os

# Install required Python packages
pip install PyJWT flask-cors

# Or add to requirements.txt and install
echo "PyJWT==2.8.0" >> requirements.txt
echo "flask-cors==4.0.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: Create Mobile API Blueprint

Create new file: `app/routes/mobile_api.py`

```python
"""
Mobile API Blueprint for Laser OS
Provides REST API endpoints for mobile application integration
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta
from app import db
from app.models import User, Operator, Project, QueueItem, LaserRun, MachineSettingsPreset

bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# JWT Configuration
JWT_SECRET_KEY = 'your-secret-key-change-in-production'
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

# TODO: Implement token generation, validation, and endpoints
# See full implementation in MOBILE_APP_INTEGRATION_PLAN.md Section 8.1
```

**Full implementation available in:** `docs/MOBILE_APP_INTEGRATION_PLAN.md` (Section 8.1)

### Step 3: Register Blueprint

Edit `app/__init__.py`:

```python
def create_app(config_name='default'):
    app = Flask(__name__)
    # ... existing configuration ...
    
    # Register existing blueprints
    from app.routes import auth, admin, main, clients, projects, queue
    # ... other imports ...
    
    # Register mobile API blueprint
    from app.routes import mobile_api
    app.register_blueprint(mobile_api.bp)
    
    return app
```

### Step 4: Configure CORS

Edit `app/__init__.py`:

```python
from flask_cors import CORS

def create_app(config_name='default'):
    app = Flask(__name__)
    # ... existing configuration ...
    
    # Configure CORS for mobile API
    CORS(app, resources={
        r"/api/mobile/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],  # Development
            "methods": ["GET", "POST", "PATCH", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False
        }
    })
    
    return app
```

### Step 5: Test Authentication Endpoint

```bash
# Start Flask development server
python run.py

# In another terminal, test login endpoint
curl -X POST http://localhost:5000/api/mobile/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Expected response:
# {
#   "success": true,
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "operator": {...}
# }
```

### Step 6: Implement Remaining Endpoints

Implement the following endpoints (see full code in integration plan):

**Authentication:**
- ✅ `POST /api/mobile/auth/login`
- ✅ `POST /api/mobile/auth/refresh`
- ✅ `POST /api/mobile/auth/logout`

**Queue Management:**
- ✅ `GET /api/mobile/queue`
- ✅ `GET /api/mobile/queue/{id}`
- ✅ `POST /api/mobile/queue/{id}/start`
- ✅ `POST /api/mobile/queue/{id}/pause`
- ✅ `POST /api/mobile/queue/{id}/complete`
- ✅ `PATCH /api/mobile/queue/{id}`

**Project Management:**
- ✅ `GET /api/mobile/projects`
- ✅ `GET /api/mobile/projects/{id}`
- ✅ `POST /api/mobile/projects/{id}/add-to-queue`
- ✅ `PATCH /api/mobile/projects/{id}`

**Presets & Operators:**
- ✅ `GET /api/mobile/presets`
- ✅ `GET /api/mobile/operators/me`
- ✅ `GET /api/mobile/operators/me/stats`

---

## Phase 2: Mobile App Integration (Week 3-4)

### Step 1: Clone Mobile App Repository

```bash
# Navigate to your projects directory
cd /path/to/projects

# Clone or copy the mobile app
cp -r laser-sync-flow-main laser-sync-flow-integrated
cd laser-sync-flow-integrated
```

### Step 2: Install Dependencies

```bash
# Install npm packages
npm install

# Install additional dependencies for API integration
npm install axios
```

### Step 3: Configure API Base URL

Create `.env.development` file:

```env
VITE_API_BASE_URL=http://localhost:5000/api/mobile
```

Create `.env.production` file:

```env
VITE_API_BASE_URL=https://your-production-domain.com/api/mobile
```

### Step 4: Create API Client

Create `src/lib/apiClient.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/mobile';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add request interceptor for auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('laser_os_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle 401 and refresh token
    // See full implementation in integration plan
    return Promise.reject(error);
  }
);

export default apiClient;
```

**Full implementation available in:** `docs/MOBILE_APP_INTEGRATION_PLAN.md` (Section 8.2)

### Step 5: Create Login Page

Create `src/pages/Login.tsx`:

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '@/lib/apiClient';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  // Render login form
  // See full implementation in integration plan
};
```

**Full implementation available in:** `docs/MOBILE_APP_INTEGRATION_PLAN.md` (Section 8.3)

### Step 6: Update App Routing

Edit `src/App.tsx`:

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Index } from './pages/Index';
import { isAuthenticated } from './lib/apiClient';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Index />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### Step 7: Replace Mock Data with API Calls

Edit `src/pages/Index.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { getQueue, getProjects, startJob, completeJob } from '@/lib/apiClient';

export const Index = () => {
  const [queueItems, setQueueItems] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    
    // Poll for updates every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [queueData, projectsData] = await Promise.all([
        getQueue(),
        getProjects()
      ]);
      setQueueItems(queueData.queue_items);
      setProjects(projectsData.projects);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Render UI with real data
  // ...
};
```

### Step 8: Test Integration

```bash
# Start backend (in Laser OS directory)
python run.py

# Start frontend (in mobile app directory)
npm run dev

# Open browser to http://localhost:5173
# Login with your Laser OS credentials
# Verify queue and projects load from API
```

---

## Phase 3: Testing (Week 5)

### Backend Unit Tests

Create `tests/test_mobile_api.py`:

```python
import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_login_success(client):
    # Test successful login
    response = client.post('/api/mobile/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

# Add more tests...
```

Run tests:
```bash
pytest tests/test_mobile_api.py -v
```

### Frontend Component Tests

```bash
# Run component tests
npm run test

# Run E2E tests (if configured)
npm run test:e2e
```

---

## Phase 4: Deployment (Week 6)

### Backend Deployment

1. **Update production configuration:**
   ```python
   # config.py
   class ProductionConfig(Config):
       JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
       CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
   ```

2. **Set environment variables:**
   ```bash
   export JWT_SECRET_KEY="your-secure-random-key"
   export CORS_ORIGINS="https://mobile.yourdomain.com"
   ```

3. **Configure Nginx/Apache for HTTPS**

### Frontend Deployment

1. **Build production bundle:**
   ```bash
   npm run build
   ```

2. **Deploy to hosting:**
   - Upload `dist/` folder to web server
   - Configure SPA routing (redirect all to index.html)
   - Set up HTTPS/SSL certificate

---

## Troubleshooting

### Common Issues

**Issue:** CORS errors in browser console  
**Solution:** Verify CORS configuration in `app/__init__.py` includes mobile app origin

**Issue:** 401 Unauthorized on all API requests  
**Solution:** Check JWT token is being sent in Authorization header

**Issue:** Token refresh not working  
**Solution:** Verify refresh token is stored in localStorage and not expired

**Issue:** Mobile app shows old data  
**Solution:** Check polling interval is running and API is returning updated data

---

## Next Steps

1. ✅ Complete backend API implementation
2. ✅ Integrate mobile app with API
3. ✅ Test all workflows end-to-end
4. ✅ Deploy to staging environment
5. ✅ Conduct user acceptance testing
6. ✅ Deploy to production
7. ✅ Train operators
8. ✅ Monitor and gather feedback

---

## Resources

- **Full Integration Plan:** `docs/MOBILE_APP_INTEGRATION_PLAN.md`
- **Executive Summary:** `docs/MOBILE_INTEGRATION_EXECUTIVE_SUMMARY.md`
- **API Documentation:** (Generate with Swagger/OpenAPI)
- **User Guide:** (Create after deployment)

---

## Support

For questions or issues during implementation:
- Review the full integration plan document
- Check existing Laser OS documentation
- Test API endpoints with Postman/Thunder Client
- Review browser console and Flask logs for errors

---

**Document End**

