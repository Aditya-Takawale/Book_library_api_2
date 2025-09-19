from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter(prefix="/secure", tags=["Security Testing"])

@router.get("/login-test", response_class=HTMLResponse)
async def secure_login_test():
    """
    Secure login test page with client-side encryption
    """
    template_path = "/Users/aditya_takawale/Book_library_api_2/app/templates/secure_login_test.html"
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content="<h1>Template not found</h1><p>Secure login test template is missing.</p>",
            status_code=404
        )

@router.get("/js/password-encryption.js")
async def get_encryption_script():
    """
    Serve the password encryption JavaScript library
    """
    script_path = "/Users/aditya_takawale/Book_library_api_2/static/js/password-encryption.js"
    
    if os.path.exists(script_path):
        return FileResponse(
            script_path,
            media_type="application/javascript",
            filename="password-encryption.js"
        )
    else:
        return HTMLResponse(
            content="console.error('Password encryption script not found');",
            status_code=404,
            media_type="application/javascript"
        )
