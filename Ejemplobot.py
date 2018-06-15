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
ignored_rcmd_ = ["", "b", "i", "u"]


class Mibot(megach.Gestor):
    """
    Mi implementación del bot
    También es posible crearla de la siguiente manera
    class Mibot(megach.RoomManager):
    """
    #
    """description of class"""

    def onInit(self):
        """Espacio para ejecutar acciones de carga de información u otras cosas"""
        print("Inicio del BOT")

    def onConnect(self, room):
        """Al haberse conectado a una sala de chat"""
        print('[{}][{}] Conectado. Intentos: {}'.format(time.strftime("%I:%M:%S %p"), room.name,
                                                        room.connectattempts))

    def onDisconnect(self, room):
        """Al desconectarse de una sala"""
        print('[{}][{}] Desconectado'.format(time.strftime("%I:%M:%S %p"), room.name))

    def onMessage(self, room, user, message):
        """Al recibir un mensaje en una sala"""
        try:
            ubic = "".join({32768: "MOD", 256: "RED", 0: "NORMAL", 2048: "BLUE", 2304: "BLUE+RED"}.get(
                    message.channel))
            print("[{0:_^10.10}][{4}][{3}] {1}: {2} ".format(
                    room.name,
                    user.name.title(),
                    message.body.replace("&#39;", "'"),
                    time.strftime("%I:%M:%S %p"),
                    ubic))
            if user.name in owners:
                if message.body.strip().split()[0] in ['|eval', '|exec']:
                    try:
                        room.message(str(eval(message.body.strip().split(' ', 1)[1])))
                    except:
                        try:
                            room.message(str(exec(message.body.strip().split(' ', 1)[1])))
                        except Exception as e:
                            raise e
                if message.body.strip().split()[0] == '|exec':
                    room.message(str(exec(message.body.strip().split()[1])))
        except Exception as e:
            room.message(str(e))

    def onPing(self, room):
        """

        @param room:
        """
        print("[{}] Ping enviado".format(time.strftime("%I:%M:%S %p")))

    def onPMConnect(self, pm):
        """
        Al conectarse al PM
        @param pm: El controlador del PM
        @return: None
        """
        print("[{}] Conectado al PM como {}".format(time.strftime("%I:%M:%s %p"), pm.currentname))

    def onPong(self, room, pong):
        """
        Al recibir un pong de una sala
        @param room: La sala en la que se recibió el pong
        @param pong: Posibles datos del pong
        """
        print("[{}][{0:_^10.10}] Pong recibido".format(time.strftime("%I:%M:%S %p"), room.name))

    def onRaw(self, room, raw):
        if raw.split(':')[0] not in ignored_rcmd_:
            if room.name in debugchats:
                print('[%s-]: %s' % (room.name, raw) + str(time.time()), file = sys.stderr)

    def onReconnect(self, room):  # TODO
        print('reconectando a ' + room.name)


accounts = [('Account1', 'Password1'),
            ('Account2', 'Password2')]
# bot = Mibot.easy_start(['pythonrpg'], USERNAME,PASSWORD ,pm= True) # También es válido así
bot = Mibot.easy_start(['pythonrpg'], pm = True, accounts = accounts)
