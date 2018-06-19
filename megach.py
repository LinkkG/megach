#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: megach.py
Title: Librería de chatango
Original Author: megamaster12 <supermegamaster32@gmail.com>
Current Maintainers and Contributors:
    Megamaster12
Version: M1.7.2
Description:
    Una librería para conectarse múltiples salas de Chatango
    Basada en las siguientes fuentes
        original chatango flash code
        cherry.py          https://github.com/Sweets/Cherry-Blossom
        ch.py              https://github.com/Nullspeaker/ch.py
        ch.py and _ws.py   https://github.com/TheClonerx/chatango-bot
    Tiene soporte para varias cosas, incluyendo:
        envío de mensajes,
        cambio de fuentes y colores,
        detección de eventos
        baneos
        marcadores
Información de contacto:
    Cualquier duda, comentario o sugerencia puedes buscarme en chatango y contactarme.
    Sería genial si incluyeras lo siguiente en tu mensaje:
        # Tu usuario y tu bot (opcional)
        # Linea de este archivo, nombre del método o sección de la que hablas
        # Descripción de tu problema o solicitud
Megamaster12 changelog
    HTML_CODES
    Added channel support for reading and messaging
    Added mod channel support
    badge support for Room and Message
    Added websocket support for rooms
        Now can listen mod channel and all received commands
################################################################
# License
################################################################
# Copyright 2011 Megamaster12
# This program is distributed under the terms of the GNU GPL.
"""
################################################################
# Imports
################################################################
import base64
from collections import namedtuple, deque
import hashlib
import html as HTML
import os
import random
import re
import select
import socket
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

################################################################
# Depuración
################################################################
debug = False
################################################################
# Cosas del servidor y las cuentas
################################################################
w12 = 75
sv2 = 95
sv4 = 110
sv6 = 104
sv8 = 101
sv10 = 110
sv12 = 116
tsweights = [['5', w12], ['6', w12], ['7', w12], ['8', w12], ['16', w12],
             ["17", w12], ["18", w12], ["9", sv2], ["11", sv2], ["12", sv2],
             ["13", sv2], ["14", sv2], ["15", sv2], ["19", sv4], ["23", sv4],
             ["24", sv4], ["25", sv4], ["26", sv4], ["28", sv6], ["29", sv6],
             ["30", sv6], ["31", sv6], ["32", sv6], ["33", sv6], ["35", sv8],
             ["36", sv8], ["37", sv8], ["38", sv8], ["39", sv8], ["40", sv8],
             ["41", sv8], ["42", sv8], ["43", sv8], ["44", sv8], ["45", sv8],
             ["46", sv8], ["47", sv8], ["48", sv8], ["49", sv8], ["50", sv8],
             ["52", sv10], ["53", sv10], ["55", sv10], ["57", sv10], ["58", sv10],
             ["59", sv10], ["60", sv10], ["61", sv10], ["62", sv10], ["63", sv10],
             ["64", sv10], ["65", sv10], ["66", sv10], ["68", sv2], ["71", sv12],
             ["72", sv12], ["73", sv12], ["74", sv12], ["75", sv12], ["76", sv12],
             ["77", sv12], ["78", sv12], ["79", sv12], ["80", sv12], ["81", sv12],
             ["82", sv12], ["83", sv12], ["84", sv12]]
_maxServernum = sum(map(lambda x: x[1], tsweights))

_users = dict()


def _getAnonId(num, ts) -> str:
    """
    Obtener una id de anon
    @param num: El tiempo en que se conectó el anon, debe ser un string con un número entero
    @param ts: El tiempo
    @return:
    """
    ts = '3452' if not ts else ts
    __reg5 = ''
    __reg1 = 0
    while __reg1 < len(num):
        __reg4 = int(num[__reg1])
        __reg3 = int(ts[__reg1])
        __reg2 = str(__reg4 + __reg3)
        __reg5 += __reg2[-1:]
        __reg1 += 1
    return __reg5


def getanonname(num: str, ssid: str) -> str:
    """Regresa el nombre de un anon usando su numero y tiempo de conexión"""
    num, ssid = num[-4:], ssid[-4:]
    return 'anon' + _getAnonId(num, ssid).zfill(4)


def _genUid():
    """Generar una uid ALeatoria de 16 dígitos"""
    return str(random.randrange(10 ** 15, 10 ** 16))


def getServer(group: str) -> str:
    """
    TODO llamar a get_server_number(group_name)
    :param group:
    :return str:
    """
    group = group.replace("_", "q")
    group = group.replace("-", "q")
    fnv = float(int(group[0:min(5, len(group))], 36))
    lnv = group[6: (6 + min(3, len(group) - 5))]
    if lnv:
        lnv = float(int(lnv, 36))
        lnv = max(lnv, 1000)
    else:
        lnv = 1000
    num = (fnv % lnv) / lnv

    cumfreq = 0
    sn = 0
    for wgt in tsweights:
        cumfreq += float(wgt[1]) / _maxServernum
        if num <= cumfreq:
            sn = int(wgt[0])
            break
    return "s" + str(sn) + ".chatango.com"


################################################################
# Cosas de los mensajes
################################################################
Channels = {
    "white":  0,
    "red":    256,
    "blue":   2048,
    "shield": 64,
    "staff":  128,
    "mod":    32780
    }  # TODO darle uso
BigMessage_Cut = 1
BigMessage_Multiple = 0
Number_of_Threads = 1


def _clean_message(msg: str) -> [str, str, str]:
    """
    TODO Revisar carácteres comilla y escapes en mensajes
    Clean a message and return the message, n tag and f tag.
    @type msg: str
    @param msg: the message
    @rtype: str, str, str
    @returns: cleaned message, n tag contents, f tag contents
    """
    n = re.search("<n(.*?)/>", msg)
    if n:
        n = n.group(1)
    f = re.search("<f(.*?)>", msg)
    if f:
        f = f.group(1)
    msg = re.sub("<n.*?/>", "", msg)
    msg = re.sub("<f.*?>", "", msg)
    msg = _strip_html(msg)
    msg = _unescape_html(msg)
    return msg, n, f


def _strip_html(msg):
    """
    Strip HTML.
    TODO Incluir todo lo relacionado con html
    """
    li = msg.split("<")
    if len(li) == 1:
        return li[0]
    else:
        ret = list()
        for data in li:
            data = data.split(">", 1)
            if len(data) == 1:
                ret.append(data[0])
            elif len(data) == 2:
                if data[0].startswith("br"):
                    ret.append("\n")
                ret.append(data[1])
        return "".join(ret)


def _unescape_html(args):
    args = args.replace("&lt;", "<")
    args = args.replace("&gt;", ">")
    args = args.replace('&#39;', "'")
    args = args.replace('&quot;', '"')
    args = args.replace("&amp;", "&")  # Esto debe ir al final
    return args
    # o.o &amp; &#39; &quot; &amp;amp; &amp;#39; &amp;quot;


def _parseNameColor(n: str) -> str:
    """Return the name color from message"""
    # probably is already the name
    return _strip_html(n)[1]


def _parseFont(f):
    """
    Lee el contendido de un etiqueta f y regresa
    color fuente y tamaño
    TODO revisar posibles errores
    ' xSZCOL="FONT"'
    :param f: El texto con la etiqueta f incrustada
    :return: Fuente, Color, Tamaño
    """
    matchs = re.findall('x(\d+){0,2}([0-9a-fA-F]{3,6})="(\d)"', f)
    if matchs and len(matchs[0]) == 3:
        return matchs[0]
    else:
        return None, None, None


################################################################
# Cosas de la conexión
################################################################


class Struct:
    """
    Una clase dinámica que recibe sus propiedades como parámetros
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)


