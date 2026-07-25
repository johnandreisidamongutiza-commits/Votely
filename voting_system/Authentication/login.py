from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
import random
import smtplib
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from voting_system import db_config

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/auth/static')

SMTP_EMAIL = 'johnandreigutiza125@gmail.com'
SMTP_PASSWORD = 'dwkn gkye wdri ragj'

def generate_unique_otp():
    return random.randint(1000, 9999)

def _send_html_email(recipient_email, subject, html_body):
    """Helper to send an HTML email."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f'VoteSystem <{SMTP_EMAIL}>'
        msg['To']      = recipient_email
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, recipient_email, msg.as_string())
        return True
    except Exception:
        return False

def send_otp_email(recipient_email, otp):
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 20px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(99,102,241,0.10);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:36px 40px 28px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,0.18);border-radius:14px;padding:10px 18px;margin-bottom:14px;">
              <span style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Votely</span>
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.70);letter-spacing:0.5px;text-transform:uppercase;font-weight:600;">Official Voting Platform</div>
          </td>
        </tr>
        <!-- Accent bar -->
        <tr><td style="height:4px;background:linear-gradient(90deg,#6366f1,#8b5cf6,#a78bfa);"></td></tr>
        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 28px;">
            <div style="font-size:22px;font-weight:800;color:#0f172a;margin-bottom:8px;letter-spacing:-0.3px;">Password Reset OTP</div>
            <div style="font-size:14px;color:#64748b;line-height:1.7;margin-bottom:28px;">
              We received a request to reset your password. Use the verification code below to continue.
            </div>
            <!-- OTP Box -->
            <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border:1.5px solid #c4b5fd;border-radius:16px;padding:28px;text-align:center;margin-bottom:24px;">
              <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#7c3aed;margin-bottom:14px;">Your OTP Code</div>
              <div style="font-size:52px;font-weight:900;letter-spacing:14px;color:#4f46e5;font-family:'Courier New',monospace;text-shadow:0 2px 8px rgba(99,102,241,0.15);">{otp}</div>
              <div style="margin-top:14px;display:inline-block;background:rgba(99,102,241,0.10);border-radius:100px;padding:5px 14px;">
                <span style="font-size:12px;color:#6366f1;font-weight:600;">⏱ Expires in 10 minutes</span>
              </div>
            </div>
            <!-- Warning -->
            <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;margin-bottom:24px;display:flex;align-items:flex-start;">
              <span style="font-size:16px;margin-right:10px;">⚠️</span>
              <span style="font-size:13px;color:#92400e;line-height:1.6;">Never share this code with anyone. Votely staff will <strong>never</strong> ask for your OTP.</span>
            </div>
            <div style="font-size:13px;color:#94a3b8;line-height:1.6;">
              If you didn't request a password reset, you can safely ignore this email.
            </div>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;padding:18px 40px;text-align:center;border-top:1px solid #e2e8f0;">
            <div style="font-size:12px;color:#94a3b8;">© 2025 <strong style="color:#6366f1;">Votely</strong> · Official Voting Platform</div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return _send_html_email(recipient_email, 'Votely — Your OTP Verification Code', html)

def send_activation_email(recipient_email, firstname, code):
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 20px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(99,102,241,0.10);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:36px 40px 28px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,0.18);border-radius:14px;padding:10px 18px;margin-bottom:14px;">
              <span style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Votely</span>
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.70);letter-spacing:0.5px;text-transform:uppercase;font-weight:600;">Official Voting Platform</div>
          </td>
        </tr>
        <!-- Accent bar -->
        <tr><td style="height:4px;background:linear-gradient(90deg,#6366f1,#8b5cf6,#a78bfa);"></td></tr>
        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 28px;">
            <div style="font-size:22px;font-weight:800;color:#0f172a;margin-bottom:8px;letter-spacing:-0.3px;">Welcome, {firstname}! 🎉</div>
            <div style="font-size:14px;color:#64748b;line-height:1.7;margin-bottom:28px;">
              Your voter account has been created. Use the activation code below to activate your account and set your password.
            </div>
            <!-- Code Box -->
            <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border:1.5px solid #c4b5fd;border-radius:16px;padding:28px;text-align:center;margin-bottom:24px;">
              <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#7c3aed;margin-bottom:14px;">Activation Code</div>
              <div style="font-size:52px;font-weight:900;letter-spacing:14px;color:#4f46e5;font-family:'Courier New',monospace;text-shadow:0 2px 8px rgba(99,102,241,0.15);">{code}</div>
              <div style="margin-top:14px;display:inline-block;background:rgba(99,102,241,0.10);border-radius:100px;padding:5px 14px;">
                <span style="font-size:12px;color:#6366f1;font-weight:600;">🔒 This code can only be used once</span>
              </div>
            </div>
            <!-- Steps -->
            <div style="margin-bottom:24px;">
              <div style="font-size:12px;font-weight:700;color:#0f172a;margin-bottom:14px;text-transform:uppercase;letter-spacing:0.8px;">How to activate:</div>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr><td style="padding:7px 0;">
                  <table cellpadding="0" cellspacing="0"><tr>
                    <td style="width:26px;height:26px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;text-align:center;vertical-align:middle;font-size:11px;font-weight:800;color:#fff;">1</td>
                    <td style="padding-left:12px;font-size:13.5px;color:#334155;">Go to the <strong>Votely login page</strong></td>
                  </tr></table>
                </td></tr>
                <tr><td style="padding:7px 0;">
                  <table cellpadding="0" cellspacing="0"><tr>
                    <td style="width:26px;height:26px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;text-align:center;vertical-align:middle;font-size:11px;font-weight:800;color:#fff;">2</td>
                    <td style="padding-left:12px;font-size:13.5px;color:#334155;">Click <strong>"Activate Account"</strong></td>
                  </tr></table>
                </td></tr>
                <tr><td style="padding:7px 0;">
                  <table cellpadding="0" cellspacing="0"><tr>
                    <td style="width:26px;height:26px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;text-align:center;vertical-align:middle;font-size:11px;font-weight:800;color:#fff;">3</td>
                    <td style="padding-left:12px;font-size:13.5px;color:#334155;">Enter your <strong>Student ID</strong>, the code above, and set your password</td>
                  </tr></table>
                </td></tr>
              </table>
            </div>
            <!-- Warning -->
            <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;">
              <span style="font-size:16px;margin-right:8px;">⚠️</span>
              <span style="font-size:13px;color:#92400e;line-height:1.6;">Never share this code with anyone. If you didn't expect this email, please contact your administrator.</span>
            </div>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;padding:18px 40px;text-align:center;border-top:1px solid #e2e8f0;">
            <div style="font-size:12px;color:#94a3b8;">© 2025 <strong style="color:#6366f1;">Votely</strong> · Official Voting Platform</div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return _send_html_email(recipient_email, f'Votely — Activate Your Account, {firstname}!', html)


def send_2fa_email(recipient_email, firstname, otp):
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 20px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(99,102,241,0.10);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:36px 40px 28px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,0.18);border-radius:14px;padding:10px 18px;margin-bottom:14px;">
              <span style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Votely</span>
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.70);letter-spacing:0.5px;text-transform:uppercase;font-weight:600;">Official Voting Platform</div>
          </td>
        </tr>
        <!-- Accent bar -->
        <tr><td style="height:4px;background:linear-gradient(90deg,#6366f1,#8b5cf6,#a78bfa);"></td></tr>
        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 28px;">
            <div style="font-size:22px;font-weight:800;color:#0f172a;margin-bottom:8px;letter-spacing:-0.3px;">Login Verification, {firstname}!</div>
            <div style="font-size:14px;color:#64748b;line-height:1.7;margin-bottom:28px;">
              A login attempt was made to your account. Use the code below to complete your sign-in.
            </div>
            <!-- OTP Box -->
            <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border:1.5px solid #c4b5fd;border-radius:16px;padding:28px;text-align:center;margin-bottom:24px;">
              <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#7c3aed;margin-bottom:14px;">Your 2FA Code</div>
              <div style="font-size:52px;font-weight:900;letter-spacing:14px;color:#4f46e5;font-family:'Courier New',monospace;text-shadow:0 2px 8px rgba(99,102,241,0.15);">{otp}</div>
              <div style="margin-top:14px;display:inline-block;background:rgba(99,102,241,0.10);border-radius:100px;padding:5px 14px;">
                <span style="font-size:12px;color:#6366f1;font-weight:600;">⏱ Expires in 10 minutes</span>
              </div>
            </div>
            <!-- Warning -->
            <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;">
              <span style="font-size:16px;margin-right:8px;">⚠️</span>
              <span style="font-size:13px;color:#92400e;line-height:1.6;">If you did not attempt to log in, please <strong>change your password immediately</strong>.</span>
            </div>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;padding:18px 40px;text-align:center;border-top:1px solid #e2e8f0;">
            <div style="font-size:12px;color:#94a3b8;">© 2025 <strong style="color:#6366f1;">Votely</strong> · Official Voting Platform</div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return _send_html_email(recipient_email, 'Votely — Your Login Verification Code', html)


@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')

        if not user_id or not password:
            return render_template('login.html', error='Invalid credentials', prev_user_id=user_id)

        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        if user:
            if user.get('status') == 'inactive':
                cursor.close(); connect.close()
                return render_template('login.html', error='Your account is not yet activated. Please check your email for the activation code.', prev_user_id=user_id)
            password_matches = False
            stored = user['password']
            if stored.startswith('$2b$') or stored.startswith('$2a$'):
                password_matches = bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8'))
            else:
                password_matches = (password == stored)
            if not password_matches:
                cursor.close(); connect.close()
                return render_template('login.html', error='Invalid credentials', prev_user_id=user_id)
            if user['role'] == 'superadmin':
                cursor.execute("SELECT is_enabled FROM user_2fa WHERE user_id=%s", (user['id'],))
                twofa = cursor.fetchone()
                cursor.close(); connect.close()
                if twofa and twofa['is_enabled']:
                    otp = str(random.randint(100000, 999999))
                    expires = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
                    connect2 = mysql.connector.connect(**db_config)
                    cursor2 = connect2.cursor()
                    cursor2.execute("UPDATE user_2fa SET otp_code=%s, otp_expires=%s WHERE user_id=%s", (otp, expires, user['id']))
                    connect2.commit(); cursor2.close(); connect2.close()
                    if not send_2fa_email(user['email'], user['firstname'], otp):
                        return render_template('login.html', error='Failed to send 2FA code. Please try again.', prev_user_id=user_id)
                    session['pending_2fa_user'] = {'id': user['id'], 'name': user['firstname'], 'role': 'superadmin', 'attempts': 0, 'resend_count': 0}
                    if '@' in user['email']:
                        local, domain = user['email'].split('@', 1)
                        session['pending_2fa_masked'] = local[0] + '***@' + domain
                    else:
                        session['pending_2fa_masked'] = '***'
                    return redirect(url_for('auth.verify_2fa'))
                else:
                    session.permanent = True
                    session['superadmin_id'] = user['id']
                    session['superadmin_name'] = user['firstname']
                    session['superadmin_last_activity'] = datetime.now().isoformat()
                    return redirect(url_for('superadmin.dashboard'))
            elif user['role'] == 'admin':
                cursor.execute("SELECT is_enabled FROM user_2fa WHERE user_id=%s", (user['id'],))
                twofa = cursor.fetchone()
                cursor.close(); connect.close()
                if twofa and twofa['is_enabled']:
                    otp = str(random.randint(100000, 999999))
                    expires = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
                    connect2 = mysql.connector.connect(**db_config)
                    cursor2 = connect2.cursor()
                    cursor2.execute("UPDATE user_2fa SET otp_code=%s, otp_expires=%s WHERE user_id=%s", (otp, expires, user['id']))
                    connect2.commit(); cursor2.close(); connect2.close()
                    if not send_2fa_email(user['email'], user['firstname'], otp):
                        return render_template('login.html', error='Failed to send 2FA code. Please try again.', prev_user_id=user_id)
                    session['pending_2fa_user'] = {'id': user['id'], 'name': user['firstname'], 'role': 'admin', 'attempts': 0, 'resend_count': 0}
                    if '@' in user['email']:
                        local, domain = user['email'].split('@', 1)
                        session['pending_2fa_masked'] = local[0] + '***@' + domain
                    else:
                        session['pending_2fa_masked'] = '***'
                    return redirect(url_for('auth.verify_2fa'))
                else:
                    session.permanent = True
                    session['admin_id'] = user['id']
                    session['admin_name'] = user['firstname']
                    session['admin_last_activity'] = datetime.now().isoformat()
                    return redirect(url_for('admin.dashboard'))
            else:
                cursor.execute("SELECT is_enabled FROM user_2fa WHERE user_id=%s", (user['id'],))
                twofa = cursor.fetchone()
                cursor.close(); connect.close()
                if twofa and twofa['is_enabled']:
                    otp = str(random.randint(100000, 999999))
                    expires = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
                    connect2 = mysql.connector.connect(**db_config)
                    cursor2 = connect2.cursor()
                    cursor2.execute("UPDATE user_2fa SET otp_code=%s, otp_expires=%s WHERE user_id=%s", (otp, expires, user['id']))
                    connect2.commit(); cursor2.close(); connect2.close()
                    if not send_2fa_email(user['email'], user['firstname'], otp):
                        return render_template('login.html', error='Failed to send 2FA code. Please try again.', prev_user_id=user_id)
                    session['pending_2fa_user'] = {'id': user['id'], 'name': user['firstname'], 'role': 'user', 'attempts': 0, 'resend_count': 0}
                    if '@' in user['email']:
                        local, domain = user['email'].split('@', 1)
                        session['pending_2fa_masked'] = local[0] + '***@' + domain
                    else:
                        session['pending_2fa_masked'] = '***'
                    return redirect(url_for('auth.verify_2fa'))
                else:
                    session.permanent = True
                    session['user_id'] = user['id']
                    session['user_name'] = user['firstname']
                    session['user_last_activity'] = datetime.now().isoformat()
                    return redirect(url_for('user.dashboard'))
        cursor.close(); connect.close()
        return render_template('login.html', error='Invalid credentials', prev_user_id=user_id)
    return render_template('login.html')


@auth.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    from flask import jsonify
    if 'pending_2fa_user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        pin = ''.join([request.form.get(f'pin{i}', '') for i in range(1, 7)])
        pending = session['pending_2fa_user']
        if pending['attempts'] >= 5:
            session.pop('pending_2fa_user', None); session.pop('pending_2fa_masked', None)
            return jsonify({'status': 'max_attempts'})
        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor(dictionary=True)
        cursor.execute("SELECT otp_code, otp_expires FROM user_2fa WHERE user_id=%s", (pending['id'],))
        row = cursor.fetchone()
        cursor.close(); connect.close()
        if not row or datetime.now() > row['otp_expires']:
            session.pop('pending_2fa_user', None); session.pop('pending_2fa_masked', None)
            return jsonify({'status': 'expired'})
        if pin == row['otp_code']:
            connect2 = mysql.connector.connect(**db_config)
            cursor2 = connect2.cursor()
            cursor2.execute("UPDATE user_2fa SET otp_code=NULL, otp_expires=NULL WHERE user_id=%s", (pending['id'],))
            connect2.commit(); cursor2.close(); connect2.close()
            uid, uname, role = pending['id'], pending['name'], pending.get('role', 'user')
            session.pop('pending_2fa_user', None); session.pop('pending_2fa_masked', None)
            session.permanent = True
            if role == 'admin':
                session['admin_id'] = uid
                session['admin_name'] = uname
                session['admin_last_activity'] = datetime.now().isoformat()
                return jsonify({'status': 'success', 'redirect': url_for('admin.dashboard')})
            elif role == 'superadmin':
                session['superadmin_id'] = uid
                session['superadmin_name'] = uname
                session['superadmin_last_activity'] = datetime.now().isoformat()
                return jsonify({'status': 'success', 'redirect': url_for('superadmin.dashboard')})
            else:
                session['user_id'] = uid
                session['user_name'] = uname
                session['user_last_activity'] = datetime.now().isoformat()
                return jsonify({'status': 'success', 'redirect': url_for('user.dashboard')})
        session['pending_2fa_user']['attempts'] += 1
        session.modified = True
        return jsonify({'status': 'invalid'})
    return render_template('verify_2fa.html', masked_email=session.get('pending_2fa_masked', '***'),
                           otp_expiry=(datetime.now() + timedelta(minutes=10)).isoformat())


@auth.route('/resend-2fa-otp')
def resend_2fa_otp():
    if 'pending_2fa_user' not in session:
        return redirect(url_for('auth.login'))
    pending = session['pending_2fa_user']
    if pending.get('resend_count', 0) >= 3:
        session.pop('pending_2fa_user', None); session.pop('pending_2fa_masked', None)
        return redirect(url_for('auth.login') + '?error=Too many resend attempts. Please log in again.')
    otp = str(random.randint(100000, 999999))
    expires = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)
    cursor.execute("UPDATE user_2fa SET otp_code=%s, otp_expires=%s WHERE user_id=%s", (otp, expires, pending['id']))
    connect.commit()
    cursor.execute("SELECT email, firstname FROM users WHERE id=%s", (pending['id'],))
    user = cursor.fetchone()
    cursor.close(); connect.close()
    if not user:
        session.pop('pending_2fa_user', None); session.pop('pending_2fa_masked', None)
        return redirect(url_for('auth.login') + '?error=Account no longer exists. Please log in again.')
    if not send_2fa_email(user['email'], user['firstname'], otp):
        return redirect(url_for('auth.login') + '?error=Failed to resend code. Please try again.')
    session['pending_2fa_user']['resend_count'] = pending.get('resend_count', 0) + 1
    session['pending_2fa_user']['attempts'] = 0
    session.modified = True
    return redirect(url_for('auth.verify_2fa'))


@auth.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        code    = request.form.get('activation_code', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Rate limiting — max 5 attempts per session
        attempts = session.get('act_attempts', 0)
        if attempts >= 5:
            return render_template('activate.html', error='Too many failed attempts. Please contact your administrator.',
                                   prev_user_id=user_id, prev_code=code)

        if not user_id or not code or not password or not confirm:
            return render_template('activate.html', error='All fields are required.',
                                   prev_user_id=user_id, prev_code=code)
        if password != confirm:
            session['act_attempts'] = attempts + 1
            return render_template('activate.html', error='Passwords do not match.',
                                   prev_user_id=user_id, prev_code=code)

        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id=%s AND activation_code=%s AND status='inactive'", (user_id, code))
        user = cursor.fetchone()
        if not user:
            cursor.close(); connect.close()
            session['act_attempts'] = attempts + 1
            return render_template('activate.html', error='Invalid Student ID or activation code.',
                                   prev_user_id=user_id, prev_code=code)

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password=%s, status='active', activation_code=NULL WHERE id=%s", (hashed, user['id']))
        connect.commit()
        cursor.close(); connect.close()
        session.pop('act_attempts', None)
        return redirect(url_for('auth.login') + '?success=Account activated! You can now log in.')

    return render_template('activate.html')


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_id          = request.form.get('user_id', '').strip()
        email            = request.form.get('email', '').strip().lower()
        new_password     = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        def _err(msg):
            return render_template('forgot_password.html', error=msg,
                                   prev_user_id=user_id, prev_email=email)

        # Rate limiting — max 5 attempts per session
        attempts = session.get('fp_attempts', 0)
        if attempts >= 5:
            return _err('Too many attempts. Please try again later.')

        if new_password != confirm_password:
            session['fp_attempts'] = attempts + 1
            return _err('Passwords do not match.')

        # Password strength check
        import re
        if (len(new_password) < 8 or
            not re.search(r'[A-Z]', new_password) or
            not re.search(r'[a-z]', new_password) or
            not re.search(r'[0-9]', new_password) or
            not re.search(r'[^A-Za-z0-9]', new_password) or
            new_password != new_password.strip()):
            session['fp_attempts'] = attempts + 1
            return _err('Password does not meet strength requirements.')

        connect = mysql.connector.connect(**db_config)
        cursor  = connect.cursor(dictionary=True)

        # Account existence check
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        account = cursor.fetchone()
        if not account:
            cursor.close(); connect.close()
            session['fp_attempts'] = attempts + 1
            return _err('No account found with that Student ID.')

        # Student ID + Email pairing check
        if account['email'].lower() != email:
            cursor.close(); connect.close()
            session['fp_attempts'] = attempts + 1
            return _err('Student ID and Email do not match.')

        # Password reuse check
        stored = account['password']
        if stored.startswith('$2b$') or stored.startswith('$2a$'):
            if bcrypt.checkpw(new_password.encode('utf-8'), stored.encode('utf-8')):
                cursor.close(); connect.close()
                return _err('New password cannot be the same as your current password.')

        cursor.close()
        connect.close()

        # Clear rate limit on success
        session.pop('fp_attempts', None)

        otp = generate_unique_otp()
        session['forgot_user'] = {
            'user_id': user_id,
            'email': email,
            'new_password': new_password,
            'otp': str(otp),
            'otp_expiry': (datetime.now() + timedelta(minutes=10)).isoformat(),
            'attempts': 0,
            'resend_count': 0
        }
        if not send_otp_email(email, otp):
            return _err('Failed to send OTP email. Please try again later.')
        return redirect(url_for('auth.verify_forgot_password'))
    return render_template('forgot_password.html')


@auth.route('/verify-forgot-password', methods=['GET', 'POST'])
def verify_forgot_password():
    from flask import jsonify
    if 'forgot_user' not in session:
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        pin = request.form.get('pin1','') + request.form.get('pin2','') + request.form.get('pin3','') + request.form.get('pin4','')
        pending = session['forgot_user']

        if datetime.now() > datetime.fromisoformat(pending['otp_expiry']):
            session.pop('forgot_user', None)
            return jsonify({'status': 'expired'})

        if pending['attempts'] >= 5:
            session.pop('forgot_user', None)
            return jsonify({'status': 'max_attempts'})

        if pin == pending['otp']:
            connect = mysql.connector.connect(**db_config)
            cursor = connect.cursor()
            hashed = bcrypt.hashpw(pending['new_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (hashed, pending['user_id']))
            connect.commit()
            cursor.close()
            connect.close()
            session.pop('forgot_user', None)
            return jsonify({'status': 'success'})

        session['forgot_user']['attempts'] += 1
        session.modified = True
        return jsonify({'status': 'invalid'})

    # GET — pass display data to template
    pending = session['forgot_user']
    email = pending['email']
    if '@' in email:
        local, domain = email.split('@', 1)
        masked_email = local[0] + '***@' + domain
    else:
        masked_email = '***'
    resends_left = 3 - pending.get('resend_count', 0)
    otp_expiry   = pending['otp_expiry']
    return render_template('verify_forgot.html',
        masked_email=masked_email,
        resends_left=resends_left,
        otp_expiry=otp_expiry
    )


@auth.route('/resend-forgot-otp')
def resend_forgot_otp():
    if 'forgot_user' not in session:
        return redirect(url_for('auth.forgot_password'))
    resend_count = session['forgot_user'].get('resend_count', 0)
    if resend_count >= 3:
        session.pop('forgot_user', None)
        return redirect(url_for('auth.forgot_password') + '?error=Too many resend attempts. Please restart.')
    otp = generate_unique_otp()
    session['forgot_user']['otp']          = str(otp)
    session['forgot_user']['otp_expiry']   = (datetime.now() + timedelta(minutes=10)).isoformat()
    session['forgot_user']['attempts']     = 0
    session['forgot_user']['resend_count'] = resend_count + 1
    session.modified = True
    if not send_otp_email(session['forgot_user']['email'], otp):
        return redirect(url_for('auth.forgot_password') + '?error=Failed to resend OTP. Please try again later.')
    return redirect(url_for('auth.verify_forgot_password'))


@auth.route('/logout/admin')
def logout_admin():
    # Log out admin only, preserve user and superadmin sessions if active
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_last_activity = session.get('user_last_activity')
    superadmin_id = session.get('superadmin_id')
    superadmin_name = session.get('superadmin_name')
    superadmin_last_activity = session.get('superadmin_last_activity')
    session.clear()
    if user_id:
        session.permanent = True
        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_last_activity'] = user_last_activity
    if superadmin_id:
        session.permanent = True
        session['superadmin_id'] = superadmin_id
        session['superadmin_name'] = superadmin_name
        session['superadmin_last_activity'] = superadmin_last_activity
    return redirect(url_for('auth.login'))


@auth.route('/logout/user')
def logout_user():
    # Log out user only, preserve admin and superadmin sessions if active
    admin_id = session.get('admin_id')
    admin_name = session.get('admin_name')
    admin_last_activity = session.get('admin_last_activity')
    superadmin_id = session.get('superadmin_id')
    superadmin_name = session.get('superadmin_name')
    superadmin_last_activity = session.get('superadmin_last_activity')
    session.clear()
    if admin_id:
        session.permanent = True
        session['admin_id'] = admin_id
        session['admin_name'] = admin_name
        session['admin_last_activity'] = admin_last_activity
    if superadmin_id:
        session.permanent = True
        session['superadmin_id'] = superadmin_id
        session['superadmin_name'] = superadmin_name
        session['superadmin_last_activity'] = superadmin_last_activity
    return redirect(url_for('auth.login'))


@auth.route('/logout/superadmin')
def logout_superadmin():
    # Log out superadmin only, preserve admin and user sessions if active
    admin_id = session.get('admin_id')
    admin_name = session.get('admin_name')
    admin_last_activity = session.get('admin_last_activity')
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_last_activity = session.get('user_last_activity')
    session.clear()
    if admin_id:
        session.permanent = True
        session['admin_id'] = admin_id
        session['admin_name'] = admin_name
        session['admin_last_activity'] = admin_last_activity
    if user_id:
        session.permanent = True
        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_last_activity'] = user_last_activity
    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
