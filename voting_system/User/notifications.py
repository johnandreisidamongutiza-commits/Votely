import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from voting_system import db_config

SMTP_EMAIL    = 'johnandreigutiza125@gmail.com'
SMTP_PASSWORD = 'dwkn gkye wdri ragj'

THRESHOLD_24H = timedelta(hours=24)
THRESHOLD_1H  = timedelta(hours=1)


def _send_email(to, subject, html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f'Votely <{SMTP_EMAIL}>'
        msg['To']      = to
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to, msg.as_string())
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')


def _already_sent(cursor, user_id, election_id, notif_type):
    cursor.execute(
        "SELECT id FROM notifications_sent WHERE user_id=%s AND election_id=%s AND type=%s",
        (user_id, election_id, notif_type)
    )
    return cursor.fetchone() is not None


def _mark_sent(cursor, user_id, election_id, notif_type):
    cursor.execute(
        "INSERT IGNORE INTO notifications_sent (user_id, election_id, type) VALUES (%s, %s, %s)",
        (user_id, election_id, notif_type)
    )


def check_and_send_notifications(user_id):
    try:
        connect = mysql.connector.connect(**db_config)
        cursor  = connect.cursor(dictionary=True)

        # Get user email
        cursor.execute("SELECT email, firstname FROM users WHERE id=%s AND status='active'", (user_id,))
        user = cursor.fetchone()
        if not user or not user['email']:
            cursor.close(); connect.close()
            return

        # Get active elections the user hasn't fully voted in
        now = datetime.now()
        cursor.execute("""
            SELECT e.id, e.title, e.end_date,
                   COUNT(DISTINCT p.id) as total_positions,
                   COUNT(DISTINCT v.position_id) as voted_positions
            FROM elections e
            JOIN positions p ON p.election_id = e.id
            LEFT JOIN votes v ON v.election_id = e.id AND v.user_id = %s
            WHERE e.status = 'active' AND e.end_date >= %s
            GROUP BY e.id
            HAVING voted_positions < total_positions
        """, (user_id, now))
        elections = cursor.fetchall()

        for election in elections:
            end_date   = election['end_date']
            time_left  = end_date - now
            title      = election['title']
            eid        = election['id']
            remaining  = election['total_positions'] - election['voted_positions']
            firstname  = user['firstname']
            email      = user['email']

            # 24h notification
            if time_left <= THRESHOLD_24H and not _already_sent(cursor, user_id, eid, '24h'):
                subject = f'Reminder: "{title}" closes in 24 hours'
                html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 20px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(99,102,241,0.10);">
        <tr>
          <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);padding:36px 40px 28px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,0.18);border-radius:14px;padding:10px 18px;margin-bottom:14px;">
              <span style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Votely</span>
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.70);letter-spacing:0.5px;text-transform:uppercase;font-weight:600;">Official Voting Platform</div>
          </td>
        </tr>
        <tr><td style="height:4px;background:linear-gradient(90deg,#6366f1,#8b5cf6,#a78bfa);"></td></tr>
        <tr>
          <td style="padding:36px 40px 28px;">
            <div style="font-size:22px;font-weight:800;color:#0f172a;margin-bottom:8px;letter-spacing:-0.3px;">⏰ Vote Before It's Too Late, {firstname}!</div>
            <div style="font-size:14px;color:#64748b;line-height:1.7;margin-bottom:24px;">
              The election <strong style="color:#0f172a;">"{title}"</strong> is closing in less than <strong style="color:#f59e0b;">24 hours</strong>. Don't miss your chance to make your voice heard!
            </div>
            <!-- Info Card -->
            <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border:1.5px solid #c4b5fd;border-radius:16px;padding:22px 24px;margin-bottom:24px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:6px 0;">
                    <span style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#7c3aed;">Election</span><br>
                    <span style="font-size:15px;font-weight:700;color:#0f172a;">{title}</span>
                  </td>
                </tr>
                <tr><td style="height:12px;"></td></tr>
                <tr>
                  <td>
                    <table cellpadding="0" cellspacing="0" width="100%">
                      <tr>
                        <td width="50%" style="padding:0 8px 0 0;">
                          <div style="background:#fff;border-radius:10px;padding:12px 14px;border:1px solid #e2e8f0;">
                            <div style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Closes On</div>
                            <div style="font-size:13px;font-weight:700;color:#0f172a;">{end_date.strftime('%b %d, %Y')}</div>
                            <div style="font-size:12px;color:#64748b;">{end_date.strftime('%I:%M %p')}</div>
                          </div>
                        </td>
                        <td width="50%" style="padding:0 0 0 8px;">
                          <div style="background:#fff;border-radius:10px;padding:12px 14px;border:1px solid #e2e8f0;">
                            <div style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Positions Left</div>
                            <div style="font-size:24px;font-weight:900;color:#6366f1;">{remaining}</div>
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </div>
            <div style="font-size:13px;color:#64748b;line-height:1.6;">
              Log in to <strong style="color:#6366f1;">Votely</strong> and cast your vote now. Every vote counts!
            </div>
          </td>
        </tr>
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
                _send_email(email, subject, html_body)
                _mark_sent(cursor, user_id, eid, '24h')
                cursor.execute(
                    "INSERT INTO user_notifications (user_id, election_id, type, message) VALUES (%s, %s, %s, %s)",
                    (user_id, eid, '24h', f'"{title}" closes in less than 24 hours. {remaining} position(s) left to vote.')
                )

            # 1h notification
            if time_left <= THRESHOLD_1H and not _already_sent(cursor, user_id, eid, '1h'):
                subject = f'Urgent: "{title}" closes in 1 hour!'
                html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:40px 20px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(99,102,241,0.10);">
        <tr>
          <td style="background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);padding:36px 40px 28px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,0.18);border-radius:14px;padding:10px 18px;margin-bottom:14px;">
              <span style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Votely</span>
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.70);letter-spacing:0.5px;text-transform:uppercase;font-weight:600;">Official Voting Platform</div>
          </td>
        </tr>
        <tr><td style="height:4px;background:linear-gradient(90deg,#ef4444,#f97316,#fbbf24);"></td></tr>
        <tr>
          <td style="padding:36px 40px 28px;">
            <div style="font-size:22px;font-weight:800;color:#0f172a;margin-bottom:8px;letter-spacing:-0.3px;">🚨 URGENT: 1 Hour Left, {firstname}!</div>
            <div style="font-size:14px;color:#64748b;line-height:1.7;margin-bottom:24px;">
              The election <strong style="color:#0f172a;">"{title}"</strong> is closing in less than <strong style="color:#ef4444;">1 hour</strong>. Log in immediately and cast your vote!
            </div>
            <!-- Urgent Info Card -->
            <div style="background:linear-gradient(135deg,#fff1f2,#ffe4e6);border:1.5px solid #fca5a5;border-radius:16px;padding:22px 24px;margin-bottom:24px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:6px 0;">
                    <span style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#dc2626;">Election</span><br>
                    <span style="font-size:15px;font-weight:700;color:#0f172a;">{title}</span>
                  </td>
                </tr>
                <tr><td style="height:12px;"></td></tr>
                <tr>
                  <td>
                    <table cellpadding="0" cellspacing="0" width="100%">
                      <tr>
                        <td width="50%" style="padding:0 8px 0 0;">
                          <div style="background:#fff;border-radius:10px;padding:12px 14px;border:1px solid #fecaca;">
                            <div style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Closes At</div>
                            <div style="font-size:13px;font-weight:700;color:#0f172a;">{end_date.strftime('%b %d, %Y')}</div>
                            <div style="font-size:12px;color:#ef4444;font-weight:700;">{end_date.strftime('%I:%M %p')}</div>
                          </div>
                        </td>
                        <td width="50%" style="padding:0 0 0 8px;">
                          <div style="background:#fff;border-radius:10px;padding:12px 14px;border:1px solid #fecaca;">
                            <div style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Positions Left</div>
                            <div style="font-size:24px;font-weight:900;color:#ef4444;">{remaining}</div>
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </div>
            <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;">
              <span style="font-size:13px;color:#92400e;line-height:1.6;">⚠️ This is your final reminder. Once the election closes, you will no longer be able to vote.</span>
            </div>
          </td>
        </tr>
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
                _send_email(email, subject, html_body)
                _mark_sent(cursor, user_id, eid, '1h')
                cursor.execute(
                    "INSERT INTO user_notifications (user_id, election_id, type, message) VALUES (%s, %s, %s, %s)",
                    (user_id, eid, '1h', f'URGENT: "{title}" closes in less than 1 hour! {remaining} position(s) left to vote.')
                )

        connect.commit()
        cursor.close()
        connect.close()

    except Exception as e:
        print(f'[NOTIFICATION ERROR] {e}')
