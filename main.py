"Module updates OS and routerOS at Mikrotik routers."
import paramiko
import yaml
import textfsm
import time
from typing import Dict
from typing import List
from typing import Any 

class UpdateMikrotik():
    def __init__(self,**device : Dict[str,str]):

        self.ip=device['ip']
        self.username=device['username']
        self.password=device['password']
        self.secret=device['secret']
        self.port=device['port']
        self.global_delay_factor=device['global_delay_factor']

    def check_possible_update_os(self) -> str:
        command1 : str
        command2 : str
        result : List[Any]

        print(f'\n--->{device["secret"]} check for posibility OS update\n')
        command1='/system package update check-for-updates'
        command2='/system routerboard print'

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.ip, username=self.username, password=self.password, port=self.port, look_for_keys=False, allow_agent=False)

        stdin,stdout,stderr = self.client.exec_command(command1)
        output=stdout.read().decode('utf-8')
        template_open=open('templates/update_os.template')
        fsm=textfsm.TextFSM(template_open)
        result = fsm.ParseText(output)
        self.client.close()
        if result[0][1]=='':
            print(f'{device["secret"]} Can not check update OS')
            return 'error'
        elif result[0][0]!=result[0][1]:
            print(f'{device["secret"]} need update os, current version is {result[0][0]}, new version is {result[0][1]}')
            return 'yes'
        else:
            print(f'{device["secret"]} has  up to date OS version {result[0][0]}')
            return 'no'

    def check_possible_update_routerboard(self) -> str :
        command2 : str
        result : List[Any]

        print(f'\n--->{device["secret"]} check for posibility ROUTERBOARD update\n')
        command2='/system routerboard print'

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.ip, username=self.username, password=self.password, port=self.port, look_for_keys=False, allow_agent=False)

        stdin,stdout,stderr = self.client.exec_command(command2)
        output=stdout.read().decode('utf-8')
        template_open=open('templates/update_routerboard.template')
        fsm=textfsm.TextFSM(template_open)
        result = fsm.ParseText(output)
        self.client.close()
        if result[0][0]!=result[0][1]:
            print(f'{device["secret"]} need to update routerboard, current version is {result[0][0]}, new version is {result[0][1]}')
            return 'yes'
        else:
            print(f'{device["secret"]} has  up to date Routerboard version {result[0][0]}')
            return 'no'

    def command_update_os(self) -> None :
        command1 : str
        command2 : str

        command1='/system package update download ; /system reboot'
        command2='y'

        print(f'Connect to {device["secret"]} to donwload OS')

        client_update_os = paramiko.SSHClient()
        client_update_os.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_update_os.connect(hostname=self.ip, username=self.username, password=self.password, port=self.port, look_for_keys=False, allow_agent=False)

        stdin,stdout,stderr = client_update_os.exec_command(command1)
        output1=stdout.read().decode('utf-8')
        client_update_os.close()
        print(f'Router  {device["secret"]} rebooting')

        return None

    def command_update_routerboard(self) -> None :
        command1 : str
        command2 : str
        command3 : str

        command1='/system routerboard upgrade'
        command2='y'
        command3='/system reboot'

        print(f'Connect to {device["secret"]} to download ROUTERBOARD')

        client_update_r = paramiko.SSHClient()
        client_update_r.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_update_r.connect(hostname=self.ip, username=self.username, password=self.password, port=self.port, look_for_keys=False, allow_agent=False)

        stdin,stdout,stderr = client_update_r.exec_command(command1)
        output1=stdout.read().decode('utf-8')
        time.sleep(3)
        stdin,stdout,stderr = client_update_r.exec_command(command2)
        output2=stdout.read().decode('utf-8')
        time.sleep(3)

        stdin,stdout,stderr = client_update_r.exec_command(command3)
        output3=stdout.read().decode('utf-8')
        client_update_r.close()

        print(f'Router  {device["secret"]} is rebooting')
        return None

    def after_update_os(self) -> str :
        command1 : str

        command1='/system package update check-for-updates'

        client_check = paramiko.SSHClient()
        client_check .set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_check.connect(hostname=self.ip, username=self.username, password=self.password, port=self.port, look_for_keys=False, allow_agent=False)

        stdin,stdout,stderr = client_check.exec_command(command1)
        output1=stdout.read().decode('utf-8')
        client_check.close()

        template_open=open('templates/update_os.template')
        fsm=textfsm.TextFSM(template_open)
        result = fsm.ParseText(output1)
        if result[0][0]==result[0][1]:
            print(f'--->{device["secret"]} OS was upgraded  SUCCESS')
            return 'yes'
        else:
            print(f'--->{device["secret"]} OS was not upgraded FAIL')
            return 'no'

    def after_update_r(self) -> str:
        command1 : str
        result:  List[Any]

        command1='/system routerboard print'

        client_check = paramiko.SSHClient()
        client_check .set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_check.connect(hostname=self.ip, username=self.username, password=self.password, port=self.port, look_for_keys=False, allow_agent=False)


        stdin,stdout,stderr = client_check.exec_command(command1)
        output1=stdout.read().decode('utf-8')

        template_open=open('templates/update_routerboard.template')
        fsm=textfsm.TextFSM(template_open)
        result = fsm.ParseText(output1)
        if result[0][0]==result[0][1]:
            print(f'--->{device["secret"]} update routerboard SUCCESS')
            return 'yes'
        else:
            print(f'--->{device["secret"]} update roaterboard  FAIL')
            return 'no'


if __name__=="__main__":
    input_devices : Dict[Any,Any]
    result1 : str
    result2 : str
    result3 : str
    result4 : str
    device : Dict[Any,Any]

    with open('devices.yml','r') as f_read:
        input_devices=yaml.safe_load(f_read)


    for device in input_devices:
        print(f'================================= {device["secret"]} =================================')
        router = UpdateMikrotik(**device)
        try:
            result1=router.check_possible_update_os()
            if result1=="yes":
                router.command_update_os()
                time.sleep(120)
                result2=router.after_update_os()
                if result2=="no":
                    with open("fail.log","a") as file_write:
                        file_write.write(f"Update of router OS {id['secret']} failed")
                    continue
                elif result2=='yes':
                    result3=router.check_possible_update_routerboard()
                    if result3=="yes":
                        result4=router.command_update_routerboard()
                        time.sleep(80)
                        result4=router.after_update_r()
                        if result4=="yes":
                            with open("success.log","a") as file_write:
                                file_write.write(f"Update of router OS and routerboard {id['secret']} was success")
                        else:
                             with open("fail.log","a") as file_write:
                                 file_write.write(f"Update of router OS {id['secret']} was success, update of routerboard was fail")
            elif result1=="no":
                result3=router.check_possible_update_routerboard()
                if result3=="yes":
                    router.command_update_routerboard()
                    time.sleep(30)
                    result4=router.after_update_r()
                    if result4=="yes":
                            with open("success.log","a") as file_write:
                                file_write.write(f"Update of router OS and routerboard {id['secret']} was success")
                    else:
                           with open("fail.log","a") as file_write:
                                 file_write.write(f"Update of router OS {id['secret']} was success, update of routerboard was fail")
        except NoValidConnectionsError  as error_output:
            print(error_output)
        except:
            print('Something goes wrong =(')
