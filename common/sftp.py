from paramiko import (
    SSHClient,
    SFTPClient,
    Transport,
    WarningPolicy
)

from .logger import logger


class SSHHelper:
    def __init__(
        self,
    ):
        self.ssh = None
        self.sftp = None
    
    def connect(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str
    ):
        try:
            self.ssh = SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(WarningPolicy())
            self.ssh.connect(hostname, port, username, password, allow_agent=False, look_for_keys=False)
            self.sftp = self.ssh.open_sftp()
        except Exception as e:
            logger.error(e)

    def run(self, command: str):
        _, stdout, _ = self.ssh.exec_command(command, timeout=5)
        result = stdout.read().decode(encoding='utf-8')
        logger.info(f'output {result} after running command: {command}')

    def get(self, local_path: str, remote_path: str):
        self.sftp.get(remote_path, local_path)

    def remove(self, remote_path: str):
        self.sftp.remove(remote_path)

    def is_remote_path_exists(self, remote_path: str):
        try:
            self.sftp.stat(remote_path)
            status = True
        except Exception as e:
            logger.error(e)
            status = False

        return status

    def close(self):
        self.ssh.close()
        self.sftp.close()
        del self.ssh
        del self.sftp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value,  exc_tb):
        self.close()


class SFTPHelper:
    def __init__(self):
        self.sftp = None

    def connect(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str
    ):
        transport = Transport((hostname, port))
        transport.connect(username, password)
        self.sftp = SFTPClient.from_transport(transport)

    def put(self, source_path: str, destination_path: str):
        self.sftp.put(source_path, destination_path)

    def get(self, local_path: str, remote_path: str):
        self.sftp.get(remote_path, local_path)

    def remove(self, remote_path: str):
        self.sftp.remove(remote_path)

    def is_remote_path_exists(self, remote_path: str):
        try:
            self.sftp.stat(remote_path)
            status = True
        except Exception as e:
            logger.error(e)
            status = False

        return status

    def close(self):
        self.sftp.close()
        del self.sftp
