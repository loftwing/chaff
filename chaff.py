import subprocess
import random
import os
import asyncio
import json
from datetime import datetime
import logging


class PortManager:
    def __init__(self, ports, stealth_port_path):
        self.ports = ports
        self.stealth_port_path = stealth_port_path

    async def spawn_stealth_port(self, port):
        while True:
            logging.info(f'[stealth] => START on {port}/tcp')
            try:
                proc = await asyncio.create_subprocess_exec(self.stealth_port_path, str(port), **subprocess_args())
                stdout, stderr = await proc.communicate()
                line = stdout.decode('ascii').rstrip()
                logging.info(f'[stealth] => {line}')
                parsed_line = json.loads(line)
                if parsed_line["returntype"] == 'con':
                    log_line = f'{datetime.now()}\t{parsed_line["ip"]}\t{parsed_line["port"]}\n'
                    with open('C:\\chaff\\chaff.log', 'a+') as f:
                        f.write(log_line)
                        f.flush()

            except Exception as e:
                logging.error(f'[stealth] =!> except: {e}')

            await asyncio.sleep(60)

    async def spawn_normal_port(self, port):
        try:
            logging.info(f'[normal] => START on {port}/tcp')
            await asyncio.start_server(cb_send_msg, '0.0.0.0', port)

        except Exception as e:
            logging.error(f'[normal] =!> except: {e}')

    def start(self):
        random.shuffle(self.ports)

        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        tasks = [
            asyncio.ensure_future(self.spawn_stealth_port(self.ports[0])),
            asyncio.ensure_future(self.spawn_normal_port(self.ports[1])),
        ]

        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()


async def cb_send_msg(_reader, writer):
    _sock_bind_addr, sock_port = writer.get_extra_info('sockname')
    sock_peer_addr, _sock_peer_port = writer.get_extra_info('peername')
    print(f'[normal] => {sock_peer_addr} | {sock_port}')

    try:
        log_line = f'{datetime.now()}\t{sock_peer_addr}\t{sock_port}\n'
        with open('C:\\chaff\\chaff.log', 'a+') as f:
            f.write(log_line)
            f.flush()
        writer.write(b'nice, my dude')
        await writer.drain()
        writer.close()
    except ConnectionResetError:
        logging.info(f'[normal] => ECONNRESET')
    except OSError as e:
        logging.info(f'[normal] =!> OSError: {e}')
    except Exception as e:
        logging.error(f'ERROR: {e}')


def subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        env = os.environ
    else:
        si = None
        env = None

    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env})
    return ret


def main():
    logging.basicConfig(filename='C:\\chaff\\operational.log', level=logging.INFO)
    logging.info("STARTUP")
    ports = [21, 22, 23, 80, 443, 8000, 8080, 25, 110, 53, 3306, 5900, 69]
    pm = PortManager(
        ports,
        'C:\\chaff\\port.exe')
    pm.start()


if __name__ == '__main__':
    main()
