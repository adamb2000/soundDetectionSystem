from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def getResponse(self):
        #print(self.requestline)
        global layout
        if(self.path == "/WEBAPP.html" or self.path == "/"):
            file = open("WEBAPP.html")
            content = file.read()
            file.close()
            return content
        elif(self.path == "/format.json"):
            file = open("format.json")
            content = file.read()
            file.close()
            return content
        elif(self.path == "/volume.txt"):
            return self.sendVol()
        elif(self.path.endswith(".jpg")):
            file = open(self.path[1:],'rb')
            content = file.read()
            file.close()
            layout = self.path[1:]
            return content
        elif(self.path == "/favicon.ico"):
            file = open("favicon.png",'rb')
            content = file.read()
            file.close()
            return content
        elif(self.path == "/imageSize"):   
            tempIm = Image.open(layout)
            w,h = tempIm.size
            content = ""
            return str(w)+","+str(h)
        else:
            return False


    def sendVol(self):
        if(len(devices)==0):
            content = "BLANK"
        else:
            content = ""
            index = 0
            size = len(devices)
            while(index < size):
                devices[index].setTimer(devices[index].getTimer()-1)
                if(devices[index].getTimer() == 0):
                    print("=========================================================================")
                    print((devices.pop(index)).getID(),"Disconnected")
                    print("=========================================================================")
                else:
                    content = content+devices[index].getID()+","+str(devices[index].getVolume())+"\n"
                    index+=1
                size = len(devices)

            if(content==""):
                content = "BLANK"
            else:
                content = content[:-1]

        print(content)
        return content


    def saveFile(self, text):
        print(len(text))
        if(len(text)>3):
            file = open("DevPosition.txt",'w')
            file.write(text)
            file.close()
            print("pos")
        else:
            file = open("size.txt",'w')
            file.write(text)
            file.close()
            print("size")


    def do_GET(self):
        response = self.getResponse()
        if(response):
            self.send_response(200)
            self.end_headers()
            if(self.path.endswith(".jpg") or self.path =="/favicon.ico"):
                self.wfile.write(response)
                print("uigfhurhguierghviupferhvuirfhviuhviub")
            else:
                self.wfile.write(response.encode('utf-8'))
                
        else:
            self.send_response(404)
            self.end_headers()


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')
        if(len(body.split(",")) == 2):
            #print(body)
            
            updateDevice(body)
        else:
            print("WEB")
            self.send_response(200)
            self.end_headers()
            self.saveFile(body)


def updateDevice(body):
    data = body.split(",")
    new = True
    for i in range(len(devices)):
        if(devices[i].getID() == data[0]):
            devices[i].setVolume(data[1])
            devices[i].setTimer(30)
            new = False
            break
    if(new):
        addDevice(data[0],data[1])
        print("newdevice")


class Device:
    def __init__(self,ID,vol):
        self.id = ID
        self.averageVol = [int(vol)]
        self.pointer = 1
        self.timer = 30
        for i in range(0,99):
            self.averageVol.append(0)

    def getID(self):
        return self.id

    def getVolume(self):
        return sum(self.averageVol)/100

    def setVolume(self,vol):
        if(vol != '-'):
            self.averageVol[self.pointer] = int(vol)
            if(self.pointer == 99):
                self.pointer = 0
            else:
                self.pointer += 1

    def getTimer(self):
        return self.timer

    def setTimer(self,value):
        self.timer = value


def addDevice(id,vol):
    devices.append(Device(id,vol))


def main():
    #loadData()
    httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()

devices = []
layout = "layout.jpg"

if __name__=="__main__":
    main()