__version__ = '1.0.3'
Version = __version__  # for backward compatibility
__all__ = ["Token","LinkhubException"]
from .linkhub import Token, LinkhubException

TokenInstance = Token()

def generateToken(LinkID,SecretKey,ServiceID,AccessID,Scope,forwardIP = None):
    return TokenInstance.get(LinkID,SecretKey,ServiceID,AccessID,Scope,forwardIP)

def getBalance(_Token):
    return TokenInstance.balance(_Token)

def getPartnerBalance(_Token):
    return TokenInstance.partnerBalance(_Token)

def getTime():
    return TokenInstance.getTime()
