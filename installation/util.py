import platform

def banner(txt=None, c="#"):
    """prints a banner of the form with a frame of # arround the txt::

      ############################
      # txt
      ############################

    .
    
    :param txt: a text message to be printed
    :type txt: string
    :param c: thecharacter used instead of c
    :type c: character 
    """
    print
    print "#", 70 * c
    print "#", txt
    print "#", 70 * c


def get_system():
    if is_ubuntu():
        return "ubuntu"
    elif is_centos():
        return "centos"
    elif is_osx():
        return"osx"
    else:
        return "unsupported"
    
    
def is_ubuntu():
    """test sif the platform is ubuntu"""
    (dist, version, release) = platform.dist()
    if dist == "ubuntu" and version != "14.04":
        print "Warning: %s %s is not tested" % (dist, version)
    return dist == 'Ubuntu'

def is_centos():
    """test if the platform is centos"""
    (dist, version, release) = platform.dist()
    if dist == "centos" and version != "6.5":
        print "Warning: %s %s is not tested" % (dist, version)
    return dist == "centos"

def is_osx():
    osx = platform.system().lower() == 'darwin'
    if osx:
        os_version = platform.mac_ver()[0]
        if os_version != '10.9.2':
            osx = False
            print "Warning: %s %s is not tested" % ('OSX', os_version)
    return osx

