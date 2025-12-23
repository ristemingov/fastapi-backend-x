from fabric import task, Connection
import deploy_config as config
import getpass

_connection = None


def get_connection():
    """Create and return a connection to the VPS"""
    global _connection

    if _connection is not None:
        return _connection

    passphrase = getpass.getpass("Enter passphrase for SSH key: ")

    connect_kwargs = {
        "key_filename": config.VPS_KEY_PATH,
        "passphrase": passphrase,
    }

    _connection = Connection(
        host=config.VPS_HOST,
        user=config.VPS_USER,
        connect_kwargs=connect_kwargs,
    )

    return _connection

@task
def deploy(ctx):
    """
    Deploy the latest changes from main branch
    """
    conn = get_connection()

    print("Deploying application...")

    with conn.cd(config.REMOTE_PROJECT_DIR):
        print("Stopping application...")
        stop_app(conn)

        print(f"Pulling latest changes from {config.GIT_BRANCH} branch...")
        conn.run(f"git fetch origin {config.GIT_BRANCH}")
        conn.run(f"git reset --hard origin/{config.GIT_BRANCH}")

        print("Updating dependencies...")
        conn.run(f"{config.REMOTE_VENV_DIR}/bin/pip install -r requirements.txt")

        print("Starting application...")
        start_app(conn)

    print("\nDeployment completed successfully!")
    print(f"Application is running at http://{config.VPS_HOST}:{config.APP_PORT}")


@task
def restart(ctx):
    """
    Restart the application
    """
    conn = get_connection()

    print("Restarting application...")

    with conn.cd(config.REMOTE_PROJECT_DIR):
        stop_app(conn)
        start_app(conn)

    print("Application restarted successfully!")


@task
def stop(ctx):
    """
    Stop the application
    """
    conn = get_connection()

    print("Stopping application...")
    stop_app(conn)
    print("Application stopped!")


@task
def start(ctx):
    """
    Start the application
    """
    conn = get_connection()

    print("Starting application...")
    with conn.cd(config.REMOTE_PROJECT_DIR):
        start_app(conn)
    print("Application started successfully!")


def stop_app(conn):
    """Helper function to stop the application"""
    result = conn.run("pgrep -f 'uvicorn main:app'", warn=True, hide=True)
    if result.ok:
        conn.run("pkill -f 'uvicorn main:app'", warn=True)
        print("Stopped existing application process")
    else:
        print("No running application process found")


def start_app(conn):
    """Helper function to start the application"""
    import time

    with conn.cd(config.REMOTE_PROJECT_DIR):
        conn.run(
            f"bash -c 'nohup {config.REMOTE_VENV_DIR}/bin/uvicorn main:app "
            f"--host {config.APP_HOST} --port {config.APP_PORT} "
            f"> app.log 2>&1 & disown'",
            hide=True
        )
        time.sleep(2)
        result = conn.run("pgrep -f 'uvicorn main:app'", warn=True, hide=True)
        if result.ok:
            print(f"Application started on {config.APP_HOST}:{config.APP_PORT} (PID: {result.stdout.strip()})")
        else:
            print("Warning: Application may not have started. Check logs with 'fab logs'")
