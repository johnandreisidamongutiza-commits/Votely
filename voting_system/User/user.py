
def create_user_activity_log(user_id, action, election_id=None, details=None):
    """Insert an activity log only if the user still exists in the DB."""
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    if cursor.fetchone():
        cursor.execute(
            "INSERT INTO activity_logs (user_id, action, election_id, details) VALUES (%s, %s, %s, %s)",
            (user_id, action, election_id, details)
        )
        connect.commit()
    cursor.close()
    connect.close()


from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import mysql.connector
import bcrypt
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from voting_system import db_config
from voting_system.User.notifications import check_and_send_notifications

user = Blueprint('user', __name__, template_folder='templates', static_folder='static')

PROFILE_PHOTO_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'profile_photos')
ALLOWED_EXTENSIONS   = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

SESSION_TIMEOUT = timedelta(minutes=30)


def _log(cursor, user_id, action, election_id, details):
    """Insert an activity log only if the user still exists in the DB."""
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    if cursor.fetchone():
        cursor.execute(
            "INSERT INTO activity_logs (user_id, action, election_id, details) VALUES (%s, %s, %s, %s)",
            (user_id, action, election_id, details)
        )

@user.before_request
def check_user_session():
    if 'user_id' not in session:
        return
    last = session.get('user_last_activity')
    if last and datetime.now() - datetime.fromisoformat(last) > SESSION_TIMEOUT:
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('user_last_activity', None)
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'session_expired'}), 401
        return redirect(url_for('auth.login') + '?error=You have been logged out due to inactivity.')
    session['user_last_activity'] = datetime.now().isoformat()

def update_election_statuses():
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor()
    cursor.execute("UPDATE elections SET status='active' WHERE status='draft' AND start_date <= NOW() AND end_date >= NOW()")
    cursor.execute("UPDATE elections SET status='ended' WHERE status='active' AND end_date < NOW()")
    connect.commit()
    cursor.close()
    connect.close()

@user.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    update_election_statuses()
    check_and_send_notifications(session['user_id'])

    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM elections WHERE (status='active' OR (status='draft' AND start_date <= NOW() AND end_date >= NOW())) ORDER BY end_date ASC"
    )
    active_elections = cursor.fetchall()
    now = datetime.now()
    for election in active_elections:
        if election['status'] == 'draft' and election['start_date'] <= now <= election['end_date']:
            election['status'] = 'active'

    cursor.execute("SELECT * FROM elections WHERE status='ended' ORDER BY end_date DESC")
    ended_elections = cursor.fetchall()

    elections = active_elections + ended_elections

    for election in elections:
        cursor.execute("SELECT COUNT(*) as total FROM positions WHERE election_id=%s", (election['id'],))
        total_positions = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as voted FROM votes WHERE user_id=%s AND election_id=%s", (session['user_id'], election['id']))
        total_voted = cursor.fetchone()['voted']
        election['total_positions'] = total_positions
        election['total_voted'] = total_voted
        election['fully_voted'] = total_voted >= total_positions and total_positions > 0

        cursor.execute("SELECT COUNT(*) as total FROM candidates WHERE election_id=%s", (election['id'],))
        election['candidate_count'] = cursor.fetchone()['total']

        cursor.execute("""
            SELECT p.name as position_name, c.firstname, c.lastname, c.photo
            FROM votes v
            JOIN positions p ON v.position_id = p.id
            JOIN candidates c ON v.candidate_id = c.id
            WHERE v.user_id=%s AND v.election_id=%s
            ORDER BY p.name
        """, (session['user_id'], election['id']))
        election['my_votes'] = cursor.fetchall()

    cursor.close()
    connect.close()

    # Fetch profile photo for sidebar avatar
    connect2 = mysql.connector.connect(**db_config)
    cursor2  = connect2.cursor(dictionary=True)
    cursor2.execute("SELECT profile_photo FROM users WHERE id=%s", (session['user_id'],))
    profile_photo = (cursor2.fetchone() or {}).get('profile_photo')
    cursor2.close(); connect2.close()

    return render_template('user_dashboard.html', username=session.get('user_name'), elections=elections, profile_photo=profile_photo, now_ts=datetime.now().timestamp())


