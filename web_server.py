import network
import socket
from time import sleep
import time
from picozero import pico_temp_sensor, pico_led, RGBLED
import machine
import _thread
import ntptime
import urequests

ssid = 'POCO M3 Pro 5G'
password = 'polanarasam'
ntptime.host = "1.europe.pool.ntp.org"
openweather_api_key = "d62b181418985a99d0d0a3043e32bfd0"

TEMPERATURE_UNITS = {
    "standard": "K",
    "metric": "°C",
    "imperial": "°F",
}
 
SPEED_UNITS = {
    "standard": "m/s",
    "metric": "m/s",
    "imperial": "mph",
}
 
units = "metric"

def get_weather(city, api_key, units='metric', lang='en'):
    '''
    Get weather data from openweathermap.org
        city: City name, state code and country code divided by comma, Please, refer to ISO 3166 for the state codes or country codes. https://www.iso.org/obp/ui/#search
        api_key: Your unique API key (you can always find it on your openweather account page under the "API key" tab https://home.openweathermap.org/api_keys
        unit: Units of measurement. standard, metric and imperial units are available. If you do not use the units parameter, standard units will be applied by default. More: https://openweathermap.org/current#data
        lang: You can use this parameter to get the output in your language. More: https://openweathermap.org/current#multi
    '''
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}&lang={lang}"
    print(url)
    res = urequests.post(url)
    return res.json()
 
def print_weather(weather_data):
    data = ""
#     print(f'Timezone: {int(weather_data["timezone"] / 3600)}')
    data += f'Timezone: {int(weather_data["timezone"] / 3600)}<br/>'
    sunrise = time.localtime(weather_data['sys']['sunrise']+weather_data["timezone"])
    sunset = time.localtime(weather_data['sys']['sunset']+weather_data["timezone"])
#     print(f'Sunrise: {sunrise[3]}:{sunrise[4]}')
    data += f'Sunrise: {sunrise[3]}:{sunrise[4]}<br/>'
#     print(f'Sunset: {sunset[3]}:{sunset[4]}')
    data += f'Sunset: {sunset[3]}:{sunset[4]}<br/>'
#     print(f'Country: {weather_data["sys"]["country"]}')
    data += f'Country: {weather_data["sys"]["country"]}<br/>'
#     print(f'City: {weather_data["name"]}')
    data += f'City: {weather_data["name"]}<br/>'
#     print(f'Coordination: [{weather_data["coord"]["lon"]}, {weather_data["coord"]["lat"]}')
    data += f'Coordination: [{weather_data["coord"]["lon"]}, {weather_data["coord"]["lat"]}<br/>'
#     print(f'Visibility: {weather_data["visibility"]}m')
    data += f'Visibility: {weather_data["visibility"]}m<br/>'
#     print(f'Weather: {weather_data["weather"][0]["main"]}')
    data += f'Weather: {weather_data["weather"][0]["main"]}<br/>'
#     print(f'Temperature: {weather_data["main"]["temp"]}{TEMPERATURE_UNITS[units]}')
    data += f'Temperature: {weather_data["main"]["temp"]}{TEMPERATURE_UNITS[units]}<br/>'
#     print(f'Temperature min: {weather_data["main"]["temp_min"]}{TEMPERATURE_UNITS[units]}')
    data += f'Temperature min: {weather_data["main"]["temp_min"]}{TEMPERATURE_UNITS[units]}<br/>'
#     print(f'Temperature max: {weather_data["main"]["temp_max"]}{TEMPERATURE_UNITS[units]}')
    data += f'Temperature max: {weather_data["main"]["temp_max"]}{TEMPERATURE_UNITS[units]}'
    data += "\n"
#     print(f'Temperature feels like: {weather_data["main"]["feels_like"]}{TEMPERATURE_UNITS[units]}')
    data += f'Temperature feels like: {weather_data["main"]["feels_like"]}{TEMPERATURE_UNITS[units]}<br/>'
#     print(f'Humidity: {weather_data["main"]["humidity"]}%')
    data += f'Humidity: {weather_data["main"]["humidity"]}%<br/>'
#     print(f'Pressure: {weather_data["main"]["pressure"]}hPa')
    data += f'Pressure: {weather_data["main"]["pressure"]}hPa<br/>'
#     print(f'Wind speed: {weather_data["wind"]["speed"]}{SPEED_UNITS[units]}')
    data += f'Wind speed: {weather_data["wind"]["speed"]}{SPEED_UNITS[units]}<br/>'
    #print(f'Wind gust: {weather_data["wind"]["gust"]}{SPEED_UNITS[units]}')
#     print(f'Wind direction: {weather_data["wind"]["deg"]}°')
    data += f'Wind direction: {weather_data["wind"]["deg"]}°<br/>'
    if "clouds" in weather_data:
