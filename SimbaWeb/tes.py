from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import os
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine

app = Flask(__name__)

engine = create_engine("mysql+pymysql://root@localhost/dbsibawa")
connection = engine.connect()
result = connection.execute('SELECT * FROM data_mhs;').fetchall()
for row in result:
    print (result[0])
