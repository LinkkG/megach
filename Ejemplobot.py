"""
Archivo de prueba para mi versión del ch
Incluirá las opciones básicas e iré añadiendo más poco a poco
"""
# Módulos básicos
# import os
import sys
import time
# import urllib.request as urlreq
# import urllib.parse as urlparse
# import queue

#  Módulos del bot
import megach

# Para depuración y pruebas
# import warnings
# warnings.simplefilter("default")

# TODO Interfaz gráfica
# Dueños, Solo minúsculas
owners = ['megamaster12', 'linkkg', 'milton797']
debug = True  # Printear cosas extra para depuración
debugchats = ['pythonrpg', 'PM']  # Conexiones donde se printeará lo recibido
# ignored commands onRaw
ignored_rcmd_ = ["i"]


class Mibot(megach.Gestor):
    """
    Mi implementación del bot
    También es posible crearla de la siguiente manera
    class Mibot(megach.RoomManager):
    """
    #
    """description of class"""

    def onInit(self):
        # super(megach.Gestor,self).__init__(*args)
        print("Inicio del BOT")

    def onConnect(self, room):
        # print('Conectado a ' + room.name+' '+str(room..connectattempts)) #megach
        print('Conectado a ' + room.name + ' ')  # ch
        # room.message("HOLA")#room._sendCommand("bm:4qun:0:hola mundo o o")

    def onDisconnect(self, room):
        print("desconectado de " + room.name)

    def onMessage(self, room, user, message):
        try:
            ubic = "".join({32768: "MOD", 256: "RED", 0: "NORMAL", 2048: "BLUE", 2304: "BLUE+RED"}.get(message.channel))
            print("[{0:<10}][{4}][{3}] {1}: {2} ".format(
                room.name,
                user.name.title(),
                message.body.replace("&#39;", "'"),
                time.strftime("%I:%M:%S %p"),
                ubic))
            if user.name in owners:
                if message.body.strip().split()[0] == '|eval':
                    room.message(str(eval(message.body.strip().split()[1])))
        except Exception as e:
            room.message(str(e))

    def onPing(self, room):
        print("Ping enviado %s " % room.name)

    def onPMConnect(self, pm):
        pass

    def onPong(self, room, pongdata):
        print("[{}] Pong recibido en " % room.name)

    def onRaw(self, room, raw):
        if raw.split(':')[0] not in ignored_rcmd_:
            if room.name in debugchats:
                print('[%s-]: %s' % (room.name, raw) + str(time.time()), file=sys.stderr)

    def onReconnect(self, room):  # TODO
        print('reconectando a ' + room.name)


bot = Mibot.easy_start(['pythonrpg'], 'UserName', 'Password', False)