#         print(f'Cloudiness: {weather_data["clouds"]["all"]}%')
        data += f'Cloudiness: {weather_data["clouds"]["all"]}%<br/>'
    elif "rain" in weather_data:
#         print(f'Rain volume in 1 hour: {weather_data["rain"]["1h"]}mm')
        data += f'Rain volume in 1 hour: {weather_data["rain"]["1h"]}mm<br/>'
#         print(f'Rain volume in 3 hour: {weather_data["rain"]["3h"]}mm')
        data += f'Rain volume in 3 hour: {weather_data["rain"]["3h"]}mm<br/>'
    elif "snow" in weather_data:
#         print(f'Snow volume in 1 hour: {weather_data["snow"]["1h"]}mm')
        data += f'Snow volume in 1 hour: {weather_data["snow"]["1h"]}mm<br/>'
#         print(f'Snow volume in 3 hour: {weather_data["snow"]["3h"]}mm')
        data += f'Snow volume in 3 hour: {weather_data["snow"]["3h"]}mm<br/>'
    return data

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection
    
# Login Page
def login():
    html = f"""
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <title>Home Automation</title>
  </head>
  <body>
    <form method="post" action="/login" style="left:50%;top:50%;position:absolute;transform: translate(-50%, -50%);">
      <div>
        <div>
          <h2>LOG IN</h2>
        </div>
        <div>
          <label for="username">
            Username <br />
            <input id="username" name="username" placeholder="Enter username" type="text"/>
          </label>
        </div>
        <br />
        <div>
          <label for="password">
            Password <br />
            <input id="password" name="password" placeholder="Enter password" type="password" />
          </label>
        </div>
        <div>
          <br />
          <button type="submit">Login</button>
        </div>
      </div>
    </form>
  </body>
</html>
           """
    return str(html)

# Index Page
def index():
    html = f"""
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <title>Home Automation</title>
  </head>
  <body>
    <div style="margin:10px;text-align:center;">
      <div>
        <h1>Home Automation using Raspberry Pi Pico W</h1>
        <p>Monitor, control and automate different home devices using single web page</p>
      </div>
      <h3>List of Devices</h3>

      <div style="display:flex;flex-direction:row;margin-left:30px;margin-right:30px;margin-bottom:30px;">

        <div style="width:50%;">
          <div style="background:#FCEDDA;box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);transition: 0.3s;margin-right:15px;">
            <div style="padding: 2px 16px;">
              <h4><b>Temperature Sensor</b></h4>
              <p>Used to control temperature of devices</p>
            </div>
            <button type="submit" style="background:#F7C5CC;width:100%;padding:10px;border:none;"><b><a style="text-decoration:none;" href="/device1">Manage</a></b></button>
          </div>
        </div>

        <div style="width:50%;">
          <div style="background:#FCEDDA;box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);transition: 0.3s;margin-right:15px;">
            <div style="padding: 2px 16px;">
              <h4><b>IR Sensor</b></h4>
              <p>Used to detect objects and used in door automation</p>
            </div>
            <button type="submit" style="background:#F7C5CC;width:100%;padding:10px;border:none;"><b><a style="text-decoration:none;" href="/device2">Manage</a></b></button>
          </div>
        </div>

      </div>

      <div style="display:flex;flex-direction:row;margin-left:30px;margin-right:30px;margin-bottom:30px;">

        <div style="width:50%;">
          <div style="background:#FCEDDA;box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);transition: 0.3s;margin-right:15px;">
            <div style="padding: 2px 16px;">
              <h4><b>Alarm Clock</b></h4>
              <p>Used to set alarm at a partcular time by the admin</p>
            </div>
            <button type="submit" style="background:#F7C5CC;width:100%;padding:10px;border:none;"><b><a style="text-decoration:none;" href="/device3">Manage</a></b></button>
          </div>
        </div>

        <div style="width:50%;">
          <div style="background:#FCEDDA;box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);transition: 0.3s;margin-right:15px;">
            <div style="padding: 2px 16px;">
              <h4><b>API Calling</b></h4>
              <p>Used to get weather forecast data from web apis</p>
            </div>
            <button type="submit" style="background:#F7C5CC;width:100%;padding:10px;border:none;"><b><a style="text-decoration:none;" href="/device4">Manage</a></b></button>
          </div>
        </div>

      </div>

    </div>
  </body>
</html>
"""
    return str(html)

