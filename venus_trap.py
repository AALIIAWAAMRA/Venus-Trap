if __name__ == "__main__":
   from ssh import main
   import argparse
   parser = argparse.ArgumentParser(description="SSH Honeypot")

   parser.add_argument('-a','--address',type=str,required=True)
   parser.add_argument('-p','--port',type=int,required=True)
   parser.add_argument('-u','--username',type=str)
   parser.add_argument('-pw','--password',type=str)
   
   parser.add_argument('-s','--ssh',action='store_true',help='Enable SSH Honeypot')
   parser.add_argument('-w','--http',action='store_true',help='Enable HTTP Honeypot')
   
   args = parser.parse_args()

   try : 
      if args.ssh :
         print("[*] Starting SSH Honeypot...")
         main(args.address,args.port,args.username,args.password)
         if not args.username : 
            args.username = "john"
         if not args.password :
            args.password = "123456"
      elif args.http :
         print("[*] Starting HTTP Honeypot...")
         if not args.username : 
            args.username = "admin"
         if not args.password :
            args.password = "admin"
         from web import *
         start_honeypot(args.port ,args.username, args.password)
      else :
         print("[-] Please specify at least one honeypot to start: --ssh or --http")
   except Exception as e:  
      print(f"[-] Exception while parsing arguments: {str(e)}")