@user.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)

    # Get elections the user voted in
    cursor.execute("""
        SELECT DISTINCT e.id, e.title, e.description, e.status, e.end_date
        FROM votes v
        JOIN elections e ON v.election_id = e.id
        WHERE v.user_id=%s
        ORDER BY e.end_date DESC
    """, (session['user_id'],))
    participated = cursor.fetchall()

    for election in participated:
        cursor.execute("""
            SELECT p.name as position_name, c.firstname, c.lastname, c.photo
            FROM votes v
            JOIN positions p ON v.position_id = p.id
            JOIN candidates c ON v.candidate_id = c.id
            WHERE v.user_id=%s AND v.election_id=%s
            ORDER BY p.name
        """, (session['user_id'], election['id']))
        election['votes'] = cursor.fetchall()
        election['participated'] = True

    # Get all ended elections (including ones user didn't vote in)
    cursor.execute("""
        SELECT id, title, description, status, end_date
        FROM elections
        WHERE status='ended'
        ORDER BY end_date DESC
    """)
    all_ended = cursor.fetchall()

    # Add metadata for all ended elections
    for election in all_ended:
        cursor.execute("SELECT COUNT(*) as total FROM positions WHERE election_id=%s", (election['id'],))
        election['total_positions'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM candidates WHERE election_id=%s", (election['id'],))
        election['candidate_count'] = cursor.fetchone()['total']
        # Check if user voted
        cursor.execute("SELECT COUNT(*) as voted FROM votes WHERE user_id=%s AND election_id=%s", (session['user_id'], election['id']))
        election['user_voted'] = cursor.fetchone()['voted'] > 0

    cursor.close()
    connect.close()

    connect2 = mysql.connector.connect(**db_config)
    cursor2  = connect2.cursor(dictionary=True)
    cursor2.execute("SELECT profile_photo FROM users WHERE id=%s", (session['user_id'],))
    profile_photo = (cursor2.fetchone() or {}).get('profile_photo')
    cursor2.close(); connect2.close()

    return render_template('history.html', 
        username=session.get('user_name'), 
        participated_elections=participated,
        all_ended_elections=all_ended,
        profile_photo=profile_photo
    )


@user.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)

    if request.method == 'POST':
        current_pw  = request.form.get('current_password', '')
        new_pw      = request.form.get('new_password', '')
        confirm_pw  = request.form.get('confirm_password', '')

        cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
        user_data = cursor.fetchone()
        if not user_data:
            cursor.close(); connect.close()
            session.clear()
            return jsonify({'success': False, 'error': 'Session expired. Please log in again.'})
        stored = user_data['password']
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
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, session['user_id']))
        connect.commit()
        cursor.close(); connect.close()
        return jsonify({'success': True})

    cursor.execute("SELECT user_id, firstname, lastname, email, profile_photo FROM users WHERE id=%s", (session['user_id'],))
    user_data = cursor.fetchone()
    if not user_data:
        cursor.close(); connect.close()
        session.clear()
        return redirect(url_for('auth.login') + '?error=Your session is no longer valid. Please log in again.')
    cursor.execute("SELECT is_enabled FROM user_2fa WHERE user_id=%s", (session['user_id'],))
    twofa = cursor.fetchone()
    user_data['twofa_enabled'] = twofa['is_enabled'] if twofa else False

    # Stats
    cursor.execute("SELECT COUNT(DISTINCT election_id) as total FROM votes WHERE user_id=%s", (session['user_id'],))
    user_data['elections_voted'] = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM votes WHERE user_id=%s", (session['user_id'],))
    user_data['positions_voted'] = cursor.fetchone()['total']

    cursor.close()
    connect.close()
    return render_template('profile.html', username=session.get('user_name'), user=user_data)

@user.route('/toggle-2fa/<action>', methods=['POST'])
def toggle_2fa(action):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    if action not in ('enable', 'disable'):
        return jsonify({'success': False, 'error': 'Invalid action.'})
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)
    cursor.execute("SELECT id FROM user_2fa WHERE user_id=%s", (session['user_id'],))
    existing = cursor.fetchone()
    enabled = 1 if action == 'enable' else 0
    if existing:
        cursor.execute("UPDATE user_2fa SET is_enabled=%s, otp_code=NULL, otp_expires=NULL WHERE user_id=%s", (enabled, session['user_id']))
    else:
        cursor.execute("INSERT INTO user_2fa (user_id, is_enabled) VALUES (%s, %s)", (session['user_id'], enabled))
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})


@user.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    file = request.files.get('photo')
    if not file or not file.filename:
        return jsonify({'success': False, 'error': 'No file selected.'})
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Only image files are allowed (jpg, png, gif).'})

    # Size check (max 5MB)
    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > 5:
        return jsonify({'success': False, 'error': f'File must be under 5MB (current: {size_mb:.1f}MB).'})

    # Delete old photo if exists
    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT profile_photo FROM users WHERE id=%s", (session['user_id'],))
    row = cursor.fetchone()
    if row and row['profile_photo']:
        old_path = os.path.join(PROFILE_PHOTO_FOLDER, row['profile_photo'])
        if os.path.exists(old_path):
            os.remove(old_path)

    # Save new photo with unique filename
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(PROFILE_PHOTO_FOLDER, filename))

    cursor.execute("UPDATE users SET profile_photo=%s WHERE id=%s", (filename, session['user_id']))
    connect.commit()
    cursor.close()
    connect.close()

    return jsonify({'success': True, 'filename': filename})


