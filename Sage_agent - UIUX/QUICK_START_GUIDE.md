# Sage API Quick Start Guide

**For:** South African Sage Business Cloud Accounting Integration  
**API Version:** v3.1  
**Last Updated:** 2025-10-10

---

## 🚀 Getting Started in 5 Steps

### Step 1: Register as a Developer (15 minutes)

1. Go to https://developer.sage.com/
2. Click "Sign Up" and create an account
3. Navigate to **Console** → **Get API Keys (Accounting)**
4. Register your application:
   - **App Name:** Your application name
   - **Callback URL:** `https://yourdomain.com/auth/callback`
   - **Description:** Brief description of your integration
5. Save your credentials:
   - `client_id`: Your application ID
   - `client_secret`: Your application secret (keep secure!)

### Step 2: Get a Test Account (10 minutes)

1. Visit https://www.sage.com/en-za/sage-business-cloud/accounting/
2. Sign up for a **30-day free trial**
3. Select **South Africa** as your region
4. Complete the business setup wizard
5. Extend your trial for development:
   - Follow: https://developer.sage.com/accounting/quick-start/extend-your-sage-business-cloud-accounting-trial/

### Step 3: Authenticate (First API Call)

**Authorization URL:**
```
https://www.sageone.com/oauth2/auth/central?filter=apiv3.1&response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_CALLBACK_URL&scope=full_access&state=random_string&country=za
```

**Exchange code for token:**
```bash
curl -X POST https://oauth.accounting.sage.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=AUTHORIZATION_CODE" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=YOUR_CALLBACK_URL"
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "expires_in": 300,
  "refresh_token": "eyJhbGci...",
  "refresh_token_expires_in": 2678400
}
```

⚠️ **Important:** Access tokens expire in 5 minutes! Implement token refresh.

### Step 4: Make Your First API Call

**Get your business ID:**
```bash
curl -X GET https://api.accounting.sage.com/v3.1/businesses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**List contacts:**
```bash
curl -X GET https://api.accounting.sage.com/v3.1/contacts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Business: YOUR_BUSINESS_ID"
```

### Step 5: Create Your First Record

**Create a customer:**
```bash
curl -X POST https://api.accounting.sage.com/v3.1/contacts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Business: YOUR_BUSINESS_ID" \
  -d '{
    "contact_types": [{"id": "CUSTOMER"}],
    "name": "Test Customer",
    "reference": "TEST001",
    "email": "test@example.com",
    "currency": {"id": "ZAR"}
  }'
```

---

## 🔑 Essential Information

### Base URL
```
https://api.accounting.sage.com/v3.1
```

### Required Headers
```http
Authorization: Bearer <access_token>
Content-Type: application/json
X-Business: <business_id>
```

### Token Lifetimes
- **Access Token:** 5 minutes
- **Refresh Token:** 31 days
- **Authorization Code:** 60 seconds

### Common Endpoints

| Resource | Endpoint | Methods |
|----------|----------|---------|
| Contacts | `/v3.1/contacts` | GET, POST, PUT, DELETE |
| Sales Invoices | `/v3.1/sales_invoices` | GET, POST, PUT, DELETE |
| Purchase Invoices | `/v3.1/purchase_invoices` | GET, POST, PUT, DELETE |
| Products | `/v3.1/products` | GET, POST, PUT, DELETE |
| Payments | `/v3.1/contact_payments` | GET, POST, PUT, DELETE |
| Receipts | `/v3.1/contact_receipts` | GET, POST, PUT, DELETE |
| Bank Accounts | `/v3.1/bank_accounts` | GET, POST, PUT, DELETE |
| Ledger Accounts | `/v3.1/ledger_accounts` | GET, POST, PUT, DELETE |
| Trial Balance | `/v3.1/trial_balance` | GET |

---

## 💡 Best Practices

### 1. Token Management
```javascript
// Pseudo-code for token refresh
if (tokenExpiresIn < 60) {  // Refresh 1 minute before expiry
  refreshAccessToken();
}
```

### 2. Error Handling
```javascript
// Handle common errors
switch (response.status) {
  case 401: // Unauthorized - refresh token
    await refreshAccessToken();
    retry();
    break;
  case 429: // Rate limit - back off
    await sleep(exponentialBackoff());
    retry();
    break;
  case 400: // Validation error
    console.error(response.body.errors);
    break;
}
```

### 3. Pagination
```javascript
// Fetch all records
let page = 1;
let allRecords = [];

