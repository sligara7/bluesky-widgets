# BlueSky Queue Monitor Web

A web-based version of the BlueSky Queue Monitor that replicates the functionality of the Qt-based application.

## Setup and Usage

### For Real Queue Server Connection

1. **Configure API Connection**:
   - Click the "⚙️ Configure" button in the header
   - Enter the Queue Server HTTP URL (e.g., `https://vm_with_queueserver.bnl.gov`)
   - Enter your API key if required

2. **Connect to Server**:
   - Click "Connect" to establish connection
   - The app will poll the server every second for updates

### Environment Setup (Similar to Qt Version)

The web version requires the same environment setup as the Qt version:

```bash
# SSH to beamline workstation
ssh -X beamline-ws.nsls2.bnl.gov

# Activate conda environment
conda activate env_with_bluesky_widgets

# Set API key (if required)
export QSERVER_HTTP_SERVER_API_KEY='your_real_api_key_here'
```

However, instead of running `queue-monitor --http-server-uri https://vm_with_queueserver.bnl.gov:443`, you:

1. Serve the web application from a web server that can proxy to the queue server
2. Or configure CORS on the queue server to allow direct browser connections
3. Open the web app in a browser and configure the API URL

### For Demo/Offline Mode

If no API URL is configured, the app runs in demo mode with simulated functionality.

## Features

### Monitor Queue Tab
- **Connection Status**: Connect/disconnect from the queue server
- **Status Monitor**: Real-time status information
- **Running Plan**: Display currently executing plan with progress bar
- **Plan Queue**: View queued plans
- **Plan History**: View completed plans with success/failure status
- **Console Monitor**: Real-time log output

### Edit and Control Queue Tab
- **Environment Controls**: Toggle environment destroy mode
- **Queue Controls**: Add plans to queue, clear entire queue
- **Execution Controls**: Start/stop queue execution
- **Plan Editor**: Edit and save plan code
- **Queue Management**: View and manage running plans, queue, and history

## API Endpoints

The web app expects the following REST API endpoints on the queue server:

- `GET /status` - Server status
- `GET /queue/status` - Queue status (plans, running plan, history)
- `POST /queue/add` - Add plan to queue
- `POST /queue/clear` - Clear queue
- `POST /queue/start` - Start queue execution
- `POST /queue/stop` - Stop queue execution
- `POST /environment/destroy` - Toggle environment destroy
- `POST /plans` - Save plan code

## Functionality

- **Connection Management**: Connect/disconnect from queue server
- **Plan Management**: Add, queue, execute, and track plans
- **Real-time Monitoring**: Live updates of plan execution progress
- **History Tracking**: Complete audit trail of plan executions
- **Console Logging**: Real-time logging of all operations
- **Environment Controls**: Safety controls for environment management

## Configuration Options

The queue server URL can be configured in several ways depending on your deployment scenario:

### 1. Environment Variable (Recommended for Docker/Kubernetes)

```bash
export QUEUE_SERVER_URL=https://actual-queue-server.bnl.gov:443
```

### 2. Nginx Map for Multiple Beamlines

Use `nginx-beamline-map.conf` to automatically route based on hostname:

```nginx
map $http_host $queue_backend {
    beamline1.nsls2.bnl.gov https://queue-bl1.bnl.gov:443;
    beamline2.nsls2.bnl.gov https://queue-bl2.bnl.gov:443;
    # ... add all beamlines
}
```

### 3. Configuration File

Use `queue_servers.conf` to centralize mappings.

### 4. Deployment Script

Use the automated deployment script:

```bash
./deploy.sh beamline1 https://queue-bl1.bnl.gov:443
```

### 5. Docker Deployment

```bash
QUEUE_SERVER_URL=https://queue-bl1.bnl.gov:443 docker-compose up
```

### 6. Configuration Generator

Generate nginx configs programmatically:

```bash
python3 generate_config.py beamline1 https://queue-bl1.bnl.gov:443 -o nginx-beamline1.conf
```

## Running the Web Application

### Development Server

```bash
# From the queue_monitor_web directory
python3 server.py --port 8000
```

Or use the built-in Python server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

### Running a local mock queueserver for testing

If you cannot reach the real queueserver from this machine, run the included
`mock_qserver.py` which implements a small subset of the HTTP API for UI
testing:

```bash
# from bluesky-widgets repo
python3 bluesky_widgets/apps/queue_monitor_web/mock_qserver.py --port 9000
```

Then in the web UI configure the API URL to `http://127.0.0.1:9000` and exercise
the full UI (add plans, start/stop, view status/history).

### Production Deployment

For production use, serve the static files from a proper web server (nginx, Apache) that can proxy API requests to the queue server and handle CORS properly.

## Beamline Workstation Deployment

Since you develop locally but need to test on actual beamline workstations (like `ssh -X beamline-ws.nsls2.bnl.gov`), here's the deployment process:

### Step 1: Prepare Deployment Package

From your local development machine:

```bash
cd /path/to/bluesky-widgets/bluesky_widgets/apps
tar -czf queue_monitor_web.tar.gz queue_monitor_web/
```

### Step 2: Transfer to Beamline Workstation

```bash
# Copy the tarball and deployment script to the beamline workstation
scp queue_monitor_web.tar.gz beamline-ws.nsls2.bnl.gov:~
scp queue_monitor_web/deploy-beamline.sh beamline-ws.nsls2.bnl.gov:~
```

### Step 3: Deploy on Beamline Workstation

SSH to the beamline workstation and run:

```bash
# SSH to workstation
ssh -X beamline-ws.nsls2.bnl.gov

# Set the queue server URL for this beamline (if different from default)
export QUEUE_SERVER_URL="https://actual-queue-server-for-this-beamline.bnl.gov:443/"

# Run the deployment script
./deploy-beamline.sh
```

The deployment script will:
- Extract the web application to `/opt/queue_monitor_web`
- Configure nginx with the correct queue server URL
- Set up proper permissions
- Enable the nginx site
- Reload nginx configuration

### Step 4: Access the Application

Once deployed, access the web application at:
- **Local access**: `http://localhost:8080`
- **Remote access**: `http://beamline-ws.nsls2.bnl.gov:8080` (if firewall allows)

### Step 5: Testing

1. Open the web application in a browser
2. Click the "⚙️ Configure" button
3. Verify the Queue Server URL is correct for that beamline
4. Click "Connect" to test the connection
5. Monitor the console for any connection errors

### Troubleshooting

- **Connection fails**: Check that the queue server URL is reachable from the workstation
- **CORS errors**: The nginx proxy should handle CORS, but verify the configuration
- **Permission denied**: Make sure you're running the deployment script with sudo if needed
- **Port 8080 blocked**: Check firewall settings or use a different port in the nginx config

### Updating the Application

To update with new changes:

```bash
# On your local machine
cd /path/to/bluesky-widgets/bluesky_widgets/apps
tar -czf queue_monitor_web.tar.gz queue_monitor_web/

# Transfer to workstation
scp queue_monitor_web.tar.gz beamline-ws.nsls2.bnl.gov:~

# On the workstation
ssh beamline-ws.nsls2.bnl.gov
./deploy-beamline.sh
```

The script will automatically update the existing installation.