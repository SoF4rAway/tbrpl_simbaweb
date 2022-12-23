from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
import os
import tempfile

app =Flask(__name__)

app.secret_key = 'cekson123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dbsibawa'
app.config['UPLOAD_FOLDER'] = 'static/upload'
mysql = MySQL(app)

#login
@app.route('/')
def awal():
    return render_template('Hompage.html')

@app.route('/pilihlogin')
def pilihlogin():
    return render_template('login-pilih.html')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method =='POST':
        nim = request.form['nim']
        nama = request.form['nama']
        dep = request.form['dep']
        fak = request.form['fak']
        jenis_kelamin = request.form['jenis_kelamin']
        email = request.form['email']
        dosPA = request.form['dosPA']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM data_mhs WHERE nim=%s', ([nim]))
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('INSERT INTO data_mhs VALUES (%s, %s, %s, NULL, %s, %s, %s, NULL, %s, %s)', ([nim], nama, jenis_kelamin, dep, fak, email, dosPA, generate_password_hash(password)))
            mysql.connection.commit()
            flash('Registrasi Berhasil', 'success')
            return redirect(url_for('login_mhs'))
        else:
            flash('NIM sudah diregistrasi', 'danger')
    return render_template('signup.html')

@app.route('/login_mhs', methods=('GET', 'POST'))
def login_mhs():
    if request.method == 'POST':
        nim = request.form['nim']
        password = request.form['password']
        
        #cek data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM data_mhs WHERE nim=%s', ([nim]))
        akun = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek NIM Anda','danger')
        elif not check_password_hash(akun[9], password):
            flash('Login gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['nim'] = akun[0]
            session['nama'] = akun[1]
            return redirect(url_for('home_mhs'))
    return render_template('login-mhs.html')

@app.route('/login_dosen', methods=('GET', 'POST'))
def login_dosen():
    if request.method == 'POST':
        nidn = request.form['nidn']
        password = request.form['password']
        
        #cek data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM data_dosen WHERE nidn=%s', ([nidn]))
        akun = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek NIDN Anda','danger')
        elif not check_password_hash(akun[8], password):
            flash('Login gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['nidn'] = akun[0]
            session['nama'] = akun[1]
            return redirect(url_for('home_dosen'))
    return render_template('login-dosen.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('nim', None)
    session.pop('nama', None)
    session.pop('nidn', None)
    return redirect(url_for('awal'))

#laman mahasiswa
@app.route('/home_mhs')
def home_mhs():
    if 'loggedin' in session:
        return render_template('home-mhs.html')
    flash('Harap Login Dahulu', 'danger')
    return redirect(url_for('login_mhs'))


@app.route('/form_mhs', methods=('GET', 'POST'))
def form_mhs():
    if 'loggedin' in session:
        if request.method == 'POST':
            nim = request.form['nim']
            smt = request.form['smt']
            cursor = mysql.connection.cursor()
            if nim != session['nim']:
                flash('Cek Kembali nim anda', 'danger')
            else:
                upload = request.files['upload']
                upload.save(os.path.join(app.config['UPLOAD_FOLDER'], upload.filename))
                loc = str(app.config['UPLOAD_FOLDER'] + "/" + upload.filename)
                cursor.execute('INSERT INTO form_pa VALUES (%s, %s, %s, %s, NULL, NULL)', (session['nim'], smt, upload.filename, loc))
                mysql.connection.commit()
                flash('Upload Berhasil', 'success')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM form_pa WHERE nim=%s', ([session['nim']]))
        form_mhs = cursor.fetchall()
        nama = session['nama']
        nim1 = session['nim']
        return render_template('formPA.html', form_mhs = form_mhs, nama = nama, nim1 = nim1)
    flash('Harap Login Dahulu', 'danger')
    return redirect(url_for('login_mhs'))

@app.route('/persetujuanPA_mhs', methods=('GET','POST'))
def persetujuanPA_mhs():
    if 'loggedin' in session:
        if request.method == 'POST':
            tipe = request.form['tipe']
            upload = request.files['upload']
            upload.save(os.path.join(app.config['UPLOAD_FOLDER'], upload.filename))
            loc = str(app.config['UPLOAD_FOLDER'] + "/" + upload.filename)
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO persetujuan_pa VALUES (%s, %s, %s, %s, NULL, NULL)',([session['nim']], tipe, upload.filename ,loc))
            mysql.connection.commit()
            flash('Upload Berhasil', 'success')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM persetujuan_pa WHERE nim=%s', ([session['nim']]))
        persetujuan_mhs = cursor.fetchall()
        nama = session['nama']
        nim1 = session['nim']
        return render_template('persetujuanPA.html', nama = nama, nim1 = nim1, persetujuan_mhs = persetujuan_mhs)
    flash('Harap Login Dahulu','danger')
    return redirect(url_for('login_mhs'))

@app.route('/sendfileform')
def sendfileform():
    loc = request.args.get('loc')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT form_unsigned FROM form_pa WHERE nim=%s AND form_unsigned_dir=%s', ([session['nim']], loc))
    file = cursor.fetchone()[0]

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    return send_file(file_path, as_attachment=True)

@app.route('/sendfilepers')
def sendfilepers():
    loc = request.args.get('loc')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT file_unsigned FROM persetujuan_pa WHERE nim=%s AND file_signed_dir=%s', ([session['nim']], loc))
    file = cursor.fetchone()[0]
    if file is None:
        flash('File Belum disetujui oleh PA', 'danger')
    else:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        return send_file(file_path, as_attachment=True)

#laman dosen
@app.route('/home_dosen')
def home_dosen():
    if 'loggedin' in session:
        return render_template('homeDosen.html')
    flash('Harap Login Dahulu', 'danger')
    return redirect(url_for('login_dosen'))

if __name__ == '__main__':
    app.run(debug=True)
