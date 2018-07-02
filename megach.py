#!/usr/bin python
# -*- coding: utf-8 -*-
"""
File: megach.py
Title: Librería de chatango
Original Author: megamaster12 <supermegamaster32@gmail.com>
Current Maintainers and Contributors:
    Megamaster12
Version: M1.9.1
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
import html as html2
import sys

if sys.version_info[1] < 5:
    from html.parser import HTMLParser

    html2.unescape = HTMLParser().unescape
import mimetypes
import os
import queue
import random
import re
import select
import socket
import time
import threading
import urllib.parse as urlparse
import urllib.request as urlreq
from urllib.error import HTTPError, URLError

################################################################
# Depuración
################################################################
version = 'M1.9.1'
version_info = version.split('.')
debug = True
################################################################
# Cosas del servidor, las cuentas y el manejo de mods
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

GroupFlags = {
    "LIST_TAXONOMY":     1,
    "NOANONS":           4, "NOFLAGGING": 8, "NOCOUNTER": 16, "NOIMAGES": 32, "NOLINKS": 64, "NOVIDEOS": 128,
    "NOSTYLEDTEXT":      256, "NOLINKSCHATANGO": 512, "NOBRDCASTMSGWITHBW": 1024, "RATELIMITREGIMEON": 2048,
    "CHANNELSDISABLED":  8192, "NLP_SINGLEMSG": 16384, "NLP_MSGQUEUE": 32768, "BROADCAST_MODE": 65536,
    "CLOSED_IF_NO_MODS": 131072, "IS_CLOSED": 262144, "SHOW_MOD_ICONS": 524288, "MODS_CHOOSE_VISIBLITY": 1048576,
    "HAS_XML":           268435456, "UNSAFE": 536870912
    }

ModFlags = {
    'DELETED':             1, 'EDIT_MODS': 2,
    'EDIT_MOD_VISIBILITY': 4, 'EDIT_BW': 8,
    'EDIT_RESTRICTIONS':   16, 'EDIT_GROUP': 32,
    'SEE_COUNTER':         64, 'SEE_MOD_CHANNEL': 128,
    'SEE_MOD_ACTIONS':     256, 'EDIT_NLP': 512,
    'EDIT_GP_ANNC':        1024, 'EDIT_ADMINS': 2048,
    'EDIT_SUPERMODS':      4096, 'NO_SENDING_LIMITATIONS': 8192,
    'SEE_IPS':             16384, 'CLOSE_GROUP': 32768,
    'CAN_BROADCAST':       65536, 'MOD_ICON_VISIBLE': 131072,
    'IS_STAFF':            262144
    }

AdminFlags = ModFlags["EDIT_MODS"] | ModFlags["EDIT_RESTRICTIONS"] | ModFlags["EDIT_GROUP"] | ModFlags["EDIT_GP_ANNC"]

Fonts = {'arial':      0, 'comic': 1, 'georgia': 2, 'handwriting': 3, 'impact': 4, 'palatino': 5, 'papirus': 6,
         'times':      7, 'typewriter': 8
}

def _genUid() -> str:
    """Generar una uid ALeatoria de 16 dígitos. Se usa en el login por seguridad"""
    return str(random.randrange(10 ** 15, 10 ** 16))


def _getAnonId(puid: str, ts: str) -> str:
    """
    Obtener una id de anon.
    @param puid: PUID del usuario de 4 cifras.
    @param ts: Tiempo de sesión en que se conectó el anon debe ser un string con un entero
    @return: Número con la id de anon
    """
    if not ts or len(ts) < 4:
        ts = '3452'
    else:
        ts = ts.split('.')[0][-4:]
    __reg5 = ''
    __reg1 = 0
    while __reg1 < len(puid):
        __reg4 = int(puid[__reg1])
        __reg3 = int(ts[__reg1])
        __reg2 = str(__reg4 + __reg3)
        __reg5 += __reg2[-1:]
        __reg1 += 1
    return __reg5


def convertPM(msg: str):  # TODO Medir velocidad y acelerar
    """
    Convertir las fuentes de un mensaje normal en fuentes para el PM
    Util para usar múltiples fuentes
    @param msg: Mensaje con fuentes incrustadas
    @return: Mensaje con etiquetas f convertidas a g
    """
    fuentes = re.findall("(<f.*?>)", msg)
    left, found, right = '', '', msg
    msg = ''
    while right and fuentes:
        left, found, right = right.partition(fuentes[0])
        s, c, f = _parseFont(found)
        s = s or '11'
        c = c or '00F'
        f = f or '1'
        c = c[::2] if len(c) == 6 else c[:3]
        msg += left + '</g>'
        msg += '<g x{:0>2.2}s{}="{}">'.format(s, c, f)
        if len(fuentes) > 1:
            fuentes = fuentes[1:]
        else:
            fuentes = []
    msg += right
    return msg


def getanonname(puid: str, tssid: str) -> str:
    """
    Regresa el nombre de un anon usando su numero y tiempo de conexión
    @param puid: La id personal de un usuario anon
    @param tssid: El tiempo de inicio de sesión para el anon
    @return: String con el nombre de usuario del anon
    """
    return 'anon' + _getAnonId(puid.zfill(8)[4:8], tssid).zfill(4)


def getServer(group: str) -> str:
    """
    Obtiene el servidor para una sala
    @param group: El nombre de la sala
    @return: string en formato s##.chatango.com
    """
    return "s" + str(getServerNumber(group)) + ".chatango.com"


def getServerNumber(group: str) -> int:
    """
    Calcula el número del servidor para una sala
    @param group: String con el nombre de la sala
    @return: Número del servidor
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
    return sn


################################################################
# Cosas de los mensajes y los canales
################################################################
Channels = {
    "white":  0,
    "red":    256,
    "blue":   2048,
    "shield": 64,
    "staff":  128,
    "mod":    32780
    }  # TODO darle uso


def _clean_message(msg: str, pm: bool = False) -> [str, str, str]:
    """
    TODO Revisar carácteres comilla y escapes en mensajes
    Clean a message and return the message, n tag and f tag.
    @type msg: str
    @param msg: the message
    @rtype: str, str, str
    @returns: cleaned message, n tag contents, f tag contents
    """
    n = re.search("<n(.*?)/>", msg)
    if pm:
        f = re.search("<f(.*?)>", msg)
        msg = re.sub("<f.*?>", "", msg)
    else:
        f = re.search("<g(.*?)>", msg)
        msg = re.sub("<g.*?>", "", msg)
    if n:
        n = n.group(1)
    if f:
        f = f.group(1)
    msg = re.sub("<n.*?/>", "", msg)
    msg = _strip_html(msg)
    msg = html2.unescape(msg).replace('\r', '\n')
    return msg, n or '', f or ''


def _strip_html(msg: str) -> str:
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


def _parseFont(f: str, pm = False) -> [str, str, str]:
    """
    Lee el contendido de un etiqueta f y regresa
    tamaño color y fuente
    @param f: El texto con la etiqueta f incrustada
    @return: Tamaño, Color, Fuente
    """
    if pm:
        matchs = re.findall('x(\d+){0,2}s([0-9a-fA-F]{3,6})=["\'](\d)["\']', f)
    else:
        matchs = re.findall('x(\d+){0,2}([0-9a-fA-F]{3,6})=["\'](\d)["\']', f)
    if matchs and len(matchs[0]) == 3:
        return matchs[0]
    else:
        return None, None, None


