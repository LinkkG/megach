"""
File: roxvent.py
Title: Librería de chatango
Original Author: megamaster12 <supermegamaster32@gmail.com>
Current Maintainers and Contributors:
    Megamaster12
Version: M1.5
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
# Copyright 2011 Lumirayz
# This program is distributed under the terms of the GNU GPL.
"""
################################################################
# Imports
################################################################
#####
#
#####

import collections
import html
import os
# noinspection PyCompatibility
import queue
import random
import re
import select
import socket
import sys
import threading
import time

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
_users = dict()


def _getAnonId(num, ts) -> str:
    """Obtener una id de anon
    TODO Cambiar el while sin perder velocidad
    """
    ts = '3452' if ts is None else ts
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
    num, ssid = num[6:10], ssid[-4:]
    return 'anon' + _getAnonId(num, ssid)


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
    maxnum = sum(map(lambda x: x[1], tsweights))
    cumfreq = 0
    sn = 0
    for wgt in tsweights:
        cumfreq += float(wgt[1]) / maxnum
        if (num <= cumfreq):
            sn = int(wgt[0])
            break
    return "s" + str(sn) + ".chatango.com"


################################################################
# Cosas de los mensajes
################################################################
Channels = {
    "white": 0,
    "red": 256,
    "blue": 2048,
    "shield": 64,
    "staff": 128,
    "mod": 32780
}
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
    if n: n = n.group(1)
    f = re.search("<f(.*?)>", msg)
    if f: f = f.group(1)
    msg = re.sub("<n.*?/>", "", msg)
    msg = re.sub("<f.*?>", "", msg)
    msg = _strip_html(msg)
    msg = html.unescape(msg)
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
    match = re.match(r'\s*x(?P<size>[0-9]{2})(?P<color>[a-zA-Z0-9]{3,6})="(?P<font>.*)"', f)
    if not match:
        return None, None, None
    else:
        color = match.groups("color")[0] if match.groups("color") else None
        font = match.groups("font")[0] if match.groups("font") else None
        size = match.groups("size")[0] if match.groups("size") else None
        return color, font, int(size)


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
    FrameInfo = collections.namedtuple("FrameInfo", ["fin", "opcode", "masked", "payload_length"])
    CONTINUATION = 0
    TEXT = 1
    BINARY = 2
    CLOSE = 8

    @staticmethod
    def encode(payload: object) -> bytes:
        """
        Encodea un mensaje y lo enmascara con las reglas obligatorias del protocolo websocket
        :param payload:El string o arreglo de bytes a encodear para websocket
        :return: El arreglo de Bytes enmascarado
        """
        opcode = WS.CONTINUATION
        pl = payload
        frame = bytearray()
        mask = os.urandom(4)
        if isinstance(pl, str):
            pl = pl.encode("utf-8", "replace")
        frame.append(opcode)
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
        returns False if the headers are invalid for a websocket handshake
        returns the key
        """
        version = None
        if isinstance(headers, (bytes, bytearray)):
            if b"\r\n\r\n" in headers:
                headers, _ = headers.split(b"\r\n\r\n", 1)
            headers = headers.decode()
        if isinstance(headers, str):
            headers = headers.splitlines()
        if isinstance(headers, list):
            if ": " not in headers[0]:
                version, _ = headers[0].split(" ", 1)
                headers = headers[1:]
            headers = {y.lower(): z for y, z in map(lambda x: x.split(": ", 1), headers)}

        if version:
            version = version.split("/")[1]
            version = tuple(int(x) for x in version.split("."))
            if version[0] < 1:
                return False
            if version[1] < 1:
                return False
        if "upgrade" not in headers or headers["upgrade"] != "websocket":
            return False
        elif "connection" not in headers or headers["connection"].lower() != "upgrade":
            return False
        elif "sec-websocket-accept" not in headers:
            return False

        return headers["sec-websocket-accept"]

    @staticmethod
    def frameInfo(buffer: bytes) -> FrameInfo:
        """
        returns a tuple that describes a frame
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
        return WS.FrameInfo(bool(buffer[0] & 128), buffer[0] & 15, bool(buffer[1] & 128), payload_length)

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
    if name is None: name = ""
    user = _users.get(name.lower())
    if not user:
        user = _User(name=name, **kwargs)
        _users[name] = user
    return user


