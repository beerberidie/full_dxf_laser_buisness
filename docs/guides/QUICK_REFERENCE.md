# Quick Reference - DXF Library Products

## Viewing Products

### Web Interface
Open your browser and navigate to:
```
http://127.0.0.1:5000/products/
```

### Command Line
View all imported products in the terminal:
```bash
python view_imported_products.py
```

## Import Commands

### Import DXF Library
To import products from the DXF library:
```bash
python import_dxf_library.py
```

**Note:** The import skips existing products by default, so you can run it multiple times safely.

## Product Statistics

- **Total Products:** 34
- **Products with DXF Files:** 34/34 (100%)
- **Products with Pricing:** 0/34 (needs to be set)

### By Material:
- **Mild Steel:** 30 products
- **Stainless Steel:** 4 products

### By Thickness:
- **2mm:** 4 products (Electronics)
- **3mm:** 7 products (Architecture, Automotive)
- **4mm:** 1 product (Food/Beverage)
- **5mm:** 1 product (Food/Beverage)
- **6mm:** 2 products (Petrochemical, Automotive)
- **8mm:** 4 products (Structural, Automotive)
- **10mm:** 9 products (Structural, Petrochemical, Marine, Sugar)
- **12mm:** 5 products (Structural, Petrochemical, Marine, Sugar)
- **No thickness:** 1 product (Sprocket guard)

## Common Tasks

### 1. Add Pricing to Products
1. Go to http://127.0.0.1:5000/products/
2. Click on a product
3. Click "Edit Product"
4. Enter the unit price
5. Click "Update Product"

### 2. Download a DXF File
1. Go to http://127.0.0.1:5000/products/
2. Click on a product
3. In the "Product Files" section, click the download icon

### 3. Add More DXF Files to a Product
1. Go to the product detail page
2. Scroll to "Product Files" section
3. Use the upload form to add more files

### 4. Search Products
On the products page:
- Use the search box to find products by name or SKU
- Use the material filter dropdown to filter by material type

### 5. Create a New Product Manually
1. Go to http://127.0.0.1:5000/products/
2. Click "+ New Product"
3. Fill in the form
4. Upload DXF files (optional)
5. Click "Create Product"

## File Locations

### DXF Library Source
```
dxf_starter_library_v1/dxf_library/
├── index.csv (metadata)
├── README.txt (library info)
└── [8 industry folders with DXF files]
```

### Product Files (Copied)
```
data/files/products/
├── 1/ (Product ID 1)
│   └── base_plate_200x200_t10_4x18_on160.dxf
├── 2/ (Product ID 2)
│   └── gusset_triangle_300x300_t12.dxf
└── ... (etc.)
```

### Database
```
data/laser_os.db
```

## Sample Products by Industry

### Structural Steel & Construction
- Base plate (SKU-MI100-0001)
- Gusset plate (SKU-MI120-0001)
- Beam end plate (SKU-MI100-0002)
- Splice/Cover plate (SKU-MI100-0003)
- Stiffener L-bracket (SKU-MI80-0001)

### Petrochemical/Oil & Gas/Mining
- Flange (SKU-MI120-0002)
- Baffle circular (SKU-MI80-0002)
- Baffle rectangular (SKU-MI60-0001)
- Manhole cover (SKU-MI100-0004)
- Support bracket/saddle (SKU-MI100-0005)

### Food/Beverage/Chemical/Pharma
- Tank end disk (SKU-ST40-0001)
- Rectangular panel (SKU-ST30-0001)
- Sanitary flange blank (SKU-ST50-0001)
- Filter plate/sieve (SKU-ST20-0001)

### Architecture/Furniture/Arts
- Decorative panel/screen (SKU-MI30-0002)
- Balustrade infill panel (SKU-MI30-0003)
- Gate/door panel (SKU-MI30-0004)
- Room divider (SKU-MI30-0005)

### Electronics & Small Parts
- Enclosure panel (SKU-MI20-0001)
- Instrument face/bezel (SKU-MI20-0002)
- Mounting L-bracket (SKU-MI20-0003)
- Heat-sink plate (SKU-MI30-0006)

## Troubleshooting

### Products not showing up?
1. Check if the import was successful:
   ```bash
   python view_imported_products.py
   ```
2. Verify the database exists:
   ```
   data/laser_os.db
   ```
3. Make sure the server is running:
   ```bash
   python run.py
   ```

### Need to re-import?
If you need to delete all products and re-import:
1. Stop the server
2. Delete the database: `data/laser_os.db`
3. Reinitialize: `flask init-db` (or use the appropriate method)
4. Re-import: `python import_dxf_library.py`

### DXF files not found?
Check that the files exist in:
```
data/files/products/{product_id}/
```

## Next Steps

### Recommended Actions:
1. ✅ **Products imported** - DONE
2. ⏳ **Set pricing** - Add unit prices to products
3. ⏳ **Test workflow** - Create a test project using these products
4. ⏳ **Customize descriptions** - Enhance product descriptions
5. ⏳ **Add categories** - Consider adding product categories

### Future Enhancements:
- Add DXF preview/rendering
- Bulk pricing import/export
- Product templates
- Material variants
- Automated quoting

## Support Files

- `DXF_LIBRARY_IMPORT_SUMMARY.md` - Detailed import documentation
- `import_dxf_library.py` - Import script
- `view_imported_products.py` - View products script
- `app/services/dxf_library_importer.py` - Import service code

## URLs

- **Products List:** http://127.0.0.1:5000/products/
- **New Product:** http://127.0.0.1:5000/products/new
- **Dashboard:** http://127.0.0.1:5000/
- **Sample Product:** http://127.0.0.1:5000/products/1

## Notes

- All products have been imported with their DXF files
- SKU codes are auto-generated based on material and thickness
- No pricing has been set yet (unit_price is NULL)
- All imports are logged in the activity_logs table
- The import is idempotent (safe to run multiple times)