def _parseNameColor(n: str) -> str:
    """Return the name color from message"""
    # probably is already the name
    return _clean_message(n)[1]

################################################################
# Inicio del bot
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
    FrameInfo = namedtuple("FrameInfo", ["fin", "opcode", "masked", "payload_length"])
    CONTINUATION = 0
    TEXT = 1
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
            headers = headers.decode(errors = 'ignore')
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

    @staticmethod
    def RPOST(url, data, headers = None):
        """ TODO Asegurar valor de retorno
        Solicitar un token de id usando un nombre y una clave
        @param data: Los datos que serán enviados en la consulta POST
        @param headers: Las cabeceras de la consulta POST
        @param url: La url a la que se hará la consulta
        """
        data = urlparse.urlencode(data).encode()
        if not headers:
            headers = {"host": "chatango.com", "origin": "http://st.chatango.com"}
        pet = urlreq.Request(url, data = data,
                             headers = headers)
        try:
            resp = urlreq.urlopen(pet)
            headers = resp.headers
            lectura = resp.read()  # TODO variable de depuración, eliminar
        except HTTPError as e:
            if debug:
                print('Error code: ', e.code)
            return None
        except URLError as e:
            if debug:
                print('Error Reason: ', e.reason)
            return None
        except Exception as e:
            if debug:
                print('Error, not controlled: ', str(e))
            return None
        return headers


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
    return user