class _User():
    # TODO revisar
    def __init__(self, name, **kwargs):
        self._showname = name
        self._name = name.lower()
        self._sids = dict()
        self._msgs = list()
        self._nameColor = '000'
        self._fontSize = 12
        self._fontFace = '0'
        self._fontColor = '0'
        self._mbg = False
        self._mrec = False
        for attr, val in kwargs.items():
            if val is None: continue
            setattr(self, '_' + attr, val)
        # TODO Más cosas del user

    ####
    # Properties
    ####
    def _getName(self):
        return self._name

    def _getSessionIds(self, room=None):
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

    def _getNameColor(self):
        return self._nameColor

    name = property(_getName)
    sessionids = property(_getSessionIds)
    rooms = property(_getRooms)
    roomnames = property(_getRoomNames)
    fontColor = property(_getFontColor)
    fontFace = property(_getFontFace)
    fontSize = property(_getFontSize)
    nameColor = property(_getNameColor)

    ####
    # Util
    ####
    def addSessionId(self, room, sid):
        """
        Agrega una sesión a una sala del usuario
        :param room: Sala donde tiene esa sesión conectado
        :param sid: Sesión del usuario
        """
        if room not in self._sids:
            self._sids[room] = set()
        self._sids[room].add(sid)


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
        self._uid = ""
        self._nameColor = "000"
        self._fontSize = 12
        self._fontFace = "0"
        self._fontColor = "000"
        self._channel = 0
        self._badge = 0
        for attr, val in kw.items():
            if val is None: continue
            setattr(self, "_" + attr, val)

    ####
    # Properties
    ####
    def _getUser(self):
        return self._user

    def _getId(self):
        return self._msgid

    def _getTime(self):
        return self._time

    def _getBody(self):
        return self._body

    def _getIP(self):
        return self._ip

    def _getFontColor(self):
        return self._fontColor

    def _getFontFace(self):
        return self._fontFace

    def _getFontSize(self):
        return self._fontSize

    def _getNameColor(self):
        return self._nameColor

    def _getRoom(self):
        return self._room

    def _getRaw(self):
        return self._raw

    def _getUnid(self):
        return self._unid

    def _getPuid(self):
        return self._puid

    def _getChannel(self):
        return self._channel

    def _getBadge(self):
        return self._badge

    msgid = property(_getId)
    time = property(_getTime)
    user = property(_getUser)
    body = property(_getBody)
    room = property(_getRoom)
    ip = property(_getIP)
    fontColor = property(_getFontColor)
    fontFace = property(_getFontFace)
    fontSize = property(_getFontSize)
    raw = property(_getRaw)
    nameColor = property(_getNameColor)
    unid = property(_getUnid)
    puid = property(_getPuid)
    uid = property(_getPuid)  # other library use uid so we create an alias
    channel = property(_getChannel)
    badge = property(_getBadge)

    ####
    # Attach/detach
    ####
    def attach(self, room, msgid):
        """
        Attach the Message to a message id.
        @type msgid: str
        @param msgid: message id
        :param room:
        """
        if self._msgid is None:
            self._room = room
            self._msgid = msgid
            self._room._msgs[msgid] = self

    def detach(self):
        """Detach the Message."""
        if self._msgid is not None and self._msgid in self._room._msgs:
            del self._room._msgs[self._msgid]
            self._msgid = None

    def delete(self):
        self._room.deleteMessage(self)