# device1
def device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit):
    html = f"""
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <title>Home Automation</title>
  </head>
  <body>
    <div style="margin:10px;text-align:center;">
      <div>
        <h1>Temperature Sensor</h1>
        <p>Used to control temperature of devices</p>
      </div>
      <div style="margin:30px;text-align:justify;">
        <p><b>Device temperature : {d1_temperature}</b></p>
        <div>
          <p><b>Device State : {d1_state}</b></p>
          <form method="post" action="/device1_state">
            <button type="submit" name="button" style="width:300px">Turn device {d1_state1}</button>
          </form>
        </div>
        <div>
          <p><b>Self Control : {d1_control}</b></p>
          <form method="post" action="/device1_control">
            <button type="submit" name="button" style="width:300px">Turn {d1_control1} self control</button>
          </form>
        </div>
        <div style="margin-top:60px;">
          <p><b>Temperature Limit : {d1_temperature_limit}</b></p>
          <form method="post" action="/device1_limit">
            <label for="input1">
              <b>Set temperature Limit</b>
              <br />
              <input required="required" id="input1" value="1" type="number" name="tl" placeholder="Set temperature Limit" />
            </label>
            <br/>
            <p>
            </p>
            <button type="submit" style="width:300px">Set Temperature Limit</button>
          </form>
        </div>

      </div>
    </div>
  </body>
</html>
            """
    return str(html)

# device2
def device2(d2_flag):
    html = f"""
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="1">
    <title>Home Automation</title>
  </head>
  <body>
    <div style="margin:10px;text-align:center;">
      <div>
        <h1>IR Sensor</h1>
        <p>Used to detect objects and used in door automation</p>
      </div>
      <div style="margin:10px;text-align:justify;">
        <h2>Object Detected : {d2_flag}</h2>
      </div>
    </div>
  </body>
</html>
            """
    return str(html)

# device3
def device3():
    html = """
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Automation</title>
    <script>
        function displaytime(){
            var session = "";
            var month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            var daylist = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

            var today = new Date();
            var day = today.getDay();
            var date = today.getFullYear() + "/" + (today.getMonth()+1) + "/" + today.getDate();
            var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

            if(today.getHours() >= 12){
                session = "PM";
            }else{
                session = "AM";
            }

            document.getElementById("displayDate").innerHTML = daylist[day] + ", " + month[today.getMonth()] + " " + today.getDate();
            document.getElementById("displayDateTime").innerHTML = date + " " + time + " " + session;
        }
        setInterval(displaytime, 10);
    </script>
  </head>
  <body>
    <div style="margin:10px;text-align:center;">
      <div>
        <h1>Alarm Clock</h1>
        <p>Used to set alarm at a partcular time by the admin</p>
      </div>
      <div style="margin:10px;text-align:justify;">
        <h2><u>Current Date and Time</u></h2>
        <p id="displayDate"></p>
        <p id="displayDateTime"></p>
        <br/><br/>
        <div>
          <h3>Alarm State : {d3_alarm}</h3>
          <form method="post" action="/device3_alarm">
            <label for="appt">
              <h3>Set Alarm</h3>
              <input type="Time" id="appt" name="alarm" required>
            </label>
            <button type="submit">Set Alarm</button>
          </form>
        </div>
      </div>
    </div>
  </body>
</html>
            """
    return str(html)

# device4
def device4(d4_data):
    html = f"""
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <title>Home Automation</title>
  </head>
  <body>
    <div style="margin:10px;text-align:center;">
      <div>
        <h1>API Calling</h1>
        <p>Used to get weather forecast data from web apis</p>
      </div>
      <div style="margin:10px;text-align:justify;">
        <h2>{d4_data}</h2>
      </div>
    </div>
  </body>
</html>
"""
    return str(html)

def device11(ip):
    print(ip)
    html = f"""
<html>
<head>
<meta http-equiv="refresh" content="1; URL=http://{ip}/device1" />
</head>
</html>
           """
    return str(html)

def device3_alarm(ip):
    print(ip)
    html = f"""
<html>
<head>
<meta http-equiv="refresh" content="1; URL=http://{ip}/device3" />
</head>
</html>
           """
    return str(html)

def device3_thread(alarm0,alarm1):
#     ntptime.settime()
#     flag = 1
#     print(alarm0 + "*" + alarm1)
#     while flag:
#         curr0 = time.localtime()[3]+5
#         curr1 = time.localtime()[4]+30
#         if(curr1 >= 60):
#             curr0 = curr0 + 1
#             curr1 = curr1 - 60
#         if(curr0 >= 24):
#             curr0 = curr0 - 24
#         curr0 = str(curr0)
#         curr1 = str(curr1)
#         if(curr0 == alarm0 and curr1 == alarm1):
#             flag = 0
#         if flag :
#             sleep(1)
#         print(curr0 + " " + curr1 + " " + alarm0 + " " + alarm1)
    sleep(40)
    print('alarm ringing')
    rgb = RGBLED(red=1, green=2, blue=3)
    rgb.color = (0, 0, 255)
    sleep(2)
    rgb.color = (255, 0, 0)
    sleep(2)
    rgb.color = (255, 0, 255)
    sleep(2)
    rgb.off()   

