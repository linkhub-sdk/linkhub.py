__version__ = '1.3.0'
Version = __version__  # for backward compatibility
__all__ = ["Token","LinkhubException"]
from .linkhub import Token, LinkhubException

TokenInstance = Token()

def generateToken(LinkID, SecretKey, ServiceID, AccessID, Scope, forwardIP = None, UseStaticIP=False, UseLocalTimeYN=True):
    return TokenInstance.get(LinkID, SecretKey, ServiceID, AccessID, Scope, forwardIP, UseStaticIP, UseLocalTimeYN)

def getBalance(_Token, UseStaticIP=False):
    return TokenInstance.balance(_Token, UseStaticIP)

def getPartnerBalance(_Token, UseStaticIP=False):
    return TokenInstance.partnerBalance(_Token, UseStaticIP)

def getPartnerURL(_Token, TOGO, UseStaticIP=False):
    return TokenInstance.getPartnerURL(_Token, TOGO, UseStaticIP)

def getTime(UseStaticIP=False, UseLocalTimeYN=True):
    return TokenInstance.getTime(UseStaticIP, UseLocalTimeYN)
