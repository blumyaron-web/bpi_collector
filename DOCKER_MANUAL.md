DOCKER MANUAL for BPI Collector

This file explains how Docker is used with this project, how to build and run the services, where data is stored, and common troubleshooting steps.

Overview
--------
The repository contains two main runnable components:

- bpi_collector: the data collector and grapher. It runs the collection loop (or single run) and writes per-run JSON and PNG files into the `data/` folder.
- dashboard: a small Flask app that serves a realtime dashboard and serves the latest graph PNG.

Both can be run directly with Python, or in Docker containers. When running with Docker you typically share the host `./data` folder into the containers so the collector writes files that the dashboard can read.

Files of interest
-----------------
- `Dockerfile` — image used by the collector service. Uses Python 3.12 and installs the project dependencies.
- `docker-compose.yml` — defines two services: `bpi-collector` and `bpi-dashboard`. It configures networking and volume mounts used for sharing `data/`.
- `data/` — persistent data directory (JSON and PNG files). Mount this directory into containers.
- `.env` / `config.ini` — configure SMTP and runtime options. Environment variables override config values when provided.

Quick start (development)
-------------------------
1. Build images and start with docker-compose (recommended during development):

```bash
# from repo root
docker-compose up -d --build
```

This will build the collector image and start both the collector (container runs according to its CMD/ENTRYPOINT) and the dashboard (Flask dev server exposed on port 8000).

2. Open the dashboard in your browser:

http://localhost:8000/

3. Inspect `data/` on the host to see JSON and PNG files created by the collector.

Running the collector manually (single run)
------------------------------------------
If you want to run just the collector once (for testing) without compose, you can run the image with `docker run`. Share the `data/` folder into the container so outputs are written to the host:

```bash
# build the image
docker build -t bpi-collector:latest .

# run a single collection from the image and mount the host data dir
docker run --rm -v "$(pwd)/data":/app/data bpi-collector:latest --samples 3 --interval 2
```

Notes:
- `--samples` and `--interval` are CLI flags accepted by the collector script (`bpi_collector.py`).
- `--send-test` will attempt to send an email using SMTP settings; ensure `config.ini` or environment variables provide valid SMTP credentials.

Using docker-compose with environment overrides
----------------------------------------------
- The `docker-compose.yml` reads environment variables from your shell or an `.env` file when present. You can create a `.env` file at the repo root with variables like `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, and `RECIPIENTS` to avoid storing secrets in `config.ini`.

Updating the image
------------------
To rebuild the image after code changes:

```bash
# rebuild and restart containers
docker-compose up -d --build

# or, rebuild only and run the collector image manually
docker build -t bpi-collector:latest .
```

If you publish the image to a registry or use CI, tag it with a version and update `docker-compose.yml` to pull the image instead of building locally.

Sharing `data/` between host and containers
------------------------------------------
Mount the host `data/` directory into the container at `/app/data`. This ensures the collector writes timestamped JSON and PNG files that the dashboard can read. Example from the `docker run` command above:

```bash
docker run --rm -v "$(pwd)/data":/app/data bpi-collector:latest ...
```

Important runtime notes
-----------------------
- The dashboard currently runs with Flask's built-in development server and should not be used as-is for production exposure. For production, use a WSGI server such as Gunicorn and a process manager.
- SMTP credentials are required for sending emails. Prefer environment variables or a Docker secret mechanism rather than committing credentials to `config.ini`.
- If you run multiple collector instances writing to the same `data/` folder, each run creates timestamped files to avoid overwriting data. Still, avoid running multiple concurrent long-running collectors unless you know the behavior you want.

Troubleshooting
---------------
- "Dashboard shows no data": confirm `data/` contains recent `bpi_data_*.json` and `bpi_graph_*.png` files. Confirm the `data/` path is the same volume mounted into both services.
- "Collector fails to start": check container logs with `docker-compose logs bpi-collector` or `docker logs <container-id>`. If it's a missing dependency, ensure `requirements.txt` matches the imports.
- "Email not sent": verify SMTP settings in `.env` or `config.ini`. For Gmail/Google accounts, you may need an app password and to enable the appropriate account settings.

Suggested next steps (optional)
-------------------------------
- Replace Flask dev server with Gunicorn in the `Dockerfile` and adjust `docker-compose.yml` for a production-ready dashboard service.
- Add a small CI workflow to build and push images on tags or merges.
- Use Docker secrets or a vault for SMTP credentials instead of plain `.env` files.

Contact
-------
If you want this manual expanded (runbook, CI example, production staging tips, or a `Makefile` for convenience commands) tell me which parts you'd like expanded.

Using Docker Desktop (GUI)
--------------------------
If you prefer the Docker Desktop app (macOS/Windows) instead of the CLI, follow these steps:

- Open Docker Desktop and confirm the Docker Engine is running.
- Build the image from the project folder:

	1. In Docker Desktop go to the "Images" tab and click the "Build" (or "Build image") action if available, or use the CLI build command from a terminal in the repo root:

		 ```bash
		 docker build -t bpi-collector:latest .
		 ```

- Start services with Compose via Docker Desktop:

	1. In Docker Desktop switch to the "Containers / Apps" or "Docker Compose" section (depending on Desktop version).
	2. Click "Add" or "Open Compose/Stack" and select the `docker-compose.yml` file in the repo root.
	3. Click "Deploy" (or "Start") to create and run the `bpi-collector` and `bpi-dashboard` services.

- Mounting the `data/` folder (important):

	- Docker Desktop will use the volume mounts declared in `docker-compose.yml`. Make sure the compose file mounts the host `./data` directory into `/app/data` (this repository's compose file does by default). If you deployed the stack from the GUI and the files are not visible in containers, check the compose definition or redeploy using the CLI `docker-compose up -d --build` which explicitly uses the repo path.

- Viewing logs and container state:

	- Use the Docker Desktop "Containers / Apps" list. Click the `bpi-collector` container and open the "Logs" tab to view stdout/stderr.
	- You can also use the CLI: `docker-compose logs -f bpi-collector` or `docker logs -f <container-id>`.

- Running a one-off command in a container:

	- In Docker Desktop you can click a running container and choose "Execute command" (or "Run command") to open a shell. From there you can run commands like `python bpi_collector.py --samples 3 --interval 2`.
	- Alternatively use the CLI: `docker run --rm -v "$(pwd)/data":/app/data bpi-collector:latest --samples 3 --interval 2`.

- Rebuilding after code changes:

	- Use the Desktop UI to stop the running stack, rebuild the image (via the Images tab or by re-deploying the compose), then start the stack again.
	- Or use the CLI which is often faster for development:

		```bash
		docker-compose up -d --build
		```

- Inspecting files created by the containers:

	- Look at the host `data/` directory (in Finder or terminal). It should contain `bpi_data_*.json` and `bpi_graph_*.png` files produced by the collector.

Notes
-----
- Some Docker Desktop versions change the UI labels and layout; the above describes common locations (Images, Containers/Apps, Compose/Stacks, Logs). If you can't find the exact buttons, use the CLI commands shown above — they work consistently.
- On macOS you may be prompted to allow file sharing for the project folder the first time you mount a host directory into a container; accept the prompt so the container can access `./data`.