@user.route('/delete-photo', methods=['POST'])
def delete_photo():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT profile_photo FROM users WHERE id=%s", (session['user_id'],))
    row = cursor.fetchone()
    if row and row['profile_photo']:
        old_path = os.path.join(PROFILE_PHOTO_FOLDER, row['profile_photo'])
        if os.path.exists(old_path):
            os.remove(old_path)
        cursor.execute("UPDATE users SET profile_photo=NULL WHERE id=%s", (session['user_id'],))
        connect.commit()
    cursor.close()
    connect.close()
    return jsonify({'success': True})


def get_results_data(election_id):
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)

    cursor.execute("SELECT * FROM elections WHERE id=%s", (election_id,))
    election = cursor.fetchone()
    if not election:
        cursor.close(); connect.close()
        return None, None, None, None

    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='user' AND status='active'")
    total_voters = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(DISTINCT user_id) as voted FROM votes WHERE election_id=%s", (election_id,))
    total_voted = cursor.fetchone()['voted']

    cursor.execute("SELECT * FROM positions WHERE election_id=%s", (election_id,))
    positions = cursor.fetchall()
    for pos in positions:
        cursor.execute("""
            SELECT c.id, c.firstname, c.lastname, c.photo,
                   COUNT(v.id) as vote_count
            FROM candidates c
            LEFT JOIN votes v ON v.candidate_id = c.id AND v.election_id=%s
            WHERE c.position_id=%s
            GROUP BY c.id
            ORDER BY vote_count DESC
        """, (election_id, pos['id']))
        candidates = cursor.fetchall()
        total_pos_votes = sum(c['vote_count'] for c in candidates)
        for c in candidates:
            c['percentage'] = round((c['vote_count'] / total_pos_votes * 100) if total_pos_votes > 0 else 0, 1)
        pos['candidates'] = candidates
        pos['winner'] = candidates[0] if candidates and candidates[0]['vote_count'] > 0 else None

    cursor.close(); connect.close()
    return election, positions, total_voters, total_voted


