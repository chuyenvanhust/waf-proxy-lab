<?php
# ── DVWA Database Config ──────────────────────────────
$_DVWA = array();
$_DVWA['db_server']   = '127.0.0.1';
$_DVWA['db_database'] = 'dvwa';
$_DVWA['db_user']     = 'dvwa';
$_DVWA['db_password'] = 'p@ssw0rd';
$_DVWA['db_port']     = '3306';

# ── Security Level mặc định ───────────────────────────
# low / medium / high / impossible
$_DVWA['default_security_level'] = 'low';

# ── reCAPTCHA (bỏ qua trong lab) ─────────────────────
$_DVWA['recaptcha_public_key']  = '';
$_DVWA['recaptcha_private_key'] = '';

# ── PHPIDS ───────────────────────────────────────────
$_DVWA['disable_authentication'] = false;
