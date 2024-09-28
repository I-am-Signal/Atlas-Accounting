from public import create_app
from flask import Flask, render_template,request,jsonify
from flask_mail import Mail, Message


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
