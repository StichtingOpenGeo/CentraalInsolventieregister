#!python
#!/usr/bin/python
"""
CIR python example
"""

import logging
import random
import string
import configparser
import os.path
import sys

# from suds import MethodNotFound
from suds.client import Client
from suds.wsse import Security, UsernameToken
from suds.sax.element import Element
from suds.sax.attribute import Attribute
from suds.xsd.sxbasic import Import

WEBSERVICE_URL = 'http://webservice.rechtspraak.nl/cir.asmx'
NS_WSA = ('wsa', 'http://schemas.xmlsoap.org/ws/2004/08/addressing')
MUST_UNDERSTAND = Attribute('SOAP-ENV:mustUnderstand', 'true')

if not os.path.isfile('credentials.ini'):

    msg = ('First create or request credentials at',
           ':\nhttps://www.rechtspraak.nl/Uitspraken-en-Registers/centraal-insolventieregister/Pages/Aanvraag-Autorisatie.aspx'
    )
    print(msg)
    sys.exit(-1)

Config = configparser.ConfigParser()
Config.read("credentials.ini")

USERNAME = Config.get('Login', 'Username')
PASSWORD = Config.get('Login', 'Password')


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)

    client = Client('%s?wsdl' % WEBSERVICE_URL)

    add_security(client, USERNAME, PASSWORD)
    add_addressing(client, WEBSERVICE_URL)

    # method = client.service.GetLastUpdate()
    # method = client.service.searchModifiedSince("2021-05-01T00:00:00")
    # client.service.searchByDate("2014-07-14T00:00:00", "01", "Uitspraken faillissement")

    method = get_method(client, 'GetLastUpdate')
    # 2021-05-31
    # method = client.service.searchModifiedSince("2021-05-30T00:00:00")

    print(method())


def add_security(client, user, passwd):
    sec = Security()
    token = UsernameToken(user, passwd)
    token.setnonce()
    # token.setcreated()
    sec.tokens.append(token)
    client.set_options(wsse=sec)


def add_addressing(client, webservice_url):
    headers = []

    addr = Element('Address', ns=NS_WSA).setText('http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous')

    headers.append(Element('Element').addPrefix(p='SOAP-ENC', u='http://www.w3.org/2003/05/soap-encoding'))
    headers.append(Element('ReplyTo', ns=NS_WSA).insert(addr).append(MUST_UNDERSTAND))
    headers.append(Element('To', ns=NS_WSA).setText(webservice_url).append(MUST_UNDERSTAND))
    headers.append(addr)
    headers.append(Element('MessageID', ns=NS_WSA).setText('urn:uuid:%s' % generate_messageid()))

    client.set_options(soapheaders=headers)


def get_method(client, method):
    try:
        m = getattr(client.service, method)
        action = client.wsdl.services[0].ports[0].methods[method].soap.action
        action = action.replace('"', '')
    except(Exception):
        print(Exception)
        return None

    action_header = Element('Action', ns=NS_WSA).setText(action)
    client.options.soapheaders.append(action_header)

    return m


def generate_messageid():
    fmt = 'xxxxxxxx-xxxxx'
    resp = ''

    for c in fmt:
        if c == '-':
            resp += c
        else:
            resp += string.hexdigits[random.randrange(16)]

    return resp

if __name__ == '__main__':
    main()