do {
  const response = await fetch(
    `/v3.1/contacts?page=${page}&items_per_page=200`
  );
  const data = await response.json();
  allRecords.push(...data.$items);
  page++;
} while (data.$next);
```

### 4. Incremental Sync
```javascript
// Sync changes since last update
const lastSync = "2025-10-10T14:00:00Z";
const response = await fetch(
  `/v3.1/sales_invoices?updated_or_created_since=${lastSync}`
);
```

---

## 🇿🇦 South Africa Specifics

### Currency
```json
{
  "currency": {
    "id": "ZAR"
  }
}
```

### VAT Rates
```json
{
  "tax_rate": {
    "id": "ZA_STANDARD"  // 15%
  }
}
```

Other tax rates:
- `ZA_ZERO` - Zero-rated (0%)
- `ZA_EXEMPT` - Exempt

### Date Format
- API: `YYYY-MM-DD` (e.g., `2025-10-10`)
- DateTime: `YYYY-MM-DDThh:mm:ssZ` (e.g., `2025-10-10T14:30:00Z`)

---

## ⚠️ Important Limitations

| Feature | Status | Workaround |
|---------|--------|------------|
| Webhooks | ❌ Not supported | Use polling with `updated_or_created_since` |
| Batch operations | ❌ Not supported | Make parallel requests with rate limiting |
| PDF export | ❌ Not supported | Generate client-side from JSON |
| Rate limits | ❓ Not documented | Implement conservative throttling (10 req/sec) |

---

## 📚 Resources

- **Full Analysis:** See `SAGE_API_ANALYSIS.md` in this repository
- **Official Docs:** https://developer.sage.com/accounting/
- **API Reference:** https://developer.sage.com/accounting/reference/
- **Community:** https://developer-community.sage.com/
- **Status Page:** https://status.sage.com/

---

## 🔧 Sample Code Snippets

### Python - Token Refresh
```python
import requests
from datetime import datetime, timedelta

class SageAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def refresh_access_token(self):
        response = requests.post(
            'https://oauth.accounting.sage.com/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
        )
        
        data = response.json()
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'])
    
    def get_valid_token(self):
        if not self.access_token or datetime.now() >= self.token_expires_at - timedelta(seconds=60):
            self.refresh_access_token()
        return self.access_token
```

### JavaScript/Node.js - API Request
```javascript
const axios = require('axios');

class SageAPI {
  constructor(accessToken, businessId) {
    this.baseURL = 'https://api.accounting.sage.com/v3.1';
    this.accessToken = accessToken;
    this.businessId = businessId;
  }
  
  async request(method, endpoint, data = null) {
    try {
      const response = await axios({
        method,
        url: `${this.baseURL}${endpoint}`,
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
          'X-Business': this.businessId
        },
        data
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error.response?.data || error.message);
      throw error;
    }
  }
  
  async getContacts(page = 1, itemsPerPage = 200) {
    return this.request('GET', `/contacts?page=${page}&items_per_page=${itemsPerPage}`);
  }
  
  async createContact(contactData) {
    return this.request('POST', '/contacts', contactData);
  }
  
  async createInvoice(invoiceData) {
    return this.request('POST', '/sales_invoices', invoiceData);
  }
}

// Usage
const api = new SageAPI('your-access-token', 'your-business-id');
const contacts = await api.getContacts();
```

---

## 🎯 Next Steps

1. ✅ Register developer account
2. ✅ Get trial Sage account
3. ✅ Implement OAuth flow
4. ✅ Test basic CRUD operations
5. ⬜ Build sync mechanism
6. ⬜ Implement error handling
7. ⬜ Add logging and monitoring
8. ⬜ Build your AI integration layer

---

**Good luck with your integration! 🚀**

For detailed information, refer to the complete `SAGE_API_ANALYSIS.md` document.

