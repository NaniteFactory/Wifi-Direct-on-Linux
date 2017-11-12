import os
import time


def setup_conf_files():
    '''start_as_go를 위한 설정파일들 생성

    :return: None
    '''
    dir = os.path.dirname(__file__) + '/conf/'  # 설정파일들 넣어둠
    _copy_file_no_overwriting(os.path.abspath(dir + 'dhcpd.conf'), os.path.abspath('/etc/dhcp/dhcpd.conf'))
    _copy_file_no_overwriting(os.path.abspath(dir + 'udhcpd.conf'), os.path.abspath('/etc/udhcpd.conf'))
    _copy_file_no_overwriting(os.path.abspath(dir + 'wpa_supplicant.conf'), os.path.abspath('/etc/wpa_supplicant.conf'))


def _copy_file_no_overwriting(src, dst):
    import shutil
    if not os.path.isfile(dst):
        print('copying... ', dst)
        shutil.copyfile(src, dst)


def _system_critical(command):
    if os.system(command) is not 0:
        raise ConnectionError('wifi direct 연결 실패')


def start_as_go_fedora(str_interface='wls35u1', str_static_ip_addr_for_p2p='192.168.1.2'):
    """Wifi direct 연결을 GO로 시작하기 (페도라 26에서 테스트함)
    1. dhcpd(dhcp 서버) 종료하고 wifi 인터페이스 내림 (인터페이스를 내리는 데에 시간이 걸리기 때문에 몇 초 대기함)
    2. wifi p2p(direct) 인터페이스 생성
    3. dhcpd(dhcp 서버) 시동하며 p2p 연결 대기

    :param str_interface: 와이파이 인터페이스명
    :param str_static_ip_addr_for_p2p: GO에게 정적 할당하는 IP 주소
    :return: None
    """
    os.system('sudo killall dhcpd')  # dhcpd 종료
    os.system('sudo wpa_cli -i ' + str_interface + ' terminate -B')  # 인터페이스 내림
    # os.system('sudo wpa_cli -i p2p-' + str_interface + '-0 terminate -B')
    time.sleep(2)  # 인터페이스가 내려갈 때까지 대기
    os.system('echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward')  # ip 패킷 포워딩 활성화
    # os.system('echo "ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1" | sudo tee /etc/wpa_supplicant.conf')
    _system_critical('sudo wpa_supplicant -d -Dnl80211 -c /etc/wpa_supplicant.conf -i' + str_interface + ' -B')  # 인터페이스 올림
    _system_critical('sudo wpa_cli -i' + str_interface + ' p2p_group_add')
    # p2p_group_add: Become an autonomous GO (p2p 인터페이스 생성)
    _system_critical('sudo ifconfig p2p-' + str_interface + '-0 ' + str_static_ip_addr_for_p2p)  # p2p 인터페이스에 정적 ip 할당
    _system_critical('sudo wpa_cli -i p2p-' + str_interface + '-0 p2p_find')  # p2p_find: Enables discovery
    os.system('sudo wpa_cli -ip2p-' + str_interface + '-0 p2p_peers')
    # p2p_peers: Shows list of discovered peers (not necessary)
    _system_critical('sudo wpa_cli -ip2p-' + str_interface + '-0 wps_pbc')
    # wps_pbc: pushbutton for GO WPS authorization to accept incoming connections (When devices try to connect to GO)
    _system_critical('sudo dhcpd')  # dhcpd 실행


def start_as_go_ubuntu(str_interface='wlan0', str_static_ip_addr_for_p2p='192.168.1.2'):
    """Wifi direct 연결을 GO로 시작하기 (우분투 16.04에서 테스트함)
    페도라와 동일. 우분투에서는 dhcpd 대신 비지박스 툴인 udhcpd 사용함.

    :param str_interface: 와이파이 인터페이스명
    :param str_static_ip_addr_for_p2p: GO에게 정적 할당하는 IP 주소
    :return: None
    """
    os.system('sudo killall udhcpd')
    os.system('sudo wpa_cli -i ' + str_interface + ' terminate -B')
    # os.system('sudo wpa_cli -i p2p-' + str_interface + '-0 terminate -B')
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

