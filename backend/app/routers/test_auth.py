from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.utils.dependencies import get_current_user
from app.schemas.user import UserResponse
import logging

logger = logging.getLogger("BookLibraryAPI")

router = APIRouter(prefix="/test", tags=["Testing"])

@router.get("/auth", response_class=HTMLResponse)
async def test_auth_page():
    """
    Simple test page for authorization
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Authorization</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .success { color: #4CAF50; background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .error { color: #f44336; background: #ffebee; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .info { color: #2196F3; background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
            button { background: #007acc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #005fa3; }
            input { padding: 8px; margin: 5px; width: 100%; max-width: 500px; border: 1px solid #ddd; border-radius: 4px; }
            .token-input { font-family: monospace; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Authorization Test Page</h1>
            <p>Use this page to test your JWT authorization token.</p>
            
            <div class="info">
                <strong>Step 1:</strong> Login at <a href="/auth/login" target="_blank">/auth/login</a> to get your access token<br>
                <strong>Step 2:</strong> Copy the access_token from the response<br>
                <strong>Step 3:</strong> Paste it below and click "Test Authorization"
            </div>
            
            <h3>Test Your Token:</h3>
            <input type="text" id="tokenInput" class="token-input" placeholder="Paste your access_token here (eyJhbGci...)">
            <br>
            <button onclick="testAuthorization()">Test Authorization</button>
            <button onclick="clearResults()">Clear</button>
            
            <div id="result"></div>
            
            <h3>Quick Test with Sample Data:</h3>
            <button onclick="testWithSampleToken()">Test with Current Working Token</button>
        </div>
        
        <script>
            const SAMPLE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGl0eWFAdGVzdC5jb20iLCJyb2xlIjoiQWRtaW4iLCJzZXNzaW9uX2lkIjoiUVhLajBaZThRTUFZMmxrTjBBMTQ5UG5ObXJ3MXRtRXc2WnFLaENqTzFDSSIsImV4cCI6MTc1NzUwMTQxOSwidHlwZSI6ImFjY2VzcyJ9.FAT8-jK4bibNVLHtjOaVlq1-qL0SRqsJNyl75QEdWnA";
            
            async function testAuthorization() {
                const token = document.getElementById('tokenInput').value.trim();
                const resultDiv = document.getElementById('result');
                
                if (!token) {
                    resultDiv.innerHTML = '<div class="error">Please enter a token first!</div>';
                    return;
                }
                
                try {
                    resultDiv.innerHTML = '<div class="info">Testing authorization...</div>';
                    
                    const response = await fetch('/auth/verify', {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.status === 'success') {
                        resultDiv.innerHTML = `
                            <div class="success">
                                <h4>🎉 Authorization Successful!</h4>
                                <p><strong>User:</strong> ${data.user.email}</p>
                                <p><strong>Role:</strong> ${data.user.role}</p>
                                <p><strong>Permissions:</strong> ${data.user.permissions.join(', ')}</p>
                                <p><strong>Session ID:</strong> ${data.user.session_id}</p>
                                <p><strong>Message:</strong> ${data.message}</p>
                            </div>
                        `;
                        
                        // Show success notification
                        showNotification('Authorization successful! You can now use protected endpoints.', 'success');
                    } else {
                        resultDiv.innerHTML = `
                            <div class="error">
                                <h4>❌ Authorization Failed</h4>
                                <p><strong>Status:</strong> ${response.status}</p>
                                <p><strong>Error:</strong> ${data.detail || 'Unknown error'}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="error">
                            <h4>❌ Request Failed</h4>
                            <p><strong>Error:</strong> ${error.message}</p>
                        </div>
                    `;
                }
            }
            
            function testWithSampleToken() {
                document.getElementById('tokenInput').value = SAMPLE_TOKEN;
                testAuthorization();
            }
            
            function clearResults() {
                document.getElementById('result').innerHTML = '';
                document.getElementById('tokenInput').value = '';
            }
            
            function showNotification(message, type) {
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed; top: 20px; right: 20px; z-index: 1000;
                    padding: 15px 20px; border-radius: 5px; color: white;
                    background: ${type === 'success' ? '#4CAF50' : '#f44336'};
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                `;
                notification.textContent = message;
                document.body.appendChild(notification);
                
                setTimeout(() => notification.remove(), 5000);
            }
        </script>
    </body>
    </html>
    """

@router.get("/swagger-tips", response_class=HTMLResponse)
async def swagger_tips():
    """
    Tips for using Swagger UI with authentication
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swagger UI Authorization Guide</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .step { background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2196F3; }
            .code { background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
            .highlight { background: #fff3cd; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 How to Use Authorization in Swagger UI</h1>
            
            <div class="step">
                <h3>Step 1: Login to Get Token</h3>
                <p>1. Go to <strong>/auth/login</strong> endpoint in Swagger UI</p>
                <p>2. Use credentials: <code>aditya@test.com</code> / <code>admin123</code></p>
                <p>3. Copy the <span class="highlight">access_token</span> from the response</p>
            </div>
            
            <div class="step">
                <h3>Step 2: Authorize in Swagger</h3>
                <p>1. Click the <strong>🔒 Authorize</strong> button (top right in Swagger UI)</p>
                <p>2. In the popup, enter: <code>Bearer </code> followed by your token</p>
                <div class="code">Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your_token_here...</div>
                <p>3. Click <strong>Authorize</strong></p>
                <p>4. Close the dialog</p>
            </div>
            
            <div class="step">
                <h3>Step 3: Test Authorization</h3>
                <p>1. Try the <strong>/auth/verify</strong> endpoint to confirm it works</p>
                <p>2. You should see a success message with your user details</p>
                <p>3. Now you can use any protected endpoint!</p>
            </div>
            
            <div class="step">
                <h3>🎯 Quick Test Links</h3>
                <p><a href="/test/auth" target="_blank">Test Authorization Page</a> - Test your token quickly</p>
                <p><a href="/docs" target="_blank">Swagger UI</a> - Full API documentation</p>
                <p><a href="/auth/verify" target="_blank">Verify Endpoint</a> - Check if you're authenticated</p>
            </div>
        </div>
    </body>
    </html>
    """
