import sys, getopt
from config import Config
from handler import Handler

# Provided callback for provisioning method feedback.
def callback(payload):
    print(payload)

def run_provisioning(argv):
    config = Config()
    opts, args = getopt.getopt(argv,"he:p:s:n:t:",["endPoint=", "templateName=","serialNumber=","thingName=","topic="])
    for opt, arg in opts:
      if opt == '-h':
         print ('main.py -e <endPoint> -p <templateName> -s <serialNumber> -n <thingName> -t <topic>')
         sys.exit()
      elif opt in ("-e", "--endPoint"):
         config.endPoint = arg
      elif opt in ("-p", "--templateName"):
         config.templateName = arg
      elif opt in ("-s", "--serialNumber"):
         config.serialNumber = arg
      elif opt in ("-n", "--thingName"):
         config.thingName = arg
      elif opt in ("-t", "--topic"):
         config.topicName = arg
    print("provisioning device with info {} ...".format(config.get_info()))
    provisioner = Handler(config)
    #Check for availability of bootstrap cert 
    try:
        with open(config.certFilepath) as f:
            provisioner.get_official_certs(callback)

    except IOError:
        print("### Bootstrap cert non-existent. Official cert may already be in place.")
    
if __name__ == "__main__":
    run_provisioning(sys.argv[1:])

    

		
	