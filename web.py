import logging
from flask import Flask, render_template , request , redirect, url_for


loggin_format = logging.Formatter("%(asctime)s - %(message)s")

web_logger = logging.getLogger("web_logger")
web_logger.setLevel(logging.INFO)
from logging.handlers import RotatingFileHandler
web_handler = RotatingFileHandler("./logs/web.log", maxBytes=5*1024*1024, backupCount=2)   
web_handler.setFormatter(loggin_format)
web_logger.addHandler(web_handler)


def main(input_usernmame = " admin" , input_password = "admin" ):
   
   app = Flask(__name__)
   
   @app.route('/')
   
   def index():
      return render_template('login.html')
   
   @app.route('/submit', methods=['POST'])
   
   def submit ():
      username = request.form['un']
      password = request.form['pw']
      
      web_logger.info(f"Login attempt with Username: {username} | Password: {password} | From IP: {request.remote_addr}")
      
      if username == input_usernmame and password == input_password:
         web_logger.info(f"Successful login for Username: {username} from IP: {request.remote_addr}")
         print(f"[+] Successful login for Username: {username} from IP: {request.remote_addr}")
         return "wooow ^_^ you logged in successfully"
      else:
         web_logger.info(f"Failed login attempt for Username: {username} from IP: {request.remote_addr}")
         print(f"[-] Failed login attempt for Username: {username} from IP: {request.remote_addr}")
         return "wrong creantials *_*"
      
   return app

def start_honeypot(port = 4444 ,input_usernmame = " admin" , input_password = "admin" ):
   my_app = main(input_usernmame , input_password)
   my_app.run(port=port , host='127.0.0.1')
   print(f"[*] Starting HTTP Honeypot on port {port}...")
   
   
   return my_app
   
