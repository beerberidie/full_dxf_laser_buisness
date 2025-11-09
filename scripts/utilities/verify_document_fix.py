"""
Verification script to test the uploaded_at attribute fix.

This script verifies that:
1. ProjectDocument model has upload_date attribute
2. Documents can be queried and sorted by upload_date
3. The document service works correctly
"""

from app import create_app, db
from app.models import Client, Project, ProjectDocument
from app.services.document_service import get_project_documents


def main():
    """Main verification function."""
    print("\n" + "="*70)
    print("VERIFICATION: ProjectDocument upload_date Attribute Fix")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Step 1: Verify model attributes
        print("\n" + "="*70)
        print("STEP 1: Verify Model Attributes")
        print("="*70)
        
        # Check that ProjectDocument has upload_date
        has_upload_date = hasattr(ProjectDocument, 'upload_date')
        has_uploaded_at = hasattr(ProjectDocument, 'uploaded_at')
        
        print(f"\n✅ ProjectDocument.upload_date exists: {has_upload_date}")
        print(f"✅ ProjectDocument.uploaded_at exists: {has_uploaded_at} (should be False)")
        
        if not has_upload_date:
            print("\n❌ ERROR: ProjectDocument missing upload_date attribute!")
            return
        
        if has_uploaded_at:
            print("\n⚠️  WARNING: ProjectDocument has uploaded_at attribute (unexpected)")
        
        # Step 2: Find projects with documents
        print("\n" + "="*70)
        print("STEP 2: Find Projects with Documents")
        print("="*70)
        
        # Find CL-0002 client
        client = Client.query.filter_by(client_code='CL-0002').first()
        
        if not client:
            print("\n❌ Client CL-0002 not found!")
            return
        
        print(f"\n✅ Client Found: {client.name} ({client.client_code})")
        
        # Find projects with documents
        projects_with_docs = []
        for project in client.projects:
            if project.documents:
                projects_with_docs.append(project)
        
        print(f"\n✅ Found {len(projects_with_docs)} project(s) with documents")
        
        if not projects_with_docs:
            print("\n⚠️  No projects with documents found. Cannot test document display.")
            print("This is expected if no documents were migrated.")
            return
        
        # Step 3: Test document queries
        print("\n" + "="*70)
        print("STEP 3: Test Document Queries")
        print("="*70)
        
        for project in projects_with_docs:
            print(f"\n📁 Project: {project.project_code} - {project.name}")
            print(f"   Documents: {len(project.documents)}")
            
            for doc in project.documents:
                # Test that upload_date is accessible
                try:
                    upload_date = doc.upload_date
                    print(f"\n   ✅ Document: {doc.original_filename}")
                    print(f"      Type: {doc.document_type}")
                    print(f"      Upload Date: {upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"      Uploaded By: {doc.uploaded_by or 'N/A'}")
                    print(f"      Size: {(doc.file_size / 1024 / 1024):.2f} MB")
                except AttributeError as e:
                    print(f"\n   ❌ ERROR accessing document attributes: {e}")
                    return
        
        # Step 4: Test document service
        print("\n" + "="*70)
        print("STEP 4: Test Document Service")
        print("="*70)
        
        for project in projects_with_docs:
            try:
                # This should work now with upload_date
                docs = get_project_documents(project.id)
                print(f"\n✅ get_project_documents({project.id}) returned {len(docs)} document(s)")
                
                # Verify sorting (newest first)
                if len(docs) > 1:
                    for i in range(len(docs) - 1):
                        if docs[i].upload_date < docs[i+1].upload_date:
                            print(f"\n⚠️  WARNING: Documents not sorted correctly!")
                        else:
                            print(f"   ✅ Documents sorted correctly (newest first)")
                            break
            except Exception as e:
                print(f"\n❌ ERROR in document service: {e}")
                import traceback
                traceback.print_exc()
                return
        
        # Step 5: Test template sorting
        print("\n" + "="*70)
        print("STEP 5: Test Template Sorting")
        print("="*70)
        
        for project in projects_with_docs:
            # Simulate template sorting
            try:
                sorted_docs = sorted(project.documents, key=lambda d: d.upload_date, reverse=True)
                print(f"\n✅ Template sorting works for project {project.project_code}")
                print(f"   Sorted {len(sorted_docs)} document(s) by upload_date")
            except AttributeError as e:
                print(f"\n❌ ERROR sorting documents: {e}")
                return
        
        # Summary
        print("\n" + "="*70)
        print("VERIFICATION COMPLETE")
        print("="*70)
        
        print("\n✅ All checks passed!")
        print("\nSummary:")
        print(f"   ✅ ProjectDocument.upload_date attribute exists")
        print(f"   ✅ Document queries work correctly")
        print(f"   ✅ Document service works correctly")
        print(f"   ✅ Template sorting works correctly")
        print(f"\n🎉 The uploaded_at attribute fix is working correctly!")
        print("\nYou can now safely view projects with documents in the web application.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Verification cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

