"""Utils functions are created here for settings files."""
import socket


def get_ip_address(ec2_instance_ip):
    """Returns ip address of the local machine if it has internet access.

    :param ec2_instance_ip: The local ip address used for an ec2 instance to
        gain internet access
    :type ec2_instance_ip: str
    :return: The ip addressed of the local socket for internet access
    :rtype: str
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((ec2_instance_ip, 80))
        ip_address = s.getsockname()[0]
    except OSError:
        ip_address = "localhost"
    return ip_address
