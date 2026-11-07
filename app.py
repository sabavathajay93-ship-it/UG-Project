from flask import (Flask, render_template, request, redirect,
                   url_for, send_file, abort, session, flash)
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid
import os
import qrcode
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

app = Flask(__name__)
app.secret_key = 'nizam-college-secret-2025'   # change in production

CERTIFICATES_DIR = os.path.join('static', 'certificates')
os.makedirs(CERTIFICATES_DIR, exist_ok=True)


# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect('certificates.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id         TEXT PRIMARY KEY,
            name       TEXT NOT NULL,
            course     TEXT NOT NULL,
            event      TEXT NOT NULL,
            date       TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # Seed default admin if not present
    if not conn.execute(
        'SELECT 1 FROM users WHERE username = ?', ('admin',)
    ).fetchone():
        conn.execute(
            'INSERT INTO users VALUES (?, ?)',
            ('admin', generate_password_hash('admin123')),
        )
    conn.commit()
    conn.close()


# ── Auth helper ───────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


# ── Certificate helpers ───────────────────────────────────────────────────────

def gen_cert_id():
    uid = uuid.uuid4().hex.upper()
    return f"NC-{uid[:4]}-{uid[4:8]}-{uid[8:12]}"


def make_qr(cert_id, base_url):
    url = f"{base_url}/verify/{cert_id}"
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1B2A4A", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def make_pdf(cert, cert_id, base_url):
    pdf_path = os.path.join(CERTIFICATES_DIR, f"{cert_id}.pdf")
    W, H = landscape(A4)

    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))

    GOLD       = colors.HexColor('#C9A84C')
    DARK_GOLD  = colors.HexColor('#8B6914')
    NAVY       = colors.HexColor('#1B2A4A')
    CREAM      = colors.HexColor('#FDFBF3')
    SOFT_GREY  = colors.HexColor('#555555')
    LIGHT_GOLD = colors.HexColor('#F0D98A')

    # Background
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Triple border
    for margin, lw, col in [(10, 9, GOLD), (20, 2, DARK_GOLD), (26, 1, GOLD)]:
        c.setStrokeColor(col)
        c.setLineWidth(lw)
        c.rect(margin, margin, W - 2*margin, H - 2*margin, fill=0, stroke=1)

    # Header band
    c.setFillColor(NAVY)
    c.rect(30, H - 108, W - 60, 78, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(30, H - 30, W - 60, 5, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 27)
    c.drawCentredString(W / 2, H - 68, "NIZAM COLLEGE")

    c.setFillColor(LIGHT_GOLD)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(W / 2, H - 89, "Osmania University  \u2022  Hyderabad, Telangana")

    # Title
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 134, "CERTIFICATE  OF  ACHIEVEMENT")

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(W * 0.22, H - 144, W * 0.78, H - 144)

    # Body
    c.setFillColor(SOFT_GREY)
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(W / 2, H - 174, "This is to certify that")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, H - 216, cert['name'])
    nw = c.stringWidth(cert['name'], "Helvetica-Bold", 30)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(W/2 - nw/2 - 20, H - 224, W/2 + nw/2 + 20, H - 224)

    c.setFillColor(SOFT_GREY)
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(W / 2, H - 250, "has successfully completed")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 275, cert['course'])

    c.setFillColor(SOFT_GREY)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, H - 302, f"organized at  \u2022  {cert['event']}")

    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H - 322, f"Dated:  {cert['date']}")

    # Signature lines
    sig_y = H - 385
    for sx, label, sublabel in [
        (110,     "Principal",          "Nizam College"),
        (W - 110, "Course Coordinator", "Nizam College"),
    ]:
        c.setStrokeColor(NAVY)
        c.setLineWidth(1)
        c.line(sx - 72, sig_y, sx + 72, sig_y)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(sx, sig_y - 14, label)
        c.setFillColor(SOFT_GREY)
        c.setFont("Helvetica", 8)
        c.drawCentredString(sx, sig_y - 26, sublabel)

    # QR Code
    qr_buf  = make_qr(cert_id, base_url)
    qr_img  = ImageReader(qr_buf)
    qr_size = 82
    qr_x    = W - 125
    qr_y    = 80
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size, mask='auto')
    c.setFillColor(SOFT_GREY)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 12, "Scan to Verify")

    # Footer
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(35, 78, W - 35, 78)

    c.setFillColor(SOFT_GREY)
    c.setFont("Helvetica", 8.5)
    c.drawString(42, 62, f"Certificate ID: {cert_id}")
    c.drawString(42, 50, f"Issued on: {cert['created_at']}")

    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(W / 2, 38,
        "This certificate is digitally generated and verifiable at Nizam College portal.")

    # Corner ornaments
    def diamond(cx, cy, r=9):
        c.setFillColor(GOLD)
        p = c.beginPath()
        p.moveTo(cx,     cy + r)
        p.lineTo(cx + r, cy)
        p.lineTo(cx,     cy - r)
        p.lineTo(cx - r, cy)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    for dx, dy in [(43, 43), (W - 43, 43), (43, H - 43), (W - 43, H - 43)]:
        diamond(dx, dy)

    c.save()
    return pdf_path


