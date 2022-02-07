from multiprocessing import cpu_count
from sqlite3 import connect
from django.shortcuts import render
from django.http import HttpResponse

import wmi,ctypes
import pythoncom
import psutil
import numpy as np

# Create your views here.
def Home(request):

    return render(request, "Index.html")

def Result(request):

    Hostname = request.GET['server']
    Server = Server_Monitoring()
    Connect = Server.Connection()
    Disk = Server.DiskInfo(Connect)
    CR_Util = Server.Utilization(Connect)
    Uptime = Server.Uptime_Status(Connect)
    
    Server_Status = ""
    if(Connect==True):
        Server_Status = "Server is online"
    else:
        Server_Status = "Server is Offline"

    return render(request, 'Result.html',{
        'Hostname':Hostname,
        'Server_status':Server_Status,
        'CPU':CR_Util['CPU'],
        'RAM':CR_Util['RAM'],
        'Uptime':Uptime,
        'Disk': Disk
        })

class Server_Monitoring:

    def Connection(self):
        try:
            pythoncom.CoInitialize()
            Connect = wmi.WMI()
            return Connect
        except:
            return HttpResponse("Connection failed")

    # Disk Space Details
    def DiskInfo(self, Connection):
        self.Conn = Connection
        
        DiskName=[]
        TotalSpace = []
        FreeSpace = []
        Spaces = []
        Percentages = []

        for d in Connection.Win32_LogicalDisk():
            DiskName.append(d.Caption)
            TotalSpace.append(round(float(d.Size) / 1024**3, 2))
            FreeSpace.append(round(float(d.FreeSpace)  / 1024**3, 2))

        Spaces = list(np.array(TotalSpace) - np.array(FreeSpace))
        UsedSpace = [round(Space,2) for Space in Spaces]
        Percentages= list((np.array(UsedSpace) / np.array(TotalSpace)*100))
        UsedPercentage = [round(Percentage,2) for Percentage in Percentages]

        Disk_Zip = zip(DiskName,TotalSpace,FreeSpace,UsedSpace,UsedPercentage)

        return Disk_Zip

            
    def Utilization(self, Connection):
        self.Conn = Connection
        CPU_value = psutil.cpu_percent(4)
        RAM_Value = psutil.virtual_memory()[2] 
        CPU_RAM = {'CPU':CPU_value,'RAM':RAM_Value}
        return CPU_RAM

    def Uptime_Status(self, Connection):

        self.Conn = Connection

        lib = ctypes.windll.kernel32
        t = lib.GetTickCount64()
        t = int(str(t)[:-3])

        mins, sec = divmod(t, 60)
        hour, mins = divmod(mins, 60)
        days, hour = divmod(hour, 24)

        Uptime = f"{days}:{hour:02}:{mins:02}:{sec:02}"
        return Uptime