class Room:
    def __init__(self, name, mgr):
        self.imsgs_drawn = 0
        self.imsg_array = list()
        self.imsgs_rendered = False
        self.lastmsgnum = 0
        self.bmsg_array = list()
        self.msg_array = list()
        self._connected = False
        self._name = name
        self._pingInterval = 200
        self.connectattempts = 0
        self._firstCommand = True
        self.groupname = name
        self._history = list()
        self.status = None
        self.groupURL = name  # TODO
        self.mgr = mgr
        self.participants = list()
        self._port = 1800  # TODO
        self.grouphistory = None
        self.ownername = ''
        self._rbuf = b''
        self.sellers_array = list()
        self._server = getServer(name)  # TODO
        self._sock = None  # TODO
        self.usercount = 0
        self._wbuf = b""
        self._wlock = False
        self._wlockbuf = b""
        self._mqueue = dict()
        self._msgs = dict()
        self._currentname = None
        self._silent = False
        # Added
        self._channel = 0
        self._badge = 0
        self._time = None
        if self.mgr:
            self._connect()
        # TODO

    ####
    # Propiedades
    ####
    def _getChannel(self):
        return self._channel

    def _setChannel(self, c):
        self._channel = c

    def _getBadge(self):
        return self._badge

    def _setBadge(self, c):
        self._badge = c

    def _getConnected(self):
        return self._connected

    def _getName(self):
        return self._name

    def _getSock(self):
        return self._sock

    def _getUser(self):
        return self.mgr.user

    def _getWbuf(self):
        return self._wbuf

    connected = property(_getConnected)
    channel = property(_getChannel, _setChannel)
    badge = property(_getBadge, _setBadge)
    name = property(_getName)
    sock = property(_getSock)
    user = property(_getUser)
    wbuf = property(_getWbuf)

    ####
    # Funciones
    ####
    ####
    # History
    ####
    def _addHistory(self, msg):
        """
        Add a message to history.
        @type msg: Message
        @param msg: message
        """
        self._history.append(msg)
        if len(self._history) > self.mgr._maxHistoryLength:
            rest, self._history = self._history[:-self.mgr._maxHistoryLength], self._history[
                                                                               -self.mgr._maxHistoryLength:]
            for msg in rest: msg.detach()

    def message(self, msg, html=False, canal=None):
        """
        TODO revisar
        Send a message. (Use "\n" for new line)
        @type msg: str
        @param msg: message
        :param canal: El número del canal. Del 0 al 4 son Normal,Rojo,Azul,Azul+Rojo,Mod
        """
        if canal == None:
            canal = self.channel
        if canal < 4:
            canal = (((canal & 2) << 2 | (canal & 1)) << 8)
        elif canal == 4:
            canal = 32768
        if msg is None:
            return
        msg = msg.rstrip()
        if not html:
            msg = msg.replace("<", "&lt;").replace(">", "&gt;")
        if len(msg) > self.mgr._maxLength:
            if self.mgr._tooBigMessage == BigMessage_Cut:
                self.message(msg[:self.mgr._maxLength], html=html)
            elif self.mgr._tooBigMessage == BigMessage_Multiple:
                while len(msg) > 0:
                    sect = msg[:self.mgr._maxLength]
                    msg = msg[self.mgr._maxLength:]
                    self.message(sect, html=html)
            return
        msg = '<n41DEED/><f x032555="1">' + msg
        msg = "<n" + self.user.nameColor + "/>" + msg

        if self._currentname != None and not self._currentname.startswith("!anon"):
            font_properties = "<f x%0.2i%s=\"%s\">" % (self.user.fontSize, self.user.fontColor, self.user.fontFace)
            if "\n" in msg:
                msg.replace("\n", "</f></p><p>%s" % (font_properties))
            msg = font_properties + msg

        msg.replace("~", "&#126;")
        self.rawMessage('%s:%s' % (canal + self.badge * 64, msg))

    def startConnection(self):
        # TODO posibles errores acá cuando no hay net o se desconecta
        self._connect()

    def _callEvent(self, evt, *args, **kw):
        getattr(self.mgr, evt)(self, *args, **kw)
        self.mgr.onEventCalled(self, evt, *args, **kw)

    def _connect(self):
        self.connectattempts += 1
        if self._sock is not None:
            self._sock.close()
            del self._sock
        self._sock = socket.socket()
        self._sock.connect((self._server, self._port))  # TODO Si no hay internet hay error acá
        self._sock.setblocking(False)
        self.status = "connecting"
        self._wbuf = (b"GET / HTTP/1.1\r\n"
                      b"Host: " + "{}:{}".format(self._server, self._port).encode() +
                      b"\r\n"
                      b"Origin: http://st.chatango.com\r\n"
                      b"Connection: Upgrade\r\n"
                      b"Upgrade: websocket\r\n"
                      b"Sec-WebSocket-Key: uJkrw+8KgVIZOr2PVaz1Yg==\r\n"
                      b"Sec-WebSocket-Version: 13\r\n"
                      b"\r\n")
        # self._setWriteLock(True)

    def disconnect(self):
        # TODO
        self._disconnect()
        self._callEvent("onDisconnect")
        del self.mgr._rooms[self.name]

    def _disconnect(self):
        # TODO
        if (self._sock is not None):
            self._sock.close()
        self._sock = None

    def getAnonName(self, num, ts):
        return 'anon' + _getAnonId(num, ts)

    def _do_handshake(self, uname=None, password=None):  # TODO auth(self)
        """Autenticar.
        Logearse como uname con password"""
        self.reset()  # TODO
        self.nomore = False
        __reg2 = ["bauth", self.groupURL, _genUid(), uname or self.mgr.name]  # TODO comando
        self._currentname = uname or self.mgr.name
        if not uname and self.mgr.password:
            __reg2.append(self.mgr.password)
        else:
            __reg2.append(password or '')
        self._sendCommand(*__reg2)

    def closeHistory(self):
        if self.grouphistory:
            self.grouphistory.visible = False

    def rawMessage(self, msg):
        """
        Send a message without n and f tags.
        @type msg: str
        @param msg: message
        """
        if not self._silent:
            self._sendCommand("bm", "meme", msg)

    def ping(self):
        """Send a ping.TODO"""
        self._sendCommand("")
        self._callEvent("onPing")
        pass

    def _reconnect(self):
        # TODO reiniciar todas las conexiones
        self._disconnect()
        self._connect()

    def reconnect(self):
        self._callEvent('onReconnect')
        self._reconnect()

    def reset(self):
        # TODO
        # self._clearmessages()
        # self.groupchat_mc.messages_mc.h = 0
        # self.groupchat_mc.messages_mc.y_top = 0
        self.closeHistory()
        self.participants_number = 0
        self.participants_number = list()
        # self.disconnect()
        # self.startConnection()
        # self.input_mc.reset()
        # group_classes.PremiumStatus.getInstance().reset()
        # group_classes.BannedWords.getInstance().clearRequests()
        # _root.chatango_msg.removeMovieClip()

    def _sendCommand(self, *args):
        """
        Send a command.
        @type args: [str, str, ...]
        @param args: command and list of arguments
        """
        if self._firstCommand:
            terminator = b"\x00"
            self._firstCommand = False
        else:
            terminator = b"\r\n\x00"

        cmd = ":".join(args).encode(errors='replace') + terminator
        self._write(WS.encode(cmd))

    def _setWriteLock(self, lock):
        # TODO
        self._wlock = lock
        if not self._wlock and self._wlockbuf:
            self._write(self._wlockbuf)
            self._wlockbuf = b""

    def _write(self, data: bytes):
        if self._wlock:
            self._wlockbuf += data
        else:
            self._wbuf += data

    def on_tagserver_data(self, data):
        """Al recibir datos del servidor"""
        self._rbuf += data
        if self.status == "connecting" and b'\r\n' * 2 in data:
            headers, self._rbuf = self._rbuf.split(b"\r\n" * 2)
            clave = WS.checkHeaders(headers)
            if clave != 'Vm7scDIsH+hcgn948Ftni+ulSAs=':
                pass  # TODO
            else:
                self.status = "connected"
                self._setWriteLock(False)
                self._do_handshake()  # auth

        else:
            r = WS.checkFrame(self._rbuf)
            while r:
                frame = self._rbuf[:r]
                self._rbuf = self._rbuf[r:]
                info = WS.frameInfo(frame)  # TODO
                payload = WS.getPayload(frame)
                if info.opcode == WS.CLOSE:  # server wants to close connection
                    pass  # self.reconnect()
                elif info.opcode == WS.TEXT:  # actual data
                    self._process(payload)
                elif debug:
                    print("unhandled frame:", "with payload", payload, file=sys.stderr)
                r = WS.checkFrame(self._rbuf)

    def _process(self, data):
        """
        Process a command string.

        @type data: str
        @param data: the command string
        """
        self._callEvent("onRaw", data)
        data = data.split(":")
        cmd, args = data[0], data[1:]
        func = "_rcmd_" + cmd
        if hasattr(self, func):
            getattr(self, func)(args)
        elif debug:
            print("unknown data:", data, file=sys.stderr)

    def _rcmd(self):
        self._callEvent('onPong')

    def _rcmd_b(self, args):  # TODO
        mtime = float(args[0])  # Hora de envío del mensaje
        name = args[1]  # Nombre de usuario si lo hay
        tempname = args[2]  # Nombre del anon si no se ha logeado
        puid = args[3]  # Id del usuario
        msgid = args[4]  # Id del mensaje
        unknown2 = args[5]
        ip = args[6]  # Ip del usuario
        color = args[7] or 0
        badge = 0
        rawmsg = ":".join(args[9:])
        if color and color.isdigit():
            color = int(color)
            if color < 256:  # Canal Normal
                badge = 0 if color < 64 else 1 if color < 128 else 2
                color = 0
            elif 256 <= color < 2048:  # Canal Rojo con o sin badge
                badge = 0 if color < 256 + 64 else 1 if color < 256 + 128 else 2
                color = 256
            elif 2048 <= color < 2304:
                badge = 0 if color < 2048 + 64 else 1 if color < 2048 + 128 else 2
                color = 2048
            elif 2304 <= color < 32768:
                badge = 0 if color < 2304 + 64 else 1 if color < 2304 + 128 else 2
                color = 2304
            elif color >= 32768:
                badge = 0 if color < 32768 + 64 else 1 if color < 32768 + 128 else 2
                color = 32768
        body, n, f = _clean_message(rawmsg)
        if name == "":
            nameColor = None
            name = "#" + args[2]
            if name == "#":
                name = "!anon" + _getAnonId(n, puid)
        else:
            if n:
                nameColor = n
            else:
                nameColor = None
        i = args[5]
        unid = args[4]
        user = User(name)
        # Create an anonymous message and queue it because msgid is unknown.
        if f:
            fontColor, fontFace, fontSize = _parseFont(f)
        else:
            fontColor, fontFace, fontSize = None, None, None
        msg = Message(time=mtime,
                      user=user,
                      body=body,
                      raw=rawmsg,
                      ip=ip,
                      nameColor=nameColor,
                      fontColor=fontColor,
                      fontFace=fontFace,
                      fontSize=fontSize,
                      unid=unid,
                      puid=puid,
                      room=self,
                      channel=color,
                      badge=badge)
        self._mqueue[i] = msg

    def _rcmd_g_participants(self, args):
        self.participants = list()
        self.sellers_array = list()
        self.participants_number = 0
        args = ':'.join(args).split(";")
        for data in args:
            self.participants_number += 1
            data = data.split(':')  # Lista de un solo usuario
            name = data[3]
            puid = data[2]
            if name.lower() == 'none':
                name = '!' + getanonname(data[1].split('.')[0], puid)
            user = User(name, room=self)
            user.addSessionId(self, data[0])
            self.participants.append(user)
            self.sellers_array.append(user)

    def _rcmd_gparticipants(self, args):
        self._rcmd_gparticipants(args)
        pass

    def _rcmd_getpremium(self, args):
        # TODO
        print("here")

    def _rcmd_i(self, args):  # TODO
        pass

    def _rcmd_inited(self, args):  # TODO
        """Em el chat es solo para desactivar la animación de espera por conexión"""
        self._sendCommand("g_participants", "start")
        self._sendCommand("getpremium", "l")
        if args and debug:
            print('New Unhandled arg on inited ', file=sys.stderr)
        if self.connectattempts <= 5:
            self._callEvent("onConnect")
            # TODO
        else:
            self._callEvent("onReconnect")
            # TODO
        pass

    def _rcmd_n(self, args):  # TODO
        pass

    def _rcmd_ok(self, args):
        self._connected = True
        self.ownername = args[0]
        self.user_id = args[1]
        self._authtype = args[2]  # TODO tipo C
        self._currentname = args[3]
        self._connectiontime = args[4]
        self._currentIP = args[5]
        self._modsServer = args[6]  # TODO Lista de mods name:number;name,number
        self._flagsdelgrupo = args[7]
        self._pingTask = self.mgr.setInterval(self.mgr._pingDelay, self.ping)
        # TODO
        pass

    def _rcmd_u(self, args):
        temp = Struct(**self._mqueue)
        if hasattr(temp, args[0]):
            msg = getattr(temp, args[0])
            if msg._user != self.user:
                # msg.user._fontColor = msg.fontColor
                # msg.user._fontFace = msg.fontFace
                # msg.user._fontSize = msg.fontSize
                # msg.user._nameColor = msg.nameColor
                pass
            del self._mqueue[args[0]]
            msg.attach(self, args[1])
            self._addHistory(msg)
            self._callEvent("onMessage", msg.user, msg)


