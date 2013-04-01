import pickle
from sh import fgrep
from sh import nova
from sh import tail
from datetime import datetime
import json
import sys
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)

# import shelve
from cm_config import cm_config
#from openstack.cm_compute import openstack as os_client

#Error Cannot Import Openstack
from openstack.cm_compute import openstack

from eucalyptus.eucalyptus_new import eucalyptus
from azure.cm_azure import cm_azure as azure 


class cloudmesh:

    ######################################################################
    # global variables that define the information managed by this class
    ######################################################################

    datastore = "data/clouds.txt"

    # dict that holds vms, flavors, images for al iaas
    clouds = {}

    # array with keys from the user
    keys = []

    ######################################################################
    # variables that we can most likely eliminate
    ######################################################################

    # user needs to come from credential ...
    user = "gvonlasz"

    ######################################################################
    # initialization methods
    ######################################################################

    def __init__(self):
        self.clear()
        #Read Yaml File to find all the cloud configurations present
        self.config();

    def clear(self):
        self.clouds = {}
        self.keys = []
        self.user = "gvonlasz"

    ######################################################################
    # the configuration method that must be called to get the cloud info
    ######################################################################

    def config(self):
        """
        reads the cloudmesh yaml file that defines which clouds build
        the cloudmesh
        """

        configuration = cm_config()
        pp.pprint (configuration)

        for cloud_name in configuration.keys():
            print "--------------------"

            try:
                credential = configuration.get(key=cloud_name)
                cloud_type = credential['cm_type']

                print credential
                print ">>>>>>>", cloud_name, cloud_type

                if cloud_type in ['openstack','eucalyptus']:
                    print "AAAAA"
                    self.clouds[cloud_name] = {'cm_type': cloud_type, 'credential': credential}
                    print "BBBB"
                    try:
                        self.clouds[cloud_name] = {'cm_type': cloud_type, 'credential': credential}
                        #self.refresh(cloud_name)
                    except Exception, e:
                        print "ERROR: can not connect to", cloud_name, e
                    print "CCCC"

                    
            except Exception:
              print "ERROR: Not a cloud:", cloud_name
        return

    ######################################################################
    # importnat get methods
    ######################################################################

    def get(self):
        """returns the dict that contains all the information"""
        return self.clouds

    ######################################################################
    # important print methods
    ######################################################################
    # includes sanitizing to remove the credentials
    ######################################################################

    def __str__(self):
        """
        tmp = self._sanitize()
        print tmp
        """

    """
    def _sanitize(self):
        # copy the self.cloud
        # delete the attributes called credential for all clouds

        all_keys =  self.clouds.keys()
        for cloud in all_keys:
            self.clouds[cloud]['credential'] = {}

        return self.clouds
    """

    def dump(self):
        """tmp = self._sanitize()"""
        print json.dumps(tmp, indent=4)

    ######################################################################
    # the refresh method that gets upto date information for cloudmesh
    # If cloudname is provided only that cloud will be refreshed 
    # else all the clouds will be refreshed
    ######################################################################

    def refresh(self, cloud_name=None):
        print "Refershing cloud %s" % cloud_name
        servers = {}        
        cloud =None;
        
        if (cloud_name == None):
            all_clouds = self.clouds.keys()
        else:
            all_clouds = [cloud_name]

        print "CLOUDS", all_clouds

        for cloud_name in all_clouds :
            print "REFRESHING", cloud_name
            try:
                type = self.clouds[cloud_name]['cm_type']
                if type == 'openstack':
                    cloud = openstack(cloud_name)
                elif type == 'eucalyptus':
                    cloud = eucalyptus(cloud_name)
                elif type == 'azure':
                    cloud = azure(cloud_name)
                #cloud.refresh()
                cloud[cloud_name].update({'name': cloud_name,
                                          'cm_type': type})
                self.clouds[cloud_name]['flavors'] = cloud.flavors
                self.clouds[cloud_name]['servers'] = cloud.servers
                self.clouds[cloud_name]['images'] = cloud.images
                
            except Exception, e:
                print e

    def add(self, name, type):
        try:
            self.clouds[name]
            print "Error: Cloud %s already exists" % name
        except:
            self.refresh(name, type)

    """
    def get_keys(self):
        return self.keys

    def refresh_keys(self):
        self.keys = []
        result = fgrep(tail(nova("keypair-list"), "-n", "+4"),"-v","+")
        for line in result:
            (front, name, signature, back) = line.split("|")
            self.keys.append(name.strip())
        return self.keys


    def refresh(self):
        keys = self.refresh_keys()
        for cloud in keys:
            self.refresh(cloud)

        # p = Pool(4)
        # update = self.refresh
        # output = p.map(update, keys)

    """

    ######################################################################
    # saves and reads the dict to and from a file
    ######################################################################
    def save(self):
        tmp = self._sanitize()
        file = open(self.datastore, 'wb')
        # pickle.dump(self.keys, file)
        pickle.dump(tmp, file)
        file.close()

    def load(self):
        file = open(self.datastore, 'rb')
        # self.keys = pickle.load(file)
        self.clouds = pickle.load(file)
        ''' above returns:
        [u'gvonlasz']
         So, call pickle again to get more:
            {'india': {'name': 'india',
            'servers': {u'2731c421-d985-44ce-91bf-2a89ce4ba033': {'cloud': 'india',
            'id': u'2731c421-d985-44ce-91bf-2a89ce4ba033',
            'ip': u'vlan102=10.1.2.85, 149.165.158.7',
            'name': u'gvonlasz-001',
            'refresh': '2013-02-11 20:30:04.472583',
            'status': u'ACTIVE'},
            ...
        '''
        self.clouds = pickle.load(file)
        file.close()

    ######################################################################
    # TODO: convenient +, += functions to add dicts with cm_type
    ######################################################################

    def __add__(self, other):
        """
        type based add function c = cloudmesh(...); b = c + other
        other can be a dict that contains information about the object
        and it will be nicely inserted into the overall cloudmesh dict
        the type will be identified via a cm_type attribute in the
        dict Nn attribute cm_cloud identifies in which cloud the
        element is stored.
        """
        if other.cm_type == "image":
            print "TODO: not implemented yet"
            return
        elif other.cm_type == "vm":
            print "TODO: not implemented yet"
            return
        elif other.cm_type == "flavor":
            print "TODO: not implemented yet"
            return
        elif other.cm_type == "cloudmesh":
            print "TODO: not implemented yet"
            return
        else:
            print "Error: %s type does not exist", cm_type
            print "Error: Ignoring add"
            return

    def __iadd__(self, other):
        """
        type based add function c = cloudmesh(...); c += other other
        can be a dict that contains information about the object and
        it will be nicely inserted into the overall cloudmesh dict the
        type will be identified via a cm_type attribute in the dict.
        Nn attribute cm_cloud identifies in which cloud the element is
        stored.
        """
        if other.cm_type == "image":
            print "TODO: not implemented yet"
            return
        elif other.cm_type == "vm":
            print "TODO: not implemented yet"
            return
        elif other.cm_type == "flavor":
            print "TODO: not implemented yet"
            return
        elif other.cm_type == "cloudmesh":
            print "TODO: not implemented yet"
            return
        else:
            print "Error: %s type does not exist", cm_type
            print "Error: Ignoring add"
            return