class _User:
    """
    Clase que representa a un usuario de chatango
    Iniciarlo sin el guion bajo para evitar inconvenientes
    """

    def __radd__(self, other):
        return str(other) + self.name

    def __add__(self, other):
        return self.name + str(other)

    def __str__(self):
        return self.showname

    def __repr__(self):
        return "<User: %s>" % self.name

    def __init__(self, name, **kwargs):
        self._fontColor = '0'
        self._fontFace = '0'
        self._fontSize = 12
        self._ip = ''
        self._isanon = not len(name) or name[0] in '!#'
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
    def fontColor(self) -> str:
        """Color de la última fuente usada por el usuario"""
        return self._fontColor

    @property
    def fontFace(self) -> str:
        """Estilo de la fuente, un entero en un string"""
        return self._fontFace

    @property
    def fontSize(self) -> int:
        """Tamaño de la última fuente usada por el usuario"""
        return self._fontSize

    @property
    def ip(self) -> str:
        """Ip del usuario, puede ser un string vacío"""
        return self._ip

    @property
    def isanon(self) -> bool:
        """Soy anon?"""
        return self._isanon

    @property
    def name(self) -> str:
        """Nombre del usuario"""
        return self._name

    @property
    def nameColor(self) -> str:
        """El color del nombre que utiliza el usuario"""
        return self._nameColor

    @property
    def showname(self) -> str:
        """Nombre visible del usuario, excluye los ! y # en los anon"""
        return self._showname.strip('!#')

    @property
    def rooms(self) -> list:
        """Las salas en las que se encuentra el usuario."""
        return list(self._sids.keys())

    @property
    def roomnames(self):
        """Lista de salas"""
        return [room.name for room in self._sids]

    def _getSessionIds(self, room = None):
        if room:
            return self._sids.get(room, set())
        else:
            return set.union(*self._sids.values())

    sessionids = property(_getSessionIds)

    ####
    # Util
    ####
    def addPersonalUserId(self, room, puid):
        """TODO comprobar"""
        if room not in self._puids:
            self._puids[room] = set()
        self._puids[room].add(puid)

    def addSessionId(self, room, sid):
        """
        TODO la lista de sesiones puede ser igual a la lista de ids?
        Agrega una sesión a una sala del usuario
        @param room: Sala donde tiene esa sesión conectado
        @param sid: Sesión del usuario
        """
        if room not in self._sids:
            self._sids[room] = set()
        self._sids[room].add(sid)

    def removeSessionId(self, room, sid):
        if room in self._sids:
            if sid in self._sids[room]:
                self._sids[room].remove(sid)
            if len(self._sids[room]) == 0:
                del self._sids[room]

    def setName(self, value):
        """Reajusta el nombre de un usuario
        # TODO para uso en participant 2. Al cambiar aquí vigilar _users
        """
        self._name = value.lower()
        self._showname = value


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

    def __len__(self):
        return len(self.body)

    def __add__(self, otro):
        return self.body + str(otro)

    def __radd__(self, otro):
        return str(otro) + self.body

    def __repr__(self):
        return '<Message>'

    def __str__(self):
        return self.body

    ####
    # Properties
    ####
    @property
    def badge(self):
        """Insignia del mensaje, Ninguna, Mod, Staff son 0 1 o 2"""
        return self._badge

    @property
    def body(self):
        """
        Cuerpo del mensaje sin saltos de linea TODO quitar espacios extra
        """
        return self._body.replace('\n', ' ').replace('  ', ' ')

    @property
    def channel(self):
        return self._channel

    @property
    def fontColor(self):
        """Color de la fuente usada en el mensaje"""
        return self._fontColor

    @property
    def fontFace(self):
        """Estilo de la fuente en el mensaje, numero en string"""
        return self._fontFace

    @property
    def fontSize(self):
        """Tamaño de la fuente usada en el mensaje"""
        return self._fontSize

    @property
    def fullbody(self):
        """Cuerpo completo del mensaje"""
        return self._body.strip()

    @property
    def ip(self):
        return self._ip

    @property
    def msgid(self):
        """ID del mensaje en la sala"""
        return self._msgid

    @property
    def nameColor(self):
        """Color del nombre de usuario en el mensaje"""
        return self._nameColor

    @property
    def puid(self):
        """Id personal del usuario del mensaje"""
        return self._puid

    @property
    def raw(self):
        return self._raw

    @property
    def room(self):
        """Sala en la que está el mensaje, puede ser PM"""
        return self._room

    @property
    def uid(self):
        """Id del usuario del mensaje TODO """
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
        """Hora de envío del mensaje"""
        return self._time

    @property
    def localtime(self):
        return time.localtime(self._time)

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
    Base para manejar las conexiones con Mensajes y salas.
    No Instanciar directamente
    """
    BIGMESSAGECUT = False  # Si es True se manda solo un pedazo de los mensajes, false y se mandan todos
    MAXLEN = 2800  # 2900 ON PM IS > 12000
    PINGINTERVAL = 90  # Intervalo para enviar pings, Si llega a 300 se desconecta

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
        self._bgmode = 0
        self._connectattempts = 0
        self._connected = False
        self._currentaccount = [name, password]
        self._currentname = name  # El usuario de esta conexión
        self._firstCommand = True  # Si es el primer comando enviado
        self._headers = b''  # Las cabeceras que se enviaron en la petición
        self._name = name  # El nombre de la sala o conexión
        self._origin = origin or 'http://st.chatango.com'
        self._password = password  # La clave de esta conexión
        self._port = port or 443  # El puerto de la conexión
        self._rbuf = b''  # El buffer de lectura  de la conexión
        self._server = server
        self._connectiontime = 0  # Hora del servidor a la que se entra
        self._correctiontime = 0  # Diferencia entre la hora local y la del server
        self._serverheaders = b''  # Las caberceras de respuesta que envió el servidor
        self._sock = None
        self._user = User(name)
        self._wbuf = b''  # El buffer de escritura a la conexión
        self._wlock = False  # Si está activo no se debe envíar nada al buffer de escritura
        self._wlockbuf = b''  # Buffer de escritura bloqueado, se almacena aquí cuando el lock está activo
        self.mgr = mgr  # El dueño de esta conexión
        if mgr:  # Si el manager está activo iniciar la conexión directamente
            self._bgmode = int(self.mgr.bgmode)
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
    def localtimetime(self):
        """Tiempo del servidor"""
        return time.localtime(time.time() + self._correctiontime)

    @property
    def time(self):
        return time.time() + self._correctiontime

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
        if not self._connected:
            self._connectattempts += 1
            self._sock = socket.socket()
            self._sock.connect((self._server, self._port))  # TODO Si no hay internet hay error acá
            self._sock.setblocking(False)
            self._handShake()
            return True
        return False

    def _disconnect(self):
        """Privado: Solo usar para reconneción
        Cierra la conexión y detiene los pings, pero el objeto sigue existiendo dentro de su mgr"""
        self._connected = False
        if self._sock is not None:
            self._sock.close()
        # TODO do i need to clear session ids?
        self._sock = None
        self._serverheaders = b''
        self._pingTask.cancel()

    def disconnect(self):
        """Público, desconección completa"""
        self._disconnect()
        if not isinstance(self, PM):
            self._callEvent('onDisconnect')
        else:
            self._callEvent('onPMDisconnect')

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
            "Sec-WebSocket-Version: {}\r\n"
            "\r\n").format(self._server, self._port, self._origin, WS.genseckey(), WS.VERSION).encode()
        self._wbuf = self._headers
        self._setWriteLock(True)
        self._pingTask = self.mgr.setInterval(self.PINGINTERVAL, self.ping)

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
                self._callEvent('onProcessError', func, e)
                print('[%s][%s] ERROR ON PROCESS "%s" "%s"' % (time.strftime('%I:%M:%S %p'), self.name, func, e),
                      file = sys.stderr)
        elif debug:
            print('[{}][{:^10.10}]UNKNOWN DATA "{}"'.format(time.strftime('%I:%M:%S %p'), self.name, ':'.join(data)),
                  file = sys.stderr)

    def _messageFormat(self, msg: str, html: bool):
        formt = ''
        msg = msg.strip().replace('\n', '\r')
        # Reemplazar varios espacios para que sean visibles sin alterar el tageo
        fc = self.user.fontColor.lower()
        nc = self.user.nameColor
        if not html:
            msg = html2.escape(msg, quote = False).replace('~', '&#126;')
        for x in 'b i u'.split():
            msg = msg.replace('<%s>' % x, '<%s>' % x.upper()).replace('</%s>' % x, '</%s>' % x.upper())
        # TODO comprobar  velocidad comparado con el otro
        # msg = msg.replace("<b>", "<B>").replace("</b>", "</B>").replace("<i>", "<I>").replace("</i>", "</I>").replace(
        #         "<u>", "<U>").replace("</u>", "</U>")
        if self.name == 'PM':
            formt = '<n{}/><m v="1"><g x{:0>2.2}s{}="{}">{}</g></m>'
            fc = fc[::2] if len(fc) == 6 else fc[:3]
            msg = msg.replace('&nbsp;', ' ')  # fix
            msg = convertPM(msg)  # TODO No ha sido completamente probado
        else:  # Room
            msg = msg.replace('\t', '&nbsp;' * 3 + ' ').replace('   ', ' ' + '&nbsp;' + ' ')  # TODO 3 en adelante
            formt = '<n{}/><f x{:0>2.2}{}="{}">{}'
            if self.user.isanon:  # El color del nombre es el tiempo de conexión y no hay fuente
                nc = str(self._connectiontime).split('.')[0][-4:]
                formt = '<n{0}/>{4}'
        if len(msg) > self.MAXLEN:  # TODO el tamaño puede ser afectado por multifuentes
            if self.BIGMESSAGECUT:
                msg = msg[:self.MAXLEN]
            else:
                tmp = msg
                msg = list()
                while len(tmp) > self.MAXLEN:
                    msg.append(tmp[:self.MAXLEN])
                    tmp = tmp[self.MAXLEN:]
        if type(msg) != list:
            msg = [msg]
        return [formt.format(nc, str(self.user.fontSize), fc, self.user.fontFace, unimsg) for unimsg in msg]

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
                if debug:
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

    def setBgMode(self, modo):
        """Activar el BG"""
        self._bgmode = modo
        if self.connected:
            self._sendCommand('msgbg', str(self._bgmode))

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

    def _rcmd_(self, pong):
        """Al recibir un pong"""
        self._callEvent('onPong')

    def _rcmd_premium(self, args):  # TODO el tiempo mostrado usa la hora del server
        # TODO usar args para definir el estado premium y el tiempo
        if self._bgmode and (args[0] == '210' or (isinstance(self, Room) and self._owner == self.user)):
            self._sendCommand('msgbg', str(self._bgmode))


class PM(WSConnection):
    """
    Clase Base para la conexiones con la mensajería privada de chatango
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
            self._bgmode = int(self.mgr.bgmode)
            self.connect()

    @property
    def blocklist(self):
        """Lista de usuarios bloqueados en la sala"""
        return self._blocklist

    @property
    def contacts(self):
        """Mis contactos en el PM"""
        return self._contacts

    def contactnames(self):
        return [x.name for x in self.contacts]

    @property
    def _getStatus(self):
        # TODO
        return self._status

    def _getAuth(self, name: str, password: str):
        """ TODO Asegurar valor de retorno
        Solicitar un token de id usando un nombre y una clave
        @type name: str
        @param name: name
        @type password: str
        @param password: password
        @rtype: str
        @return: auid
        """
        data = {
            "user_id":     name,
            "password":    password,
            "storecookie": "on",
            "checkerrors": "yes"
            }
        resp = WS.RPOST("http://chatango.com/login", data)
        if not resp:
            return None
        for header, value in resp.items():
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
        if isinstance(user, str):  # TODO externalizar
            user = User(user)
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
        if user not in self._status:
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
        @param html: Indica si se permite código html en el contenido del mensaje
        @param user: Usuario al que enviar el mensaje
        @param msg: Mensaje que se envia (string)
        """
        if msg:
            if isinstance(user, _User):  # TODO externalizar
                user = user.name
            msg = self._messageFormat(str(msg), html)
            for unimsg in msg:
                self._sendCommand("msg", user, unimsg)
                self._callEvent('onPMMessageSend', User(user), unimsg)
            return True

    def _write(self, data: bytes):
        if not self._wlock:
            self._wbuf += data
        else:
            self._wlockbuf += data

    def _rcmd_OK(self, args):
        self._connected = True
        if args:
            print(args)
        self._sendCommand("wl")  # TODO
        self._sendCommand("getblock")  # TODO
        self._sendCommand("getpremium")
        self._callEvent('onPMConnect')

    def _rcmd_block_list(self, args):  # TODO
        self._blocklist = set()
        for name in args:
            if name == "":
                continue
            self._blocklist.add(User(name))

    def _rcmd_DENIED(self, args):  # TODO
        self._callEvent("onLoginFail")
        self._disconnect()

    def _rcmd_idleupdate(self, args):  # TODO
        pass

    def _rcmd_kickingoff(self, args):  # TODO
        self.disconnect()

    def _rcmd_msg(self, args):  # msg TODO
        name = args[0] or args[1]  # Usuario o tempname
        if not name:
            name = args[2]  # Anon es unknown
        user = User(name)  # Usuario
        mtime = float(args[3]) - self._correctiontime  # 1530420101.72 Time TODO corregir el tiempo
        unknown2 = args[4]  # 0 TODO what is this?
        rawmsg = ':'.join(args[5:])  # Mensaje
        body, n, f = _clean_message(rawmsg, pm = True)
        nameColor = n or None
        fontSize, fontColor, fontFace = _parseFont(f)
        msg = Message(
                body = body,
                fontColor = fontColor,
                fontFace = fontFace,
                fontSize = fontSize or '11',
                nameColor = nameColor,
                puid = None,
                raw = rawmsg,
                room = self,
                time = mtime,
                unid = None,
                unknown2 = unknown2,
                user = user
                )
        self._callEvent("onPMMessage", user, msg)

    def _rcmd_msgoff(self, args):  # TODO
        user = User(args[0])
        body = _strip_html(":".join(args[5:]))
        self._callEvent("onPMOfflineMessage", user, body)

    def _rcmd_reload_profile(self, args):  # TODO completar
        pass

    def _rcmd_seller_name(self, args):  # TODO completar
        pass

    def _rcmd_track(self, args):  # TODO completar
        pass

    def _rcmd_time(self, args):
        """Se recibe el tiempo del servidor y se calcula el valor de correccion"""
        self._connectiontime = args[0]
        self._correctiontime = float(self._connectiontime) - time.time()

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

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)

    def __init__(self, name: str, mgr: object = None, account: tuple = None):
        # TODO , server = None, port = None, uid = None):
        # TODO not account start anon
        super().__init__(name = account[0], password = account[1])
        self._badge = 0
        self._banlist = dict()
        self._channel = 0
        self._currentaccount = account
        self._currentname = account[0]
        self._flags = None
        # self._history = list() cambiado de tipo
        self._mqueue = dict()
        self._mods = dict()
        self._msgs = dict()
        self._name = name
        self._nameColor = ''
        self._port = 1800  # TODO
        self._rbuf = b''
        self._server = getServer(name)  # TODO
        self._connectiontime = 0
        self._recording = 0
        self._silent = False
        self._time = None
        self._timecorrection = 0
        self._info = ['', '']
        self._owner = None
        self._unbanlist = dict()
        self._user = None
        self._users = deque()  # TODO reemplazar userlist con userdict y userhistory
        self._userdict = dict()  # TODO {ssid:{user},}
        self._userhistory = deque(maxlen = 10)  # TODO {{time: <user>},}
        # self.user_id = None TODO
        self._usercount = 0
        # self.imsgs_drawn = 0 # TODO
        # self.imsgs_rendered = False # TODO
        self.mgr = mgr
        self.msgs = dict()  # TODO esto y history es lo mismo?
        self.status = None
        if self.mgr:
            self._bgmode = int(self.mgr.bgmode)
            super().connect()
        self._maxHistoryLength = Gestor.maxHistoryLength  # Por que no guardar un número por sala ?)
        self._history = deque(maxlen = self._maxHistoryLength)
        # TODO

    ####################
    # Propiedades
    ####################
    @property
    def allshownames(self):
        """Todos los nombres de usuarios en la sala, incluyendo anons"""
        return [x.showname for x in set(self._userdict.values())]

    @property
    def alluserlist(self):
        """Lista de todos los usuarios en la sala, incluyendo anons"""
        return list(self._userdict.values())

    @property
    def allusernames(self):
        return sorted([x.name for x in set(self._userdict.values())])

    @property
    def badge(self):
        """Insignia usada en la sala"""
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
        """Nombre del bot en la sala, TODO esto o currentname"""
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
        """
        Nombre de usuario que el bot tiene en la sala
        TODO carece de utilidad si se puede usar user.name
        """
        return self._currentname

    @property
    def flags(self):
        return self._flags

    @flags.setter  # TODO ajustarlo para cambiar la sala
    def flags(self, value):
        print("HOLA")
        self._flags = value

    @property
    def info(self):
        """Información de la sala, una lista [titulo,información]"""
        return self._info

    @property
    def mods(self):
        """Los mods de la sala"""
        return set(self._mods.keys())

    @property
    def modflags(self):
        """Flags de los mods en la sala. Se puede saber que permisos tienen"""
        return dict([(user.name, self._mods[user]) for user in self._mods])

    @property
    def modnames(self):
        """Nombres de los moderadores en la sala"""
        return [x.name for x in self.mods]

    @property
    def nameColor(self):
        """Color del nombre que se usa en los mensajes de la sala"""
        return self._nameColor

    @property
    def owner(self):
        """El dueño de la sala"""
        return self._owner

    @property
    def ownername(self):
        """Nombre del dueño de la sala"""
        return self.owner.name

    @property
    def silent(self):
        """Hablo o no?
        TODO Buffer de mensajes
        """
        return self._silent

    @property
    def shownames(self):
        return sorted(list(set([x.showname for x in self.userlist])), key = lambda s: s.lower())

    @property
    def unbanlist(self):
        return self._unbanlist

    @property
    def user(self):
        """Mi usuario"""
        return self._user

    @property
    def userlist(self):
        """Lista de usuarios en la sala, por defecto muestra todos los usuarios (no anons) sin incluir sesiones extras"""
        return self._getUserlist(1, 1)

    @property
    def alluserCount(self):
        return len(self.alluserlist)

    @property
    def userCount(self):
        """Cantidad de usuarios en la sala"""
        if self.flags.NOCOUNTER:
            return len(self.userlist)
        else:
            return self._usercount

    @property
    def usernames(self):
        """Nombres de usuarios en la sala. Por defecto usado los valores de userlist"""
        return sorted(list(set([x.name for x in self.userlist])))

    @property
    def userhistory(self):
        # TODO regresar solo la ultima sesión para cada usuario
        return self._userhistory

    def _addHistory(self, msg):
        """
        Agregar un mensaje al historial
        @param msg: El mensaje TODO
        """
        if len(self._history) == self._history.maxlen:
            rest = self._history.popleft()
            rest.detach()
        self._history.append(msg)

    def _getUserlist(self, todos = 0, unica = 0, memoria = 0):  # TODO Revisar
        ul = None  # TODO Si hay flag de usuarios invisibles usar el history
        if not todos:
            ul = map(lambda x: x.user,
                     self._history[-memoria:])  # TODO memoria no debe ser mayor a la cantidad de elementos
        else:
            ul = list(set([x for x in self._userdict.values() if not x.isanon]))
        if unica:
            return list(set(ul))
        return ul

    ####################
    # Comandos de la sala
    ####################
    def addMod(self, user, powers = '82368'):  # TODO los poderes serán recibidos de modflags
        """
        Agrega un moderador nuevo a la sala con los poderes básicos
        @param user: str. Usuario que será mod
        @param powers: Poderes del usuario mod, un string con números
        """
        if isinstance(user, _User):
            user = user.name
        self._sendCommand('addmod:{}:{}'.format(user, powers))

    def banMessage(self, msg: Message) -> bool:
        if self.getLevel(self.user) > 0:
            name = '' if msg.user.name[0] in '!#' else msg.user.name
            self.rawBan(msg.unid, msg.ip, name)
            return True
        return False

    def banUser(self, user: str) -> bool:
        """
        Banear un usuario (si se tiene el privilegio)
        @param user: El usuario, str o _User
        @return: Bool indicando si se envió el comando
        """
        msg = self.getLastMessage(user)
        if msg:
            return self.banMessage(msg)
        return False

    def clearall(self):  # TODO
        """Borra todos los mensajes"""
        if self.user == self._owner or self._user in self._mods and self._mods.get(self._user).EDIT_GROUP:
            self._sendCommand("clearall")
            return True
        else:
            return False

    def clearUser(self, user):  # TODO probar con anons
        if self.getLevel(self.user) > 0:
            msg = self.getLastMessage(user)
            if msg:
                name = '' if msg.user.name[0] in '!#' else msg.user.name
                self._sendCommand("delallmsg", msg.unid, msg.ip, name)
                return True
        return False

    def deleteMessage(self, message):  # TODO Algo anda mal
        if self.getLevel(self.user) > 0:
            self._sendCommand("delmsg", message.msgid)
            return True
        return False

    def deleteUser(self, user):
        if self.getLevel(self.user) > 0:
            msg = self.getLastMessage(user)
            if msg:
                self.deleteMessage(user)
        return False

    def findUser(self, name):
        # TODO, capacidad para recibir un User
        if name.lower() in self.allusernames:
            return User(name)
        return None

    def flagMessage(self, msg):
        self._sendCommand('g_flag', msg.msgid)  # TODO test or msgunid

    def flagUser(self, user):
        msg = self.getLastMessage(user)
        if msg:
            self.flagMessage(msg)
            return True
        return False

    def getLastMessage(self, user = None):
        """Obtener el último mensaje de un usuario en una sala"""
        if not user:
            user = self._user
        if isinstance(user, str):
            user = User(user)
        msg = [msg for msg in reversed(self._history) if msg.user == user]  # TODO hacerlo sin crear nuevo usuario
        if msg:
            return msg[0]
        return None

    def getLevel(self, user):
        """Obtener el nivel de un usuario en la sala"""
        if isinstance(user, str):
            user = User(user)
        if user == self._owner:
            return 3
        if user in self._mods:
            if self._mods.get(user).isadmin:
                return 2
            else:
                return 1
        return 0

    def login(self, uname = None, password = None, account = None):
        # if account: TODO login aunque tenga otra cuenta conectada?
        #    self
        # , self.name, _genUid(), self._currentaccount[0], self._currentaccount[1]]  # TODO comando
        # self._currenname = self._currentaccount[0]
        if not account:
            account = [self._currentaccount[0], self._currentaccount[1]]
        if uname:
            account = [uname, '']
            if password:
                account[1] = password
        if isinstance(account, str):
            cuenta = {k.lower(): [k, v] for k, v in self.mgr._accounts}.get(account.lower(), self.mgr._accounts[0])
            cuenta[0] = account  # Poner el nombre tal cual
            account = cuenta
            self._currentaccount = [account[0], account[1]]
        self._sendCommand('blogin', account[0], account[1])

    def logout(self):  # TODO ordenar
        """logout of user in a room"""
        self._sendCommand("blogout")

    def message(self, msg, html: bool = False, canal = None, badge = None):
        """TODO channel 5 para la combinacion esa y un badge
        TODO cola de mensajes
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
        msg = self._messageFormat(msg, html)
        if not badge:
            badge = self.badge
        for x in msg:
            self.rawMessage('%s:%s' % (canal + badge * 64, x))

    def rawMessage(self, msg):
        """
        Send a message without n and f tags.
        @type msg: str
        @param msg: message
        """
        if not self._silent:
            # TODO meme se debe enviar un string aleatorio en base 36
            self._sendCommand("bm", "meme", msg)

    def removeMod(self, user, powers):  # TODO parametro no utilizado
        if isinstance(user, _User):  # TODO externalizar
            user = user.name
        self._sendCommand('removemod:{}', user)

    def setRecordingMode(self, modo):
        self._recording = int(modo)
        if self.connected:
            self._sendCommand('msgmedia', str(self._recording))

    def setSilent(self, silent):  # TODO
        self._silent = silent

    def unbanUser(self, user):
        rec = self.banRecord(user)
        if rec:
            self.rawUnban(rec["target"].name, rec["ip"], rec["unid"])
            return True
        else:
            return False

    def updateFlags(self, flag = None, enabled = True):
        if flag:
            if self.flags and flag in dir(self.flags):
                if flag in GroupFlags:
                    if enabled:
                        self._sendCommand("updategroupflags", str(GroupFlags[flag]), '0')
                    else:
                        self._sendCommand("updategroupflags", '0', str(GroupFlags[flag]))
                    return True
        return False

    def updateInfo(self, title = '', info = ''):
        title = title or self._info[0]
        info = info or self._info[1]
        data = {
            "erase":  0, "l": 1, "d": info, "n": title, "u": self.name, "lo": self._currentaccount[0],
            "p":      self._currentaccount[1],
            "origin": "st.chatango.com",
            }
        if WS.RPOST("http://chatango.com/updategroupprofile", data):
            return True
        return False

    def updateMod(self, user, powers = '82368'):  # TODO
        if isinstance(user, _User):
            user = user.name
        self._sendCommand('updmod:{}:{}'.format(user, powers))

    def updateProfile(self, age = '', gender = '', country = '', about = '', fullpic = None,
                      show = False):  # TODO country is not working
        # WARNING, fullpic is not working do not use"
        data = {

            "origin": "st.chatango.com",
            "u":      self._currentaccount[0],
            "p":      self._currentaccount[1],
            "auth":   "pwd", "arch": "h5", "src": "group", "action": "update",
            "age":    age, "gender": gender, "location": country, "line": about,

            }
        headers = None
        if fullpic:
            data.update({"action": "fullpic"})
            boundary = '--SEPARADOR'
            data = tuple(data.items())
            partes = []
            partes.extend(
                    ['--' + boundary,
                     'Content-Disposition: form-data; name="%s"' % name,
                     '',
                     value,
                     ]
                    for name, value in data
                    )
            partes.extend([
                ['--' + boundary,
                 'Content-Disposition: file; name="Filedata"; filename="%s"' % fullpic,
                 'Content-Type: %s' % mimetypes.guess_type(fullpic)[0],
                 '',
                 str(open(fullpic, "rb").read()),
                 ]])
            flattened = list(__import__("itertools").chain(*partes))
            flattened.append('--' + boundary + '--')
            flattened.append('')
            data = '\r\n'.join(str(x) for x in flattened)
            headers = {
                "host":           "chatango.com", "origin": "http://st.chatango.com",
                "Content-type":   'multipart/form-data; boundary=' + boundary,
                "Content-length": len(data)  # len(data)
                }

        if WS.RPOST("http://chatango.com/updateprofile", data, headers = headers):
            return True
        else:
            return False
        pass

    ####################
    # Utilería del bot
    ####################
    def banRecord(self, user):
        if isinstance(user, _User):  # TODO externalizar
            user = user.name
        if user.lower() in [x.name for x in self._banlist]:
            return self._banlist[User(user)]
        return None

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

    @staticmethod
    def _parseFlags(flags: str, molde: dict) -> Struct:  # TODO documentar
        flags = int(flags)
        return Struct(**dict([(mf, molde[mf] & flags != 0) for mf in molde]))

    def requestBanlist(self):  # TODO revisar
        self._sendCommand('blocklist', 'block',
                          str(int(time.time() + self._correctiontime)),
                          'next', '500', 'anons', '1')

    def rawBan(self, unid, ip, name):  # TODO documentar
        self._sendCommand("block", unid, ip, name)

    def rawUnban(self, name, ip, unid):
        self._sendCommand("removeblock", unid, ip, name)

    def requestUnBanlist(self):
        pass

    ####################
    # Comandos recibidos
    ####################
    def _rcmd_aliasok(self, args):
        """
        Se ha iniciado sesión con el alias indicado
        """
        # TODO Cambiar el self.user por el alias usado en login
        pass

    def _rcmd_b(self, args):  # TODO reducir proceso
        # TODO el reconocimiento de otros bots en anon está incompleto
        mtime = float(args[0]) - self._timecorrection  # Hora de envío del mensaje
        name = args[1]  # Nombre de usuario si lo hay
        tempname = args[2]  # Nombre del anon si no se ha logeado
        puid = args[3]  # Id del usuario Si no está no se debe procesar
        unid = args[4]  # TODO Id del mensaje?
        msgnum = args[5]  # Número del mensaje Si no está no se debe procesar
        ip = args[6]  # Ip del usuario
        channel = args[7] or 0  # TODO se puede saber el premium con esto premium=4 bg=(8 y premium)
        unknown2 = args[8]
        rawmsg = ':'.join(args[9:])
        badge = 0
        # TODO reemplazar por los flags
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
                # TODO problemas acá, se debe encontrar el tiempo de conexión con esa puid
                # name=[u.name for u in self.userlist if u.sessionids==p]
                name = "!" + getanonname(puid, n)
        else:
            if n:
                nameColor = n
            else:
                nameColor = None
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
                      nameColor = nameColor,
                      puid = puid,
                      raw = rawmsg,
                      room = self,
                      time = mtime,
                      unid = unid,
                      unknown2 = unknown2,
                      user = user
                      )
        self._mqueue[msgnum] = msg

    def _rcmd_blocked(self, args):  # TODO Que era todo esto?
        user = None
        if args[3]:
            user = User(args[3])
        target = None
        if args[2] == "":
            msx = [msg for msg in self._history if msg.unid == args[0]]
            if msx:
                target = msx[0].user
            self._callEvent('onAnonBan', user, target)
        else:
            target = User(args[2])
            self._callEvent("onBan", user, target)
        self._banlist[target] = {"unid": args[0], "ip": args[1], "target": target, "time": float(args[4]), "src": user}

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

    def _rcmd_clearall(self, args):  # TODO comentar
        self._callEvent("onClearall", args[0])

    def _rcmd_delete(self, args):
        """Borrar un mensaje de mi vista actual"""
        msg = self._msgs.get(args[0])
        if msg and msg in self._history:
            self._history.remove(msg)
            self._callEvent("onMessageDelete", msg.user, msg)
            msg.detach()

    def _rcmd_deleteall(self, args):  # TODO
        user = None
        msgs = list()
        for msgid in args:
            msg = self._msgs.get(msgid)
            if msg and msg in self._history:
                self._history.remove(msg)
                user = msg.user
                msg.detach()
                msgs.append(msg)
        self._callEvent('onDeleteUser', user, msgs)

    def _rcmd_denied(self, args):  # TODO
        pass

    def _rcmd_getannc(self, args):  # TODO falta rcmd
        pass

    def _rcmd_g_participants(self, args):
        self._userdict = dict()
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
                    name = '!' + getanonname(puid, contime)
            user = User(name, room = self, isanon = isanon, puid = puid)
            if user in ({self._owner} | self.mods):
                user.setName(name)
            user.addSessionId(self, ssid)
            self._userdict[ssid] = user

    def _rcmd_gparticipants(self, args):
        """Comando viejo de chatango, ya no se usa, pero aún puede seguirlo enviando"""
        self._rcmd_g_participants(args[1:])

    def _rcmd_getpremium(self, args):
        # TODO
        if self._bgmode:
            self._sendCommand('msgbg', str(self._bgmode))

    def _rcmd_groupflagsupdate(self, args):
        flags = args[0]
        self._flags = self._parseFlags(flags, GroupFlags)
        self._callEvent('onFlagsUpdate')

    def _rcmd_i(self, args):  # TODO
        mtime = float(args[0]) - self._correctiontime
        name = args[1]
        tname = args[2]
        puid = args[3]
        unid = args[4]
        i = args[5]  # TODO what is this for?
        ip = args[6]  # TODO espacios 7 y 8
        rawmsg = ":".join(args[9:])
        msg, n, f = _clean_message(rawmsg)
        if name == "":
            nameColor = None
            name = "#" + tname
            if name == "#":
                name = "!" + getanonname(puid, n)
        else:
            if n:
                nameColor = _parseNameColor(n)
            else:
                nameColor = None
        user = User(name)
        # Create an anonymous message and queue it because msgid is unknown.
        if f:
            fontColor, fontFace, fontSize = _parseFont(f)
        else:
            fontColor, fontFace, fontSize = None, None, None
        msg = Message(
                time = mtime,
                user = user,
                body = msg,
                raw = rawmsg,
                ip = ip,
                nameColor = nameColor,
                fontColor = fontColor,
                fontFace = fontFace,
                fontSize = fontSize,
                unid = unid,
                puid = puid,
                room = self
                )
        if len(self._history) <= self._history.maxlen:
            self._history.appendleft(msg)
            self._callEvent("onHistoryMessage", user, msg)

    def _rcmd_inited(self, args):  # TODO
        """Em el chat es solo para desactivar la animación de espera por conexión"""
        self._sendCommand("g_participants", "start")
        self._sendCommand("getpremium", "l")
        self.requestBanlist()
        self.requestUnBanlist()
        if self.attempts == 1:
            self._callEvent("onConnect")
            # TODO
        else:
            self._callEvent("onReconnect")
            # TODO
        if args and debug:
            print('New Unhandled arg on inited ', file = sys.stderr)

    def _rcmd_logoutok(self, args):
        """Me he desconectado, ahora usaré mi nombre de anon"""
        # TODO revisar este comando
        self._currentname = '!' + getanonname(self._puid, str(self._connectiontime))  # TODO de donde era user_id?
        self._user = User(self._currentname, nameColor = str(self._connectiontime).split('.')[0][-4:])

    def _rcmd_mods(self, args):  # TODO
        mods = dict()
        for mod in args:
            name, powers = mod.split(',', 1)
            mods[User(name)] = self._parseFlags(powers, ModFlags)
            mods[User(name)].isadmin = int(powers) & AdminFlags != 0
        premods = self.mods
        self._mods = mods
        if self._user not in premods:  # Si el bot no estaba en los mods antes
            self._callEvent('onModChange', set(mods.keys()) - premods)  # TODO, problemas acá?
        else:
            for user in set(mods.keys()) - premods:  # Con Mod
                self._callEvent("onModAdd", user)
            for user in premods - set(mods.keys()):  # Sin Mod
                self._callEvent("onModRemove", user)

    def _rcmd_miu(self, args):  # TODO documentar
        self._callEvent('onPictureChange', User(args[0]))

    def _rcmd_n(self, args):  # TODO aún hay discrepancias en el contador
        """Cambió la cantidad de usuarios en la sala"""
        if not self.flags.NOCOUNTER:
            self._usercount = int(args[0], 16)
            # assert not self._userdict or len(self._userdict) == self._usercount, 'Warning count doesnt match'  # TODO
            self._callEvent("onUserCountChange")

    def _rcmd_ok(self, args):  # TODO
        self._connected = True
        self._owner = User(args[0])
        self._puid = args[1]  # TODO
        self._authtype = args[2]  # M=Ok, N= ? TODO tipo C
        self._currentname = args[3]
        self._connectiontime = args[4]
        self._correctiontime = int(float(self._connectiontime) - time.time())
        self._currentIP = args[5]
        mods = args[6]
        flags = args[7]
        self._flags = self._parseFlags(flags, GroupFlags)
        # Auth type1|
        if self._authtype == 'M':  # Login Correcto
            self._user = User(self._currentname)
            pass
        elif self._authtype == 'C':  # Login incorrecto
            self._user = User('!' + getanonname(self._connectiontime, self._puid))
        elif self._authtype == 'N':
            pass
        if mods:
            for x in mods.split(';'):
                powers = x.split(',')[1]
                self._mods[User(x.split(',')[0])] = self._parseFlags(powers, ModFlags)
                self._mods[User(x.split(',')[0])].isadmin = int(powers) & AdminFlags != 0

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
        if name == 'None':
            if tname != 'None':
                name = '#' + tname
            else:
                name = '!' + getanonname(puid, contime)
        user = User(name, puid = puid)
        if cambio == '0':  # Leave
            user.removeSessionId(self, ssid)  # Quitar la id de sesión activa
            self._callEvent('onLeave', user, puid)
            if ssid in self._userdict:  # Remover el usuario de la sala
                self._userhistory.append([contime, self._userdict.pop(ssid)])
            if user.isanon:
                self._callEvent('onAnonLeave', user, puid)
        elif cambio == '1':  # Join
            user.addSessionId(self, ssid)  # Agregar la sesión al usuario
            self._userdict[ssid] = user  # Agregar la sesión a la sala
            if not user.isanon and user not in self.userlist:
                self._callEvent('onJoin', user, puid)
            elif user.isanon:
                self._callEvent('onAnonJoin', user, puid)
        else:  # 2 Account Change
            # Quitar la cuenta anterior de la lista y agregar la nueva
            # TODO conectar cuentas que han cambiado usando este método
            before = None
            if ssid in self._userdict:
                before = self._userdict[ssid]
            if before and before.isanon:  # Login
                if user.isanon:  # Anon Login
                    self._callEvent('onAnonLogin', user, puid)  # TODO
                else:  # User Login
                    self._callEvent('onUserLogin', user, puid)
            elif not before.isanon:  # Logout
                if before in self.userlist:
                    self._userhistory.append([contime, before])
                    self._callEvent('onUserLogout', user, puid)
            user.addPersonalUserId(self, puid)
            self._userdict[ssid] = user

    def _rcmd_show_fw(self, args):  # TODO
        self._callEvent('onFloodWarning')

    def _rcmd_show_tb(self, args):  # TODO documentar
        self._callEvent("onFloodBan", int(args[0]))

    def _rcmd_tb(self, args):
        """Flood Ban sigue activo"""
        self._callEvent("onFloodBanRepeat", int(args[0]))

    def _rcmd_u(self, args):  # TODO
        if args[0] in self._mqueue:
            msg = self._mqueue.pop(args[0])
            if msg._user != self.user:
                msg.user._fontColor = msg.fontColor
                msg.user._fontFace = msg.fontFace
                msg.user._fontSize = msg.fontSize
                msg.user._nameColor = msg.nameColor
            msg.attach(self, args[1])
            self._addHistory(msg)
            if (msg.channel >= 4 or msg.badge) and msg.user not in [self.owner] + list(self.mods):  # TODO
                self._mods[msg.user] = self._parseFlags('82368',
                                                        ModFlags)  # TODO lo añade con el poder más básico y el badge
                self._mods[msg.user].isadmin = int('82368') & AdminFlags != 0
            self._callEvent("onMessage", msg.user, msg)

    def _rcmd_unblocked(self, args):  # TODO
        args = ":".join(args).split(";")[-1].split(":")  # TODO checar
        user = User(args[3])
        target = args[2]
        if target == "":
            msx = [msg for msg in self._history if msg.unid == args[0]]
            if msx:
                target = msx[0].user
            self._callEvent('onAnonUnban', user, target)
        else:
            target = User(args[2])
            del self._banlist[target]
            self._callEvent("onUnban", user, target)
        self._unbanlist[user] = {"unid": args[0], "ip": args[1], "target": target, "time": float(args[4]), "src": user}

    def _rcmd_unblocklist(self, args):  # TODO
        self._unbanlist = dict()
        sections = ":".join(args).split(";")
        for section in sections:
            params = section.split(":")
            if len(params) != 5:
                continue
            if params[2] == "":
                continue
            user = User(params[2] or 'Anon')
            self._unbanlist[user] = {
                "unid":   params[0],
                "ip":     params[1],
                "target": user,
                "time":   float(params[3]),
                "src":    User(params[4])
                }
        self._callEvent("onUnBanlistUpdate")

    def _rcmd_updgroupinfo(self, args):  # TODO documentar
        self._info = [urlreq.unquote(args[0]), urlreq.unquote(args[1])]
        self._callEvent('onUpdateInfo')


