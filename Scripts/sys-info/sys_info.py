import psutil
import platform
from datetime import datetime
import pyfiglet
from colorama import Fore, Style, init
import os

#reference: https://thepythoncode.com/article/get-hardware-system-information-python

#initializing colorama
init()

def print_sys_header():

    head = pyfiglet.figlet_format("System Overview", font="slant")
    print(f"{Fore.CYAN}{head}{Style.RESET_ALL}")

def print_sys_info():

    print(f"{Fore.GREEN}** SYSTEM INFORMATION:{Style.RESET_ALL}")

    uname = platform.uname()

    sys_info = {
        "system": uname.system,
        "node name": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor
    }
    print_dict(sys_info)

def print_boot_time():

    bt = datetime.fromtimestamp(psutil.boot_time())
    print(f"{Fore.GREEN}** BOOT TIME:-------- {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}{Style.RESET_ALL}")

def print_cpu_info():

    print(f"{Fore.GREEN}** CPU INFORMATION:{Style.RESET_ALL}")

    cpufreq = psutil.cpu_freq()

    #format per core str
    pad = 23
    dash = 7
    pc = ""
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        pc += f"Core {i + 1}: {percentage}%\n" + " " * pad + "-" * dash + " "
    pc = pc[:-(pad + dash + 2)]

    cpu_info = {
        "physical cores": psutil.cpu_count(logical=False),
        "total cores": psutil.cpu_count(logical=True),
        "max frequency": f"{cpufreq.max:.2f}Mhz",
        "min frequency": f"{cpufreq.min:.2f}Mhz",
        "current frequency": f"{cpufreq.current:.2f}Mhz",
        "CPU usage per core": pc,
        "total CPU usage": f"{psutil.cpu_percent()}%"
    }

    print_dict(cpu_info)

def print_sys_mem():

    print(f"{Fore.GREEN}** MEMORY USAGE:{Style.RESET_ALL}")

    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()

    sys_mem = {
        "total": format_bytes(vm.total),
        "available": format_bytes(vm.available),
        "used": format_bytes(vm.used),
        "percent": f"{vm.percent}%"
    }

    swap_mem = {
        "total": format_bytes(sm.total),
        "free": format_bytes(sm.free),
        "used": format_bytes(sm.used),
        "percent": f"{sm.percent}%"
    }
    
    print_dict(sys_mem)
    print(" * SWAP Memory:")
    print_dict(swap_mem)

def print_disk_use():

    print(f"{Fore.GREEN}** DISK USAGE:{Style.RESET_ALL}")

    #get all partitions
    print(" * Partitions:")
    part = psutil.disk_partitions()
    for p in part:

        print(f"  - Device:----------------- {p.device}")

        p_dict = {
            "mountpoint": p.mountpoint,
            "file system type": p.fstype
        }

        try:
            p_usage = psutil.disk_usage(p.mountpoint)
        except PermissionError:
            continue

        p_dict["total size"] = format_bytes(p_usage.total)
        p_dict["used"] = format_bytes(p_usage.used)
        p_dict["free"] = format_bytes(p_usage.free)
        p_dict["percentage"] = str(p_usage.percent) + "%"

        print_dict(p_dict)

    #get io stats
    print(" * Disk I/O:")
    disk_io = psutil.disk_io_counters()
    io_dict = {
        "total read": format_bytes(disk_io.read_bytes),
        "total write": format_bytes(disk_io.write_bytes)
    }

    print_dict(io_dict)

def print_net_info():

    print(f"{Fore.GREEN}** NETWORK INFORMATION:{Style.RESET_ALL}")

    print(" * Network Interfaces:")
    if_addrs = psutil.net_if_addrs()
    
    # Track if we've already printed an interface
    printed_interfaces = set()
    
    for interface_name, interface_addresses in if_addrs.items():
        print(f"  - Interface: {interface_name}")
        
        ipv4_dict = {}
        ipv6_dict = {}
        mac_dict = {}
        
        for address in interface_addresses:
            # Map the address families based on your system
            if address.family == 2:  # AF_INET (IPv4)
                ipv4_dict["IP address"] = address.address
                ipv4_dict["Netmask"] = address.netmask
                ipv4_dict["Broadcast IP"] = address.broadcast
            elif address.family == 30:  # IPv6
                ipv6_dict["IPv6 address"] = address.address
                ipv6_dict["Netmask"] = address.netmask
                ipv6_dict["Scope"] = address.broadcast  # IPv6 uses scope instead of broadcast
            elif address.family == 18:  # MAC address
                mac_dict["MAC address"] = address.address
        
        # Print each address type if it has content
        if any(v is not None and v != "" for v in ipv4_dict.values()):
            print_dict(ipv4_dict)
        if any(v is not None and v != "" for v in mac_dict.values()):
            print_dict(mac_dict)
        if any(v is not None and v != "" for v in ipv6_dict.values()):
            print_dict(ipv6_dict)
    
    #get IO statistics since boot
    print(" * I/O Statistics:")
    net_io = psutil.net_io_counters()
    io_dict = {
        "total bytes sent": format_bytes(net_io.bytes_sent),
        "total bytes received": format_bytes(net_io.bytes_recv)
    }
    print_dict(io_dict)

#helpers

def format_bytes(bytes, suffix="B"):
    """ Format bytes into readable format.

    Args:
        bytes (int): number of bytes
        suffix (str, optional): Defaults to "B".

    Returns:
        string: string representation of number of bytes
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def print_dict(d):   
    if len(d) == 0:
        return

    max_key_len = max(len(key) for key in d.keys())
    pad_len = max_key_len + 8

    for key, val in d.items():
        key_f = str(key).capitalize() + ":"
        dash_len = pad_len - len(key_f)
        dash_pad = "-" * dash_len
        print(f"\t{key_f}{dash_pad} {val}")
    

def main():
    lb = "=" * 60

    print_sys_header()
    print(lb)

    print_sys_info()        #system info
    print(lb)

    print_boot_time()       #boot time
    print(lb)

    print_cpu_info()        #CPU info
    print(lb)

    print_sys_mem()         #system memory
    print(lb)

    print_disk_use()        #disk usage
    print(lb)

    print_net_info()        #network information
    print(lb)




    print(f"\n{Fore.MAGENTA}~ Generated by zayatzy0's System Info Tool{Style.RESET_ALL}")

if __name__ == "__main__":
    main()