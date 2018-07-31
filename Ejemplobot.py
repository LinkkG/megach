#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Archivo de prueba para mi versión del ch
Incluirá las opciones básicas e iré añadiendo más poco a poco
Versión 1.5.2
"""
# Módulos básicos
import math
import megach
import os
import random
import socket
import string
import sys
import time
import urllib.request as urlreq
import urllib.parse as urlparse

version = '1.5.2'
#  Módulos del bot
# TODO Interfaz gráfica
# Dueños, Solo minúsculas
owners = ['megamaster12', 'linkkg', 'milton797']
# Depuración
class config:
    botnames = 'e15 examplebot boteto'.split()
    debug = False  # Printear cosas extra para depuración
    debugchats = ['pythonrpg', 'PM']  # Conexiones donde se printeará lo recibido
    # ignored commands onRaw
    prefijos = '| %'.split()  # Uno o más prefijos separados por espacio



class Mibot(megach.Gestor):
    """
    Mi implementación del bot
    También es posible crearla de la siguiente manera
    class Mibot(megach.RoomManager):
    """

    def onInit(self):
        """Espacio para ejecutar acciones de carga de información u otras cosas"""
        print("Inicio del BOT")
        self.setNameColor("FF0000")  # el color del nombre de usuario en hexadecimal
        self.setFontColor("0000FF")  # el color de la letra
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
            nick = '@' + user
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
                cmd, args = message.body.lower(), ""
            
            # cmd= comando usado #args=argumentos que recibe el comando
            # Comprobar si se usó el prefijo y separarlo del comando
            if cmd and cmd[0] in config.prefijos:
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

                elif cmd in ['sim', 'simi']:
                    clave, definicion = [x.strip() for x in args.split(":", 1)]
                    archivo = open(os.path.join(os.getcwd(), 'simi.json'), "a", encoding = 'utf-8')
                    archivo.write(clave + ":" + definicion + "\n")
                    resultado = "Respuesta guardada correctamente ;)"
                    room.message(resultado)

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
                            except Exception as e2:
                                raise Exception(str(e2) + str(err))
                    if cmd in ['ex']:
                        room.message(str(exec(args)))
            else:
                mention = False
                cmd = message.body
                resultado = ''
                splitted = ''.join(x for x in cmd if x.isalnum() or x in [' ']).split()
                ######################################################
                # NO PREFIX USED

                for x in config.botnames + [room.user.showname.lower()]:
                    if x in splitted:
                        cmd = ''.join(cmd.split(x)).strip()  # Clear mentions
                        mention = True
                if not mention:
                    return  # Nothing left here
                if len(splitted) == 1:
                    room.message(random.choice(['¿Que pasa?', '¿Que quiere prro v:<', '¿Necesitas hamor?']))
                    return
                ######################################################
                # SIMI SECTION
                try:
                    consulta, definicion = define('simi.json', cmd)
                    plantilla = string.Template(definicion)
                    if room:
                        donde = room.name
                    else:
                        donde = "Mensajería Privada"
                    resultado = plantilla.safe_substitute(**{
                        'nick':    nick,
                        'r':       '\r',
                        'prefix':  random.choice(config.prefijos),
                        'prefijo': random.choice(config.prefijos),
                        'name':    self.user.name,
                        'room':    donde
                        })
                    if not resultado:
                        resultado = 'No answer, sorry :v'
                except Exception as e15:
                    resultado = ' Simi error ' + str(e15)
                room.message(resultado)

        except Exception as e4:
            room.message(str(e4))
    
    def onPMConnect(self, pm):
        """
        Al conectarse al PM
        @param pm: El PM
        """
        print("[{}] Conectado al PM como {}".format(time.strftime('%I:%M:%S %p'), pm.currentname))

    def onPMOfflineMessage(self, pm, user, message):
        """
        Al recibir un mensaje estando offline
        @param pm: El PM
        @param user: Remitente
        @param body: Mensaje recibido
        """
        print("[{}][{:_^10.10}][{}]:{}".format(time.strftime("%I:%M:%S %p"), pm.name, user, message))

    def onPMMessage(self, pm, user, message):
        """
        Al recibir un mensaje en el PM
        @param pm: El PM
        @param user: El usuario que manda el mensaje
        @param message: El mensaje recibido
        """
        print("[{}][{:_^10.10}][{}]:{}".format(time.strftime("%I:%M:%S %p"), pm.name, user.name, message))
    

    def onReconnect(self, room):
        """
        Al reconectarse a una sala
        @param room: Sala a la que se ha reconectado
        """
        print('[{}]Reconectado en {} intentos '.format(room.name, room.attempts))


def crea(archivo, texto):
    """
    Crea una definicion en un archivo con formato indicado por dos puntos
    @param archivo: Archivo al que agregar la definición
    @param texto: Texto que incluya dos puntos
    """
    if ':' not in texto:
        return False
    archivo = open(archivo, 'a', encoding = 'utf-8')
    clave, valor = texto.split(':', 1)
    archivo.write('%s:%s' % (clave.title(), valor + '\n'))
    return True


def define(archivo, texto = '', match = 1):
    """Busca una definición exacta en un archivo.
    Formato de archivo->frase:defincion"""
    if not os.path.exists(archivo):  # Si no existe
        open(archivo, 'a', encoding = 'utf-8').close()  # Crearlo
    texto = limpiaTexto(texto)
    archivo = open(archivo, encoding = 'utf-8')
    # Separar texto para buscar por palabras
    sep = texto.split()
    # Crear un arreglo con las lineas del archivo
    lineas = archivo.read().splitlines()
    # Cada uno de los valores que tenga coincidencias con la busqueda
    matches = []
    for x in lineas:
        if any([z in limpiaTexto(x.split(':', 1)[0]) for z in sep if len(z) >= match]):
            matches.append(x)
    # Nivel 2
    # Buscar la mayor coincidencia
    mayor = -1
    filtro = []
    if matches:
        for x in matches:
            actual = len(
                    [a for a in sep if a in limpiaTexto(x.split(':')[0]).split()])
            if actual > mayor:
                mayor = actual
                filtro.clear()
                filtro.append(x)
            elif actual == mayor:
                filtro.append(x)
        a, b = random.choice(filtro).split(':', 1)
        return a, b
    else:
        return '', ''


def limpiaTexto(texto):
    """Regresa texto en minúsculas y sin acentos"""
    texto = texto.lower().strip()
    limpio = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "@": "", "?": "", "!": "", ",": "", ".": "", "¿": ""
        }
    for y in limpio:
        if y in texto:
            texto = texto.replace(y, limpio[y])
    return texto


def mysimianswer(cmd, **kw):
    """Regresa una respuesta del simi.json al lado del fichero"""
    ruta = os.path.join(os.getcwd(), 'simi.json')
    consulta, definicion = define(ruta, cmd)
    plantilla = string.Template(definicion)
    if 'room' in kw:
        donde = kw['room'].name
    else:
        donde = "Mensajería Privada"
    resultado = plantilla.safe_substitute(**kw)
    return resultado or 'No answer, sorry :v'

accounts = [('Account1', 'Pass1'),
            ('Cuenta2', 'Clave2')]
try:
    # bot = Mibot.easy_start(['pythonrpg'], USERNAME,PASSWORD ,pm= True) # También es válido así
    bot = Mibot.easy_start(['pythonrpg'], pm = True, accounts = accounts)
except socket.gaierror as e:  # En caso de que no haya internet
    print("No hay internet, haz algo O.o")
