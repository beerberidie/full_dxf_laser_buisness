# Bulk Import Templates

## Overview
These templates allow you to bulk import clients, projects, and associated files into Laser OS.

## Files Generated
- `clients_import_template.csv` - Template for importing clients
- `projects_import_template.csv` - Template for importing projects and files

## Instructions

### 1. Prepare Your Data

#### Clients CSV
**Required Fields:**
- `name` - Client company name (REQUIRED)

**Optional Fields:**
- `client_code` - Leave blank to auto-generate (format: CL-XXXX)
- `contact_person` - Primary contact name
- `email` - Contact email address
- `phone` - Contact phone number
- `address` - Physical/postal address
- `notes` - Additional notes

#### Projects CSV
**Required Fields:**
- `client_code` - Must match an existing client code (REQUIRED)
- `name` - Project name/description (REQUIRED)

**Optional Fields:**
- `project_code` - Leave blank to auto-generate (format: JB-yyyy-mm-CLxxxx-###)
- `description` - Detailed project description
- `status` - Quote | Approved | In Progress | Completed | Cancelled (default: Quote)
- `quote_date` - Date format: YYYY-MM-DD or DD/MM/YYYY
- `approval_date` - Date project was approved
- `due_date` - Project due date
- `completion_date` - Date project was completed
- `quoted_price` - Initial quoted price (numbers only, no currency symbols)
- `final_price` - Final invoiced price
- `material_type` - e.g., "Mild Steel 3mm", "Stainless Steel 2mm"
- `material_quantity_sheets` - Number of sheets required
- `parts_quantity` - Number of parts to cut
- `estimated_cut_time` - Estimated cutting time in minutes
- `drawing_creation_time` - Time spent creating drawings in minutes
- `number_of_bins` - Number of bins for parts
- `scheduled_cut_date` - Scheduled cutting date
- `pop_received` - true/false - Proof of payment received
- `pop_received_date` - Date POP was received
- `pop_deadline` - POP deadline date
- `client_notified` - true/false - Client has been notified
- `delivery_confirmed` - true/false - Delivery confirmed
- `notes` - Additional notes

**File Fields (comma or semicolon separated file paths):**
- `dxf_files` - DXF design files (e.g., "file1.dxf,file2.dxf")
- `quote_files` - Quote documents (PDF, images)
- `invoice_files` - Invoice documents
- `pop_files` - Proof of payment documents
- `delivery_note_files` - Delivery note documents
- `image_files` - Project images

### 2. Organize Your Files

Create a directory structure for your files:
```
import_files/
├── dxf/
│   ├── brackets.dxf
│   ├── signage.dxf
│   └── panels.dxf
├── quotes/
│   ├── quote_001.pdf
│   └── quote_002.pdf
├── invoices/
│   └── invoice_002.pdf
├── pops/
│   └── pop_002.pdf
└── images/
    ├── photo1.jpg
    └── photo2.jpg
```

In your CSV, reference files relative to the base directory:
- `dxf/brackets.dxf`
- `quotes/quote_001.pdf`
- `images/photo1.jpg,images/photo2.jpg`

### 3. Run the Import

**Validate data first (recommended):**
```bash
python bulk_import.py --validate-only --clients clients.csv --projects projects.csv
```

**Import clients only:**
```bash
python bulk_import.py --clients clients.csv
```

**Import projects with files:**
```bash
python bulk_import.py --projects projects.csv --files-dir ./import_files
```

**Import everything:**
```bash
python bulk_import.py --all --clients clients.csv --projects projects.csv --files-dir ./import_files
```

### 4. Verify Import

After import:
1. Check the console output for any errors
2. Log into Laser OS web interface
3. Navigate to Clients and Projects to verify data
4. Check that files are properly linked to projects

## Tips

- **Always validate first** using `--validate-only` flag
- **Start with clients** before importing projects
- **Use absolute paths** or organize files in a single base directory
- **Check client codes** - projects must reference existing clients
- **Date formats** - Use YYYY-MM-DD for consistency
- **File paths** - Use forward slashes (/) even on Windows
- **Multiple files** - Separate with commas or semicolons
- **Leave blank** - Auto-generated fields (client_code, project_code) can be left empty
- **Backup first** - Always backup your database before bulk imports

## Troubleshooting

**"Client not found"**
- Ensure client_code in projects CSV matches an existing client
- Import clients first, then projects

**"File not found"**
- Check file paths are relative to --files-dir
- Verify files exist in the specified location
- Use forward slashes in paths

**"Invalid date format"**
- Use YYYY-MM-DD format (e.g., 2024-01-15)
- Or DD/MM/YYYY format (e.g., 15/01/2024)

**"Invalid status"**
- Use exact status names: Quote, Approved, In Progress, Completed, Cancelled

## Support

For issues or questions, check the main Laser OS documentation or contact support.
