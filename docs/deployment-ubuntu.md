# Ubuntu Deployment Guide

## Supported Ubuntu Version
* Ubuntu 22.04 LTS

## Required Packages
* Python 3.10+
* MySQL Server (for production)
* Nginx (Reverse Proxy)
* Gunicorn

## Runtime Installation Steps
```bash
sudo apt update
sudo apt install python3-pip python3-venv mysql-server nginx
```

## Firewall Configuration
```bash
sudo ufw allow 'Nginx Full'
```

## Reverse Proxy Example (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Systemd Service Example
```ini
[Unit]
Description=Gunicorn instance to serve Yoga School Management
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/yoga-school-management
Environment="PATH=/var/www/yoga-school-management/venv/bin"
ExecStart=/var/www/yoga-school-management/venv/bin/gunicorn --workers 3 --bind localhost:5001 app:app

[Install]
WantedBy=multi-user.target
```

## Logs Path
* Application: `/var/www/yoga-school-management/app.log`
* Gunicorn: `journalctl -u yoga-management`
* Nginx: `/var/log/nginx/error.log`

## Restart Procedure
```bash
sudo systemctl restart yoga-management
```
