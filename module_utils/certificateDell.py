"""
certificateDell module
This module uses swagger ecs api and sign,revoke and check a Dell certificate using CSR file or using a DNS name.
API Documentation: https://sro.onecloud.dell.com/sites/CYB/CD/_layouts/15/WopiFrame.aspx?sourcedoc=%7B4256F605-154A-4A1C-89E0-FD56CC263015%7D&file=SRO-ECS-API.pdf&action=default

Authorization:
    - Windows Authentication

Implemented methods:
    - SubmitCSR
    - RevokeCertificate
    - GetExpiringCertificates

"""

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
import os
import secrets
import string
import json
# from OpenSSL import crypto
# from OpenSSL.crypto import load_certificate_request, FILETYPE_PEM

class ecsAPIDell:

    #Initiate constructor with application information needed and windows authentication to the swagger api
    def __init__(self,app_name,app_id,group_email,requester_name,requester_email,manager_name,manager_email,win_auth_user,win_auth_pass):
        self.swagger_url = "https://ecsapi.dell.com/v1/"
        self.app_name = app_name 
        self.app_id = app_id 
        self.group_email = group_email 
        self.requester_name = requester_name 
        self.requester_email = requester_email 
        self.manager_name = manager_name 
        self.manager_email = manager_email 
        self.header= {
            'Content-type':'application/json', 
            'Accept':'application/json'
            }
        
        self.auth = HTTPBasicAuth(win_auth_user, win_auth_pass)

    #Revoke certificate
    #r_code (1,3,4,5):
    #1 keyCompromise: is used in revoking an end-entity certificate; it indicates that it is known or suspected that the subject's private key, or other aspects of the subject validated in the certificate, have been compromised.
    #3 affiliationChanged indicates that the subject's name or other information in the certificate has been modified but there is no cause to suspect that the private key has been compromised.
    #4 superseded indicates that the certificate has been superseded (i.e. a new certificate has been requested to replace the one being revoked) but there is no cause to suspect that the private key has been compromised.
    #5 cessationOfOperation indicates that the certificate is no longer needed for the purpose for which it was issued but there is no cause to suspect that the private key has been compromised.
    def revokeCertificate(self,serial_number,r_code,r_msg):
        api_call = "RevokeCertificate"
        JSON_body = {
            "certificateSerialNumber": serial_number,
            "revokeReasonCode": r_code,
            "revokeComment": r_msg
            }

        try: 
            response  = requests.request("POST", self.swagger_url + api_call, 
                                                 headers=self.header,
                                                 json=JSON_body,
                                                 verify=False,
                                                 auth=self.auth)

            return (response.text) 

        except HTTPError as http_err:
            return("HTTP Error:", http_err)
        except Exception as err:
            return("Error:", err)

    #Inform numbers of days to expire a certificate
    def getExpiringCertificates(self,daystillexperation):

        api_call = "GetExpiringCertificates"
        params = {'DaysTillExperation': daystillexperation}

        try:
            response = requests.request("GET",self.swagger_url + api_call,
                                              headers=self.header,
                                              params=params,
                                              verify=False,
                                              auth=self.auth)
            
            return(response.text)

        except HTTPError as http_err:
            return("HTTP Error:", http_err)
        except Exception as err:
            return("Error:", err)

    #generate random password with special character
    def generateKey(self):
        special_character = '#$!%&=+-'
        alphabet = string.ascii_letters + string.digits + special_character
        password = ''.join(secrets.choice(alphabet) for i in range(20))   
    
        return password

    #generate certificate from existing CSR file
    def generateCertFromCSRFile(self,csr_file):
        with open(csr_file, 'rb') as fh:
            csr_data = fh.read()
        self.CSR = x509.load_pem_x509_csr(bytes(csr_data), default_backend())
        self.COMMON_NAME = str(self.CSR.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)
        # self.req = load_certificate_request(FILETYPE_PEM, csr_file)
        # self.req.add_extensions([crypto.X509Extension(b'subjectAltName', False, self.COMMON_NAME.encode())])
        # print(self.req)
        self.submitCSR()

    #generate a new certificate from a DNS name
    def generateCertFromDNS(self,*args):
        self.CSR = None
        self.COUNTRY_NAME='US'
        self.STATE_OR_PROVINCE_NAME = 'TX'
        self.LOCALITY_NAME = "Austin"
        self.ORGANIZATION_NAME = "Dell Technologies"
        self.COMMON_NAME = args[0] 
        self.SUBJECT_ALTERNATIVE_NAME = []
        for dns in args:
            self.SUBJECT_ALTERNATIVE_NAME.append(dns)
        self.submitCSR()

    def submitCSR(self):
        api_call = "SubmitCSR"
        #generate private key and certificate passwords
        home_dir = str(os.getcwd()) + "/certs/" + self.COMMON_NAME + "/"
        if not os.path.isdir(home_dir):
            os.makedirs(home_dir)
        #setting file locations
        PrivateKeyFilePath = home_dir + self.COMMON_NAME + "-privatekey.pem"
        CSRFilePath = home_dir +  self.COMMON_NAME + ".csr"
        PFXFilePath = home_dir  + self.COMMON_NAME + ".pfx"
        JSONFilePath = home_dir + self.COMMON_NAME +".json"
        PEMFilePath = home_dir + self.COMMON_NAME +".pem"
        key = None
        JSON_response = None
        pfx_private_key = self.generateKey()
        csr_private_key = self.generateKey()
        try: 
            #in case of not a CSR file, build one 
            if self.CSR is None:
                
                key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=None)

                with open(PrivateKeyFilePath, "wb") as f:
                    f.write(key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.BestAvailableEncryption(str.encode(csr_private_key)),
                ))

                SANs =[]
                for SAN in self.SUBJECT_ALTERNATIVE_NAME:
                    SANs.append(x509.DNSName(SAN))
                    
                csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
                      x509.NameAttribute(NameOID.COUNTRY_NAME,self.COUNTRY_NAME),
                      x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.STATE_OR_PROVINCE_NAME),
                      x509.NameAttribute(NameOID.LOCALITY_NAME,self.LOCALITY_NAME),
                      x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.ORGANIZATION_NAME),
                      x509.NameAttribute(NameOID.COMMON_NAME, self.COMMON_NAME),
                      ])).add_extension(
                      x509.SubjectAlternativeName(SANs),
                      critical=False,).sign(key, hashes.SHA256())

                CSR = csr.public_bytes(serialization.Encoding.PEM)
                with open(CSRFilePath, "wb") as f:
                    f.write(csr.public_bytes(serialization.Encoding.PEM))
            else:
                CSR = self.CSR.public_bytes(serialization.Encoding.PEM)

            JSON_body = {
                "csr": CSR.decode("utf-8"),
                "applicationName": self.app_name,
                "trouxID": self.app_id,
                "groupEmail": self.group_email,
                "requesterName": self.requester_name,
                "requesterEmail": self.requester_email,
                "managerName": self.manager_name,
                "managerEmail": self.manager_email,
                "includeCertficateChain": False
            }

            #submit CSR using windows authentication
            response  = requests.request("POST", self.swagger_url + api_call,
                                                 headers=self.header,
                                                 json=JSON_body,
                                                 verify=False,
                                                 auth=self.auth)

            JSON_response = response.json()

            if self.CSR is None:
                passwords = { 
                    "CSR Private key password": csr_private_key,
                    "PFX Private Key password": pfx_private_key
                }

                JSON_response.update(passwords)

            json_object = json.dumps(JSON_response, indent=4)
            
            # Writing to json details about certificate
            with open(JSONFilePath, "w") as j:
                j.write(json_object)

            Certificate_Information = JSON_response["certificateInformation"]

            certificates = Certificate_Information["certificates"]

            PEM_cert = str.encode(certificates[0])

            #if it is not a CSR, build a .pfx certificate
            if self.CSR is None:
                Return_Cert = x509.load_pem_x509_certificate(PEM_cert)
                Cert_Chain_List =[]
                if len(certificates) > 1:
                    for cert in range(1,len(certificates)):
                        PEM_Cert_Chain = str.encode(certificates[cert])
                        PEM_Cert_Chain_Bytes = x509.load_pem_x509_certificate(PEM_Cert_Chain)
                        Cert_Chain_List.append(PEM_Cert_Chain_Bytes)

                Cert_Name = str.encode(self.COMMON_NAME)
                Cert_Password_Bytes = serialization.BestAvailableEncryption(str.encode(pfx_private_key));    
                certificate_Bytes = pkcs12.serialize_key_and_certificates(Cert_Name,key,Return_Cert,Cert_Chain_List,Cert_Password_Bytes)

                with open(PFXFilePath, "wb") as f:
                    f.write(certificate_Bytes)

            #build PEM certificate
            with open(PEMFilePath, "wb") as f:
                f.write(PEM_cert)
            
            if Certificate_Information["status"] == "Error":
                print ("Error:" + Certificate_Information["message"])
            else:
                print("Certificate issued. Path for generated files: " + home_dir)

        except HTTPError as http_err:
            print("HTTP Error:", http_err)
        except Exception as err:
            print("Error:", err, JSON_response)