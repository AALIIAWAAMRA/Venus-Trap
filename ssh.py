# ==================ssh honyport logiuqe===================
# we need to build a function to : 
   #log username passwd and IP address
   # emulate a small shell 
   # handel client connections & handel ssh hanshake 


import logging
import socket
import paramiko
import threading



logging_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ssh_logger = logging.getLogger("ssh_logger")
ssh_logger.setLevel(logging.INFO)
from logging.handlers import RotatingFileHandler
ssh_handler = RotatingFileHandler("./logs/ssh.log", maxBytes=5*1024*1024, backupCount=2)   # 5 MB per file 2 backups so make sure that this paramter fit your prefernces
ssh_handler.setFormatter(logging_format)
ssh_logger.addHandler(ssh_handler)

cmnd_logger = logging.getLogger("ssh_cmd_logger")
cmnd_logger.setLevel(logging.INFO)
cmnd_handler = RotatingFileHandler("./logs/cmd_ssh.log", maxBytes=5*1024*1024, backupCount=2)   # 5 MB per file 2 backups so make sure that this paramter fit your prefernces
cmnd_handler.setFormatter(logging_format)
cmnd_logger.addHandler(cmnd_handler)


def fake_shell(channel,client_ip):
   channel.send(b"user@rhel:~$ ")
   commande = b""
   while True:
      char = channel.recv(1)
      channel.send(char)
      if not char :
         channel.close()
         # break
      commande += char
      
      
      # if char == b"\r":
      #    if commande.strip() == b"exit":
      #       response = b"logout\r\n"
      #       channel.close()
      #    elif commande.strip() == b"pwd":
      #       response = b"/home/user\r\n" 
      #    elif commande.strip() == b"whoami":
      #       response = b"user\r\n"
      #    elif commande.strip() == b"ls":
      #       response = b"file1.txt  file2.txt  secret.doc\r\n"
      #    elif commande.strip().startswith(b"cat "):
      #       filename = commande.strip().split(b" ")[1]
      #       if filename == b"secret.doc":
      #          response = b"Top Secret Document Content\r\n"
      #       if filename in [b"file1.txt", b"file2.txt"]:
      #          response = filename + b" content\r\n"  
      #       else:
      #          response = b"cat: " + filename + b": No such file or directory\r\n"
      #    else:
      #       response = b"bash: " + commande.strip() + b": command not found\r\n"
      # cmnd_logger.info(f"Command from {client_ip}: {commande.strip().decode('utf-8', errors='ignore')}")
      # channel.send(response)
      # channel.send(b"user@rhel:~$ ")
      # commande = b""
      
      if char == b"\r":
         command = commande.strip()

         cmnd_logger.info(
            f"Command from {client_ip}: {command.decode(errors='ignore')}"
         )

         if command == b"exit":
            channel.send(b"logout\r\n")
            break
         elif command == b"pwd":
            channel.send(b"/home/user\r\n")
         elif command == b"whoami":
            channel.send(b"user\r\n")
         elif command == b"ls":
            channel.send(b"file1.txt  file2.txt  secret.doc\r\n")
         else:
            channel.send(b"bash: command not found\r\n")

         channel.send(b"user@rhel:~$ ")
         commande = b""

      
      
      
