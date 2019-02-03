#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Archivo de prueba para mi versión del ch
Autor: Megamaster12
Incluirá las opciones básicas e iré añadiendo más poco a poco
Versión 1.5.3
"""
################################################################
# No brrar las dos primeras lineas, son opciones de python para el archivo
# Estos son comentarios, la compu no los lee y el python los ignora
# Se escriben para uno mismo, o para otro programador|
# Acostumbrate a hacerlo siempre
# Lo que este a la derecha de # es ignorado
# Asi que no lo pongas a la izquierda del codigo u.u
################################################################
# Módulos básicos
import megach  # Mi megach, es una librería pública para chatango
import os  # Para acceder a cosas específicas de tu sistema operativo
import random  # Para seleccion aleatoria
import socket  # Para administrar conexiones
import string  # Para operaciones con cadenas de texto
import sys  # Para detalles de tu versión de python
import time  # Para operaciones con la hora
import urllib.request as urlreq  # Consultas web
import urllib.parse as urlparse  # Lectura de datos web

version = '1.5.3'



class config:
    botnames = 'e15 examplebot boteto'.split()
    # Dueños, Solo minúsculas
    owners = ['megamaster12', 'linkkg', 'milton797']
    # Uno o más prefijos separados por espacio
    prefijos = '% $'.split()
    # Ruta para el archivo simi
    rutasim = os.path.join(os.getcwd(), 'simi.json')


class Mibot(megach.Gestor):
    """
    Mi implementación del bot
    También es posible crearla de la siguiente manera
    class Mibot(megach.RoomManager):
    """

    def onInit(self):
        """
        Espacio para ejecutar acciones de carga de información u otras
        cosas que se deben hacer al inicio
        """
        print("Inicio del BOT")
        self.setNameColor("FF0000")  # color del nombre en hexadecimal
        self.setFontColor("0000FF")  # color de la letra en hexadecimal
        self.setFontFace("Typewriter")  # Fuente del bot
        self.setFontSize(12)  # Tamaño de fuente, el maximo es 14 sin premium
        self.enableBg()  # Si el bot tiene premium, activar el bg

    def onMessage(self, room, user, message):
        """Al recibir un mensaje en una sala"""
        try:
            nick = '@' + user
            ubic = "".join({
                32768: "MOD", 256: "RED", 0: "NORMAL", 2048: "BLUE",
                2304:  "BLUE+RED"
                }.get(
                    message.channel))
            print("[{0:_^10.10}][{4}][{3}] {1}: {2} ".format(
                    room.name,
                    user.name.title(),
                    message.body.replace("&#39;", "'"),
                    time.strftime("%I:%M:%S %p"),
                    ubic))
            if user == room.user:
                return

            if len(
                    message.body.split()) > 1:  # Si el mensaje contenía más
                # de una palabra
                # El comando será la primera palabra y los argumentos serán
                # el resto
                # El .replace es para que puedas usar el simbolo ' en tus
                # mensajes
                cmd, args = message.body.split(" ", 1)
            else:
                # El comando será el mensaje(1 palabra) y los argumentos
                # serán algo vacío
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
                # Aqui comienzan los comandos, puedes poner los que quieras
                # mientras esten dentro
                ################################################################
                if cmd == "all":  # Decir los nombres de todos los usuarios
                    # en la sala
                    usuarios = sorted(room.shownames)
                    usuarios = '{} y {}'.format(', '.join(usuarios[:-2]),
                                                usuarios[-1])
                    room.message("Lista completa de los usuarios: " + usuarios)

                elif cmd == "baila":  # Enviar un mensaje bailando,
                    # si lo cambias por un gif animado queda mejor
                    room.message("o(^^o) ---- ^(oo)^ ---- (o^^)o")

                # Conectarse a una sala distinta
                elif cmd in ['conecta', 'join'] and user.name in config.owners:
                    if self.joinRoom(args):
                        room.message("Conectado ♪")
                    else:
                        room.message("No puedo ir...")

                # Desconectarse de alguna sala
                elif cmd == "desconecta" and user.name in config.owners:
                    if args.lower() in self._rooms:
                        self.leaveRoom(args)
                        room.message("Desconectado")
                    else:
                        room.message("No estoy conectado a " + args)

                # Mencionar las salas donde el bot está conectado
                elif cmd in ["donde", "where"]:
                    salas = ["{} ({})".format(x.name, x.userCount) for x in
                             self.rooms]
                    room.message("Estoy en: " + ', '.join(salas))

                # Repetir un mensaje
                elif cmd in ["say", "write"]:
                    room.message(args)

                # Enseñarle una frase al simi del bot
                elif cmd in ['sim', 'simi']:
                    clave, definicion = [x.strip() for x in args.split(":", 1)]
                    archivo = open(os.path.join(os.getcwd(), 'simi.json'), "a",
                                   encoding = 'utf-8')
                    archivo.write(clave + ":" + definicion + "\n")
                    resultado = "Respuesta guardada correctamente ;)"
                    room.message(resultado)

                ################################################################
                # Sección para desarrolladores
                ################################################################
                if user.name in config.owners:
                    if cmd in ['eval', 'ev'] and args:
                        args = message.fullbody.split(' ', 1)[1]
                        try:
                            room.message(str(eval(args)))
                        except Exception as err:
                            try:
                                room.message(str(exec(args)))
                            except Exception as e2:

                                raise Exception(str(e2) + '---' + str(err) + (
                                        str(e2) == str(
                                        err) and 'son iguales' or 'no me '
                                                                  'salen '
                                                                  'igual :v'))
                    if cmd in ['ex']:
                        room.message(str(exec(args)))
            else:  # if prefix, este es el else
                cmd = message.body
                splitted = ''.join(x for x in cmd if
                                   x.isalnum() or x in [' ']).lower().split()
                ######################################################
                # NO PREFIX USED
                for x in config.botnames + [room.user.name.lower()]:
                    if x in splitted:
                        cmd = ''.join(cmd.split(x)).strip()  # Clear mentions
                        break
                else:
                    return  # No mentions al bot
                if len(splitted) == 1:
                    room.message(random.choice(
                            ['¿Que pasa?', '¿Que quiere prro v:<',
                             '¿Necesitas hamor?']))
                    return
                ######################################################
                # SIMI SECTION
                try:
                    resultado = mysimianswer(cmd, nick = nick, r = '\r',
                                             prefix = random.choice(
                                                     config.prefijos),
                                             prefijo = random.choice(
                                                     config.prefijos),
                                             name = room.user.showname,
                                             room = room)
                    if not resultado:
                        resultado = 'No answer, sorry :v'
                except Exception as e15:
                    resultado = ' Simi error ' + str(e15)
                #######################################################
                room.message(resultado)

        except Exception as e4:
            room.message(str(e4))

    def onPMMessage(self, pm, user, message):
        """
        Al recibir un mensaje en el PM
        @param pm: El PM
        @param user: El usuario que manda el mensaje
        @param message: El mensaje recibido
        """
        print("[{}][{:_^10.10}][{}]:{}".format(time.strftime("%I:%M:%S %p"),
                                               pm.name, user.name, message))

    def onPMOfflineMessage(self, pm, user, message):
        """
        Al recibir un mensaje estando offline
        @param message: Mensaje recibido
        @param pm: El PM
        @param user: Remitente
        @param body: Mensaje recibido
        """
        print("[{}][{:_^10.10}][{}]:{}".format(time.strftime("%I:%M:%S %p"),
                                               pm.name, user, message))

    def onConnect(self, room):
        """Se activa al conectarse a una sala de chat"""
        print('[%s][%s] Conectado como %s en %s intento%s' % (
            time.strftime("%I:%M:%S %p"),
            room,
            room.user,
            room.attempts,
            room.attempts > 1 and 's' or ''
            )
              )

    def onPMConnect(self, pm):
        """Al conectarse al PM"""
        print('[%s][%s] Conectado como %s en %s intento%s' % (
            time.strftime("%I:%M:%S %p"),
            pm,
            pm.user,
            pm.attempts,
            pm.attempts > 1 and 's' or ''
            )
              )

    def onReconnect(self, room):
        """
        Al reconectarse a una sala
        @param room: Sala a la que se ha reconectado
        """
        print('[%s][%s]Reconectado en %s intento%s' % (
            time.strftime("%I:%M:%S %p"),
            room,
            room.attempts,
            room.attempts > 1 and 's' or '')
              )

    def onDisconnect(self, room):
        """Al desconectarse de una sala"""
        print('[%s][%s] Desconectado' % (time.strftime("%I:%M:%S %p"), room))


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
        if any([z in limpiaTexto(x.split(':', 1)[0]) for z in sep if
                len(z) >= match]):
            matches.append(x)
    # Nivel 2
    # Buscar la mayor coincidencia
    mayor = -1
    filtro = []
    if matches:
        for x in matches:
            actual = len(
                    [a for a in sep if
                     a in limpiaTexto(x.split(':')[0]).split()])
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
    resultado = plantilla.safe_substitute(**kw)
    return resultado or 'No answer, sorry :v'


accounts = [('Account1', 'Pass1'),
            ('Cuenta2', 'Clave2')]
try:
    # bot = Mibot.easy_start(['pythonrpg'], USERNAME,PASSWORD ,pm= True) #
    # También es válido así
    bot = Mibot.easy_start(['pythonrpg'], pm = True, accounts = accounts)
except socket.gaierror as e:  # En caso de que no haya internet
    print("No hay internet, haz algo O.o")