class Gestor:
    _TimerResolution = 0.2
    _maxHistoryLength = 700
    _maxLength = 1800
    _pingDelay = 200  # 20

    def __init__(self, name=None, password=None, pm=None):
        self._name = name
        self._password = password
        self._pm = pm
        self._rooms = dict()
        self._rooms_queue = queue.Queue()
        self._rooms_lock = threading.Lock()
        self._running = False
        self._tasks = set()

    ####
    # Propiedades
    ####
    def _getName(self):
        return self._name

    def _getPassword(self):
        return self._password

    def _getUser(self):
        return User(self._name)

    name = property(_getName)
    password = property(_getPassword)
    user = property(_getUser)

    @classmethod
    def easy_start(cls, rooms=None, name=None, password=None, pm=True):
        if not rooms:
            rooms = str(input('Nombres de salas separados por coma: ')).split(';')
        if not rooms:
            rooms = []
        if name is None: name = str(input("Usuario: "))
        if not name:
            name = ''
        if password is None: password = str(input("User password: "))
        if not password:
            password = ''
        self = cls(name, password, pm)
        for room in rooms:
            self.joinRoom(room)
        self.main()

    def onInit(self):
        pass

    class _Task:
        def __init__(self, mgr):
            """
            Inicia una tarea nueva
            :param mgr: El dueño de esta tarea y el que la mantiene con vida
            """
            self.mgr = mgr

        def cancel(self):
            """Sugar for removeTask."""
            self.mgr.removeTask(self)

    def getConnections(self):
        li = list(self._rooms.values())
        if self._pm:
            li.extend(self._pm.getConnections())
        return [c for c in li if c._sock is not None]

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

    def joinRoom(self, room):
        if room not in self._rooms:
            self._rooms[room] = Room(room, self)  # TODO
            return True
        else:
            return None
        pass

    def main(self):
        # TODO
        self.onInit()
        self._running = True
        while self._running:
            try:
                conns = self.getConnections()
                if not conns:
                    self._running = False
                socks = [x._sock for x in conns]
                wsocks = [x._sock for x in conns if x._wbuf]
                rd, wr, sp = select.select(socks, wsocks, socks, self._TimerResolution)
                for sock in wr:  # Enviar
                    try:
                        con = [x for x in conns if x.sock == sock][0]
                        size = sock.send(con._wbuf)
                        con._wbuf = con._wbuf[size:]
                    except Exception as e:
                        print("error al enviar" + str(e), sys.stderr)
                        ##
                for sock in rd:  # Recibir
                    con = [x for x in conns if x.sock == sock][0]
                    chunk = sock.recv(1024)
                    if chunk:  # TODO
                        con.on_tagserver_data(chunk)
                    else:
                        pass  # con.disconnect()#.disconnect()#con.reconnect()
            except Exception as e:
                print("error en main " + str(e), file=sys.stderr)
                raise e
            self._tick()

    def setInterval(self, intervalo, funcion, *args, **kwargs):
        """
        Llama a una función cada intervalo con los argumentos indicados
        @type intervalo int
        @param intervalo:intervalo
        TODO
        :param funcion:  La función que será ejecutada durante el intérvalo
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

    def _tick(self):
        now = time.time()
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

    @staticmethod
    def _write(room, data):
        # Todo Eliminar, esto no sirve
        room._write(data)

        # room._wbuf += data

    def onConnect(self, room):
        pass

    def onDisconnect(self, room):
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

    def onMessage(self, room, user, message):
        pass

    def onPing(self, room):
        pass

    def onPong(self, room):
        pass

    def onRaw(self, room, raw):
        """
        Called before any command parsing occurs.
        @type room: Room
        @param room: room where the event occured
        @type raw: str
        @param raw: raw command data
        """
        pass

    def onReconnect(self, room):  # TODO

        pass
