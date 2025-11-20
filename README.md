# odoo19-lolo

Opinionated starter kit for Odoo 19 development and deployment. Includes Docker Compose stacks for local dev and Hostinger VPS production, shared configuration, and deployment helpers.

## Repository layout
```
odoo19-lolo/
├── docker-compose.yml            # Local dev stack
├── docker-compose.prod.yml       # Production stack
├── Dockerfile                    # Extend the Odoo base image when needed
├── odoo.conf                     # Shared configuration
├── .env.example                  # Template environment variables
├── addons/                       # Place your custom modules here
├── deploy/                       # Deployment assets
│   ├── hostinger_setup.md        # VPS setup guide
│   ├── nginx/odoo.conf           # Nginx reverse proxy config
│   └── scripts/                  # Deployment + backup helpers
└── .vscode/settings.json         # Editor settings
```

## Prerequisites
- Docker Desktop (local development)
- Git
- VS Code (recommended) with Python + XML extensions

## Quick start (local development)
1. Clone the repository:
   ```bash
   git clone git@github.com:<your-org>/odoo19-lolo.git
   cd odoo19-lolo
   ```
2. Start the stack:
   ```bash
   docker compose up -d
   ```
3. Access Odoo at [http://localhost:8069](http://localhost:8069).
4. Create the first database via the web UI (use the password from `admin_passwd` in `odoo.conf`).
5. Add custom modules into `addons/` and install them from the Apps menu.

### Hot reload / fast iteration
The `dev` flag in `odoo.conf` reads `ODOO_DEV_MODE` (defaults to `reload` for dev). Set `ODOO_DEV_MODE=` in `.env` for production to disable hot reload. If you run into odd reload behavior, clear the variable and restart the container.

### Common troubleshooting
- **Module not found**: Verify the module folder lives directly under `addons/` and contains a valid `__manifest__.py`.
- **Database reset**: Stop containers, remove volumes, and restart:
  ```bash
  docker compose down -v
  docker compose up -d
  ```
- **Changing passwords or ports**: Copy `.env.example` to `.env`, adjust values, and restart the stack.

## Production deployment (Hostinger VPS)
- Use `docker-compose.prod.yml` with your `.env` file. No dev/hot-reload flags are enabled when `ODOO_DEV_MODE` is empty.
- Reverse proxy with Nginx using `deploy/nginx/odoo.conf` and secure with Let’s Encrypt via Certbot.
- Persistent named volumes keep Postgres data and Odoo filestore.
- Step-by-step VPS guide: [deploy/hostinger_setup.md](deploy/hostinger_setup.md).

### Deploy flow
1. Push changes to GitHub.
2. SSH to the VPS and run:
   ```bash
   ./deploy/scripts/deploy.sh
   ```
   This pulls main, updates images, and restarts the stack.

### Backup flow
- Run `deploy/scripts/backup_db.sh` to create timestamped `pg_dump` backups.
- Add a cronjob for nightly backups (see guide).

## Git workflow
- Branches: `main` (production), `staging` (pre-prod), `feature/*` for development.
- Typical cycle: develop locally → commit → push feature branch → PR → merge to staging/main → deploy via `deploy.sh`.

## CI template (optional)
A minimal GitHub Actions workflow builds the Odoo image on pushes to `main` or `staging` and can be extended to push to a registry.

## Conventions
- Shared configuration in `odoo.conf` with environment variable overrides.
- Keep custom addons in `addons/` and avoid modifying the base image unless necessary.
- Use `Dockerfile` when you need extra Python dependencies or tools.
