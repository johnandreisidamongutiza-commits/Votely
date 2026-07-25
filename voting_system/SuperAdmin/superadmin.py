from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import mysql.connector
import bcrypt
import random
import string
from datetime import datetime, timedelta
from voting_system import db_config

superadmin = Blueprint('superadmin', __name__, template_folder='templates', static_folder='static', static_url_path='/superadmin/static')
SESSION_TIMEOUT = timedelta(minutes=30)


def _log(cursor, user_id, action, election_id, details):
    """Insert an activity log only if the user still exists in the DB."""
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    if cursor.fetchone():
        cursor.execute(
            "INSERT INTO activity_logs (user_id, action, election_id, details) VALUES (%s, %s, %s, %s)",
            (user_id, action, election_id, details)
        )

@superadmin.before_request
def check_superadmin_session():
    if 'superadmin_id' not in session:
        return
    last = session.get('superadmin_last_activity')
    if last and datetime.now() - datetime.fromisoformat(last) > SESSION_TIMEOUT:
        session.pop('superadmin_id', None)
        session.pop('superadmin_name', None)
        session.pop('superadmin_last_activity', None)
        return redirect(url_for('auth.login') + '?error=You have been logged out due to inactivity.')
    session['superadmin_last_activity'] = datetime.now().isoformat()

@superadmin.route('/')
def index():
    return redirect(url_for('superadmin.dashboard'))

@superadmin.route('/dashboard')
def dashboard():
    if 'superadmin_id' not in session:
        return redirect(url_for('auth.login'))
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='admin'")
    admin_count = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='user' AND status='active'")
    voter_count = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM elections WHERE status='active'")
    active_elections = cursor.fetchone()['total']
    cursor.close()
    connect.close()
    return render_template('superadmin_dashboard.html',
        username=session.get('superadmin_name'),
        active_page='dashboard',
        admin_count=admin_count,
        voter_count=voter_count,
        active_elections=active_elections
    )

@superadmin.route('/manage-admins')
def manage_admins():
    if 'superadmin_id' not in session:
        return redirect(url_for('auth.login'))
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)
    cursor.execute("SELECT id, user_id, firstname, lastname, email, status FROM users WHERE role='admin' AND status != 'archived' ORDER BY firstname, lastname")
    admins = cursor.fetchall()
    cursor.execute("SELECT id, user_id, firstname, lastname, email, status FROM users WHERE role='admin' AND status = 'archived' ORDER BY firstname, lastname")
    archived_admins = cursor.fetchall()
    cursor.close()
    connect.close()
    return render_template('superadmin_manage_admins.html',
        username=session.get('superadmin_name'),
        admins=admins,
        archived_admins=archived_admins,
        active_page='manage_admins'
    )

@superadmin.route('/create-admin', methods=['POST'])
def create_admin():
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    import re
    USER_ID_RE = re.compile(r'^ADM-\d{4}$')
    NAME_RE    = re.compile(r"^[A-Za-z\s'\-]{3,30}$")
    EMAIL_RE   = re.compile(r"^(?!.*\.\.)(?!.*\.$)[^\W][a-zA-Z0-9._%+\-]{0,63}@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$")
    PW_RE      = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,}$')

    user_id   = request.form.get('user_id', '').strip().upper()
    firstname = ' '.join(request.form.get('firstname', '').strip().split()).title()
    lastname  = ' '.join(request.form.get('lastname', '').strip().split()).title()
    email     = request.form.get('email', '').strip().lower()
    password  = request.form.get('password', '')

    if not all([user_id, firstname, lastname, email, password]):
        return jsonify({'success': False, 'error': 'All fields are required.'})
    if not USER_ID_RE.match(user_id):
        return jsonify({'success': False, 'error': 'Admin ID must follow the format ADM-XXXX (e.g. ADM-0001).'})
    if not NAME_RE.match(firstname):
        return jsonify({'success': False, 'error': 'First name must be 3–30 characters, letters only.'})
    if not NAME_RE.match(lastname):
        return jsonify({'success': False, 'error': 'Last name must be 3–30 characters, letters only.'})
    if not EMAIL_RE.match(email):
        return jsonify({'success': False, 'error': 'Enter a valid email address.'})
    if not PW_RE.match(password):
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character.'})

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE user_id=%s OR email=%s", (user_id, email))
    if cursor.fetchone():
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Admin ID or email is already in use.'})

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO users (user_id, firstname, lastname, email, password, role, status) VALUES (%s,%s,%s,%s,%s,'admin','active')",
        (user_id, firstname, lastname, email, hashed)
    )
    _log(cursor, session['superadmin_id'], 'Created Admin', None, f'Created admin account {user_id} ({firstname} {lastname})')
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})