class Gestor:
    """
    Clase Base para manejar las demás conexiones
    """
    _TimerResolution = 0.2
    maxHistoryLength = 700
    PMHost = "c1.chatango.com"

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def __init__(self, name: str = None, password: str = None, pm: bool = None, accounts = None):
        self._accounts = accounts
        self._colasalas = queue.Queue()
        if accounts is None:
            self._accounts = [(name, password)]
        self._jt = None  # Join Thread
        self._name = self._accounts[0][0]
        self._password = self._accounts[0][1]
        self._rooms = dict()
        self._running = False
        self._user = User(self._name)
        self._tasks = set()
        self._pm = None
        self.bgmode = False
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
    def rooms(self):
        """Mis salas"""
        return list(x for x in self._rooms.values() if x.sock is not None)

    @property
    def user(self):
        return self._user

    @property
    def roomnames(self):
        return list(self._rooms.keys())

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
        if not rooms:
            rooms = str(input('Nombres de salas separados por coma: ')).split(',')
        if '' in rooms:
            rooms = []
        if not name and not accounts:
            name = str(input("Usuario: "))
        if not name:
            name = ''
        if not password and not accounts:
            password = str(input("Contraseña: "))
        if not password:
            password = ''
        if not accounts:
            accounts = [(name, password)]
        self = cls(name, password, pm, accounts)
        for room in rooms:

            self.joinRoom(room)

        self.main()

    def onInit(self):
        """Invocado antes de empezar los demás procesos en main"""
        pass

    class _Task:
        def __str__(self):
            return '<%s Task: "%s" [%s]>' % (
                'Interval' if self.isInterval else 'Timeout', self.func.__name__, self.timeout)

        def __init__(self, mgr, func = None, timeout = None):
            """
            Inicia una tarea nueva
            @param mgr: El dueño de esta tarea y el que la mantiene con vida
            """
            self.func = func
            self.isInterval = False
            self.mgr = mgr
            self.timeout = timeout

        def cancel(self):
            """Sugar for removeTask."""
            self.mgr.removeTask(self)

    def findUser(self, name):
        return [x.name for x in self._rooms.values() if x.findUser(name)]

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

    def joinRoom(self, room: str, account = None):
        """
        Unirse a una sala con la cuenta indicada
        @param room: Sala a la que unirse
        @param account:  Opcional, para entrar con otra cuenta del bot solo escribir su nombre
        """
        if account is None:
            account = self._accounts[0]
        if isinstance(account, str):  # TODO externalizar
            cuenta = {k.lower(): [k, v] for k, v in self._accounts}.get(account.lower(), self._accounts[0])
            cuenta[0] = account
            account = cuenta
        if room not in self._rooms:
            # self._rooms[room] = Room(room, self, account)
            self._colasalas.put((room, account))
            return True
        else:
            return False

    def _joinThread(self):
        while True:
            room, account = self._colasalas.get()
            con = Room(room, self, account)
            self._rooms[room] = con

    def leaveRoom(self, room):
        if isinstance(room, Room):
            room = room.name
        if room.lower() in self._rooms:
            self._rooms[room].disconnect()
            self._rooms.pop(room)

    def main(self):
        """
        Poner en marcha al bot
        # TODO
        """
        self.onInit()
        self._running = True
        self._jt = threading.Thread(target = self._joinThread, name = "Join rooms")
        self._jt.daemon = True
        self._jt.start()
        while self._running:
            # try:
            if self._running:
                conns = self.getConnections()
                socks = [x.sock for x in conns]
                wsocks = [x.sock for x in conns if x.wbuf]
                if not conns and not socks and not wsocks:
                    rd, wr, sp = [], [], []
                else:
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
                            # Conexión perdida
                            if not con._connected:  # Nunca se recibió comandos de la conexión
                                con.disconnect()
                            else:
                                print("{}: Fallo de recv, reconectando...".format(con.name))  # con.reconnect()  #
                                con.reconnect()
                            # TODO ConnectionRefusedError
                    except socket.error as cre:  # socket.error - ConnectionResetError
                        # TODO esto no funciona si hay muchas salas
                        self.test = cre  # variable de depuración para android
                        print('Conexión perdida, reintentando en 10 segundos...')
                        counter = con.attempts or 1
                        while counter:
                            try:
                                con.reconnect()
                                counter = 0
                            except socket.gaierror:  # En caso de que no haya internet
                                print(
                                        '[{}][{:^5}] Aún no hay internet...'.format(time.strftime('%I:%M:%S %p'),
                                                                                    counter),
                                        file = sys.stderr)
                                counter += 1
                                time.sleep(10)
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
        self.bgmode = activo
        for room in self.rooms:
            room.setBgMode(int(activo))
        if self.pm:
            self.pm.setBgMode(int(activo))

    def enableRecording(self, activo = True):
        """Enable recording if available."""
        self.user._mrec = True
        for room in self.rooms:
            room.setRecordingMode(int(activo))

    def setFontColor(self, hexfont):
        self.user._fontColor = str(hexfont)

    def setFontFace(self, facenum):
        """
        # TODO usar el nombre
        @param facenum: El número de la fuente en un string
        """

        self.user._fontFace = str(Fonts.get(str(facenum).lower(), facenum))

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
        @param tiempo: Tiempo en segundos hasta que se ejecute la función
        @param funcion: La función que será invocada
        """
        task = self._Task(self)
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

    def _tick(self):
        now = time.time()
        for task in set(self._tasks):
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

    def onAnonBan(self, room, user, target):
        """
        Al ser baneado un anon en la sala
        @param room: Sala donde ocurre
        @param user: Usuario que banea
        @param target: puede ser un User o None TODO debería ser un user
        """
        pass

    def onAnonJoin(self, room, user, ssid):
        pass

    def onAnonLeave(self, room, user, ssid):
        pass

    def onAnonLogin(self, room, user, ssid):
        pass

    def onBan(self, room, user, target):
        pass

    def onBanlistUpdate(self, room):
        """
        Al ser actualizada la lista de ban de la sala
        @param room: Sala donde ocurre el cambio
        """
        pass

    def onClearall(self, room, result):
        """
        Al ser borrados todos los mensajes de la sala
        @param room: Sala donde se han borrado los mensajes
        @param result: Resultado, puede ser 'ok' o 'error'. El error solo aparece si el bot ha sido quien solicita el
        borrado
        """
        pass

    def onConnect(self, room):
        """
        Al conectarse a una sala
        @param room:Sala a la que se ha conectado
        """
        pass

    def onDeleteUser(self, room, user, msgs):
        """
        Cuando se borran todos los mensajes de un usuario específico
        @param room: Sala donde se borran los mensajes
        @param user: Usuario al que se le borran los mensajes
        @param msgs: Lista de mensajes borrados
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

    def onFlagsUpdate(self, room):
        """
        Cuando cambian las reglas internas de una sala
        @param room: Sala donde ocurre el cambio
        """
        pass

    def onFloodBan(self, room: Room, tiempo: int):
        """
        Al recibir un ban por flood en una sala
        @param room: La sala donde se recibió el ban
        @param tiempo: El tiempo restante del ban en segundos
        """
        pass

    def onFloodBanRepeat(self, room: Room, tiempo: int):
        """
        Cuando se ha reconectado y aún tiene un ban activo por flood
        @param room: La sala donde se recibió el ban
        @param tiempo: El tiempo restante del ban en segundos
        """
        pass

    def onFloodWarning(self, room):
        """
        Al recibir una advertencia de flood
        @param room: Sala en la que se recibe la advertencia
        """
        pass

    def onHistoryMessage(self, room, user, message):
        """
        Al cargar un mensaje anterior a la conexión del bot en la sala. Util para mantener registrado hasta los
        momentos en los que no está el bot
        @param room: Sala donde se cargó el mensaje
        @param user: Usuario del mensaje
        @param message: El mensaje cargado
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

    def onMessageDelete(self, room, user, message):
        """
        Al borrarse un mensaje en una sala
        @param room: La sala donde se ha borrado el mensaje
        @param user: El usuario del mensaje
        @param message: El mensaje borrado
        """
        pass

    def onModAdd(self, room, user):
        pass

    def onModChange(self, room, users):
        pass

    def onModRemove(self, room, user):
        pass

    def onPMContactlistReceive(self, pm):
        """
        Al recibir mis contactos en el pm
        @param pm: El PM
        """
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

    def onPMDisconnect(self, pm):
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

    def onPMMessageSend(self, pm, user, message):
        """
        Cuando se envía un mensaje al pm
        @param pm: El PM
        @param user: El usuario al que se envía el mensaje
        @param message: El mensaje enviado
        """
        pass

    def onPictureChange(self, room, user):
        """
        Cuando un usuario cambia su imagen de perfil en una sala
        @param room: La sala en la que se cambió la imagen
        @param user: El usuario
        """
        pass

    def onPing(self, room: Room):
        """
        Al enviar un ping a una sala
        @param room: La sala en la que se envía el ping
        """
        pass

    def onPMOfflineMessage(self, pm, user, body):
        """
        Al recibir un mensaje cuando no se estuvo conectado
        @param pm: El PM
        @param user: El usuario que envió el mensaje
        @param body: El mensaje
        """
        pass

    def onPong(self, room: Room):
        """
        Al recibir un pong en una sala
        @param room: La sala en la que se recibe el pong
        """
        pass

    def onProcessError(self, room, func, e):
        """
        Cuando ocurre un error en un proceso
        @param room: Sala donde ocurre el error (puede ser PM)
        @param func: Función donde ocurrió el error
        @param e: Excepción generada
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

    def onUnban(self, room, user, target):  # TODO comentar
        pass

    def onUpdateInfo(self, room):
        """
        Cuando se actualiza la información de una sala
        @param room: Sala donde ocurre el cambio
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
