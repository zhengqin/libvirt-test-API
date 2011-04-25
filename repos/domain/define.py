#!/usr/bin/evn python
"""This test case is used for testing
   define domain from xml
   mandatory arguments:guesttype
                       guestname
   optional arguments: memory
                       vcpu
                       disksize
                       fullimagepath
                       imagetype
                       hdmodel
                       nicmodel
                       macaddr
                       ifacetype
                       source
"""

__author__ = 'Alex Jia: ajia@redhat.com'
__date__ = 'Mon Jan 28, 2010'
__version__ = '0.1.0'
__credits__ = 'Copyright (C) 2009 Red Hat, Inc.'
__all__ = ['usage', 'check_define_domain', 'define']

import os
import re
import sys

def append_path(path):
    """Append root path of package"""
    if path in sys.path:
        pass
    else:
        sys.path.append(path)

pwd = os.getcwd()
result = re.search('(.*)libvirt-test-API', pwd)
append_path(result.group(0))

from lib.Python import connectAPI
from lib.Python import domainAPI
from utils.Python import utils
from utils.Python import xmlbuilder

def usage():
    print '''usage: mandatory arguments:guesttype
                           guestname
       optional arguments: memory
                           vcpu
                           disksize
                           fullimagepath
                           imagetype
                           hdmodel
                           nicmode
                           macaddr
                           ifacetype
                           source
          '''

def check_params(params):
    """Verify inputing parameter dictionary"""
    logger = params['logger']
    keys = ['guestname', 'guesttype']
    for key in keys:
        if key not in params:
            logger.error("%s is required" %key)
            usage()
            return 1
    return 0

def check_define_domain(guestname, guesttype, logger):
    """Check define domain result, if define domain is successful,
       guestname.xml will exist under /etc/libvirt/qemu/
       and can use virt-xml-validate tool to check the file validity
    """
    if "kvm" in guesttype:
        path = "/etc/libvirt/qemu/%s.xml" % guestname
    elif "xen" in guesttype:
        path = "/etc/xen/%s" % guestname
    else:
        logger.error("unknown guest type")
    if os.access(path, os.R_OK):
        return True
    else:
        return False

def define(params):
    """Define a domain from xml"""
    # Initiate and check parameters
    params_check_result = check_params(params)
    if params_check_result:
        return 1
    logger = params['logger']
    guestname = params['guestname']
    guesttype = params['guesttype']
    test_result = False

    # Connect to local hypervisor connection URI
    util = utils.Utils()
    uri = util.get_uri('127.0.0.1')
    conn = connectAPI.ConnectAPI()
    virconn = conn.open(uri)

    # Get capabilities debug info
    caps = conn.get_caps()
    logger.debug(caps)

    # Generate damain xml
    dom_obj = domainAPI.DomainAPI(virconn)
    xml_obj = xmlbuilder.XmlBuilder()
    domain = xml_obj.add_domain(params)
    xml_obj.add_disk(params, domain)
    xml_obj.add_interface(params, domain)
    dom_xml = xml_obj.build_domain(domain)
    logger.debug("domain xml:\n%s" %dom_xml)

    # Define domain from xml
    try:
        dom_obj.define(dom_xml)
        if  check_define_domain(guestname, guesttype, logger):
            logger.info("define a domain form xml is successful")
            test_result = True
        else:
            logger.error("fail to check define domain")
            test_result = False
    except:
        logger.error("fail to define a domain from xml")
        test_result = False
    finally:
        conn.close()
        logger.info("closed hypervisor connection")

    if test_result:
        return 0
    else:
        return 1

def define_clean(params):
    """ clean testing environment """
    pass