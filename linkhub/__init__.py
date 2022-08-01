__version__ = '1.5.0'
Version = __version__  # for backward compatibility
__all__ = ["Token","LinkhubException"]
from .linkhub import Token, LinkhubException

TokenInstance = Token()

def generateToken(LinkID, SecretKey, ServiceID, AccessID, Scope, forwardIP = None, UseStaticIP=False, UseLocalTimeYN=True, UseGAIP=False):
    return TokenInstance.get(LinkID, SecretKey, ServiceID, AccessID, Scope, forwardIP, UseStaticIP, UseLocalTimeYN, UseGAIP)

def getBalance(_Token, UseStaticIP=False, UseGAIP=False):
    return TokenInstance.balance(_Token, UseStaticIP, UseGAIP)

def getPartnerBalance(_Token, UseStaticIP=False, UseGAIP=False):
    return TokenInstance.partnerBalance(_Token, UseStaticIP, UseGAIP)

def getPartnerURL(_Token, TOGO, UseStaticIP=False, UseGAIP=False):
    return TokenInstance.getPartnerURL(_Token, TOGO, UseStaticIP, UseGAIP)

def getTime(UseStaticIP=False, UseLocalTimeYN=True, UseGAIP=False):
    return TokenInstance.getTime(UseStaticIP, UseLocalTimeYN, UseGAIP)
