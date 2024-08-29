import time
import json
from typing import List
from pathlib import Path
from datetime import datetime

from common.network_adaptors import get_adaptors
from common.udp import UdpHelper
from common.sftp import SSHHelper
from common.file_helper import poll_files
from common.logger import logger


class Leader:

    def __init__(self):
        self.last_file_path = None
        self.error_bits_log_mapping = {}
        # Log.configure()
        self.dut_connection, self.dut_params = self.__get_dut_connection_params()

    def poll_system_log(self):
        message = None
        adaptors = get_adaptors()
        for key, address in adaptors.items():
            logger.info(f'polling {key}: {address}')
            host_address = address, 51000
            udp = UdpHelper(*host_address)
            try:
                udp.send_to('test')
                message = udp.receive_from(1024)
            except Exception as e:
                logger.error(e)
                # message = None
            finally:
                udp.close()
            logger.info(f'message: {message} in host_address: {host_address} for {key}')
            if message:
                return host_address

    def poll_system_log_files(self, log_dir: str, error_bits: List[str], demo: bool = False):
        last_latest_file = ''
        while True:
            try:
                latest_file = poll_files(log_dir)
                logger.info(f'polling the latest log file {latest_file}')
                if not latest_file:
                    continue
                with open(latest_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    found_map = {
                        error_bit: True for line in lines
                        for error_bit in error_bits
                        if f'ErrorBits = {error_bit}' in line
                    }
                if any(found_map.values()):
                    current_datetime = datetime.now().strftime('%Y%m%dT%H:%M:%S')
                    if last_latest_file != latest_file:
                        self.error_bits_log_mapping.update(
                            {
                                current_datetime: (
                                    [key for key in found_map if found_map[key]], latest_file
                                )
                            }
                        )
                    self.capture_runtime_log() if not demo else ...
                    logger.info(f'finish to capture runtime log with error bits map {found_map}')
                    # return latest_file
                last_latest_file = latest_file
                logger.info(f'not find error bits {error_bits}')
            except SystemExit as e:
                logger.error(e)
                break
            except Exception as e:
                logger.error(e)
                raise

    def capture_runtime_log(self):
        ssh_helper = SSHHelper()
        ssh_helper.connect(
            self.dut_connection['master_ip'],
            22,
            self.dut_connection['username'],
            self.dut_connection['password']
        )
        current_datetime = datetime.now().strftime('%Y%m%dT%H%M%S')
        log_file_name = f'log_{current_datetime}.zip'
        ssh_helper.run(f'cssShell.sh log -az {log_file_name}')
        time.sleep(5)
        remote_log_path = f'/run/{log_file_name}.zip'
        interval = 0
        start_time = time.time()
        while not ssh_helper.is_remote_path_exists(remote_log_path) and interval < 300:
            logger.info(f'waiting for {log_file_name}')
            time.sleep(2)
            interval = time.time() - start_time
        if interval >= 300:
            logger.info(f'{remote_log_path} does not generate successfully!')
        runtime_logs_path = Path('runtime_logs')
        if not runtime_logs_path.exists():
            runtime_logs_path.mkdir(exist_ok=True)
        ssh_helper.get(f'runtime_logs/{log_file_name}', remote_log_path)
        ssh_helper.close()

    def __get_dut_connection_params(self):
        with open(Path('./config/setting.json'), 'r', encoding='utf-8') as f:
            setting = json.load(f)
            dut_connection = setting.get('dut_connection')
            dut_params = setting.get('dut_params')
        # json.dump(setting, f)

        return dut_connection, dut_params


# if __name__ == '__main__':
#     leader = Leader()
#     leader.capture_runtime_log()
