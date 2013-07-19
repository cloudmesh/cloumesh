""" run with

nosetests -v --nocapture --nologcapture
nosetests -v  --nocapture test_inventory.py:Test_Inventory.test_06
nosetests -v

"""
from datetime import datetime

from cloudmesh.inventory.resources import Inventory
from cloudmesh.inventory.resources import FabricService
from cloudmesh.inventory.resources import FabricServer
import json
from  pprint import pprint

from cloudmesh.util.util import HEADING


class Test_Inventory:

    # filename = "$HOME/.futuregrid/cloudmesh-new.yaml"

    def setup(self):
        self.inventory = Inventory("nosetest")

    def tearDown(self):
        pass
        # self.inventory.disconnect()

    def test00_disconnect(self):
        HEADING("00 DISCONNECT")
        print "NOT YET IMPLEMENTED"

    def test01_clean(self):
        HEADING("test01_clean")
        self.inventory.clean()

    def test02_add_Service(self):
        HEADING("test02_add_Service")
        now = datetime.now()
        service = FabricService(
            name='Euca',
            date_start=now,
            date_update=now,
            date_stop=now
        )
        self.inventory.save(service)

    def test03_add_Server(self):
        HEADING("test03_add_Server")
        now = datetime.now()
        service = FabricService(
            name='OpenStack',
            date_start=now,
            date_update=now,
            date_stop=now
        )
        self.inventory.save(service)

        server = FabricServer(
            name='Hallo4',
            date_start=now,
            date_update=now,
            date_stop=now,
            services=[service]
        )

        self.inventory.save(server)


    def test05_create(self):
        HEADING("test05_create")
        self.inventory.create(
            "server", "dynamic", "india[9-11].futuregrid.org,india[01-02].futuregrid.org")
        print self.inventory.pprint()
        assert self.inventory.exists("server", "india01.futuregrid.org")

    def test06_loop_print(self):
        HEADING("test06_loop_print")
        for server in self.inventory.servers:
            print server.data

    def test07_exists(self):
        HEADING("test07_exists")
        assert self.inventory.exists(
            "server", "india01.futuregrid.org") is True

    def test08_print(self):
        HEADING("test08_print")
        self.inventory.pprint()

    def test09_count(self):
        HEADING("test09_count")
        print self.inventory.servers.count(), self.inventory.services.count()
        assert (self.inventory.servers.count() == 6) and (
            self.inventory.services.count() == 2)

    def test10_set(self):
        HEADING("test10_set")
        self.inventory.clean()
        self.inventory.create(
            "server",
            "dynamic",
            "india01.futuregrid.org")

        print self.inventory.pprint()
        print self.inventory.exists("server", "india01.futuregrid.org")

        self.inventory.set_service(
            "india01-opensatck",
            "india01.futuregrid.org",
            "openstack")

        self.inventory.pprint()

    def test11_add(self):
        HEADING("test11_add")
        self.inventory.clean()
        self.inventory.create(
            "server",
            "dynamic",
            "india01.futuregrid.org")

        print self.inventory.pprint()
        print self.inventory.exists("server", "india01.futuregrid.org")

        self.inventory.add_service(
            "india01-opensatck",
            "india01.futuregrid.org",
            "openstack")

        self.inventory.pprint()

    def test12_logging(self):
        self.test11_add()
        HEADING("test12_logging")
        s = self.inventory.get("server", "india01.futuregrid.org")[0]
        print s.data
        s.stop()
        s.start()
        s.start()

    def test_category(self):
        self.inventory.clean()
        self.inventory.create("server", "dynamic", "i[1-3]")
        self.inventory.save()

        for server in self.inventory.servers:
            server.subkind = "dynamic"

        server.bad = "bad"
        server.cm_category = ["compute","test"]
        print server.name,server.cm_category
        server.save()


        servers = self.inventory.servers(name="i1")
        for server in servers:
            pprint (server.data)

        print "HALLO"
        pprint (server.__dict__)
        
    #print "MASTER", server.name,server.category    
        #for server in self.inventory.servers:
        #    print server.name, server.category