class Server(paramiko.ServerInterface):
   def __init__(self,client_ip,input_username=None,input_password=None):
      self.event = threading.Event()
      self.client_ip = client_ip
      self.input_username = input_username
      self.input_password = input_password 
   def check_channel_request(self, kind: str, chanid: int):  # this a callback function from paramiko is call it when the client  secsefullly authenticate and try to open a channel if i return OPEN_SUCCEEDED the channel will be opened if i return any other value the channel will be refused
      if kind == "session":
         ssh_logger.info(
               f"Accepted channel '{kind}' (id={chanid}) from {self.client_ip}"
         )
         return paramiko.OPEN_SUCCEEDED
      else:
         ssh_logger.warning( 
               f"Rejected channel '{kind}' from {self.client_ip}" # i reject any channel that is not from the type session example X11 , direct-tcpip
         )
         return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
   def get_allowed_auths(self,username): 
      ssh_logger.info(
        f"Authentication methods requested for user '{username}' from IP: {self.client_ip}")
      return "password"
   def check_auth_password(self, username, password):
      ssh_logger.info(f'client{self.client_ip} attepted connection with ' + f'username: {username}' f'password: {password}')
      cmnd_logger.info(f'{self.client_ip}' + f'{username}' f'{password}')
      # it 's good to set a loop that give the first 10 attempt  with false and then with true to make the honeypot more realistic
      if self.input_username is not None and self.input_password is not None : #i will improve this coindition later to handel more auth methods
         if username == self.input_username and password ==  self.input_password :
            ssh_logger.info(f"Successful login - Username: {username}, Password: {password}, IP: {self.client_ip}")
            return paramiko.AUTH_SUCCESSFUL
         else:
            ssh_logger.info(f"Failed login attempt - Username: {username}, Password: {password}, IP: {self.client_ip}")
            return paramiko.AUTH_FAILED
      else :
         ssh_logger.info(f"Failed login attempt - Username: {username}, Password: {password}, IP: {self.client_ip}")
         return paramiko.AUTH_FAILED
   def check_channel_shell_request(self, channel):  # this a callback function from paramiko is call it when the client  secsefullly authenticate and open a channel from the type chanell and know he send shell request if i return true there is  a shell if return false  there is no shell
      if channel is None:
        ssh_logger.warning(
            f"Shell request rejected (no channel) from IP: {self.client_ip}")
        return False
      ssh_logger.info(
        f"Shell request accepted on channel {channel.get_id()} "
        f"from IP: {self.client_ip}")
      self.event.set()
      return True
   def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes): #also a callback fucation from paramiko is call it when the client  secsefullly authenticate and open a channel from the type chanell and know he send pty request if i return true there is  a pty if return false  there is no pty and it will be exute after the shell request
      if channel is None:
        ssh_logger.warning(
            f"PTY request rejected (no channel) from IP: {self.client_ip}")
        return False

      ssh_logger.info(
        f"PTY request accepted | "
        f"Term={term}, Size={width}x{height}, "
        f"IP={self.client_ip}")
      return True
   def check_channel_exec_request(self, channel, command): #also a callback fucation from paramiko is call it when the client  secsefullly authenticate and open a channel from the type chanell and know he send exec request if i return true there is  a exec if return false  there is no exec and it can exute before  the pty request because will not open any terminal
      # command = str(commannd) is wrong becuse the commande in bytes so  the resalt is "b'ls'"
      try:
        command = command.decode("utf-8", errors="ignore")
      except Exception:
        command = "<decode error>"

      ssh_logger.info(
        f"EXEC request received | "
        f"Command='{command}' | "
        f"IP={self.client_ip}")
      # Honeypot behavior: allow exec but fake execution
      self.exec_command = command
      # self.event.set()
      return True


def  establish_conn(client,addr,username,passwd): #the brain that handel all ssh connections
   client_ip = addr[0]
   print(f"[+] Connection from {client_ip}")
   try : 
      transport = paramiko.Transport(client) # is the hole ssh transport layer that handel the ssh hanshake and encryption also the authontecation
      SSH_BANNER = "SSH-2.0-OpenSSH_7.4"
      transport.local_version = SSH_BANNER
      server = Server(client_ip=client_ip,input_username=username,input_password=passwd)
      # host_key = "server.key" 
      host_key = paramiko.RSAKey(filename="server.key")  # load the server private key
      transport.add_server_key(host_key)
      
      # in the new version of Open is very strict you need to specify the ciphers and macs that you want to use otherwise the connection will fail
      sec = transport.get_security_options()

      sec.ciphers = (
         'aes128-ctr',
         'aes192-ctr',
         'aes256-ctr'
      )

      sec.digests = (
         'hmac-sha2-256',
         'hmac-sha2-512'
      )

      transport.start_server(server=server)
      
      channel =  transport.accept(100)# wait 100 seconds for the client to request  a channel for to be open if the client not request a channel in this time the channel will be closed
      
      if channel is None :
         ssh_logger.warning(f"No channel request from IP: {client_ip}")
         
      standred_banner = b"Welcome to RHEL 10.04.6 LTS(Nidhal Lahcen)"
      channel.send(standred_banner)
      fake_shell(channel,client_ip)
      
   except Exception as e: 
      ssh_logger.error(f"Exception for IP {client_ip}: {str(e)}")
      print(f"[-] Exception for IP {client_ip}: {str(e)}")
      
   finally :
      
      try :
         transport.close()
         ssh_logger.info(f"Connection closed for IP: {client_ip}")
         
      except :
         ssh_logger.error(f"Error closing connection for IP: {client_ip}")
         print(f"[-] Error closing connection for IP: {client_ip}")
         
      client.close()
         
      
def main (address, port, username,password):
   #hi devs ^_^  paramiko.Transport is layer 7 and socket is layer 4 so we need to create a socket first to listen for incoming connections then we will pass the accepted connections to paramiko transport to handel the ssh hanshake and authontecation sounds great *_^
   socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # ipv4 , tcp
   socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   socks.bind((address,port)) 
   
   socks.listen(100) # max 100 connections in the waiting queue
   print(f"[+] SSH Honeypot listening on {address}:{port}") 
   
   
   while True :  
      try : 
         client,addr = socks.accept()  # client is a new socket object (TCP connection ) to handel the connection with the client and addr is a tuple (ip,port)
         ssh_honypoet_thread = threading.Thread(target=establish_conn, args=(client,addr,username,password)) #this will be create eachthread and the trhrea call the client_handler function and pass the arguments for here
         ssh_honypoet_thread.start()
      except Exception as e:
         ssh_logger.error(f"Exception in main loop: {str(e)}")
         print(f"[-] Exception in main loop: {str(e)}")
         
         
