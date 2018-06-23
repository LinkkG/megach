#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Archivo de prueba para mi versión del ch
Incluirá las opciones básicas e iré añadiendo más poco a poco
Versión 1.5.1
"""
# Módulos básicos
import math
import os
import socket
import sys
import time
import urllib.request as urlreq
import urllib.parse as urlparse

#  Módulos del bot
import megach

# Para depuración y pruebas
# import warnings
# warnings.simplefilter("default")

# TODO Interfaz gráfica
# Dueños, Solo minúsculas
owners = ['megamaster12', 'linkkg', 'milton797']
# Depuración

debug = False  # Printear cosas extra para depuración
debugchats = ['pythonrpg', 'PM']  # Conexiones donde se printeará lo recibido
# ignored commands onRaw
ignored_rcmd_ = "i u OK".split() + ['']
prefijos = '| %'.split()  # Uno o más prefijos separados por espacio


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
        self.setNameColor("FF0000")  # el color del nombre de usuario en hexadecimal
        self.setFontColor("00FF33")  # el color de la letra
        self.setFontFace("Typewriter")  # el tipo de letra, usas los tipos de letra que hay en chatango
        self.setFontSize(12)  # tamaño de la letra, supuestamente el maximo es 14 sin premium
        self.enableBg()  # por si le pones bg al bot, esto se lo activa
    
    def onConnect(self, room):
        """Al haberse conectado a una sala de chat"""
        print('[{}][{}] Conectado. Intentos: {}'.format(time.strftime("%I:%M:%S %p"), room.name,
                                                        room.attempts))
    
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
            if len(message.body.split()) > 1:  # Si el mensaje contenía más de una palabra
                # El comando será la primera palabra y los argumentos serán el resto
                # El .replace es para que puedas usar el simbolo ' en tus mensajes
                cmd, args = message.body.split(" ", 1)
            else:
                # El comando será el mensaje(1 palabra) y los argumentos serán algo vacío
                cmd, args = message.body, ""

            # cmd= comando usado #args=argumentos que recibe el comando
            # Comprobar si se usó el prefijo y separarlo del comando
            if cmd and cmd[0] in prefijos:
                prfx = True
                cmd = cmd[1:].lower()
            else:
                prfx = False
            if prfx:  # Si se uso el prefijo
                ################################################################
                # Aqui comienzan los comandos, puedes poner los que quieras mientras esten dentro
                ################################################################
                if cmd == "all":
                    usuarios = sorted(room.shownames)
                    usuarios = '{} y {}'.format(', '.join(usuarios[:-2]), usuarios[-1])
                    room.message("Lista completa de los usuarios: " + usuarios)
                    # usuarios=sorted([(x.showname + ( ('(%s)' % len(x._getSessionIds(room))) if len(
                    # x._getSessionIds(room)) > 1 else '')) for x in
                    #                              room._getUserlist(1)])
                elif cmd in ['conecta', 'join'] and user.name in owners:
                    if self.joinRoom(args):
                        room.message("Conectado ♪")
                    else:
                        room.message("No puedo ir...")

                elif cmd == "desconecta" and user.name in owners:
                    if args.lower() in self._rooms:
                        self.leaveRoom(args)
                        room.message("Desconectado")
                    else:
                        room.message("No estoy conectado a " + args)


                elif cmd in ["donde", "where"]:
                    salas = ["{} ({})".format(x.name, x.userCount) for x in self.rooms]
                    room.message("Estoy en: " + ', '.join(salas))
                
                elif cmd == "baila":
                    room.message("o(^^o) ---- ^(oo)^ ---- (o^^)o")

                elif cmd in ["say", "write"]:
                    room.message(args)

                ################################################################
                # Sección para desarrolladores
                ################################################################
                if user.name in owners:
                    if cmd in ['eval', 'ev'] and args:
                        args = message.fullbody.split(' ', 1)[1]
                        try:
                            room.message(str(eval(args)))
                        except Exception as err:
                            try:
                                room.message(str(exec(args)))
                            except Exception as e:
                                raise Exception(str(e) + str(err))
                    if cmd in ['ex']:
                        room.message(str(exec(args)))
        except Exception as e:
            room.message(str(e))
    
    def onPMConnect(self, pm):
        """
        Al conectarse al PM
        @param pm: El controlador del PM
        @return: None
        """
        print("[{}] Conectado al PM como {}".format(time.strftime('%I:%M:%S %p'), pm.currentname))

    def onPMMessage(self, pm, user, message):
        """
        Al recibir un mensaje en el PM
        @param pm: El PM
        @param user: El usuario que manda el mensaje
        @param message: El mensaje recibido
        """
        print("[{}][{:_^10.10}][{}]:{}".format(time.strftime("%I:%M:%S %p"), pm.name, user.name, message))
    
    def onRaw(self, room, raw):
        """Al recibir un comando de chatango"""
        if debug and raw.split(':')[0] not in ignored_rcmd_:
            if room.name in debugchats:
                print('[{0}][{1:_^10.10}]{2}'.format(time.strftime("%I:%M:%S %p"), room.name, raw), file = sys.stderr)

    def onReconnect(self, room):
        """
        Al reconectarse a una sala
        @param room: Sala a la que se ha reconectado
        """
        print('[{}]Reconectado en {} intentos '.format(room.name, room.attempts))


accounts = [('Account1', 'Password1'),
            ('Cuenta2', 'Clave2')]
# bot = Mibot.easy_start(['pythonrpg'], USERNAME,PASSWORD ,pm= True) # También es válido así
try:
    bot = Mibot.easy_start(['pythonrpg'], pm = True, accounts = accounts)
except socket.gaierror as e:  # En caso de que no haya internet
    print("No hay internet, haz algo O.o")