@user.route('/results/<int:election_id>')
def results(election_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    election, positions, total_voters, total_voted = get_results_data(election_id)
    if not election:
        return redirect(url_for('user.dashboard'))

    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor()
    _log(cursor, session['user_id'], 'Viewed Results', election_id, None)
    connect.commit()
    cursor.close()
    connect.close()

    return render_template('results.html',
        username=session.get('user_name'),
        election=election,
        positions=positions,
        total_voters=total_voters,
        total_voted=total_voted
    )


@user.route('/results-data/<int:election_id>')
def results_data(election_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    election, positions, total_voters, total_voted = get_results_data(election_id)
    if not election:
        return jsonify({'error': 'Election not found'})
    result = {
        'total_voters': total_voters,
        'total_voted': total_voted,
        'turnout': round((total_voted / total_voters * 100) if total_voters > 0 else 0, 1),
        'positions': []
    }
    for pos in positions:
        result['positions'].append({
            'name': pos['name'],
            'candidates': [{
                'id': c['id'],
                'name': f"{c['firstname']} {c['lastname']}",
                'photo': c['photo'],
                'vote_count': c['vote_count'],
                'percentage': c['percentage']
            } for c in pos['candidates']],
            'winner': f"{pos['winner']['firstname']} {pos['winner']['lastname']}" if pos['winner'] else None
        })
    return jsonify(result)


@user.route('/vote/<int:election_id>')
def vote_page(election_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)
    now = datetime.now()

    cursor.execute("SELECT * FROM elections WHERE id=%s AND status='active' AND start_date <= %s AND end_date >= %s", (election_id, now, now))
    election = cursor.fetchone()
    if not election:
        cursor.close(); connect.close()
        return redirect(url_for('user.dashboard'))

    cursor.execute("SELECT * FROM positions WHERE election_id=%s", (election_id,))
    positions = cursor.fetchall()
    for pos in positions:
        cursor.execute("SELECT * FROM candidates WHERE position_id=%s AND election_id=%s", (pos['id'], election_id))
        pos['candidates'] = cursor.fetchall()

    cursor.execute("SELECT position_id FROM votes WHERE user_id=%s AND election_id=%s", (session['user_id'], election_id))
    already_voted_positions = [row['position_id'] for row in cursor.fetchall()]

    cursor.close()
    connect.close()

    return render_template('vote.html',
        username=session.get('user_name'),
        election=election,
        positions=positions,
        already_voted_positions=already_voted_positions
    )


@user.route('/notifications/read', methods=['POST'])
def mark_notifications_read():
    if 'user_id' not in session:
        return jsonify({'success': False})
    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor()
    cursor.execute("UPDATE user_notifications SET is_read=1 WHERE user_id=%s", (session['user_id'],))
    connect.commit()
    cursor.close(); connect.close()
    return jsonify({'success': True})


@user.route('/notifications/list')
def list_notifications():
    if 'user_id' not in session:
        return jsonify([])
    connect = mysql.connector.connect(**db_config)
    cursor  = connect.cursor(dictionary=True)
    cursor.execute("SELECT id, type, message, is_read, created_at FROM user_notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 20", (session['user_id'],))
    rows = cursor.fetchall()
    cursor.close(); connect.close()
    return jsonify([{**r, 'created_at': r['created_at'].strftime('%b %d, %I:%M %p')} for r in rows])


@user.route('/submit-vote', methods=['POST'])
def submit_vote():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    data = request.get_json()
    votes = data.get('votes', [])
    election_id = data.get('election_id')

    if not election_id:
        return jsonify({'success': False, 'error': 'No election specified.'})

    now = datetime.now()
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)

    cursor.execute("SELECT * FROM elections WHERE id=%s AND status='active' AND start_date <= %s AND end_date >= %s", (election_id, now, now))
    election = cursor.fetchone()
    if not election:
        cursor.close(); connect.close()
        return jsonify({'success': False, 'error': 'Election is not currently active.'})

    for v in votes:
        cursor.execute("SELECT id FROM votes WHERE user_id=%s AND position_id=%s AND election_id=%s",
            (session['user_id'], v['position_id'], election_id))
        if cursor.fetchone():
            cursor.close(); connect.close()
            return jsonify({'success': False, 'error': 'You have already voted for one or more of these positions.'})

    # Race condition guard — verify candidate and position still exist
    for v in votes:
        cursor.execute("SELECT id FROM candidates WHERE id=%s AND position_id=%s AND election_id=%s",
            (v['candidate_id'], v['position_id'], election_id))
        if not cursor.fetchone():
            cursor.close(); connect.close()
            return jsonify({'success': False, 'error': 'One or more candidates are no longer available. Please refresh and try again.'})

    for v in votes:
        cursor.execute(
            "INSERT INTO votes (user_id, candidate_id, position_id, election_id) VALUES (%s, %s, %s, %s)",
            (session['user_id'], v['candidate_id'], v['position_id'], election_id)
        )

    cursor.execute("SELECT COUNT(*) as total FROM positions WHERE election_id=%s", (election_id,))
    total_positions = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as voted FROM votes WHERE user_id=%s AND election_id=%s", (session['user_id'], election_id))
    total_voted = cursor.fetchone()['voted']

    connect.commit()

    cursor.execute("SELECT title FROM elections WHERE id=%s", (election_id,))
    election_title = cursor.fetchone()['title']
    cursor.execute("SELECT COUNT(*) as total FROM positions WHERE election_id=%s", (election_id,))
    pos_count = cursor.fetchone()['total']
    _log(cursor, session['user_id'], 'Submitted Vote', election_id, f'Voted in {len(votes)} out of {pos_count} positions')
    connect.commit()
    cursor.close()
    connect.close()
    return jsonify({'success': True, 'redirect': url_for('user.vote_confirm', election_id=election_id)})


@user.route('/vote-confirm/<int:election_id>')
def vote_confirm(election_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    connect = mysql.connector.connect(**db_config)
    cursor = connect.cursor(dictionary=True)
    cursor.execute("SELECT * FROM elections WHERE id=%s", (election_id,))
    election = cursor.fetchone()
    if not election:
        cursor.close(); connect.close()
        return redirect(url_for('user.dashboard'))
    cursor.execute("""
        SELECT p.name as position_name, c.firstname, c.lastname, c.photo
        FROM votes v
        JOIN positions p ON v.position_id = p.id
        JOIN candidates c ON v.candidate_id = c.id
        WHERE v.user_id=%s AND v.election_id=%s
        ORDER BY p.name
    """, (session['user_id'], election_id))
    my_votes = cursor.fetchall()
    cursor.execute("SELECT profile_photo FROM users WHERE id=%s", (session['user_id'],))
    profile_photo = (cursor.fetchone() or {}).get('profile_photo')
    cursor.close(); connect.close()
    return render_template('vote_confirm.html',
        username=session.get('user_name'),
        election=election,
        my_votes=my_votes,
        profile_photo=profile_photo,
        submitted_at=datetime.now().strftime('%B %d, %Y %I:%M %p')
    )
