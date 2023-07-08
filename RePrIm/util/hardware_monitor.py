import os
import clr


if not os.path.isfile(os.path.join(os.path.split(__file__)[0], 'lib.dll')):
    os.renames(os.path.join(os.path.split(__file__)[0], 'lib.py'), os.path.join(os.path.split(__file__)[0], 'lib.dll'))

openhardwaremonitor_hwtypes = [
    'Mainboard', 'SuperIO', 'CPU', 'RAM', 'GpuNvidia', 'GpuAti', 'TBalancer', 'Heatmaster', 'HDD'
]
openhardwaremonitor_sensortypes = [
    'Voltage', 'Clock', 'Temperature', 'Load', 'Fan', 'Flow', 'Control', 'Level',
    'Factor', 'Power', 'Data', 'SmallData'
]

degrees = {"Load": "%", "Clock": "MHz", "Temperature": "°C", "Fan": "RPM", "Power": "Wt", }

HardwareHandle = None


def initialize_openhardwaremonitor():
    clr.AddReference(os.path.join(os.path.split(__file__)[0], 'lib.dll'))

    from OpenHardwareMonitor import Hardware
    handle = Hardware.Computer()
    handle.MainboardEnabled = True
    handle.CPUEnabled = True
    handle.RAMEnabled = True
    handle.GPUEnabled = True
    handle.HDDEnabled = True
    handle.Open()
    return handle


def fetch_stats():
    global HardwareHandle
    if not HardwareHandle:
        HardwareHandle = initialize_openhardwaremonitor()

    answer = []
    for i in HardwareHandle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            ans = parse_sensor(sensor)
            if ans:
                answer.append(ans)

        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                ans = parse_sensor(subsensor)
                if ans:
                    answer.append(ans)
    return answer


def parse_sensor(sensor):
    if not sensor:
        return
    if str(sensor.SensorType) not in degrees.keys():
        return
    ref = "HDD " if str(sensor.Name) == 'Used Space' else ""
    return f"{ref}{sensor.Name} {sensor.SensorType} - {round(sensor.Value, 2)} {degrees[str(sensor.SensorType)]}"
