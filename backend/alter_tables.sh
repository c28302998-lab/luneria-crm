#!/bin/bash
sqlite3 sql_app.db "ALTER TABLE telegram_accounts ADD COLUMN assigned_worker_id INTEGER;"
sqlite3 sql_app.db "ALTER TABLE telegram_accounts ADD COLUMN responsible_admin_id INTEGER;"
sqlite3 sql_app.db "ALTER TABLE email_accounts ADD COLUMN responsible_admin_id INTEGER;"