def serve(connection,ip):
    #Start a web server
    login_flag = 0
    d1_temperature = 0
    d1_state = 'ON'
    d1_state1 = 'OFF'
    d1_control = 'ON'
    d1_control1 = 'OFF'
    d1_temperature_limit = 33
    d2_flag = 'NO'
    d3_alarm_flag = 'OFF'
    pico_led.on()
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request) # mohan : remove this later
        method = ""
        url = ""
        html = ""
        try:
            method = request.split()[0]
            url = request.split()[1]
        except IndexError:
            pass
        
        if (method == 'b\'GET' and url == '/'):
            html = login()
        elif (method == 'b\'POST' and url == '/login'):
            data = request.split("\\r\\n\\r\\n")[1]
            if(data == "username=admin&password=admin'"):
                html = index()
                login_flag = 1
            else:
                html = "<p>Invalid Credentials</p>"
        elif (login_flag==0):
            html = "<p>Login to automate the home devices</p>"
        elif (method=='b\'GET' and url=='/device1'):
            d1_temperature = pico_temp_sensor.temp
            if(d1_control=='ON'):
                if(d1_temperature>=d1_temperature_limit):
                    pico_led.off()
                    d1_state = 'OFF'
                    d1_state1 = 'ON'
                else:
                    pico_led.on()
                    d1_state = 'ON'
                    d1_state1 = 'OFF'
            html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
        elif (method=='b\'POST' and url=='/device1_state'):
            d1_control = 'OFF'
            d1_control1 = 'ON'
            if(d1_state=='ON'):
                pico_led.off()
                d1_state = 'OFF'
                d1_state1 = 'ON'
            elif(d1_state=='OFF'):
                pico_led.on()
                d1_state = 'ON'
                d1_state1 = 'OFF'
            d1_temperature = pico_temp_sensor.temp
            html = device11(ip)
#             html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
        elif (method=='b\'GET' and url=='/device1_state'):
            d1_temperature = pico_temp_sensor.temp
            html = device11(ip)
#             html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
        elif (method=='b\'POST' and url=='/device1_control'):
            if(d1_control=='ON'):
                d1_control = 'OFF'
                d1_control1 = 'ON'
            else:
                d1_control = 'ON'
                d1_control1 = 'OFF'
            d1_temperature = pico_temp_sensor.temp
            html = device11(ip)
#             html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
        elif (method=='b\'GET' and url=='/device1_control'):
            d1_temperature = pico_temp_sensor.temp
            html = device11(ip)
#             html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
        elif (method=='b\'POST' and url=='/device1_limit'):
            data = request.split("\\r\\n\\r\\n")[1]
            data = data.split("=")[1]
            data = data.split("'")[0]
            d1_temperature_limit = int(data)
            d1_temperature = pico_temp_sensor.temp
            html = device11(ip)
#             html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
        elif (method=='b\'GET' and url=='/device1_limit'):
            d1_temperature = pico_temp_sensor.temp
#             html = device1(d1_temperature,d1_state,d1_state1,d1_control,d1_control1,d1_temperature_limit)
            html = device11(ip)
        elif (method=='b\'GET' and url=='/device2'):
            ir = machine.Pin(21,machine.Pin.IN)
            if ir.value()==1:
                d2_flag = 'NO'
            elif ir.value()==0:
                d2_flag = 'YES'
            html = device2(d2_flag)
        elif (method=='b\'GET' and url=='/device3'):
            html = device3()
        elif (method=='b\'POST' and url=='/device3_alarm'):
            data = request.split("\\r\\n\\r\\n")[1]
            data = data.split("%3A")
            d3_hours = data[0]
            d3_minutes = data[1]
            print(d3_hours + " * " + d3_minutes)
            d3_alarm_flag = 'ON'
            second_thread = _thread.start_new_thread(device3_thread, (d3_hours,d3_minutes))   
            html = device3_alarm(ip)
        elif (method=='b\'GET' and url=='/device3_alarm'):
            html = device3_alarm(ip)
        elif (method=='b\'GET' and url=='/device4'):
            weather_data = get_weather('dhanbad', openweather_api_key, units=units)
            weather=weather_data["weather"][0]["main"]
            t=weather_data["main"]["temp"]
            rh=weather_data["main"]["humidity"]
            # get time
            hours=time.localtime()[3]+int(weather_data["timezone"] / 3600)
            mins=time.localtime()[4]
            weather_data1 = print_weather(weather_data)
            html = device4(weather_data1)
        else:
            html = "<p> NULL </p>"
        client.send(html)
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection,ip)
except KeyboardInterrupt:
    machine.reset()