@superadmin.route('/edit-admin/<int:admin_id>', methods=['POST'])
def edit_admin(admin_id):
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    import re
    NAME_RE  = re.compile(r"^[A-Za-z\s'\-]{3,30}$")
    EMAIL_RE = re.compile(r"^(?!.*\.\.)(?!.*\.$)[^\W][a-zA-Z0-9._%+\-]{0,63}@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$")
    PW_RE    = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,}$')

    firstname = ' '.join(request.form.get('firstname', '').strip().split()).title()
    lastname  = ' '.join(request.form.get('lastname', '').strip().split()).title()
    email     = request.form.get('email', '').strip().lower()
    password  = request.form.get('password', '').strip()

    if not all([firstname, lastname, email]):
        return jsonify({'success': False, 'error': 'First name, last name, and email are required.'})
    if not NAME_RE.match(firstname):
        return jsonify({'success': False, 'error': 'First name must be 3–30 characters, letters only.'})
    if not NAME_RE.match(lastname):
        return jsonify({'success': False, 'error': 'Last name must be 3–30 characters, letters only.'})
    if not EMAIL_RE.match(email):
        return jsonify({'success': False, 'error': 'Enter a valid email address.'})

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)

    cursor.execute("SELECT id, password FROM users WHERE role='admin' AND id=%s", (admin_id,))
    admin = cursor.fetchone()
    if not admin:
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Admin not found.'})

    cursor.execute("SELECT id FROM users WHERE email=%s AND id != %s", (email, admin_id))
    if cursor.fetchone():
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Email is already in use by another account.'})

    if password:
        if not PW_RE.match(password):
            cursor.close(); connect.close()
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character.'})
        stored = admin['password']
        if stored.startswith('$2b$') or stored.startswith('$2a$'):
            if bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8')):
                cursor.close(); connect.close()
                return jsonify({'success': False, 'error': 'New password cannot be the same as the current password.'})
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "UPDATE users SET firstname=%s, lastname=%s, email=%s, password=%s WHERE id=%s",
            (firstname, lastname, email, hashed, admin_id)
        )
    else:
        cursor.execute(
            "UPDATE users SET firstname=%s, lastname=%s, email=%s WHERE id=%s",
            (firstname, lastname, email, admin_id)
        )

    _log(cursor, session['superadmin_id'], 'Edited Admin', None, f'Updated admin account ID {admin_id} ({firstname} {lastname})')
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})

@superadmin.route('/delete-admin/<int:admin_id>', methods=['POST'])
def delete_admin(admin_id):
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)

    cursor.execute("SELECT id, user_id FROM users WHERE role='admin' AND id=%s", (admin_id,))
    admin = cursor.fetchone()
    if not admin:
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Admin not found.'})

    # Reassign elections created by this admin to superadmin before deleting
    cursor.execute("UPDATE elections SET created_by=%s WHERE created_by=%s", (session['superadmin_id'], admin_id))
    _log(cursor, session['superadmin_id'], 'Deleted Admin', None, f'Deleted admin account {admin["user_id"]}')
    cursor.execute("DELETE FROM users WHERE id=%s", (admin_id,))
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})

@superadmin.route('/archive-admin/<int:admin_id>', methods=['POST'])
def archive_admin(admin_id):
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT id, user_id, firstname, lastname FROM users WHERE role='admin' AND id=%s AND status != 'archived'", (admin_id,))
    admin = cursor.fetchone()
    if not admin:
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Admin not found or already archived.'})
    cursor.execute("UPDATE users SET status='archived' WHERE id=%s", (admin_id,))
    _log(cursor, session['superadmin_id'], 'Archived Admin', None, f'Archived admin account {admin["user_id"]} ({admin["firstname"]} {admin["lastname"]})')
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})


