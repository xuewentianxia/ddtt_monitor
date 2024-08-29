import subprocess
import platform


class NetworkHelper:

    def __init__(self):
        pass

    def check_ping_ok(self, host_ip: str) -> bool:
        try:
            option = 'n' if platform.system().lower() == "windows" else 'c'
            output = subprocess.check_output(
                f'ping -{option} 1 {host_ip}',
                shell=True
            )
            ping_status = True
        except Exception:
            ping_status = False

        return ping_status

    def ping_ok(self, ip: str) -> bool:
        p = subprocess.Popen(f'ping {ip}', stdout=subprocess.PIPE)
        # the stdout=subprocess.PIPE will hide the output of the ping command
        p.wait()
        status = p.poll() == 0

        return status
