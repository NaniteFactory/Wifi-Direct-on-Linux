import os
import time


def _copy_file_no_overwriting(src, dst):
    import shutil
    if not os.path.isfile(dst):
        print('copying... ', dst)
        shutil.copyfile(src, dst)


def setup_conf_files():
    """Setup configuration files that are needed to run start_as_go~().

    :return: None
    """
    dir_ = os.path.dirname(__file__) + '/conf/'  # a directory those .conf files are in
    _copy_file_no_overwriting(os.path.abspath(dir_ + 'dhcpd.conf'), os.path.abspath('/etc/dhcp/dhcpd.conf'))
    _copy_file_no_overwriting(os.path.abspath(dir_ + 'udhcpd.conf'), os.path.abspath('/etc/udhcpd.conf'))
    _copy_file_no_overwriting(os.path.abspath(dir_ + 'wpa_supplicant.conf'), os.path.abspath('/etc/wpa_supplicant.conf'))


def _system_critical(command):
    if os.system(command) is not 0:
        raise ConnectionError('Failed to configure the WiFi Direct')


def start_as_go_fedora(str_interface='wls35u1', str_static_ip_addr_for_p2p='192.168.1.2'):
    """Starts a Wifi direct interface as GO (Tested on Fedora 26)
    1. Destroy dhcpd and a wifi connection. (It usually takes some little time to kill off a wifi thing so wait for couple seconds...)
    2. Bring up a wifi p2p(direct) interface.
    3. Wait for incoming p2p connection of clients, starting dhcpd (dhcpd is a DHCP server).

    :param str_interface: A name of your wifi interface.
    :param str_static_ip_addr_for_p2p: A static ip address to be given to your p2p interface. (This is only for the server(GO). The client should use a DHCP IP.)
    :return: None
    """
    os.system('sudo killall dhcpd')  # kill current dhcpd running if there is any
    os.system('sudo wpa_cli -i ' + str_interface + ' terminate -B')  # this will down your interface
    os.system('sudo wpa_cli -i p2p-' + str_interface + '-0 terminate -B')  # kill p2p interface as well
    time.sleep(2)  # wait for the interface to go down
    os.system('echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward')  # enabling kernel ip forwarding (routing) in Linux
    # os.system('echo "ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1" | sudo tee /etc/wpa_supplicant.conf')
    _system_critical('sudo wpa_supplicant -d -Dnl80211 -c /etc/wpa_supplicant.conf -i' + str_interface + ' -B')  # this brings up an interface
    _system_critical('sudo wpa_cli -i' + str_interface + ' p2p_group_add')
    # p2p_group_add: Become an autonomous GO (this creates a p2p interface)
    _system_critical('sudo ifconfig p2p-' + str_interface + '-0 ' + str_static_ip_addr_for_p2p)  # assign a static ip to your p2p interface
    _system_critical('sudo wpa_cli -i p2p-' + str_interface + '-0 p2p_find')  # p2p_find: Enables discovery
    os.system('sudo wpa_cli -ip2p-' + str_interface + '-0 p2p_peers')
    # p2p_peers: Shows list of discovered peers (not necessary)
    _system_critical('sudo wpa_cli -ip2p-' + str_interface + '-0 wps_pbc')
    # wps_pbc: pushbutton for GO WPS authorization to accept incoming connections (When devices try to connect to GO)
    _system_critical('sudo dhcpd')  # start dhcpd


def start_as_go_ubuntu(str_interface='wlan0', str_static_ip_addr_for_p2p='192.168.1.2'):
    """Starts a Wifi direct interface as GO (Tested on Ubuntu 16.04)
    Mostly same as the one in Fedora, except that Ubuntu uses udhcpd (which is a BusyBox utility) instead of dhcpd.

    :param str_interface: A name of your wifi interface.
    :param str_static_ip_addr_for_p2p: A static ip address to be given to your p2p interface. (This is only for the server(GO). The client should use a DHCP IP.)
    :return: None
    """
    os.system('sudo killall udhcpd')
    os.system('sudo wpa_cli -i ' + str_interface + ' terminate -B')
    os.system('sudo wpa_cli -i p2p-' + str_interface + '-0 terminate -B')
    time.sleep(1)
    os.system('echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward')
    # os.system('echo "ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1" | sudo tee /etc/wpa_supplicant.conf')
    _system_critical('sudo wpa_supplicant -d -Dnl80211 -c /etc/wpa_supplicant.conf -i' + str_interface + ' -B')
    _system_critical('sudo wpa_cli -i' + str_interface + ' p2p_group_add')
    _system_critical('sudo ifconfig p2p-' + str_interface + '-0 ' + str_static_ip_addr_for_p2p)
    _system_critical('sudo wpa_cli -i p2p-' + str_interface + '-0 p2p_find')
    os.system('sudo wpa_cli -ip2p-' + str_interface + '-0 p2p_peers')
    _system_critical('sudo wpa_cli -ip2p-' + str_interface + '-0 wps_pbc')
    _system_critical('sudo udhcpd /etc/udhcpd.conf &')


if __name__ == "__main__":
    # example
    import wifid
    wifid.setup_conf_files()
    try:
        wifid.start_as_go_fedora()
    except ConnectionError:
        print('ConnectionError from wifid')

