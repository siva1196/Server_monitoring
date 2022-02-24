from django.shortcuts import render
from django.http import HttpResponse

import wmi
import pythoncom
import numpy as np
from socket import *
import datetime, os

# Create your views here.
def Home(request):

    return render(request,'Home.html')

def Index(request):

    return render(request, 'Index.html')

def Result(request):

    if request.method == "POST":
        Hostname = request.POST['server']
        Username = request.POST['username']    
        Password = request.POST['password']

    Ping = os.system("ping -n 1 " + Hostname)
    if Ping == 0:
        Server_status = "Accessible"
        Server = Server_Monitoring(Hostname,Username,Password)
        Disk = Server.DiskInfo()
        CPU_Util = Server.Utilization()
        Uptime = Server.Uptime_Status()

        return render(request, 'Result.html',{
            'Hostname':Hostname,
            'Server_Status':Server_status,
            'CPU':CPU_Util['CPU'],
            'RAM':CPU_Util['RAM'],
            'Uptime':Uptime,
            'Disk': Disk
        })
    else:
        Server_status = "Not Accessible"
        CPU_Util = {'CPU':None,'RAM':None}
        Uptime = None
        Disk = None 
        return render(request, 'Result.html',{
            'Hostname':Hostname,
            'Server_Status':Server_status,
            'CPU':CPU_Util['CPU'],
            'RAM':CPU_Util['RAM'],
            'Uptime':Uptime,
            'Disk': Disk
        })

class Server_Monitoring:

    def __init__(self,Host,User,Pass):
        self.Host = Host
        self.User = User
        self.Pass = Pass

    def Connection(self,Hostname, Username, Password):
        self.Host = Hostname
        self.User = Username
        self.Pass = Password
        global Server_status
        try:
            pythoncom.CoInitialize()
            Connect = wmi.WMI(self.Host, user = self.User, password = self.Pass)
            Server_status = "Connected"
            return Connect

        except wmi.x_wmi:
            return HttpResponse("<h2>Your Username and Password of "+getfqdn(Hostname)+" are wrong.</h2>")

    # Disk Space Details
    def DiskInfo(self):
        Connect = Server_Monitoring.Connection(self,self.Host, self.User, self.Pass)
        
        DiskName=[]
        TotalSpace = []
        FreeSpace = []
        Spaces = []
        Percentages = []

        for d in Connect.Win32_LogicalDisk(DriveType=3):
            DiskName.append(d.Caption)
            TotalSpace.append(round(float(d.Size) / 1024**3, 2))
            FreeSpace.append(round(float(d.FreeSpace)  / 1024**3, 2))

        Spaces = list(np.array(TotalSpace) - np.array(FreeSpace))
        UsedSpace = [round(Space,2) for Space in Spaces]
        Percentages= list((np.array(UsedSpace) / np.array(TotalSpace)*100))
        UsedPercentage = [round(Percentage,2) for Percentage in Percentages]

        Disk_Zip = zip(DiskName,TotalSpace,FreeSpace,UsedSpace,UsedPercentage)

        return Disk_Zip
          
    def Utilization(self):
        global Total_RAM
        global Free_RAM
        Connect = Server_Monitoring.Connection(self,self.Host, self.User, self.Pass)
        Processer = Connect.Win32_Processor()
        Cpu = Connect.Win32_ComputerSystem ()
        Ram = Connect.Win32_PerfFormattedData_PerfOS_Memory()
        for c in Processer:
            CPU_value =c.LoadPercentage
        for c in Cpu:
            Total_ram = int(c.TotalPhysicalMemory)
        for r in Ram:
            Free_RAM = int(r.AvailableBytes)
        Used_RAM = Total_ram - Free_RAM
        Used_Percentage = round((Used_RAM / Total_ram) *100,2)
        CPU_RAM = {'CPU':CPU_value,'RAM':Used_Percentage}
        return CPU_RAM

    def Uptime_Status(self):
        Connect = Server_Monitoring.Connection(self,self.Host, self.User, self.Pass)
        Os = Connect.Win32_OperatingSystem()
        LastBoot = str()
        for o in Os:
            LastBoot = o.LastBootUpTime
        SplitBoot = LastBoot.split(".")[0]
        BootTime = datetime.datetime.strptime(SplitBoot,"%Y%m%d%H%M%S")
        date = datetime.datetime.now()
        Uptime = date - BootTime
        return str(Uptime).split(".")[0]