@superadmin.route('/restore-admin/<int:admin_id>', methods=['POST'])
def restore_admin(admin_id):
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT id, user_id, firstname, lastname FROM users WHERE role='admin' AND id=%s AND status='archived'", (admin_id,))
    admin = cursor.fetchone()
    if not admin:
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Admin not found or not archived.'})
    cursor.execute("UPDATE users SET status='active' WHERE id=%s", (admin_id,))
    _log(cursor, session['superadmin_id'], 'Restored Admin', None, f'Restored admin account {admin["user_id"]} ({admin["firstname"]} {admin["lastname"]})')
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})


@superadmin.route('/admin-logs')
def admin_logs():
    if 'superadmin_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('superadmin_admin_logs.html', username=session.get('superadmin_name'), active_page='admin_logs')


@superadmin.route('/admin-logs-data')
def admin_logs_data():
    if 'superadmin_id' not in session:
        return jsonify({'error': 'Unauthorized'})

    page     = int(request.args.get('page', 1))
    per_page = 15
    offset   = (page - 1) * per_page

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)

    cursor.execute("DELETE FROM activity_logs WHERE created_at < NOW() - INTERVAL 6 MONTH")
    connect.commit()

    cursor.execute("""
        SELECT COUNT(*) as total FROM activity_logs l
        JOIN users u ON l.user_id = u.id
        WHERE u.role IN ('admin', 'superadmin')
    """)
    total      = cursor.fetchone()['total']
    total_pages = max(1, -(-total // per_page))

    cursor.execute("""
        SELECT l.id, u.user_id, u.firstname, u.lastname, l.action, l.election_id, l.details, l.created_at
        FROM activity_logs l
        JOIN users u ON l.user_id = u.id
        WHERE u.role IN ('admin', 'superadmin')
        ORDER BY l.created_at DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    logs = cursor.fetchall()
    cursor.close()
    connect.close()

    for log in logs:
        log['created_at'] = log['created_at'].strftime('%b %d, %Y %I:%M %p')

    return jsonify({'logs': logs, 'total': total, 'page': page, 'total_pages': total_pages})


# ── SUPERADMIN PROFILE ──

import os as _os
SUPERADMIN_PHOTO_FOLDER = _os.path.join(_os.path.abspath(_os.path.dirname(__file__)), 'static', 'profile_photos')

@superadmin.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'superadmin_id' not in session:
        return redirect(url_for('auth.login'))

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)

    if request.method == 'POST':
        import bcrypt
        current_pw = request.form.get('current_password', '')
        new_pw     = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        cursor.execute("SELECT * FROM users WHERE id=%s", (session['superadmin_id'],))
        sa_data = cursor.fetchone()
        if not sa_data:
            cursor.close(); connect.close()
            session.clear()
            return jsonify({'success': False, 'error': 'Session expired. Please log in again.'})
        stored = sa_data['password']
        if stored.startswith('$2b$') or stored.startswith('$2a$'):
            match = bcrypt.checkpw(current_pw.encode('utf-8'), stored.encode('utf-8'))
        else:
            match = (current_pw == stored)

        if not match:
            cursor.close(); connect.close()
            return jsonify({'success': False, 'error': 'Current password is incorrect.'})
        if new_pw != confirm_pw:
            cursor.close(); connect.close()
            return jsonify({'success': False, 'error': 'New passwords do not match.'})
        if stored.startswith('$2b$') or stored.startswith('$2a$'):
            if bcrypt.checkpw(new_pw.encode('utf-8'), stored.encode('utf-8')):
                cursor.close(); connect.close()
                return jsonify({'success': False, 'error': 'New password cannot be the same as your current password.'})

        hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, session['superadmin_id']))
        connect.commit()
        cursor.close(); connect.close()
        return jsonify({'success': True})

    cursor.execute("SELECT id, user_id, firstname, lastname, email, profile_photo FROM users WHERE id=%s", (session['superadmin_id'],))
    sa_data = cursor.fetchone()
    if not sa_data:
        cursor.close(); connect.close()
        session.clear()
        return redirect(url_for('auth.login') + '?error=Your session is no longer valid. Please log in again.')
    cursor.execute("SELECT is_enabled FROM user_2fa WHERE user_id=%s", (session['superadmin_id'],))
    twofa = cursor.fetchone()
    sa_data['twofa_enabled'] = twofa['is_enabled'] if twofa else False

    # Stats
    cursor.execute("SELECT COUNT(*) as total FROM elections WHERE created_by=%s", (session['superadmin_id'],))
    sa_data['elections_managed'] = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='admin'")
    sa_data['admins_created'] = cursor.fetchone()['total']

    # Recent activity logs
    cursor.execute("""
        SELECT action, details, created_at FROM activity_logs
        WHERE user_id=%s ORDER BY created_at DESC LIMIT 5
    """, (session['superadmin_id'],))
    recent_logs = cursor.fetchall()

    cursor.close(); connect.close()
    return render_template('superadmin_profile.html', username=session.get('superadmin_name'), sa=sa_data, recent_logs=recent_logs, active_page='profile')


@superadmin.route('/upload-superadmin-photo', methods=['POST'])
def upload_superadmin_photo():
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    from flask import send_from_directory
    from werkzeug.utils import secure_filename
    import uuid

    ALLOWED = {'png', 'jpg', 'jpeg', 'gif'}
    file = request.files.get('photo')
    if not file or not file.filename:
        return jsonify({'success': False, 'error': 'No file selected.'})
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED:
        return jsonify({'success': False, 'error': 'Only image files are allowed (jpg, png, gif).'})

    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > 5:
        return jsonify({'success': False, 'error': f'File must be under 5MB (current: {size_mb:.1f}MB).'})

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT profile_photo FROM users WHERE id=%s", (session['superadmin_id'],))
    row = cursor.fetchone()
    if row and row['profile_photo']:
        old_path = _os.path.join(SUPERADMIN_PHOTO_FOLDER, row['profile_photo'])
        if _os.path.exists(old_path):
            _os.remove(old_path)

    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(_os.path.join(SUPERADMIN_PHOTO_FOLDER, filename))

    cursor.execute("UPDATE users SET profile_photo=%s WHERE id=%s", (filename, session['superadmin_id']))
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True, 'filename': filename})


@superadmin.route('/delete-superadmin-photo', methods=['POST'])
def delete_superadmin_photo():
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT profile_photo FROM users WHERE id=%s", (session['superadmin_id'],))
    row = cursor.fetchone()
    if row and row['profile_photo']:
        old_path = _os.path.join(SUPERADMIN_PHOTO_FOLDER, row['profile_photo'])
        if _os.path.exists(old_path):
            _os.remove(old_path)
        cursor.execute("UPDATE users SET profile_photo=NULL WHERE id=%s", (session['superadmin_id'],))
        connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})


@superadmin.route('/superadmin-profile-photo/<filename>')
def superadmin_profile_photo(filename):
    from flask import send_from_directory
    return send_from_directory(SUPERADMIN_PHOTO_FOLDER, filename)


@superadmin.route('/toggle-superadmin-2fa/<action>', methods=['POST'])
def toggle_superadmin_2fa(action):
    if 'superadmin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    if action not in ('enable', 'disable'):
        return jsonify({'success': False, 'error': 'Invalid action.'})
    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT id FROM user_2fa WHERE user_id=%s", (session['superadmin_id'],))
    existing = cursor.fetchone()
    enabled  = 1 if action == 'enable' else 0
    if existing:
        cursor.execute("UPDATE user_2fa SET is_enabled=%s, otp_code=NULL, otp_expires=NULL WHERE user_id=%s", (enabled, session['superadmin_id']))
    else:
        cursor.execute("INSERT INTO user_2fa (user_id, is_enabled) VALUES (%s, %s)", (session['superadmin_id'], enabled))
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})
