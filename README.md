# Contract-Management
Lightweight, powerful open-source Python contract app: simple, secure. Instant setup, minimal design. Google Drive for private, protected scans. Admin/guest access control. Easy &amp; efficient. #ContractManagement #Python #OpenSource #Security
🚀 Lightweight Contract Management Powerhouse! Say goodbye to complex deployments and get started instantly!

✨ Minimalist Design: Focused functionality, zero learning curve, and a small, fast footprint!

🔒 Security First: Upload contract scans directly to your personal Google Drive. Enjoy private links, keeping your sensitive business data out of platform hands! Leverage Google Drive's robust permissions to control access. Plus, with account permission management, Admins see the original links, while Guests only view the subject and summary – enhanced data security!

💪 Practicality Above All: Convenient, efficient, and powerful despite its small size!

#ContractManagement #Python #OpenSource #GoogleDrive #Security #Minimalist #EasyDeploy #DataPrivacy

# Deployment Guide for Contract Management System
## System Requirements
- Python 3.12.10 or higher
- Chrome browser (desktop/mobile compatible)
## Local Deployment
1. Clone the repository:
```
git clone https://github.com/gyhongyu/Contract-Management.git
cd Contract-Management
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Initialize the database:
- The contract.db file will be automatically created on first run
- Ensure Database.xlsx is present in the root directory for dropdown menu data
4. Run the application:
```
python run.py
```
## PythonAnywhere Deployment
### Initial Setup
1. Create a new web app:
   
   - Choose "Manual Configuration"
   - Select Python 3.12
2. Upload project files:
   
   - Create a ZIP file of your project
   - Upload to PythonAnywhere using the Files tab
   - Extract using:
   ```
   unzip -o app.zip -d /home/yourusername/
   mysite/
   ```
### Virtual Environment Setup
```
mkvirtualenv --python=/usr/bin/python3.12 
myenv
workon myenv
pip install -r requirements.txt
```
### WSGI Configuration
Modify /var/www/yourusername_pythonanywhere_com_wsgi.py :

```
import sys
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

from run import app as application
```
### Common Issues & Solutions
1. File Permissions
   
   - If you get permission errors:
   ```
   chmod 755 /home/yourusername/mysite
   chmod 644 /home/yourusername/mysite/
   contract.db
   ```
2. Database Access
   
   - Ensure contract.db is writable:
   ```
   touch /home/yourusername/mysite/contract.
   db
   chmod 666 /home/yourusername/mysite/
   contract.db
   ```
3. File Upload Issues
   
   - When updating files, use -o flag with unzip to overwrite without prompts:
   ```
   unzip -o app.zip
   ```
4. Path Issues
   
   - Always use absolute paths in PythonAnywhere
   - Update paths in config.py if needed
5. Virtual Environment
   
   - If packages are missing, reactivate the environment:
   ```
   workon myenv
   ```
### Security Notes
- Change default admin password after first login
- Keep Database.xlsx secure as it contains system configuration
- Regularly backup contract.db
### Maintenance
1. To update the application:
```
git pull
pip install -r requirements.txt
touch /var/www/
yourusername_pythonanywhere_com_wsgi.py
```
2. To restart the web app:
- Use the PythonAnywhere Web tab
- Click the Reload button
### Troubleshooting
- Check error logs in the Web tab
- Verify file permissions
- Ensure all required files are present
- Confirm virtual environment is active
- Validate WSGI file configuration
