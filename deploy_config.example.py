# VPS Connection Settings
VPS_HOST = "YOUR_IP_ADDRESS"
VPS_USER = "YOUR_USERNAME"
VPS_KEY_PATH = "PATH_TO_YOUR_KEY"
# Deployment Settings
REMOTE_PROJECT_DIR = "/home/{}/fastapi-backend-x".format(VPS_USER)
REMOTE_VENV_DIR = "{}/venv".format(REMOTE_PROJECT_DIR)
GIT_REPO = "YOUR_GIT_REPO_URL"
GIT_BRANCH = "main"

# Application Settings
APP_PORT = 8080
APP_HOST = "0.0.0.0"