# ── Public routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['admin'] = username
            next_url = request.args.get('next') or url_for('admin_dashboard')
            return redirect(next_url)
        error = 'Invalid username or password.'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/verify/<cert_id>')
def verify(cert_id):
    conn = get_db()
    cert = conn.execute(
        'SELECT * FROM certificates WHERE id = ?', (cert_id,)
    ).fetchone()
    conn.close()
    return render_template('verify.html', cert=cert, cert_id=cert_id)


@app.route('/pdf/<cert_id>')
def get_pdf(cert_id):
    conn = get_db()
    cert = conn.execute(
        'SELECT * FROM certificates WHERE id = ?', (cert_id,)
    ).fetchone()
    conn.close()
    if not cert:
        abort(404)
    pdf_path = os.path.join(CERTIFICATES_DIR, f"{cert_id}.pdf")
    if not os.path.exists(pdf_path):
        base_url = request.host_url.rstrip('/')
        make_pdf(cert, cert_id, base_url)
    return send_file(pdf_path, mimetype='application/pdf')


# ── Admin routes (login required) ─────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn  = get_db()
    certs = conn.execute(
        'SELECT * FROM certificates ORDER BY rowid DESC'
    ).fetchall()
    conn.close()
    return render_template('admin.html', certificates=certs,
                           admin_user=session['admin'])


@app.route('/generate', methods=['POST'])
@admin_required
def generate():
    name   = request.form.get('name',   '').strip()
    course = request.form.get('course', '').strip()
    event  = request.form.get('event',  '').strip()
    date   = request.form.get('date',   '').strip()

    if not all([name, course, event, date]):
        return redirect(url_for('admin_dashboard'))

    cert_id    = gen_cert_id()
    created_at = datetime.now().strftime('%B %d, %Y')
    fmt_date   = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')

    conn = get_db()
    conn.execute(
        'INSERT INTO certificates VALUES (?, ?, ?, ?, ?, ?)',
        (cert_id, name, course, event, fmt_date, created_at),
    )
    conn.commit()
    cert = conn.execute(
        'SELECT * FROM certificates WHERE id = ?', (cert_id,)
    ).fetchone()
    conn.close()

    base_url = request.host_url.rstrip('/')
    make_pdf(cert, cert_id, base_url)

    return redirect(url_for('view_cert', cert_id=cert_id))


@app.route('/certificate/<cert_id>')
@admin_required
def view_cert(cert_id):
    conn = get_db()
    cert = conn.execute(
        'SELECT * FROM certificates WHERE id = ?', (cert_id,)
    ).fetchone()
    conn.close()
    if not cert:
        abort(404)
    return render_template('certificate.html', cert=cert)


@app.route('/download/<cert_id>')
@admin_required
def download(cert_id):
    conn = get_db()
    cert = conn.execute(
        'SELECT * FROM certificates WHERE id = ?', (cert_id,)
    ).fetchone()
    conn.close()
    if not cert:
        abort(404)
    pdf_path = os.path.join(CERTIFICATES_DIR, f"{cert_id}.pdf")
    if not os.path.exists(pdf_path):
        base_url = request.host_url.rstrip('/')
        make_pdf(cert, cert_id, base_url)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"NizamCollege_Certificate_{cert_id}.pdf",
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
