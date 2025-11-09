# Sage API Integration Analysis

**Document Version:** 1.0  
**Date:** 2025-10-10  
**Target Region:** South Africa  
**API Version:** v3.1

---

## Table of Contents

1. [Part 1: Codebase Summary](#part-1-codebase-summary)
2. [Part 2: Sage API Integration Requirements](#part-2-sage-api-integration-requirements)
   - [1. Product Identification](#1-product-identification)
   - [2. Authentication Details](#2-authentication-details)
   - [3. Primary Data Objects & Endpoints](#3-primary-data-objects--endpoints)
   - [4. Response Formats & Example Payloads](#4-response-formats--example-payloads)
   - [5. Rate Limits & Webhooks](#5-rate-limits--webhooks)
   - [6. Documentation & Sandbox Access](#6-documentation--sandbox-access)
   - [7. Regional & Version Notes](#7-regional--version-notes)
   - [8. Advanced Features](#8-advanced-features)
3. [Gaps & Further Investigation](#gaps--further-investigation)

---

## Part 1: Codebase Summary

### Project Purpose and Architecture

This repository contains **Sage API documentation and OpenAPI/Swagger specifications** for integrating with Sage Business Cloud Accounting. The codebase is a **documentation-only repository** containing:

- **Swagger/OpenAPI JSON files** for all major API modules
- **API guide documentation** (Word document format)
- **WordPress format schema** (for potential content management integration)

**Key Observation:** This is NOT an implementation codebase but rather a **reference documentation repository** containing API specifications.

### Key Components

The repository contains the following Swagger specification files:

1. **swagger.accounting.json** - Transactions and journal entries
2. **swagger.accounting_setup.json** - Chart of Accounts
3. **swagger.attachments.json** - File attachment management
4. **swagger.banking.json** - Bank accounts and transactions
5. **swagger.contacts.json** - Customer and supplier management
6. **swagger.currencies.json** - Currency and exchange rates
7. **swagger.invoicing_general.json** - Invoice status codes and types
8. **swagger.invoicing_purchases.json** - Purchase invoices and credit notes
9. **swagger.invoicing_sales.json** - Sales invoices, quotes, and estimates
10. **swagger.opening_balances.json** - Opening balance management
11. **swagger.payments.json** - Payments and receipts
12. **swagger.products_services.json** - Products and services catalog
13. **swagger.reporting.json** - Trial balance and reports
14. **swagger.settings.json** - Business and financial settings
15. **swagger.taxes.json** - Tax rates and VAT management
16. **swagger.user_businesses.json** - User accounts and business access

### Technologies and Frameworks

- **API Specification:** Swagger 2.0 (OpenAPI 2.0)
- **Data Format:** JSON
- **Protocol:** HTTPS
- **Authentication:** OAuth 2.0

### Current Implementation Status

The repository contains **complete API specifications** for Sage Business Cloud Accounting v3.1. All major accounting modules are documented with:
- Endpoint definitions
- Request/response schemas
- Example payloads
- Access control requirements
- Regional availability indicators

### Existing Sage API Integrations

**No active code implementation exists** in this repository. It serves as a reference for developers building integrations.

---

## Part 2: Sage API Integration Requirements

### 1. Product Identification

#### Full Product Name
**Sage Business Cloud Accounting** (formerly SageOne)

#### Correct Base API URL
```
https://api.accounting.sage.com/v3.1
```

**Regional Note:** The base URL is the same globally, but authentication routing differs by region. South African businesses authenticate through the same OAuth flow but select "South Africa" during the country selection step.

#### Product Targeted by Codebase
The Swagger specifications target **Sage Business Cloud Accounting API v3.1**, which supports:
- 🇨🇦 Canada
- 🇬🇧 United Kingdom  
- 🇮🇪 Ireland
- 🇺🇸 United States
- 🇫🇷 France
- 🇿🇦 **South Africa** (via Southern Hemisphere API)

**Important:** South African businesses use a separate regional API instance but follow the same v3.1 specification.

---

### 2. Authentication Details

#### Authentication Method
**OAuth 2.0 Authorization Code Flow** (with optional PKCE support)

#### Required HTTP Headers

**For API Requests:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
X-Business: <business_id>
```

**For OAuth Token Requests:**
```http
Content-Type: application/x-www-form-urlencoded
Accept: application/json
```

#### Complete Authentication Flow

**Step 1: Authorization Request**

Redirect users to:
```
https://www.sageone.com/oauth2/auth/central?filter=apiv3.1&response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_CALLBACK_URL&scope=full_access&state=RANDOM_STRING
```

**Required Parameters:**
- `client_id` - Your application's client ID
- `response_type` - Always `code`
- `redirect_uri` - Your registered callback URL
- `filter` - Set to `apiv3.1` to show only v3.1 compatible countries
- `scope` - Either `readonly` or `full_access`
- `state` - CSRF protection token (recommended)

**Optional Parameters:**
- `country` - Pre-select country (e.g., `za` for South Africa)
- `locale` - Language preference (e.g., `en-GB`)
- `code_challenge` - PKCE challenge (recommended for security)
- `code_challenge_method` - `S256` or `plain`

**Step 2: Exchange Authorization Code for Access Token**

```http
POST https://oauth.accounting.sage.com/token
Content-Type: application/x-www-form-urlencoded
Accept: application/json

client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&code=AUTHORIZATION_CODE
&grant_type=authorization_code
&redirect_uri=YOUR_CALLBACK_URL
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzUxMi...",
  "scope": "full_access",
  "token_type": "bearer",
  "expires_in": 300,
  "refresh_token": "eyJhbGciOiJSUzUxMi...",
  "refresh_token_expires_in": 2678400,
  "requested_by_id": "c3c32d1c-41ba-483f-a3ff-49fdb57b9c38"
}
```

**Token Lifetimes:**
- **Access Token:** 5 minutes (300 seconds)
- **Refresh Token:** 31 days (2,678,400 seconds)
- **Authorization Code:** 60 seconds (single-use)

#### Token Refresh Mechanism

```http
POST https://oauth.accounting.sage.com/token
Content-Type: application/x-www-form-urlencoded
Accept: application/json

client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&grant_type=refresh_token
&refresh_token=YOUR_REFRESH_TOKEN
```

**Important:** Each refresh returns a NEW refresh token. The old refresh token is invalidated.

#### Scopes/Permissions

- `readonly` - Read-only access to all data
- `full_access` - Full read/write access

**Granular Permissions:** Access is further controlled by user roles in specific areas:
- Sales (Full Access, Read Only, Restricted Access)
- Purchases (Full Access, Read Only, Restricted Access)
- Contacts (Full Access, Read Only, Restricted Access)
- Bank (Full Access, Read Only, Restricted Access)
- Journals (Full Access)
- Settings (Full Access, Read Only)
- Reporting (Full Access, Read Only)

---

### 3. Primary Data Objects & Endpoints

#### Customer/Contact Management
```
GET    /v3.1/contacts                    - List all contacts
GET    /v3.1/contacts/{id}               - Get specific contact
POST   /v3.1/contacts                    - Create contact
PUT    /v3.1/contacts/{id}               - Update contact
DELETE /v3.1/contacts/{id}               - Delete contact

GET    /v3.1/contact_types               - List contact types (CUSTOMER, VENDOR)
GET    /v3.1/addresses                   - List addresses
POST   /v3.1/addresses                   - Create address
GET    /v3.1/contact_persons             - List contact persons
POST   /v3.1/contact_persons             - Create contact person
```

#### Supplier/Vendor Management
(Uses same `/contacts` endpoint with `contact_type` = `VENDOR`)

#### Sales Invoices
```
GET    /v3.1/sales_invoices              - List all sales invoices
GET    /v3.1/sales_invoices/{id}         - Get specific invoice
POST   /v3.1/sales_invoices              - Create invoice
PUT    /v3.1/sales_invoices/{id}         - Update invoice
DELETE /v3.1/sales_invoices/{id}         - Delete invoice
POST   /v3.1/sales_invoices/{id}/release - Release (finalize) invoice

GET    /v3.1/sales_quotes                - List sales quotes
POST   /v3.1/sales_quotes                - Create quote
GET    /v3.1/sales_estimates             - List sales estimates
POST   /v3.1/sales_estimates             - Create estimate
GET    /v3.1/sales_credit_notes          - List credit notes
POST   /v3.1/sales_credit_notes          - Create credit note
```

#### Purchase Invoices
```
GET    /v3.1/purchase_invoices           - List all purchase invoices
GET    /v3.1/purchase_invoices/{id}      - Get specific invoice
POST   /v3.1/purchase_invoices           - Create invoice
PUT    /v3.1/purchase_invoices/{id}      - Update invoice
DELETE /v3.1/purchase_invoices/{id}      - Delete invoice

GET    /v3.1/purchase_credit_notes       - List credit notes
POST   /v3.1/purchase_credit_notes       - Create credit note
```

#### Items/Products
```
GET    /v3.1/products                    - List all products
GET    /v3.1/products/{id}               - Get specific product
POST   /v3.1/products                    - Create product
PUT    /v3.1/products/{id}               - Update product
DELETE /v3.1/products/{id}               - Delete product

GET    /v3.1/services                    - List all services
POST   /v3.1/services                    - Create service
GET    /v3.1/stock_items                 - List stock items
POST   /v3.1/stock_items                 - Create stock item
GET    /v3.1/stock_movements             - List stock movements
POST   /v3.1/stock_movements             - Create stock movement
```

#### Payments
```
GET    /v3.1/contact_payments            - List all payments
GET    /v3.1/contact_payments/{id}       - Get specific payment
POST   /v3.1/contact_payments            - Create payment
PUT    /v3.1/contact_payments/{id}       - Update payment
DELETE /v3.1/contact_payments/{id}       - Delete payment

GET    /v3.1/contact_receipts            - List all receipts
POST   /v3.1/contact_receipts            - Create receipt
GET    /v3.1/contact_allocations         - List allocations
POST   /v3.1/contact_allocations         - Create allocation
```

#### Accounts/Chart of Accounts
```
GET    /v3.1/ledger_accounts             - List all ledger accounts
GET    /v3.1/ledger_accounts/{id}        - Get specific account
POST   /v3.1/ledger_accounts             - Create account
PUT    /v3.1/ledger_accounts/{id}        - Update account
DELETE /v3.1/ledger_accounts/{id}        - Delete account

GET    /v3.1/ledger_account_types        - List account types
```

#### Journal Entries
```
GET    /v3.1/journals                    - List all journals
GET    /v3.1/journals/{id}               - Get specific journal
POST   /v3.1/journals                    - Create journal entry
PUT    /v3.1/journals/{id}               - Update journal entry
DELETE /v3.1/journals/{id}               - Delete journal entry

GET    /v3.1/other_payments              - List other payments
POST   /v3.1/other_payments              - Create other payment
GET    /v3.1/other_receipts              - List other receipts
POST   /v3.1/other_receipts              - Create other receipt
```

#### Reports
```
GET    /v3.1/trial_balance               - Get trial balance
GET    /v3.1/profit_and_loss             - Get P&L report
GET    /v3.1/balance_sheet               - Get balance sheet
```

#### Banking
```
GET    /v3.1/bank_accounts               - List all bank accounts
GET    /v3.1/bank_accounts/{id}          - Get specific bank account
POST   /v3.1/bank_accounts               - Create bank account
PUT    /v3.1/bank_accounts/{id}          - Update bank account
DELETE /v3.1/bank_accounts/{id}          - Delete bank account

GET    /v3.1/bank_transfers              - List bank transfers
POST   /v3.1/bank_transfers              - Create bank transfer
GET    /v3.1/bank_deposits               - List bank deposits
POST   /v3.1/bank_deposits               - Create bank deposit
GET    /v3.1/bank_reconciliations        - List reconciliations
POST   /v3.1/bank_reconciliations        - Create reconciliation
```

#### Taxes
```
GET    /v3.1/tax_rates                   - List all tax rates
GET    /v3.1/tax_rates/{id}              - Get specific tax rate
POST   /v3.1/tax_rates                   - Create tax rate
PUT    /v3.1/tax_rates/{id}              - Update tax rate

GET    /v3.1/tax_schemes                 - List tax schemes
GET    /v3.1/tax_return_frequencies      - List return frequencies
```

#### Settings & Configuration
```
GET    /v3.1/businesses                  - List accessible businesses
GET    /v3.1/businesses/{id}             - Get business details
PUT    /v3.1/businesses/{id}             - Update business settings

GET    /v3.1/business_settings           - Get business settings
PUT    /v3.1/business_settings           - Update business settings
GET    /v3.1/financial_settings          - Get financial settings
PUT    /v3.1/financial_settings          - Update financial settings
GET    /v3.1/invoice_settings            - Get invoice settings
PUT    /v3.1/invoice_settings            - Update invoice settings

GET    /v3.1/users                       - List users
GET    /v3.1/users/{id}                  - Get user details
```

#### Currencies
```
GET    /v3.1/currencies                  - List all currencies
GET    /v3.1/currencies/{id}             - Get specific currency
GET    /v3.1/exchange_rates              - List exchange rates
POST   /v3.1/exchange_rates              - Create exchange rate
```

#### Attachments
```
GET    /v3.1/attachments                 - List all attachments
GET    /v3.1/attachments/{id}            - Get specific attachment
POST   /v3.1/attachments                 - Upload attachment
DELETE /v3.1/attachments/{id}            - Delete attachment
```

---

### 4. Response Formats & Example Payloads

#### GET Request Example - Retrieve Contact

**Request:**
```http
GET https://api.accounting.sage.com/v3.1/contacts/cced5085c2d24394a758c5d16b38fca1 HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012
```

**Response (200 OK):**
```json
{
  "id": "cced5085c2d24394a758c5d16b38fca1",
  "displayed_as": "Bobs Building Supplies (BBS001)",
  "$path": "/contacts/cced5085c2d24394a758c5d16b38fca1",
  "created_at": "2022-12-30T13:59:24Z",
  "updated_at": "2023-06-13T10:40:55Z",
  "links": [
    {
      "href": "https://accounts-extra.sageone.com/contacts/customers/130175300",
      "rel": "alternate",
      "type": "text/html"
    }
  ],
  "contact_types": [
    {
      "id": "CUSTOMER",
      "displayed_as": "Customer",
      "$path": "/contact_types/CUSTOMER"
    }
  ],
  "name": "Bobs Building Supplies",
  "reference": "BBS001",
  "default_sales_ledger_account": {
    "id": "7a5ecfcf884911ed84fa0252b90cda0d",
    "displayed_as": "Other income (4900)",
    "$path": "/ledger_accounts/7a5ecfcf884911ed84fa0252b90cda0d"
  },
  "default_sales_tax_rate": {
    "id": "GB_STANDARD",
    "displayed_as": "Standard 20.00%",
    "$path": "/tax_rates/GB_STANDARD"
  },
  "tax_number": "GB938484382",
  "notes": "",
  "locale": "en",
  "main_address": {
    "id": "1a3b9bdf20a64df1a8657715788132f6",
    "displayed_as": "12",
    "$path": "/addresses/1a3b9bdf20a64df1a8657715788132f6"
  },
  "bank_account_details": {
    "account_name": null,
    "account_number": null,
    "sort_code": null,
    "bic": null,
    "iban": null
  },
  "credit_limit": "2000.0",
  "credit_days": 30,
  "currency": {
    "id": "GBP",
    "displayed_as": "Pound Sterling (GBP)",
    "$path": "/currencies/GBP"
  },
  "email": null,
  "is_active": true
}
```

#### GET Request Example - List Contacts (Paginated)

**Request:**
```http
GET https://api.accounting.sage.com/v3.1/contacts?page=1&items_per_page=10 HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012
```

**Response (200 OK):**
```json
{
  "$total": 148,
  "$page": 1,
  "$next": "/contacts?page=2&items_per_page=10",
  "$back": null,
  "$itemsPerPage": 10,
  "$items": [
    {
      "id": "bd7860529a6445f7898b4418feced4b1",
      "displayed_as": "HMRC Reclaimed (HMRC Rec)",
      "$path": "/contacts/bd7860529a6445f7898b4418feced4b1"
    },
    {
      "id": "eaab22cbff1e4f33883fa39961124ac7",
      "displayed_as": "HMRC Payments (HMRC Pay)",
      "$path": "/contacts/eaab22cbff1e4f33883fa39961124ac7"
    }
  ]
}
```

#### POST Request Example - Create Contact

**Request:**
```http
POST https://api.accounting.sage.com/v3.1/contacts HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012

{
  "contact_types": [
    {
      "id": "CUSTOMER"
    }
  ],
  "name": "Acme Corporation",
  "reference": "ACM001",
  "email": "info@acmecorp.com",
  "tax_number": "ZA1234567890",
  "credit_limit": 5000.00,
  "credit_days": 30,
  "currency": {
    "id": "ZAR"
  },
  "main_address": {
    "address_line_1": "123 Main Street",
    "city": "Johannesburg",
    "postal_code": "2000",
    "country": {
      "id": "ZA"
    }
  }
}
```

**Response (201 Created):**
```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "displayed_as": "Acme Corporation (ACM001)",
  "$path": "/contacts/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "created_at": "2025-10-10T14:30:00Z",
  "updated_at": "2025-10-10T14:30:00Z",
  "contact_types": [
    {
      "id": "CUSTOMER",
      "displayed_as": "Customer",
      "$path": "/contact_types/CUSTOMER"
    }
  ],
  "name": "Acme Corporation",
  "reference": "ACM001",
  "email": "info@acmecorp.com",
  "tax_number": "ZA1234567890",
  "credit_limit": "5000.0",
  "credit_days": 30,
  "currency": {
    "id": "ZAR",
    "displayed_as": "South African Rand (ZAR)",
    "$path": "/currencies/ZAR"
  },
  "is_active": true
}
```

#### POST Request Example - Create Sales Invoice

**Request:**
```http
POST https://api.accounting.sage.com/v3.1/sales_invoices HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012

{
  "contact": {
    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
  },
  "date": "2025-10-10",
  "due_date": "2025-11-09",
  "reference": "INV-2025-001",
  "invoice_lines": [
    {
      "description": "Professional Services - October 2025",
      "ledger_account": {
        "id": "7a5ecfcf884911ed84fa0252b90cda0d"
      },
      "quantity": 40,
      "unit_price": 150.00,
      "tax_rate": {
        "id": "ZA_STANDARD"
      }
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4",
  "displayed_as": "SI-2025-001",
  "$path": "/sales_invoices/x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4",
  "created_at": "2025-10-10T14:35:00Z",
  "updated_at": "2025-10-10T14:35:00Z",
  "contact": {
    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "displayed_as": "Acme Corporation (ACM001)",
    "$path": "/contacts/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
  },
  "date": "2025-10-10",
  "due_date": "2025-11-09",
  "reference": "INV-2025-001",
  "invoice_number": "SI-2025-001",
  "total_quantity": 40.0,
  "net_amount": 6000.00,
  "tax_amount": 900.00,
  "total_amount": 6900.00,
  "outstanding_amount": 6900.00,
  "currency": {
    "id": "ZAR",
    "displayed_as": "South African Rand (ZAR)",
    "$path": "/currencies/ZAR"
  },
  "status": {
    "id": "DRAFT",
    "displayed_as": "Draft"
  },
  "invoice_lines": [
    {
      "id": "line-001",
      "description": "Professional Services - October 2025",
      "quantity": 40.0,
      "unit_price": 150.00,
      "net_amount": 6000.00,
      "tax_rate": {
        "id": "ZA_STANDARD",
        "displayed_as": "Standard 15.00%",
        "$path": "/tax_rates/ZA_STANDARD"
      },
      "tax_amount": 900.00,
      "total_amount": 6900.00
    }
  ]
}
```

---

### 5. Rate Limits & Webhooks

#### Rate Limits

**Current Status:** Sage Business Cloud Accounting API documentation does not explicitly publish rate limits in the public documentation.

**Best Practices:**
- Implement exponential backoff for retry logic
- Monitor response headers for potential rate limit indicators
- Batch operations where possible
- Cache frequently accessed data

**Recommended Approach:**
- Contact Sage Developer Support for specific rate limit information
- Monitor API responses for HTTP 429 (Too Many Requests) status codes
- Implement request throttling in your application (suggested: max 10 requests/second)

#### Rate Limit Headers

**Note:** Rate limit headers are not documented in the official API specification. Monitor responses for:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

#### Webhooks

**Current Status:** ❌ **Webhooks are NOT currently supported** by Sage Business Cloud Accounting API v3.1.

**Alternative Approaches:**
1. **Polling with Filters:**
   - Use `updated_or_created_since` parameter on GET endpoints
   - Use `deleted_since` parameter to track deletions
   - Example: `GET /v3.1/sales_invoices?updated_or_created_since=2025-10-10T14:00:00Z`

2. **Timestamp-based Synchronization:**
   - Store last sync timestamp
   - Query for changes since last sync
   - Process incremental updates

**Example Polling Request:**
```http
GET https://api.accounting.sage.com/v3.1/sales_invoices?updated_or_created_since=2025-10-10T14:00:00Z&items_per_page=200 HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
X-Business: 12345678-1234-1234-1234-123456789012
```

---

### 6. Documentation & Sandbox Access

#### Official Developer Documentation
**Main Portal:** https://developer.sage.com/accounting/

**Key Documentation Links:**
- **API Reference:** https://developer.sage.com/accounting/reference/
- **Authentication Guide:** https://developer.sage.com/accounting/guides/authenticating/authentication/
- **Quick Start Guide:** https://developer.sage.com/accounting/quick-start/
- **Regional Considerations:** https://developer.sage.com/accounting/guides/regional-considerations/
- **Migration Guides:** https://developer.sage.com/accounting/guides/migrating/

#### API Specification
**Full Swagger File:** Available at https://developer.sage.com/accounting/reference/
- Individual module specifications available in this repository

#### Sandbox/Test Environment

**Trial Account Setup:**
1. Visit: https://www.sage.com/en-za/sage-business-cloud/accounting/
2. Sign up for a **30-day free trial** of Sage Business Cloud Accounting
3. Select **South Africa** as your region
4. Complete business setup with test data

**Test Company Setup:**
- Sage provides sample data during trial setup
- You can create multiple test businesses under one account
- Use the trial to test all API endpoints without affecting production data

**Important:** Extend your trial for development purposes:
- Follow guide: https://developer.sage.com/accounting/quick-start/extend-your-sage-business-cloud-accounting-trial/

#### Developer Portal Registration

**Registration URL:** https://developer.sage.com/

**Steps:**
1. Create a Sage Developer account
2. Navigate to "Console" → "Get API Keys (Accounting)"
3. Register your application:
   - Provide app name and description
   - Configure OAuth callback URLs
   - Receive `client_id` and `client_secret`
4. Test authentication flow with trial account

**Developer Console:** https://developer.sage.com/console/

---

### 7. Regional & Version Notes

#### Current API Version
**Version:** v3.1
**Release Status:** Stable (Current)

#### API Versioning Strategy
**URL-based versioning:** Version is specified in the URL path
```
https://api.accounting.sage.com/v3.1/contacts
```

**Previous Versions:**
- v3.0 (deprecated)
- v2.0 (deprecated)
- v1.0 (deprecated)

**Migration Path:** v2 → v3.1 migration guide available at:
https://developer.sage.com/accounting/guides/migrating/migrate-from-v2-to-v3-1/

#### South Africa-Specific Considerations

**1. Currency:**
- Default currency: ZAR (South African Rand)
- Multi-currency support available

**2. Tax Rates:**
- Standard VAT rate: 15% (as of 2025)
- Tax rate ID: `ZA_STANDARD`
- Zero-rated: `ZA_ZERO`
- Exempt: `ZA_EXEMPT`

**3. Regional API Instance:**
- South African businesses use the same base URL
- Authentication routes to appropriate regional server
- Data residency: Hosted in appropriate region for compliance

**4. Date Format:**
- ISO 8601 format: `YYYY-MM-DD`
- DateTime format: `YYYY-MM-DDThh:mm:ssZ`

**5. Number Formatting:**
- Decimal separator: `.` (period)
- Amounts returned as strings to preserve precision
- Example: `"1234.56"`

#### Differences Between Regions

**UK vs US vs South Africa:**

| Feature | UK/Ireland | Canada/US | South Africa |
|---------|-----------|-----------|--------------|
| API Version | v3.1 | v3.1 | v3.1 |
| Base URL | Same | Same | Same |
| Tax System | VAT | Sales Tax/GST | VAT |
| Standard Tax Rate | 20% | Varies | 15% |
| Currency | GBP/EUR | CAD/USD | ZAR |
| Date Format | DD/MM/YYYY (display) | MM/DD/YYYY (display) | DD/MM/YYYY (display) |
| API Date Format | ISO 8601 (all regions) | ISO 8601 (all regions) | ISO 8601 (all regions) |

**Important:** All regions use the same API specification (v3.1), but:
- Tax rates and schemes differ
- Regulatory features vary (e.g., CIS in UK, 1099 in US)
- Some endpoints may have regional availability restrictions

#### Deprecated Endpoints

**From v2 to v3.1:**
- Legacy authentication endpoints (v1/v2 OAuth)
- Some v2-specific query parameters
- Old pagination format

**Upcoming Changes:**
- Monitor https://developer.sage.com/accounting/ for deprecation notices
- Subscribe to Sage Developer newsletter for updates
- Check API changelog regularly

---

### 8. Advanced Features

#### File Attachments

**Supported:** ✅ Yes

**Endpoints:**
```
GET    /v3.1/attachments                 - List all attachments
GET    /v3.1/attachments/{id}            - Download attachment
POST   /v3.1/attachments                 - Upload attachment
DELETE /v3.1/attachments/{id}            - Delete attachment
```

**Upload Example:**
```http
POST https://api.accounting.sage.com/v3.1/attachments HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: multipart/form-data
X-Business: 12345678-1234-1234-1234-123456789012

--boundary
Content-Disposition: form-data; name="file"; filename="invoice.pdf"
Content-Type: application/pdf

[Binary file content]
--boundary
Content-Disposition: form-data; name="transaction_id"

x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4
--boundary--
```

**Supported File Types:**
- PDF, JPEG, PNG, GIF
- Microsoft Office documents (Word, Excel)
- Text files
- Maximum file size: Typically 10MB (verify with current documentation)

**Attachment Associations:**
- Sales Invoices
- Purchase Invoices
- Credit Notes
- Contacts
- Bank Transactions

**Query Parameter:**
```
GET /v3.1/sales_invoices?has_attachments=true
```

#### Report Exports

**Supported:** ✅ Partial (JSON format only)

**Available Reports:**
```
GET /v3.1/trial_balance                  - Trial balance report
GET /v3.1/profit_and_loss                - P&L statement
GET /v3.1/balance_sheet                  - Balance sheet
```

**Export Formats:**
- **JSON:** ✅ Native API response format
- **PDF:** ❌ Not directly supported via API
- **Excel/CSV:** ❌ Not directly supported via API

**Workaround for PDF/Excel:**
- Retrieve JSON data via API
- Generate PDF/Excel in your application
- Use third-party libraries (e.g., jsPDF, ExcelJS)

**Trial Balance Example:**
```http
GET https://api.accounting.sage.com/v3.1/trial_balance?from_date=2025-01-01&to_date=2025-10-10 HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
X-Business: 12345678-1234-1234-1234-123456789012
```

**Response:**
```json
{
  "from_date": "2025-01-01",
  "to_date": "2025-10-10",
  "ledger_accounts": [
    {
      "ledger_account": {
        "id": "abc123",
        "displayed_as": "Sales Revenue (4000)"
      },
      "debit": "0.00",
      "credit": "125000.00",
      "balance": "-125000.00"
    }
  ]
}
```

#### Bank Integration

**Supported:** ✅ Yes (via Bank Feeds)

**Endpoints:**
```
GET    /v3.1/bank_accounts               - List bank accounts
POST   /v3.1/bank_accounts               - Create bank account
GET    /v3.1/bank_transfers              - List transfers
POST   /v3.1/bank_transfers              - Create transfer
GET    /v3.1/bank_deposits               - List deposits
POST   /v3.1/bank_deposits               - Create deposit
GET    /v3.1/bank_reconciliations        - List reconciliations
POST   /v3.1/bank_reconciliations        - Create reconciliation
```

**Bank Feed Integration:**
- Sage supports direct bank feeds from major South African banks
- API allows creating bank transactions programmatically
- Reconciliation can be automated via API

**Bank Transaction Import Example:**
```http
POST https://api.accounting.sage.com/v3.1/bank_deposits HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012

{
  "bank_account": {
    "id": "bank-account-id"
  },
  "date": "2025-10-10",
  "reference": "DEP-001",
  "total_amount": 5000.00,
  "bank_deposit_lines": [
    {
      "ledger_account": {
        "id": "ledger-account-id"
      },
      "description": "Customer payment",
      "amount": 5000.00
    }
  ]
}
```

#### Payment Gateway Integration

**Supported:** ✅ Yes (via Sage Pay integration)

**Note:** Payment processing is handled through Sage's payment services, not directly via the Accounting API.

**Integration Approach:**
1. Use Sage Pay API for payment processing
2. Record payment in Sage Accounting via API
3. Link payment to invoice using allocations

**Payment Recording Example:**
```http
POST https://api.accounting.sage.com/v3.1/contact_receipts HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012

{
  "contact": {
    "id": "contact-id"
  },
  "bank_account": {
    "id": "bank-account-id"
  },
  "date": "2025-10-10",
  "reference": "PAYMENT-12345",
  "total_amount": 6900.00,
  "payment_method": {
    "id": "CREDIT_CARD"
  }
}
```

**Allocation to Invoice:**
```http
POST https://api.accounting.sage.com/v3.1/contact_allocations HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
Content-Type: application/json
X-Business: 12345678-1234-1234-1234-123456789012

{
  "transaction": {
    "id": "receipt-id"
  },
  "allocated_artefacts": [
    {
      "artefact": {
        "id": "invoice-id"
      },
      "amount": 6900.00
    }
  ]
}
```

#### Batch Operations

**Supported:** ❌ No native batch endpoint

**Workaround:**
- Make multiple individual API calls
- Implement parallel requests with rate limiting
- Use async/await patterns in your application
- Process in batches of 10-20 items at a time

**Example Pattern (Pseudo-code):**
```javascript
async function batchCreateContacts(contacts) {
  const batchSize = 10;
  const results = [];

  for (let i = 0; i < contacts.length; i += batchSize) {
    const batch = contacts.slice(i, i + batchSize);
    const promises = batch.map(contact =>
      createContact(contact)
    );
    const batchResults = await Promise.all(promises);
    results.push(...batchResults);

    // Rate limiting delay
    await sleep(1000);
  }

  return results;
}
```

#### Search and Filtering

**Supported:** ✅ Yes (extensive filtering capabilities)

**Common Query Parameters:**

**Pagination:**
```
?page=1&items_per_page=200
```
- Default: 20 items per page
- Maximum: 200 items per page

**Sorting:**
```
?sort=created_at:desc
?sort=name:asc
```

**Filtering by Date:**
```
?updated_or_created_since=2025-10-10T14:00:00Z
?deleted_since=2025-10-10T14:00:00Z
?from_date=2025-01-01&to_date=2025-12-31
```

**Filtering by Status:**
```
?status_id=PAID
?status_id=UNPAID
?status_id=OVERDUE
```

**Filtering by Contact:**
```
?contact_id=abc123
```

**Attribute Selection:**
```
?attributes=all                          - Include all attributes
?nested_attributes=all                   - Include nested objects
?show_balance=true                       - Include balance calculations
```

**Search Example:**
```http
GET https://api.accounting.sage.com/v3.1/contacts?search=Acme&items_per_page=50&attributes=all HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
X-Business: 12345678-1234-1234-1234-123456789012
```

**Complex Filter Example:**
```http
GET https://api.accounting.sage.com/v3.1/sales_invoices?status_id=UNPAID&from_date=2025-01-01&to_date=2025-10-10&sort=due_date:asc&items_per_page=200 HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzUxMi...
X-Business: 12345678-1234-1234-1234-123456789012
```

**Response Pagination:**
```json
{
  "$total": 1523,
  "$page": 1,
  "$next": "/sales_invoices?page=2&items_per_page=200",
  "$back": null,
  "$itemsPerPage": 200,
  "$items": [...]
}
```

---

## Gaps & Further Investigation

### Information Gaps Identified

1. **Rate Limits:**
   - ❓ Exact rate limit values not publicly documented
   - ❓ Rate limit headers not confirmed
   - **Action:** Contact Sage Developer Support for specifics

2. **Webhooks:**
   - ❌ Not currently supported
   - **Action:** Monitor roadmap for future webhook support

3. **Batch Operations:**
   - ❌ No native batch endpoints
   - **Action:** Implement client-side batching with rate limiting

4. **PDF/Excel Export:**
   - ❌ Not directly supported via API
   - **Action:** Generate reports client-side from JSON data

5. **Maximum File Size for Attachments:**
   - ❓ Not explicitly documented
   - **Action:** Test with various file sizes; likely 10MB limit

6. **South Africa-Specific Tax Features:**
   - ❓ SARS integration details unclear
   - ❓ E-filing support via API not documented
   - **Action:** Consult Sage ZA support for compliance features

### Recommended Next Steps

1. **Register Developer Account:**
   - Create account at https://developer.sage.com/
   - Register your application
   - Obtain API credentials

2. **Set Up Test Environment:**
   - Sign up for Sage Business Cloud Accounting trial (South Africa)
   - Extend trial for development
   - Populate with test data

3. **Implement Authentication:**
   - Build OAuth 2.0 flow
   - Implement token refresh mechanism
   - Securely store tokens

4. **Test Core Endpoints:**
   - Contacts (CRUD operations)
   - Sales Invoices (create, retrieve, update)
   - Payments and allocations
   - Reports (trial balance)

5. **Build Error Handling:**
   - Handle 401 (unauthorized) - refresh token
   - Handle 429 (rate limit) - implement backoff
   - Handle 400 (validation errors) - parse error messages
   - Handle 500 (server errors) - retry logic

6. **Implement Sync Strategy:**
   - Use `updated_or_created_since` for incremental sync
   - Store last sync timestamp
   - Handle deletions with `deleted_since`

7. **Monitor and Optimize:**
   - Log all API calls
   - Monitor response times
   - Implement caching where appropriate
   - Optimize pagination strategies

### Additional Resources

**Community Support:**
- Developer Community: https://developer-community.sage.com/
- Stack Overflow: Tag `sage-accounting-api`

**Status Page:**
- https://status.sage.com/ - Monitor API uptime

**Sample Applications:**
- https://developer.sage.com/accounting/guides/sample-apps/

**Postman Collection:**
- Available in developer documentation for testing

---

## Conclusion

This analysis provides a comprehensive overview of the Sage Business Cloud Accounting API v3.1 for South African integration. The API is well-documented, RESTful, and supports all core accounting operations required for a conversational AI integration.

**Key Takeaways:**
- ✅ OAuth 2.0 authentication with 5-minute access tokens
- ✅ Comprehensive REST API covering all accounting objects
- ✅ Good filtering and pagination support
- ✅ South Africa fully supported with ZAR currency and 15% VAT
- ❌ No webhooks (use polling with timestamp filters)
- ❌ No batch operations (implement client-side)
- ❓ Rate limits not publicly documented (implement conservative throttling)

**For AI Integration:**
The API is suitable for building a conversational AI agent that can:
- Read and query all accounting data
- Create and update transactions
- Generate reports
- Manage contacts and invoices
- Process payments

Implement a robust sync mechanism using timestamp-based polling and maintain proper OAuth token management for reliable operation.

---

**Document End**


