from androguard.core.bytecodes.apk import APK
import frida
import json
import subprocess
import os
from datetime import datetime
from loguru import logger
from rich import print
from rich.console import Console
from utils import *
console = Console()

path_data="./malware data"
dir_file = os.listdir('./malware data')
target=path_data+'/'


def on_message(message, data):
    """
    Parameters
    ----------
    message
    data
    Returns
    -------
    """
    file_log = open(file_log_frida, "a")
    if message["type"] == "send":
        if type(message["payload"]) is str:
            
            if "API Monitor" not in message["payload"]:
                message_dict = json.loads(message["payload"])
            else:
                file_log.write(str(message["payload"]) + "\n")
                #try:
                    #console.log(json.loads(message["payload"]))
                #except json.decoder.JSONDecodeError as e:
                    #pass
                #return
        else:
            #print("***************")
            message_dict = message["payload"]
        if "Error" not in str(message_dict):
            message_dict["time"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            file_log.write(str(message_dict) + "\n")
            #try:
                #console.log(json.loads(message["payload"]))
            #except json.decoder.JSONDecodeError as e:
                    #pass
    file_log.close()

def create_script_frida(path_frida_script_template):
    """
    Parameters
    ----------
    list_api_to_monitoring
    path_frida_script_template
    Returns
    -------
    """
    list_api_to_monitoring=[ "Device Info","Device Data","Database"]
    with open(path_frida_script_template) as frida_script_file:
        script_frida_template = frida_script_file.read()
    with open(os.path.join(os.path.dirname(__file__), "api_android_monitor", "api_monitor.json")) as f:
        api_monitor = json.load(f)
    script_frida = ""
    for i in range(18):
        x=api_monitor[i]['hooks']
        for dt in x:
                #print(dt['clazz'])
            script_frida += (script_frida_template.replace("class_name", '"' + dt['clazz'] + '"').replace("method_name", '"' + dt['method'] + '"')+ "\n\n")
    
    return script_frida
 
def command_execution(cammand):
    p = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0].strip().decode(errors="backslashreplace")
    return output
for fi in dir_file:
    print(fi)
    apk_path=target+fi
    package_name = install_app_and_install_frida(apk_path)
    print(package_name)
    file_log_frida = os.path.join(os.path.dirname(__file__), "logs")
    pid = None
    device = None
    session = None
    #try:
    device = frida.get_usb_device(1)
    pid = device.spawn([package_name])
    session = device.attach(pid)
    print(pid)
    logger.info(f"Succesfully attacched frida to the app {package_name}")
    
    dir_frida = os.path.join(file_log_frida, package_name.replace(".", "_"))
    print(file_log_frida)
    print(dir_frida)
    if not os.path.exists(dir_frida):
        os.makedirs(dir_frida)

    file_log_frida = os.path.join(dir_frida, "monitoring_api_frida_{}.txt".format(package_name.replace(".", "_")))
    
    path="C:/Users/acer/Desktop/Sandboxing/api_android_monitor/frida_script_template.js"
    script_frida = create_script_frida(path)
    script = session.create_script(script_frida.strip().replace("\n", ""))
    script.on("message", on_message)
    script.load()
    device.resume(pid)
    #api = script.exports
    time.sleep(10)

    start = time.time()
    #while True:
        #command = input("Press 0 to exit\n\n")
        #if command == "0":
            #break
   
   
    command = 'adb shell pidof' + " " + package_name
    res=command_execution(command)
    print(res)
    time.sleep(7)
    path="/sdcard/Download/"+package_name+".txt"
    
    from subprocess import Popen, PIPE
    proc = Popen(['adb','shell','strace','-o',path,'-T','-tt','-e','trace=all','-f','-p',res], stdout=PIPE, stderr=PIPE)
    print(proc.pid)
    print("execute monkey")
    time.sleep(7)
    command_m='adb shell monkey -p'+" "+ package_name+" "+ '-v 500'
    os.system(command_m)
    
    time.sleep(3)
    commans_k='adb shell kill strace'+" "+ res
    os.system(commans_k)
    time.sleep(4)
    path1="C:/Users/acer/Desktop/test"
    command2= "adb pull -p " + path +" "+ path1
    os.system(command2)
    command3= "adb shell rm" +" " + path
    os.system(command3)

    time.sleep(5)

    command4 = "adb uninstall"+" " + package_name
    os.system(command4)
    time.sleep(5)