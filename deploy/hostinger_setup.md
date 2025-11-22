# Hostinger VPS Setup Guide for Odoo 19 (Docker)

This guide walks through preparing an Ubuntu VPS on Hostinger to deploy **odoo19-lolo** with Docker and Nginx.

## 1) Prepare the VPS
1. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
2. Install dependencies:
   ```bash
   sudo apt install -y ca-certificates curl gnupg lsb-release git ufw
   ```
3. Install Docker Engine and Compose plugin (official repository):
   ```bash
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   sudo usermod -aG docker $USER
   ```
   Log out/in to pick up the Docker group membership.
4. (Optional) Create a non-root deploy user:
   ```bash
   sudo adduser deploy
   sudo usermod -aG sudo,docker deploy
   ```
5. Configure SSH keys for GitHub access (as your deploy user):
   ```bash
   ssh-keygen -t ed25519 -C "deploy@odoo"
   cat ~/.ssh/id_ed25519.pub  # add to GitHub Deploy Keys
   ```
6. Basic firewall allowing SSH/HTTP/HTTPS:
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

## 2) Clone the repository
```bash
git clone git@github.com:<your-org>/odoo19-lolo.git
cd odoo19-lolo
cp .env.example .env
# Edit .env with your secrets: POSTGRES_PASSWORD, ADMIN_PASSWD, DOMAIN, LETSENCRYPT_EMAIL
```

## 3) Start the production stack
```bash
docker compose -f docker-compose.prod.yml up -d
```
- Odoo binds to `127.0.0.1:8069` (web) and `127.0.0.1:8072` (longpolling) for the host to proxy.
- The DB data and filestore persist via named volumes (`postgres-data`, `filestore`).

## 4) Configure Nginx reverse proxy
1. Install Nginx:
   ```bash
   sudo apt install -y nginx
   ```
2. Copy the provided vhost and adjust the domain as needed:
   ```bash
   sudo cp deploy/nginx/odoo.conf /etc/nginx/sites-available/odoo.conf
   sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/odoo.conf
   ```
3. Test and reload:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## 5) Obtain and configure SSL (Let’s Encrypt)
1. Install Certbot:
   ```bash
   sudo snap install core; sudo snap refresh core
   sudo snap install --classic certbot
   sudo ln -s /snap/bin/certbot /usr/bin/certbot
   ```
2. Obtain a certificate (DNS A record must already point to the VPS):
   ```bash
   sudo certbot --nginx -d ${DOMAIN} --email ${LETSENCRYPT_EMAIL} --agree-tos --redirect
   ```
3. Auto-renewal is handled by Certbot’s systemd timer. You can verify with:
   ```bash
   sudo systemctl list-timers | grep certbot
   ```

## 6) Backup strategy
- Use the provided script to dump the database:
  ```bash
  ./deploy/scripts/backup_db.sh odoo19-prod-db /home/deploy/backups
  ```
- Add a cronjob for nightly backups (example runs at 1:30 AM):
  ```cron
  30 1 * * * /home/deploy/odoo19-lolo/deploy/scripts/backup_db.sh odoo19-prod-db /home/deploy/backups >> /home/deploy/backup.log 2>&1
  ```
- Consider syncing backups offsite (rclone, rsync to object storage).

## 7) Zero/low-downtime deploys
```bash
cd /home/deploy/odoo19-lolo
git pull origin main
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```
- Compose recreates containers only when images change.
- Use healthchecks/load balancer if you need stricter zero-downtime guarantees.

## 8) Troubleshooting
- Check logs:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f odoo
  docker compose -f docker-compose.prod.yml logs -f db
  ```
- If the DB password changes, update both `.env` and any existing DB user password inside Postgres.
- Ensure DNS points to the VPS before requesting SSL.