##########################################################################
# MAIN METHOD FOR TESTING
##########################################################################

if __name__ == "__main__":

    c = cloudmesh()
    print c.clouds
    """
    c.config()

    c.dump()


    c = cloud_mesh()

    c.refresh()
    c.add('india', 'openstack')
    c.add('sierra', 'openstack')
    c.refresh_keys()
    c.dump()
    c.save()
    print 70 * "-"
    c.clear()
    c.dump()
    print 70 * "-"
    c.load()
    c.dump()
    print 70 * "-"
    """

    """
    india_os = {
        "OS_TENANT_NAME" : '',
        "OS_USERNAME" : '',
        "OS_PASSWORD" : '',
        "OS_AUTH_URL" : '',
        }


    (attribute, passwd) = fgrep("OS_PASSWORD","%s/.futuregrid/openstack/novarc" % os.environ['HOME']).replace("\n","").split("=")

    india_os['OS_PASSWORD'] = passwd



    username = india_os['OS_USERNAME']
    password = india_os['OS_PASSWORD']
    authurl = india_os['OS_AUTH_URL']
    tenant = india_os['OS_TENANT_NAME']

    print password
    '''
    username = os.environ['OS_USERNAME']
    password = os.environ['OS_PASSWORD']
    authurl = os.environ['OS_AUTH_URL']
    '''
    india = cloud_openstack("india", authurl, tenant, username, password)

    india._vm_show("gvonlasz-001")
    india.dump()
    india._vm_show("gvonlasz-001")
    india.dump()
    """
