# Windows Firewall Setup for OpenAI API

If Windows Firewall is blocking Python outbound connections to OpenAI, follow these steps:

## Option 1: Allow Python Through Firewall (Recommended)

1. **Open Windows Defender Firewall**
   - Press `Win + R`, type `wf.msc`, press Enter
   - Or: Start > Windows Defender Firewall with Advanced Security

2. **Create Outbound Rule**
   - Click **Outbound Rules** in the left panel
   - Click **New Rule...** in the right panel
   - **Rule Type**: Select "Program", click Next
   - **Program**: Browse to your Python executable:
     ```
     C:\Users\PRATEEK SARASWAT\AppData\Local\Programs\Python\Python311\python.exe
     ```
     (adjust path based on your Python installation)
   - **Action**: Select "Allow the connection", click Next
   - **Profile**: Check all (Domain, Private, Public), click Next
   - **Name**: Enter "Python OpenAI", click Finish

3. **Allow Python Scripts**
   - Also allow the python.exe in your project venv:
     ```
     C:\Users\PRATEEK SARASWAT\OneDrive\Desktop\Excellence Technologies\CLIENT-AI-PROJECT\backend\venv311\Scripts\python.exe
     ```

## Option 2: Temporarily Disable Firewall (For Testing)

1. Open Command Prompt as Administrator
2. Run:
   ```cmd
   netsh advfirewall set allprofiles state off
   ```
3. Test the chatbot
4. Re-enable:
   ```cmd
   netsh advfirewall set allprofiles state on
   ```

## Option 3: Allow Specific Domain

1. Create outbound rule for port 443 (HTTPS)
2. In the "Scope" tab, add remote IP addresses:
   - `api.openai.com`
   - `172.65.0.0/16` (OpenAI's IP range)

## Verify the Rule Works

Run this in your backend terminal:
```bash
# Test if Python can reach OpenAI
python -c "import requests; print(requests.get('https://api.openai.com/v1/models', headers={'Authorization': 'Bearer YOUR_API_KEY'}).status_code)"
```

## Alternative: Use System Proxy

If you're behind a corporate proxy, set the environment variables:
```cmd
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
```

Then restart the backend.
