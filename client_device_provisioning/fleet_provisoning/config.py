import os

class Config:
    def __init__(self, templateName='robot-gg-server-template', endPoint='', serialNumber='', thingName='', topicName='ros2_mock_telemetry_topic'):
        self.templateName=templateName
        self.endPoint=  endPoint
        self.serialNumber = serialNumber
        self.thingName = thingName
        self.topicName = topicName
        self.claimCertPath=os.path.abspath(os.path.join(os.getcwd(), os.pardir, "claim")) 
        self.certFilepath=os.path.join(self.claimCertPath, "bootstrap-certificate.pem")
        self.privateKeyFilepath=os.path.join(self.claimCertPath, "bootstrap-privateKey.pem")
        self.caFilepath=os.path.join(os.getcwd(), "certs", "root.ca.pem")
       
    def get_info(self):
        return f"{self.endPoint} {self.templateName} {self.serialNumber} {self.thingName} {self.topicName}"