class WS:
    """
    Agrupamiento de métodos estáticos para encodear y chequear frames en conexiones del protocolo WebSocket
    """
    # TODO revisar
    FrameInfo = namedtuple("FrameInfo", ["fin", "opcode", "masked", "payload_length"])
    CONTINUATION = 0
    TEXT = 1
    BINARY = 2
    CLOSE = 8
    PING = 9
    VERSION = 13

    @staticmethod
    def genseckey():
        """Genera una clave de Seguridad Websocket"""
        return base64.encodebytes(os.urandom(16)).decode('utf-8').strip()

    @staticmethod
    def encode(payload: object) -> bytes:
        """
        Encodea un mensaje y lo enmascara con las reglas obligatorias del protocolo websocket
        :param payload:El string o arreglo de bytes a encodear para websocket
        :return: El arreglo de Bytes enmascarado
        """
        opcode = WS.TEXT
        pl = payload
        frame = bytearray()
        mask = os.urandom(4)
        if isinstance(pl, str):
            pl = pl.encode("utf-8", "replace")
        frame.append(opcode | 128)
        int()
        if len(pl) <= 125:
            frame.append(len(pl) | 128)
        elif len(pl) <= 65535:
            frame.append(126 | 128)
            frame += len(pl).to_bytes(2, "big")
        else:
            frame.append(127 | 128)
            frame += len(pl).to_bytes(8, "big")
        frame += mask
        frame += bytes(x ^ mask[i % 4] for i, x in enumerate(pl))
        return bytes(frame)

    @staticmethod
    def checkFrame(buffer: bytes):
        """
        returns False if the buffer doesn't starts with a valid frame
        returns the size of the frame in success
        """
        if len(buffer) < 2:
            return False
        min_size = 2
        payload_length = 0
        if buffer[1] & 128:
            min_size += 4
        if (buffer[1] & 127) <= 125:
            payload_length = buffer[1] & 127
        elif (buffer[1] & 127) == 126:
            min_size += 2
            if len(buffer) < 4:
                return False
            payload_length += int.from_bytes(buffer[2:4], "big")
        elif (buffer[1] & 127) == 127:
            min_size += 8
            if len(buffer) < 10:
                return False
            payload_length += int.from_bytes(buffer[2:10], "big")
        if len(buffer) < (min_size + payload_length):
            return False
        return min_size + payload_length

    @staticmethod
    def checkHeaders(headers):
        """
        Regresa False si los headers son inválidos para un handshake websocket
        Regresa un diccionario con los headers
        @param headers:
        @return: dict/None
        """
        if isinstance(headers, bytes):
            headers = WS.getHeaders(headers)
        version = headers.get('version')
        if version:
            version = version.split("/")[1]
            version = tuple(int(x) for x in version.split("."))
            if version[0] < 1:
                return False
            if version[1] < 1:
                return False
        if "upgrade" not in headers or headers["upgrade"].lower() != "websocket":
            return False
        elif "connection" not in headers or headers["connection"].lower() != "upgrade":
            return False
        elif "sec-websocket-accept" not in headers:
            return False
        return headers["sec-websocket-accept"]

    @staticmethod
    def frameInfo(buffer: bytes) -> FrameInfo:
        """
        Regresa una tupla con la descripción de un frame
        @param buffer: Frame que se va a examinar
        @return: objeto FrameInfo
        """
        r = WS.checkFrame(buffer)
        if not r:
            raise ValueError("buff is not a valid frame")
        payload_length = 0
        if (buffer[1] & 127) <= 125:
            payload_length = buffer[1] & 127
        elif (buffer[1] & 127) == 126:
            payload_length += int.from_bytes(buffer[2:4], "big")
        elif (buffer[1] & 127) == 127:
            payload_length += int.from_bytes(buffer[2:10], "big")
        # noinspection PyCallByClass
        return WS.FrameInfo(bool(buffer[0] & 128), buffer[0] & 15, bool(buffer[1] & 128),
                            payload_length)

    @staticmethod
    def getHeaders(headers: bytes) -> dict:
        """
        Recibe una serie de datos, comprueba si es un handshake válido para websocket y retorna un diccionario
        @param headers: Los datos recibidos
        @return: Los headers en formato dict
        """
        if isinstance(headers, (bytes, bytearray)):
            if b"\r\n\r\n" in headers:
                headers, _ = headers.split(b"\r\n\r\n", 1)
            headers = headers.decode()
        if isinstance(headers, str):
            headers = headers.splitlines()
        if isinstance(headers, list):  # Convertirlo en diccionario e ignorar los valores incorrectos
            headers = map((lambda x: x.split(':', 1) if len(x.split(':')) > 1 else ('', '')), headers)
            headers = {z.lower().strip(): y.lower().strip() for z, y in headers if z and y}
        return headers

    @staticmethod
    def getPayload(buffer: bytes):
        """
        Decodifica un mensaje enviado por el servidor y lo vuelve legible para usarlo más fácil
        :param buffer: Bytes que serán procesados
        :return: Un string procesado o [int,string procesado]
        """
        info = WS.frameInfo(buffer)
        if not info.payload_length:
            payload = b""
        elif info[2]:  # if masked
            payload = WS.unmask_buff
        else:
            payload = buffer[-(info[3]):]
        if info[1] == WS.TEXT and info.fin:
            return payload.decode("utf-8", "replace")
        elif info[1] == WS.CLOSE:
            return int.from_bytes(payload[:2], "big"), payload[2:].decode("utf-8", "replace")
        return payload

    @staticmethod
    def getServerSeckey(headers: bytes, key: bytes = 'b') -> str:
        """
        Calcula la respuesta que debe dar el servidor según la clave de seguridad que se le envió
        @param headers: Los valores enviados al servidor. Si se recibe, se ignorará el parámetro key
        @param key: La clave que se le envió.
        @return: Clave que debería enviar el servidor (string)
        """
        if headers:
            key = WS.getHeaders(headers)['sec-websocket-key'].encode()
        sha = hashlib.sha1(key + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
        return base64.b64encode(sha.digest()).decode()

    @staticmethod
    def unmask_buff(buffer: bytes) -> bytes:
        """
        Recibe bytes con una mascara de websocket y la remueve para leerlos con fácilidad
        :param buffer: Los datos enmascarados
        :return: Los mismos datos sin su máscara
        """
        mask = buffer[:4]
        return bytes(x ^ mask[i % 4] for i, x in enumerate(buffer[4:]))


def User(name: str, **kwargs):
    """
    Un def que representa a la clase _User. Si el usuario ya existe, mejor regresa ese
    y en caso de que no, lo crea y lo agrega a la lista
    :param name: Nombre del usuario
    :param kwargs: Datos que contendrá el usuario
    :return: Usuario nuevo o encontrado en la lista
    """
    if name is None:
        name = ""
    user = _users.get(name.lower())

    if not user:
        user = _User(name = name, **kwargs)
        _users[name.lower()] = user
    user._showname = name  # TODO
    return user


class _User:
    # TODO revisar
    def __repr__(self):
        return "<User: %s>" % (self.name)
    
    def __init__(self, name, **kwargs):
        self._fontColor = '0'
        self._fontFace = '0'
        self._fontSize = 12
        self._ip = ''
        self._isanon = False
        self._mbg = False
        self._msgs = list()  # TODO Mantener historial reciente de un usuario
        self._mrec = False
        self._name = name.lower()
        self._nameColor = '000'
        self._puids = dict()
        self._showname = name
        self._sids = dict()
        for attr, val in kwargs.items():
            if val is None:
                continue
            setattr(self, '_' + attr, val)
        # TODO Más cosas del user

    # Propiedades
    @property
    def ip(self):
        return self._ip

    @property
    def isanon(self):
        return self._isanon

    @property
    def name(self):
        return self._name

    @property
    def nameColor(self):
        return self._nameColor

    @property
    def showname(self):
        return self._showname.strip('!#')

    def setName(self, value):
        self._name = value.lower()
        self._showname = value
    
    def _getSessionIds(self, room = None):
        if room:
            return self._sids.get(room, set())
        else:
            return set.union(*self._sids.values())

    def _getRooms(self):
        return self._sids.keys()

    def _getRoomNames(self):
        return [room.name for room in self._getRooms()]

    def _getFontColor(self):
        return self._fontColor

    def _getFontFace(self):
        return self._fontFace

    def _getFontSize(self):
        return self._fontSize

    sessionids = property(_getSessionIds)
    rooms = property(_getRooms)
    roomnames = property(_getRoomNames)
    fontColor = property(_getFontColor)
    fontFace = property(_getFontFace)
    fontSize = property(_getFontSize)

    ####
    # Util
    ####
    def addSessionId(self, room, sid):
        """ TODO
        Agrega una sesión a una sala del usuario
        :param room: Sala donde tiene esa sesión conectado
        :param sid: Sesión del usuario
        """
        if room not in self._sids:
            self._sids[room] = set()
        self._sids[room].add(sid)

    def addPersonalUserId(self, room, puid):
        """TODO comprobar"""
        if room not in self._puids:
            self._puids[room] = set()
        self._puids[room].add(puid)

    def removeSessionId(self, room, sid):
        if room in self._sids:
            self._sids[room].remove(sid)
            if len(self._sids[room]) == 0:
                del self._sids[room]

class Message:
    """
    Clase que representa un mensaje en una sala o en privado
    TODO revisar
    """

    def __init__(self, **kw):
        """
        :param kw:Parámetros del mensaje
        """
        self._msgid = None
        self._time = None
        self._user = None
        self._body = None
        self._room = None
        self._raw = ""
        self._ip = None
        self._unid = ""
        self._puid = ""
        self._uid = ""  # TODO ELIMINAR
        self._nameColor = "000"
        self._fontSize = 12
        self._fontFace = "0"
        self._fontColor = "000"
        self._channel = 0
        self._badge = 0
        for attr, val in kw.items():
            if val is None:
                continue
            setattr(self, "_" + attr, val)

    def __repr__(self):
        return self.body.rstrip('\n')
    
    def __str__(self):
        return '[%s][%s]:%s' % (self.room.name, self.user.name, self.body)

    ####
    # Properties
    ####
    @property
    def badge(self):
        return self._badge

    @property
    def body(self):
        return self._body.replace('\n', '').replace('  ', ' ')

    @property
    def channel(self):
        return self._channel

    @property
    def fontColor(self):
        return self._fontColor

    @property
    def fontFace(self):
        return self._fontFace

    @property
    def fontSize(self):
        return self._fontSize

    @property
    def ip(self):
        return self._ip

    @property
    def msgid(self):
        return self._msgid

    @property
    def nameColor(self):
        return self._nameColor

    @property
    def puid(self):
        return self._puid

    @property
    def raw(self):
        return self._raw

    @property
    def room(self):
        return self._room

    @property
    def uid(self):
        return self._puid

    @property
    def unid(self):
        return self._unid
    
    @property
    def user(self) -> _User:
        """El usuario del mensaje"""
        return self._user

    @property
    def time(self):
        return self._time

    ####
    # Attach/detach
    ####
    def attach(self, room, msgid):
        """
        TODO esto debería llamar a un método incrustado en room
        Attach the Message to a message id.
        @type msgid: str
        @param msgid: message id
        @param room: Sala a la que se agregará
        """
        if self._msgid is None:
            self._room = room
            self._msgid = msgid
            self._room.msgs[msgid] = self

    def detach(self):
        """Detach the Message."""
        if self._msgid is not None and self._msgid in self._room.msgs:
            del self._room.msgs[self._msgid]
            self._msgid = None

    def delete(self):
        """Borrar el mensaje de la sala (Si es mod)"""
        self._room.deleteMessage(self)


class WSConnection:
    """
    Base para manejar las conexiones con Mensajes y salas
    """
    
    def __init__(self, mgr: object = None, name: str = '', password: str = '', server: str = '',
                 port: str = None, origin: str = '') -> None:
        """
        @param mgr: El dueño de esta conexión
        @param name: El nombre de usuario si no hay se conecta como anon
        @param password: La clave si no hay se usará un nombre temporal o anon
        @param server:
        @param port:
        @param origin:
        """
        self._connectattempts = 0
        self._connected = False
        self._currentaccount = [name, password]
        self._currentname = name  # El usuario de esta conexión
        self._firstCommand = True  # Si es el primer comando enviado
        self._headers = b''  # Las cabeceras que se enviaron en la petición
        self._name = name  # El nombre de la sala o conexión
        self._origin = origin or 'http://st.chatango.com'
        self._password = password  # La clave de esta conexión
        self._pingInterval = 90  # Intervalo para enviar pings, Si llega a 300 se desconecta
        self._port = port or 443  # El puerto de la conexión
        self._rbuf = b''  # El buffer de lectura  de la conexión
        self._server = server
        self._connectiontime = 0  # Hora local a la que se entra
        self._servertime = 0  # Hora del servidor a la que se entra
        self._serverheaders = b''  # Las caberceras de respuesta que envió el servidor
        self._sock = None
        self._user = User(name)
        self._wbuf = b''  # El buffer de escritura a la conexión
        self._wlock = False  # Si está activo no se debe envíar nada al buffer de escritura
        self._wlockbuf = b''  # Buffer de escritura bloqueado, se almacena aquí cuando el lock está activo
        self.mgr = mgr  # El dueño de esta conexión
        if mgr:  # Si el manager está activo iniciar la conexión directamente
            self.connect()
    
    @property
    def account(self) -> str:
        """La cuenta que se está usando actualmente, por seguridad la clave solo será accesible con .password"""
        cuenta = User(self._currentaccount[0])
        cuenta.password = self._currentaccount[1]
        return cuenta
    
    @property
    def attempts(self) -> int:
        """Los intentos de conexión antes de tener exito o rendirse"""
        return self._connectattempts
    
    @property
    def connected(self) -> bool:
        """Estoy conectado?"""
        return self._connected
    
    @property
    def currentname(self) -> str:
        """El nombre de usuario que está usando actualmente el bot en esta conexión"""
        return self._currentname
    
    @property
    def name(self) -> str:
        """El nombre de la conexión (sala o PM)"""
        return self._name
    
    @property
    def sock(self) -> socket.socket:
        """El socket usado"""
        return self._sock
    
    @property
    def user(self) -> _User:
        """El usuario de esta conexión"""
        return self._user
    
    @property
    def wbuf(self) -> bytes:
        """Buffer de escritura"""
        return self._wbuf

    def connect(self) -> bool:
        """ Iniciar la conexión con el servidor y llamar a _handshake() """
        self._connectattempts += 1
        self._sock = socket.socket()
        self._sock.connect((self._server, self._port))  # TODO Si no hay internet hay error acá
        self._sock.setblocking(False)
        self._handShake()
        return True
    
    def _disconnect(self):
        """Privado: Solo usar para reconneción
        Cierra la conexión y detiene los pings, pero el objeto sigue existiendo dentro de su mgr"""
        if self._sock is not None:
            self._sock.close()
        self._sock = None
        self._pingTask.cancel()
    
    def disconnect(self):
        """Público, desconección completa"""
        self._disconnect()
        if isinstance(self, PM):
            self.mgr.pm = None  # TODO
        else:
            self.mgr.rooms.pop(self.name)  # TODO
        self._callEvent('onDisconnect')  # TODO ondisconnect del pm?
    
    def reconnect(self):
        """
        Vuelve a iniciar la conexión a la Sala/PM
        """
        self._disconnect()
        self._reset()
        self.connect()
    
    def _reset(self):
        """
        Reinicia algunas variables para la conexión
        ADVERTENCIA usar con cuidado
        """
        self._headers = b''
        self._serverheaders = b''
        self._wbuf = b''  # El buffer de escritura a la conexión
        self._wlock = False  # Si está activo no se debe envíar nada al buffer de escritura
        self._wlockbuf = b''  # Buffer de escritura bloqueado, se almacena aquí cuando el lock está activo
    
    def _handShake(self):
        """Crea un handshake y lo guarda en las variables antes de enviarlo a la conexión"""
        self._headers = (
            "GET / HTTP/1.1\r\n"
            "Host: {}:{}\r\n"
            "Origin: {}\r\n"
            "Connection: Upgrade\r\n"
            "Upgrade: websocket\r\n"
            "Sec-WebSocket-Key: {}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).format(self._server, self._port, self._origin, WS.genseckey()).encode()
        self._wbuf = self._headers
        self._setWriteLock(True)
        self._pingTask = self.mgr.setInterval(self._pingInterval, self.ping)
    
    def _login(self):
        """Sobreescribir. PM y Room lo hacen diferente"""
        pass
    
    def _callEvent(self, evt, *args, **kw):
        getattr(self.mgr, evt)(self, *args, **kw)
        self.mgr.onEventCalled(self, evt, *args, **kw)
    
    def _process(self, data: str):
        """
        TODO si en este punto los datos incluyen \x00 hay que revisar algo
        Procesar un comando recibido del servidor
        @param data: Un string
        @return: None
        """
        data = data.rstrip("\r\n\x00")
        self._callEvent("onRaw", data)
        data = data.split(":")
        cmd, args = data[0], data[1:]
        func = "_rcmd_" + cmd
        if hasattr(self, func):
            try:  # TODO no se supone que ocurran, si lo hacen hay que revisar el proceso
                getattr(self, func)(args)
            except Exception as e:
                print('ERROR ON PROCESS "%s" "%s"' % (func, e), file = sys.stderr)
        elif debug:
            print('[{}][{:^10.10}]UNKNOWN DATA "{}"'.format(time.strftime('%I:%M:%S %p'), self.name, ':'.join(data)),
                  file = sys.stderr)

    def onData(self, data: bytes):
        """
        Al recibir datos del servidor
        @param data: Los datos recibidos y sin procesar
        """
        self._rbuf += data  # Agregar los datos al buffer de lectura
        if not self._serverheaders and b'\r\n' * 2 in data:
            self._serverheaders, self._rbuf = self._rbuf.split(b'\r\n' * 2)
            clave = WS.checkHeaders(self._serverheaders)
            if clave != WS.getServerSeckey(self._headers) and debug:
                print(
                        'Un proxy ha enviado una respuesta en caché, puede que no estés conectado a la versión más '
                        'reciente del servidor',
                        file = sys.stderr)
            self._setWriteLock(False)
            self._login()
        else:
            r = WS.checkFrame(self._rbuf)
            while r:  # Comprobar todos los frames en el buffer de lectura
                frame = self._rbuf[:r]
                self._rbuf = self._rbuf[r:]
                info = WS.frameInfo(frame)  # Información sobre el frame recibido
                payload = WS.getPayload(frame)
                if info.opcode == WS.CLOSE:  # El servidor quiere cerrar la conexión
                    pass  # self._
                elif info.opcode == WS.TEXT:  # El frame contiene datos
                    self._process(payload)
                elif debug:
                    print('Frame no controlado: "{}"'.format(payload), file = sys.stderr)
                r = WS.checkFrame(self._rbuf)
    
    def ping(self):
        """Enviar un ping al servidor para mantener la conexión activa"""
        # TODO Calcular el proximo ping
        self._sendCommand('')
        self._callEvent('onPing')
    
    def _rcmd_(self, pong):
        """Al recibir un pong"""
        self._callEvent('onPong')
    
    def _sendCommand(self, *args):
        """
        Envía un comando al servidor
        @type args: [str, str, ...]
        @param args: command and list of arguments
        """
        if self._firstCommand:
            terminator = "\x00"
            self._firstCommand = False
        else:
            terminator = "\r\n\x00"
        cmd = ":".join(args) + terminator
        self._write(WS.encode(cmd))
    
    def _setWriteLock(self, lock: bool):
        self._wlock = lock
        if not self._wlock and self._wlockbuf:
            self._wbuf += self._wlockbuf
            self._wlockbuf = b''
    
    def _write(self, data: bytes):
        """Escribir datos en el buffer de envío al servidor"""
        if self._wlock:
            self._wlockbuf += data
        else:
            self._wbuf += data


class PM(WSConnection):
    """
    Clase Base para la conexión con la mensajería privada de chatango
    """
    
    def __init__(self, mgr, name, password):
        """
        Clase que maneja una conexión con la mensajería privada de chatango
        TODO agregar posibilidad de anon
        @param mgr: Administrador de la clase
        @param name: Nombre del usuario
        @param password: Contraseña para la conexión
        """
        super().__init__(name = name, password = password)
        self._auth_re = re.compile(
                r"auth\.chatango\.com ?= ?([^;]*)", re.IGNORECASE
                )
        self._blocklist = set()
        self._contacts = set()
        self._name = 'PM'
        self._currentname = name
        # self._origin='st.chatango.com'
        self._port = 8080  # TODO
        self._server = 'c1.chatango.com'
        # self._server = 'i0.chatango.com'  # TODO
        self._status = dict()
        self.mgr = mgr
        if self.mgr:
            self.connect()

    @property
    def blocklist(self):
        return self._blocklist

    @property
    def contacts(self):
        """Mis contactos en el PM"""
        return self._contacts
    
    @property
    def _getStatus(self):
        # TODO
        return self._status
    
    def _getAuth(self, name, password):
        """
        Request an auid using name and password.
        @type name: str
        @param name: name
        @type password: str
        @param password: password
        @rtype: str
        @return: auid
        """
        data = urllib.parse.urlencode({
            "user_id":     name,
            "password":    password,
            "storecookie": "on",
            "checkerrors": "yes",
            "origin":      "st.chatango.com"
            }).encode()
        try:
            resp = urllib.request.urlopen("http://chatango.com/login", data)
            headers = resp.headers
        except HTTPError as e:
            if debug:
                print('Error code: ', e.code)
            return None
        except URLError as e:
            if debug:
                print('Error Reason: ', e.reason)
            return None
        except Exception:
            return None
        
        for header, value in headers.items():
            if header.lower() == "set-cookie":
                m = self._auth_re.search(value)
                if m:
                    auth = m.group(1)
                    if auth == "":
                        return None
                    return auth
        return None
    
    def _login(self):
        # TODO el 2 es la versión del cliente
        __reg2 = ["tlogin", self._getAuth(self.mgr.name, self.mgr.password), "2"]
        if not __reg2[1]:
            self._callEvent("onLoginFail")
            self.disconnect()
            return False
        self._sendCommand(*__reg2)

    def addContact(self, user):  # TODO
        """add contact"""
        if user not in self._contacts:
            self._sendCommand("wladd", user.name)
            self._contacts.add(user)
            self._callEvent("onPMContactAdd", user)

    def removeContact(self, user):  # TODO
        """remove contact"""
        if user in self._contacts:
            self._sendCommand("wldelete", user.name)
            self._contacts.remove(user)
            self._callEvent("onPMContactRemove", user)

    def block(self, user):  # TODO
        """block a person"""
        if user not in self._blocklist:
            self._sendCommand("block", user.name, user.name, "S")
            self._blocklist.add(user)
            self._callEvent("onPMBlock", user)

    def unblock(self, user):  # TODO
        """unblock a person"""
        if user in self._blocklist:
            self._sendCommand("unblock", user.name)

    def track(self, user):  # TODO
        """get and store status of person for future use"""
        self._sendCommand("track", user.name)

    def checkOnline(self, user):  # TODO
        """return True if online, False if offline, None if unknown"""
        if user in self._status:
            return self._status[user][1]
        else:
            return None

    def getIdle(self, user):  # TODO
        """return last active time, time.time() if isn't idle, 0 if offline, None if unknown"""
        if not user in self._status:
            return None
        if not self._status[user][1]:
            return 0
        if not self._status[user][2]:
            return time.time()
        else:
            return self._status[user][2]

    def message(self, user, msg, html: bool = False):
        """
        Enviar un pm a un usuario
        @param user: Usuario al que enviar el mensaje
        @param msg: Mensaje que se envia (string)
        """
        if isinstance(user, _User):
            user = user.name
        fc = self.user.fontColor
        fc = fc[::2] if len(fc) == 6 else fc[:3]
        if not html:
            msg = HTML.escape(msg).replace('~', '')
        self._sendCommand("msg", user,
                          '<n{}/><m v="1"><g x{}s{}="{}">{}</g></m>'.format(
                                  self.user.nameColor,
                                  self.user.fontSize, fc.lower(),
                                  self.user.fontFace, msg
                                  )
                          )
    
    def _write(self, data: bytes):
        if not self._wlock:
            self._wbuf += data
        else:
            self._wlockbuf += data
    
    def _rcmd_OK(self, args):
        if args:
            print(args)
        self._sendCommand("wl")  # TODO
        self._sendCommand("getblock")  # TODO
        self._callEvent('onPMConnect')

    def _rcmd_block_list(self, args):  # TODO
        self._blocklist = set()
        for name in args:
            if name == "":
                continue
            self._blocklist.add(User(name))

    def _rcmd_DENIED(self, args):
        self._disconnect()
        self._callEvent("onLoginFail")

    def _rcmd_idleupdate(self, args):  # TODO
        pass

    def _rcmd_kickingoff(self, args):  # TODO
        self.disconnect()

    def _rcmd_msg(self, args):  # msg TODO
        user = User(args[0])
        body = _unescape_html(_strip_html(":".join(args[5:])))
        self._callEvent("onPMMessage", user, body)

    def _rcmd_msgoff(self, args):  # TODO
        user = User(args[0])
        body = _strip_html(":".join(args[5:]))
        self._callEvent("onPMOfflineMessage", user, body)

    def _rcmd_track(self, args):  # TODO
        pass

    def _rcmd_toofast(self, args):  # TODO esto solo debería parar un momento
        self.disconnect()

    def _rcmd_unblocked(self, user):  # TODO
        """call when successfully unblocked"""
        if user in self._blocklist:
            self._blocklist.remove(user)
            self._callEvent("onPMUnblock", user)

    def _rcmd_wl(self, args):
        """Lista de contactos recibida"""  # TODO
        self._contacts = set()
        for i in range(len(args) // 4):
            name, last_on, is_on, idle = args[i * 4: i * 4 + 4]
            user = User(name)
            if last_on == "None":
                pass  # in case chatango gives a "None" as data argument TODO
            elif not is_on == "on":
                self._status[user] = [int(last_on), False, 0]
            elif idle == '0':
                self._status[user] = [int(last_on), True, 0]
            else:
                self._status[user] = [int(last_on), True, time.time() - int(idle) * 60]
            self._contacts.add(user)
        self._callEvent("onPMContactlistReceive")

    def _rcmd_wloffline(self, args):  # TODO
        user = User(args[0])
        last_on = float(args[1])
        self._status[user] = [last_on, False, 0]
        self._callEvent("onPMContactOffline", user)

    def _rcmd_wlonline(self, args):  # TODO
        user = User(args[0])
        last_on = float(args[1])
        self._status[user] = [last_on, True, last_on]
        self._callEvent("onPMContactOnline", user)


class Room(WSConnection):
    """
    Base para manejar las conexiones con las salas. Hereda de WSConnection y tiene todas
    sus propiedades
    """
    
    def __init__(self, name: str, mgr: object = None, account: tuple = None):
        # TODO , server = None, port = None, uid = None):
        # TODO not account start anon
        super().__init__(name = account[0], password = account[1])
        self._badge = 0
        self._channel = 0
        self._currentaccount = account
        self._currentname = account[0]
        self._history = list()
        self._mqueue = dict()
        self._mods = set()
        self._msgs = dict()
        self._name = name
        self._port = 1800  # TODO
        self._rbuf = b''
        self._server = getServer(name)  # TODO
        self._connectiontime = 0
        self._silent = False
        self._time = None
        self._owner = None
        self._user = None
        self._users = deque()  # TODO reemplazar userlist con userdict y userhistory
        self._userdict = dict()  # TODO {ssid:{user},}
        self._userhistory = deque(maxlen = 10)  # TODO {{time: <user>},}
        self.user_id = None
        self._userCount = 0
        self._userlist = list()
        self.bmsg_array = list()
        self.imsgs_drawn = 0
        self.imsgs_rendered = False
        self.imsg_array = list()
        self.lastmsgnum = 0
        self.msg_array = list()
        self.mgr = mgr
        self.msgs = dict()  # TODO Revisar utilidad y diferencia con el _history
        self.participants = list()
        self.participants_number = list()
        self.sellers_array = list()
        self.status = None
        self.usercount = 0
        if self.mgr:
            super().connect()
        self._maxHistoryLength = Gestor.maxHistoryLength  # Por que no guardar un número por sala ?)
        # TODO
    
    ####
    # Propiedades
    ####
    @property
    def allshownames(self):
        return [x.showname for x in set(self._userdict.values())]

    @property
    def alluserlist(self):
        return list(self._userdict.values())

    @property
    def allusernames(self):
        return [x.username for x in set(self._userdict.values())]
    
    @property
    def badge(self):
        return self._badge

    @badge.setter
    def badge(self, value):
        self._badge = value

    @property
    def banlist(self):
        """La lista de usuarios baneados en la sala"""
        return self._banlist

    @property
    def botname(self):  # TODO anon o temp !#
        return self.name

    @property
    def channel(self):
        """El canal que uso en la sala"""
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    @property
    def currentname(self):
        return self._currentname

    @property
    def mods(self):
        """Los mods de la sala"""
        return self._mods

    @property
    def modnames(self):
        return [x.name for x in self.mods]

    @property
    def owner(self):
        """El dueño de la sala"""
        return self._owner

    @property
    def ownername(self):
        return self.owner.name

    @property
    def silent(self):
        """Hablo o no?
        TODO Buffer de mensajes
        """
        return self._silent

    @silent.setter
    def silent(self, value):
        self._silent = value

    @property
    def shownames(self):
        return list(set([x.showname for x in self.userlist]))
    
    @property
    def unbanlist(self):
        return self._unbanlist

    @property
    def user(self):
        """Mi usuario"""
        return self._user

    @property
    def userlist(self):
        return self._getUserlist(1, 1)

    @property
    def userCount(self):
        """Cantidad de usuarios en la sala"""
        return self._userCount

    @property
    def usernames(self):
        return list(set([x.name for x in self.userlist]))

    @property
    def userhistory(self):
        # TODO regresar solo la ultima sesión para cada usuario
        return self._userhistory
    
    def _addHistory(self, msg):
        """
        Agregar un mensaje al historial
        @param msg: El mensaje TODO
        """
        self._history.append(msg)
        if len(self._history) > self._maxHistoryLength:
            rest, self._history = self._history[:-self._maxHistoryLength], self._history[
                                                                           -self._maxHistoryLength:]
            for msg in rest:
                msg.detach()

    def _getUserlist(self, todos = 0, unica = 0, memoria = 0):  # TODO Revisar
        ul = None  # TODO Si hay flag de usuarios invisibles usar el history
        if not todos:
            ul = map(lambda x: x.user, self._history[-memoria:])
        else:
            ul = self._userlist
        if unica:
            return list(set(ul))
        return ul
    
    ####
    # Comandos
    ####
    def logout(self):  # TODO ordenar
        """logout of user in a room"""
        self._sendCommand("blogout")
    
    def message(self, msg, html: bool = False, canal = None):
        """
        Envía un mensaje
        @param html: si se habilitarán los carácteres html, en caso contrario se reemplazarán los carácteres especiales
        @type msg: str
        @param msg: message
        @param canal: el número del canal. del 0 al 4 son normal,rojo,azul,azul+rojo,mod
        """
        if canal is None:
            canal = self.channel
        if canal < 4:
            canal = (((canal & 2) << 2 | (canal & 1)) << 8)
        elif canal == 4:
            canal = 32768
        if msg is None:
            return
        msg = msg.strip().replace('\n', '\r')
        if not html:
            msg = HTML.escape(msg, quote = False)
        if len(msg) > self.mgr._maxLength:
            if self.mgr._tooBigMessage == BigMessage_Cut:
                self.message(msg[:self.mgr._maxLength], html = html)
            elif self.mgr._tooBigMessage == BigMessage_Multiple:
                while len(msg) > 0:
                    sect = msg[:self.mgr._maxLength]
                    msg = msg[self.mgr._maxLength:]
                    self.message(sect, html = html)
            return
        msg = "<n" + self.user.nameColor + "/>" + msg

        if self._currentname and not self._currentname.startswith("!anon"):
            font_properties = "<f x%0.2i%s=\"%s\">" % (self.user.fontSize, self.user.fontColor, self.user.fontFace)
            if "\n" in msg:
                msg.replace("\n", "</f></p><p>%s" % font_properties)
            msg = font_properties + msg
        msg.replace("~", "&#126;")
        self.rawMessage('%s:%s' % (canal + self.badge * 64, msg))

    def rawMessage(self, msg):
        """
        Send a message without n and f tags.
        @type msg: str
        @param msg: message
        """
        if not self._silent:
            self._sendCommand("bm", "meme", msg)

    def setBgMode(self, modo):
        """Activar el BG"""
        self._bgmode = modo
        if self.connected:
            self._sendCommand('msgbg', str(self._bgmode))

    def setRecordingMode(self, modo):
        self._recording = modo
        if self.connected:
            self._sendCommand('msgmedia', str(self._bgmode))
    
    @staticmethod
    def getAnonName(num: str, ts: str):
        """
        Obtener el nombre de anon para una sesión
        @param num: El número de la sesión
        @param ts: El tiempo de la conexión
        @return:  anon####
        """
        return 'anon' + _getAnonId(num, ts)
    
    def _login(self, uname = None, password = None):  # TODO, Name y password no shilven
        """
        Autenticar. Logearse como uname con password. En caso de no haber ninguno usa la _currentaccount
        @param uname: Nombre del usuario (string)
        @param password: Clave del usuario (string)
        @return:
        """
        __reg2 = ["bauth", self.name, _genUid(), self._currentaccount[0], self._currentaccount[1]]  # TODO comando
        self._currenname = self._currentaccount[0]
        self._sendCommand(*__reg2)
    
    def reset(self):
        """Reiniciar todos los valores por defecto no confundir con _reset"""
        # TODO
        self.participants_number = 0

    def _rcmd_b(self, args):  # TODO reducir proceso
        mtime = float(args[0])  # Hora de envío del mensaje
        name = args[1]  # Nombre de usuario si lo hay
        tempname = args[2]  # Nombre del anon si no se ha logeado
        puid = args[3]  # Id del usuario
        msgid = args[4]  # Id del mensaje
        msgnum = args[5]
        ip = args[6]  # Ip del usuario
        channel = args[7] or 0
        badge = 0
        rawmsg = ":".join(args[9:])
        if channel and channel.isdigit():
            channel = int(channel)
            if channel < 256:  # Canal Normal
                badge = 0 if channel < 64 else 1 if channel < 128 else 2
                channel = 0
            elif 256 <= channel < 2048:  # Canal Rojo con o sin badge
                badge = 0 if channel < 256 + 64 else 1 if channel < 256 + 128 else 2
                channel = 256
            elif 2048 <= channel < 2304:
                badge = 0 if channel < 2048 + 64 else 1 if channel < 2048 + 128 else 2
                channel = 2048
            elif 2304 <= channel < 32768:
                badge = 0 if channel < 2304 + 64 else 1 if channel < 2304 + 128 else 2
                channel = 2304
            elif channel >= 32768:
                badge = 0 if channel < 32768 + 64 else 1 if channel < 32768 + 128 else 2
                channel = 32768
        body, n, f = _clean_message(rawmsg)
        if name == "":
            nameColor = None
            name = "#" + tempname
            if name == "#":
                name = "!" + getanonname(n, puid)
        else:
            if n:
                nameColor = n
            else:
                nameColor = None
        i = args[5]
        unid = args[4]
        user = User(name, ip = ip, isanon = name[0] in '#!')  # TODO
        if ip != user.ip:
            user._ip = ip
        if f:
            fontSize, fontColor, fontFace = _parseFont(f.strip())
        else:
            fontColor, fontFace, fontSize = None, None, None
        msg = Message(badge = badge,
                      body = body,
                      channel = channel,
                      fontColor = fontColor,
                      fontFace = fontFace,
                      fontSize = fontSize or '11',
                      mnum = msgnum,
                      ip = ip,
                      msgid = msgid,
                      nameColor = nameColor,
                      puid = puid,
                      raw = rawmsg,
                      room = self,
                      time = mtime,
                      unid = unid,
                      user = user
                      )
        self._mqueue[i] = msg

    def _rcmd_blocked(self, args):  # TODO
        if args[2] == "":
            return
        target = User(args[2])
        user = User(args[3])
        self._banlist[target] = {"unid": args[0], "ip": args[1], "target": target, "time": float(args[4]), "src": user}
        self._callEvent("onBan", user, target)

    def _rcmd_blocklist(self, args):  # TODO
        self._banlist = dict()
        sections = ":".join(args).split(";")
        for section in sections:
            params = section.split(":")
            if len(params) != 5:
                continue
            if params[2] == "":
                continue
            user = User(params[2])
            self._banlist[user] = {
                "unid":   params[0],
                "ip":     params[1],
                "target": user,
                "time":   float(params[3]),
                "src":    User(params[4])
                }
        self._callEvent("onBanlistUpdate")

    def _rcmd_delete(self, args):
        """Borrar un mensaje de mi vista actual"""
        msg = self._msgs.get(args[0])
        if msg and msg in self._history:
            self._history.remove(msg)
            self._callEvent("onMessageDelete", msg.user, msg)
            msg.detach()

    def _rcmd_deleteall(self, args):  # TODO
        for msgid in args:
            self._rcmd_delete([msgid])

    def _rcmd_denied(self, args):  # TODO
        pass

    def _rcmd_getannc(self, args):  # TODO
        pass
    
    def _rcmd_g_participants(self, args):
        self._userdict = dict()
        self._userlist = list()
        args = ':'.join(args).split(";")
        for data in args:
            data = data.split(':')  # Lista de un solo usuario
            ssid = data[0]  # Id de la sesión
            contime = data[1]  # Hora de conexión a la sala
            puid = data[2]  # Id de la conexión (en la sala)
            name = data[3]  # Nombre de usuario registrado
            tname = data[4]  # Nombre temporal
            isanon = False  # TODO externalizar esta parte
            if name == 'None':
                isanon = True
                if tname != 'None':
                    name = '#' + tname
                else:
                    name = '!' + getanonname(contime.split('.')[0], puid)
            user = User(name, room = self, isanon = isanon, puid = puid)
            if user in ({self._owner} | self._mods):
                user.setName(name)
            user.addSessionId(self, ssid)
            self._userdict[ssid] = user
            if not isanon:
                self._userlist.append(user)
    
    def _rcmd_gparticipants(self, args):
        """Comando viejo de chatango, ya no se usa, pero aún puede seguirlo enviando"""
        self._rcmd_g_participants(args[1:])
    
    def _rcmd_getpremium(self, args):
        # TODO
        self.mgr.setPremium(args)
        self._sendCommand('msgbg', str(self._bgmode))
    
    def _rcmd_i(self, args):  # TODO
        pass
    
    def _rcmd_inited(self, args):  # TODO
        """Em el chat es solo para desactivar la animación de espera por conexión"""
        self._sendCommand("g_participants", "start")
        self._sendCommand("getpremium", "l")
        if args and debug:
            print('New Unhandled arg on inited ', file = sys.stderr)
        if self.attempts == 1:
            self._callEvent("onConnect")
            # TODO
        else:
            self._callEvent("onReconnect")
            # TODO
        pass

    def _rcmd_logoutok(self, args):
        """Me he desconectado, ahora usaré mi nombre de anon"""
        # TODO revisar este comando
        self._currentname = getanonname(self._servertime.split('.'), self.user_id)
    
    def _rcmd_mods(self, args):  # TODO
        modnames = args
        mods = set(map(lambda x: User(x.split(",")[0]), modnames))
        premods = self._mods
        for user in mods - premods:  # modded
            self._mods.add(user)
            self._callEvent("onModAdd", user)
        for user in premods - mods:  # demodded
            self._mods.remove(user)
            self._callEvent("onModRemove", user)
        self._callEvent("onModChange")
    
    def _rcmd_n(self, args):  # TODO
        """Cambió la cantidad de usuarios en la sala"""
        self._userCount = int(args[0], 16)
        assert self._userdict and len(self._userdict) == self._userCount, 'Warning count doesnt match'  # TODO
        self._callEvent("onUserCountChange")

    def _rcmd_ok(self, args):  # TODO
        self._connected = True
        self._connectiontime = time.time()
        self._owner = User(args[0])
        self.user_id = args[1]  # TODO
        self._authtype = args[2]  # M=Ok, N= ? TODO tipo C
        self._currentname = args[3]
        self._servertime = args[4]
        self._currentIP = args[5]
        self._modsServer = args[6]  # TODO Lista de mods name:number;name,number
        self._flags = args[7]
        self._user = User(self._currentname)
        if self._authtype == 'N':
            # TODO revisar todo esto
            pass

    def _rcmd_participant(self, args):
        """
        Cambio en la lista de participantes
        TODO _historysessions a un usuario para saber quien es
        """
        cambio = args[0]  # Leave Join Change
        ssid = args[1]  # Session ID, cambia por sesión (o pestaña del navegador).
        puid = args[2]  # Personal User ID (en la sala)
        name = args[3]  # Visible Name
        tname = args[4]  # Anon Name
        unknown = args[5]  #
        contime = args[6]  # Hora del cambio
        isanon = False  # TODO externalizar esta parte
        if name == 'None':
            isanon = True
            if tname != 'None':
                name = '#' + tname
            else:
                name = '!' + getanonname(contime.split('.')[0], puid)
        #    return
        user = User(name, puid = puid, isanon = isanon)
        if cambio == '0':  # Leave
            user.removeSessionId(self, ssid)  # Quitar la id de sesión activa
            if user in self._userlist:
                self._userlist.remove(user)
                self._callEvent('onLeave', user, puid)
            if ssid in self._userdict:  # Remover el usuario de la sala
                self._userhistory.append([contime, self._userdict.pop(ssid)])
            if user.isanon:
                self._callEvent('onAnonLeave', user, puid)
        elif cambio == '1':  # Join
            user.addSessionId(self, ssid)  # Agregar la sesión al usuario
            self._userdict[ssid] = user  # Agregar la sesión a la sala
            if not user.isanon and user not in self._userlist:
                self._callEvent('onJoin', user, puid)
                self._userlist.append(user)
            elif user.isanon:
                self._callEvent('onAnonJoin', user, puid)
        else:  # 2 Account Change
            before = None
            if ssid in self._userdict:
                before = self._userdict[ssid]
            if before and before.isanon:  # Login
                if user.isanon:  # Anon Login
                    self._callEvent('onAnonLogin', user, puid)  # TODO
                else:  # User Login
                    self._userlist.append(user)
                    self._callEvent('onUserLogin', user, puid)
            elif not before.isanon:  # Logout
                if before in self._userlist:
                    self._userlist.remove(before)
                    self._userhistory.append([contime, before])
                    self._callEvent('onUserLogout', user, puid)
            self._userdict[ssid] = user
    
    def _rcmd_premium(self, args):  # TODO
        pass

    def _rcmd_show_fw(self, args):  # TODO
        pass

    def _rcmd_show_tb(self, args):  # TODO
        self._callEvent("onFloodBan")

    def _rcmd_tb(self, args):  # TODO
        self._callEvent("onFloodBanRepeat")

    def _rcmd_u(self, args):  # TODO
        temp = Struct(**self._mqueue)
        if hasattr(temp, args[0]):
            msg = getattr(temp, args[0])
            if msg._user != self.user:
                msg.user._fontColor = msg.fontColor
                msg.user._fontFace = msg.fontFace
                msg.user._fontSize = msg.fontSize
                msg.user._nameColor = msg.nameColor
            del self._mqueue[args[0]]
            msg.attach(self, args[1])
            self._addHistory(msg)
            if (msg.channel >= 4 or msg.badge) and msg.user is not self.owner:  # TODO
                self._mods.add(msg.user)
            self._callEvent("onMessage", msg.user, msg)

    def _rcmd_unblocked(self, args):  # TODO
        args = ":".join(args).split(";")[-1].split(":")
        if args[2] == "":
            return
        target = User(args[2])
        user = User(args[3])
        del self._banlist[target]
        self._unbanlist[user] = {"unid": args[0], "ip": args[1], "target": target, "time": float(args[4]), "src": user}
        self._callEvent("onUnban", user, target)

    def _rcmd_unblocklist(self, args):  # TODO
        self._unbanlist = dict()
        sections = ":".join(args).split(";")
        for section in sections:
            params = section.split(":")
            if len(params) != 5:
                continue
            if params[2] == "":
                continue
            user = User(params[2])
            self._unbanlist[user] = {
                "unid":   params[0],
                "ip":     params[1],
                "target": user,
                "time":   float(params[3]),
                "src":    User(params[4])
                }
        self._callEvent("onUnBanlistUpdate")


class Gestor:
    """
    Clase Base para manejar las demás conexiones
    """
    _TimerResolution = 0.2
    maxHistoryLength = 700
    _maxLength = 1800
    _pingDelay = 90  # 20
    PMHost = "c1.chatango.com"

    def __init__(self, name: str = None, password: str = None, pm: bool = None, accounts = None):
        self._accounts = accounts
        if accounts is None:
            self._accounts = [(name, password)]
        self._name = self._accounts[0][0]
        self._password = self._accounts[0][1]
        self._rooms = dict()
        self._running = False
        self._user = User(self._name)
        self._tasks = set()
        self._pm = None
        if pm:
            self._pm = PM(mgr = self, name = self.name, password = self.password)
    
    ####
    # Propiedades
    ####
    @property
    def accounts(self):
        return dict((x[0].lower(), User(x[0])) for x in self._accounts)
    
    @property
    def name(self):
        """El nombre de la sala/conexión"""
        return self._name
    
    @property
    def password(self):
        return self._password

    @property
    def pm(self):
        """Mi PM"""
        return self._pm
    
    @property
    def user(self):
        return self._user
    
    @property
    def rooms(self):
        """Mis salas"""
        return self._rooms
    
    @classmethod
    def easy_start(cls, rooms: list = None, name: str = None, password: str = None, pm: bool = True,
                   accounts: [(str, str), (str, str), ...] = None):
        """
        Inicio rápido del bot y puesta en marcha
        @param rooms: Una lista de sslas
        @param name: Nombre de usuario
        @param password: Clave de conexión
        @param pm: Si se usará el PM o no
        @param accounts: Una lista/tupla de cuentas ((clave,usuario),(clave,usuario))
        """
        # if not rooms:
        #    rooms = str(input('Nombres de salas separados por coma: ')).split(';')
        # if '' in rooms:
        #    rooms = []
        # if name is None: name = str(input("Usuario: "))
        # if not name:
        #    name = ''
        # if password is None: password = str(input("User password: "))
        # if not password:
        #    password = ''
        self = cls(name, password, pm, accounts)
        for room in rooms:
            self.joinRoom(room)

        self.main()
    
    def onInit(self):
        """Invocado antes de empezar los demás procesos en main"""
        pass
    
    class _Task:
        def __init__(self, mgr):
            """
            Inicia una tarea nueva
            @param mgr: El dueño de esta tarea y el que la mantiene con vida
            """
            self.mgr = mgr

        def cancel(self):
            """Sugar for removeTask."""
            self.mgr.removeTask(self)
    
    def getConnections(self):
        """
        Regresa una lista de las conexiones existentes
        """
        li = list(self._rooms.values())
        if self._pm:
            li.append(self._pm)
        return [c for c in li if c.sock is not None]
    
    def getRoom(self, room: str) -> Room:
        """
        @type room: str
        @param room: room
        @rtype: Room
        @return: the room
        """
        if room in self._rooms:
            return self._rooms[room]
        else:
            return Room("", self)  # TODO
    
    def joinRoom(self, room: str, account = None):
        """
        Unirse a una sala con la cuenta indicada
        @param room: Sala a la que unirse
        @param account:  Opcional, para entrar con otra cuenta del bot solo escribir su nombre
        """
        if account is None:
            account = self._accounts[0]
        if isinstance(account, str):
            account = {k.lower(): [k, v] for k, v in self._accounts}.get(account.lower(), self._accounts[0])
        if room not in self._rooms:
            try:
                self._rooms[room] = Room(room, self, account)  # TODO
            except:
                return False
            return True
        else:
            return None

    def leaveRoom(self, room):
        if isinstance(room, Room):
            room = room.name
        if room in self._rooms:
            self._rooms[room].disconnect()
    
    def main(self):
        """
        Poner en marcha al bot
        # TODO
        """
        self.onInit()
        self._running = True
        while self._running:
            # try:
            if self._running:
                conns = self.getConnections()
                socks = [x.sock for x in conns]
                wsocks = [x.sock for x in conns if x.wbuf]
                rd, wr, sp = select.select(socks, wsocks, socks, self._TimerResolution)
                for sock in wr:  # Enviar
                    try:
                        con = [x for x in conns if x.sock == sock][0]
                        size = sock.send(con.wbuf)
                        con._wbuf = con.wbuf[size:]
                    except Exception as e:
                        if debug:
                            print("Error sock.send " + str(e), sys.stderr)
                for sock in rd:  # Recibir
                    con = [x for x in conns if x.sock == sock][0]
                    try:
                        chunk = sock.recv(1024)
                        if chunk:  # TODO
                            con.onData(chunk)
                        else:
                            print("{}: Fallo de recv, reconectando...".format(con.name))  # con.reconnect()  #
                            # Conexión perdida
                            con.reconnect()
                            # TODO ConnectionRefusedError
                    except ConnectionResetError:
                        print('Conexión perdida, reintentando en 10 segundos...')
                        counter = con.attempts or 1
                        while counter:
                            try:
                                time.sleep(10)
                                con.reconnect()
                                counter = 0
                            except socket.gaierror:  # En caso de que no haya internet
                                print(
                                        '[{}][{:^5}] Aún no hay internet...'.format(time.strftime('%I:%M:%S %p'),
                                                                                    counter),
                                        file = sys.stderr)
                                counter += 1

            # except ConnectionResetError as e:
            #    time.sleep(5)

            # except Exception as e:
            #    print("error en main " + str(e), file = sys.stderr)
            # raise e
            self._tick()
        # Finish
        for conn in self.getConnections():
            conn.disconnect()
    
    def removeTask(self, task):
        """Eliminar una tarea"""
        if task in self._tasks:
            self._tasks.remove(task)

    def stop(self):
        """Detiene al bot"""
        self._running = False
    
    def enableBg(self, activo = True):
        """Enable background if available."""
        self.user._mbg = True
        for room in self.rooms:
            self.getRoom(room).setBgMode(int(activo))
    
    def enableRecording(self):
        """Enable recording if available."""
        self.user._mrec = True
        for room in self.rooms:
            self.getRoom(room).setRecordingMode(1)
    
    def setFontColor(self, hexfont):
        self.user._fontColor = hexfont
    
    def setFontFace(self, facenum):
        """
        # TODO usar el nombre
        @param facenum: El número de la fuente
        """
        
        self.user._fontFace = facenum
    
    def setFontSize(self, sizenum):
        """Cambiar el tamaño de la fuente
        TODO para la sala
        """
        self.user._fontSize = sizenum
    
    def setInterval(self, intervalo, funcion, *args, **kwargs):
        """
        Llama a una función cada intervalo con los argumentos indicados
        @param funcion: La función que será invocada
        @type intervalo int
        @param intervalo:intervalo
        TODO
        """
        task = self._Task(self)
        task.mgr = self
        task.target = time.time() + intervalo
        task.timeout = intervalo
        task.func = funcion
        task.isInterval = True
        task.args = args
        task.kw = kwargs
        self._tasks.add(task)
        return task

    def setTimeout(self, tiempo, funcion, *args, **kwargs):
        """
        Llama a una función cada intervalo con los argumentos indicados
        @param funcion: La función que será invocada
        @type intervalo int
        @param intervalo:intervalo
        TODO
        """
        task = self._Task(self)
        task.mgr = self
        task.target = time.time() + tiempo
        task.timeout = tiempo
        task.func = funcion
        task.isInterval = False
        task.args = args
        task.kw = kwargs
        self._tasks.add(task)
        return task
    
    def setNameColor(self, hexcolor):
        self.user._nameColor = hexcolor
        # for x in self._rooms: TODO
        #    x.user.setnameColor(hexcolor)
    
    def setPremium(self, args):
        """
        # TODO detectar el estado de mi cuenta
        @param args:
        @return:
        """
        pass
    
    def _tick(self):
        now = time.time()
        # print(time.time())
        for task in self._tasks:
            try:
                if task.target <= now:
                    task.func(*task.args, **task.kw)
                    if task.isInterval:
                        task.target = now + task.timeout
                    else:
                        task.cancel()
            except Exception as e:
                print('Task error {}: {}'.format(task.func, e))
                task.cancel()

    def onAnonJoin(self, room, user, ssid):
        pass

    def onAnonLeave(self, room, user, ssid):
        pass

    def onAnonLogin(self, room, user, ssid):
        pass

    def onConnect(self, room):
        """
        Al conectarse a una sala
        @param room:Sala a la que se ha conectado
        """
        pass
    
    def onDisconnect(self, room):
        """
        Al desconectarse de una sala
        @param room: Sala en la que se ha perdido la conexión
        """
        pass
    
    def onEventCalled(self, room, evt, *args, **kw):
        """
        Called on every room-based event.
        @type room: Room
        @param room: room where the event occured
        @type evt: str
        @param evt: the event
        """
        pass

    def onJoin(self, room, user, ssid):
        pass

    def onLeave(self, room, user, ssid):
        pass

    def onLoginFail(self, room):
        """
        Al fracasar un intento de acceso
        @param room: Sala o PM
        @return:
        """
        pass

    def onLogout(self, room, user, ssid):
        pass

    def onMessage(self, room: Room, user: _User, message: Message):
        """
        Al recibir un mensaje en una sala
        @param room: Sala en la que se ha recibido el mensaje
        @param user: Usuario que ha enviado (_User)
        @param message: El mensaje enviado (Message)
        @return:
        """
        pass

    def onPMContactlistReceive(self, pm):  # TODO
        """Al recibir mis contactos en el pm"""
        pass
    
    def onPMConnect(self, pm: PM):
        """
        Al conectarse a la mensajería privada
        @param pm: El PM
        """
        pass
    
    def onPMContactOffline(self, pm: PM, user: _User):
        """
        Cuando un contacto se desconecta del pm
        @param pm: El PM
        @param user: El usuario desconectado
        """
        pass

    def onPMContactOnline(self, pm, user):
        """
        Cuando un contacto se conecta al pm
        @param pm: El PM
        @param user: El usuario conectado
        """
        pass

    def onPMMessage(self, pm, user, message):
        """
        Al recibir un mensaje privado de un usuario
        @param pm: El PM
        @param user: El usuario que manda el mensaje
        @param message: El mensaje es de tipo (Message)
        @return:
        """
        pass
    
    def onPing(self, room: Room):
        """
        Al enviar un ping a una sala
        @param room: La sala en la que se envía el ping
        """
        pass

    def onPong(self, room: Room):
        """
        Al recibir un pong en una sala
        @param room: La sala en la que se recibe el pong
        """
        pass
    
    def onRaw(self, room, raw):
        """
        ANtes de ejecutar la lectura de cualquier comando
        @type room: Room
        @param room: La sala donde ocurre el evento
        @type raw: str
        @param raw: Los datos "crudos"
        """
        pass
    
    def onReconnect(self, room):
        """
        Al reconectarse a una sala
        @param room: Sala en la que se ha reconectado
        """
        pass

    def onUserCountChange(self, room):
        """
        Al cambiar la cantidad de usuarios en una sala
        @param room: Sala en la que cambió la cantidad de usuarios
        """
        pass

    def onUserLogin(self, room, user, puid):
        pass

    def onUserLogout(self, room, user, puid):
        pass


class RoomManager(Gestor):
    """
    Compatibilidad con la ch
    """
    pass
