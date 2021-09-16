# -*- coding: utf-8 -*-
# code for console Encoding difference. Dont' mind on it
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import sys
import imp
imp.reload(sys)
try: sys.setdefaultencoding('UTF8')
except Exception as E: pass

import linkhub
from linkhub import LinkhubException

class LinkhubTokenTestCase(unittest.TestCase):

    def test_setUp(self):
        self.token =  linkhub.generateToken('TESTER','SwWxqU+0TErBXy/9TVjIPEnI0VTUMMSQZtJf3Ed8q3I=','POPBILL_TEST','1234567890',['member','110'], "", True, False, False)
        print(self.token)

    # def test_checkToken(self):
    #     self.assertEqual(self.token.serviceID,"POPBILL_TEST","서비스아이디 불일치")

    # def test_getBalance(self):
    #     balance = linkhub.getBalance(self.token,True)
    #     self.assertGreaterEqual(balance,0,'잔액 0 이상.')

    # def test_getPartnerBalance(self):
    #     balance = linkhub.getPartnerBalance(self.token,True)
    #     self.assertGreaterEqual(balance,0,'잔액 0 이상.')

    # def test_getTime(self):
    #     time = linkhub.getTime(True, False)
    #     print(time)

    # def test_getPartnerURL(self):
    #     try :
    #         url = linkhub.getPartnerURL(self.token, "CHRG",True)
    #         print url
    #     except Exception as e :
    #         print(e.code)
    #         print(e.message)

if __name__ == '__main__':
    unittest.main()
