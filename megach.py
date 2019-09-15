#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: megach.py
Title: Librería de chatango
Original Author: Megamaster12 <supermegamaster32@gmail.com>
Current Maintainers and Contributors:
 Megamaster12
"""
################################################################
# Imports
################################################################
import base64
import builtins
import hashlib
import html as html2
import json
import mimetypes
import os
import queue
import random
import re
import select
import socket
import string
import sys
import threading
import time
import urllib.parse as urlparse
import urllib.request as urlreq
from collections import namedtuple, deque
from datetime import datetime
from urllib.error import HTTPError, URLError
from xml.etree import cElementTree as ET

if sys.version_info[1] < 5:
    from html.parser import HTMLParser

    html2.unescape = HTMLParser().unescape

################################################################
# Depuración
################################################################
version = 'M.1.7.2'
version_info = version.split('.')
debug = True
autoupdate = True
path = ''
updated = 1556469390  # 2019-04-28 10:36 AM
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

specials = {'mitvcanal': 56, 'animeultimacom': 34, 'cricket365live': 21, 'pokemonepisodeorg': 22, 'animelinkz': 20,
            'sport24lt': 56, 'narutowire': 10, 'watchanimeonn': 22, 'cricvid-hitcric-': 51, 'narutochatt': 70,
            'leeplarp': 27, 'stream2watch3': 56, 'ttvsports': 56, 'ver-anime': 8, 'vipstand': 21, 'eafangames': 56,
            'soccerjumbo': 21, 'myfoxdfw': 67, 'kiiiikiii': 21, 'de-livechat': 5, 'rgsmotrisport': 51,
            'dbzepisodeorg': 10, 'watch-dragonball': 8, 'peliculas-flv': 69}
tsweights = [['5', w12], ['6', w12], ['7', w12], ['8', w12], ['16', w12],
             ["17", w12], ["18", w12], ["9", sv2], ["11", sv2], ["12", sv2],
             ["13", sv2], ["14", sv2], ["15", sv2], ["19", sv4], ["23", sv4],
             ["24", sv4], ["25", sv4], ["26", sv4], ["28", sv6], ["29", sv6],
             ["30", sv6], ["31", sv6], ["32", sv6], ["33", sv6], ["35", sv8],
             ["36", sv8], ["37", sv8], ["38", sv8], ["39", sv8], ["40", sv8],
             ["41", sv8], ["42", sv8], ["43", sv8], ["44", sv8], ["45", sv8],
             ["46", sv8], ["47", sv8], ["48", sv8], ["49", sv8], ["50", sv8],
             ["52", sv10], ["53", sv10], ["55", sv10], ["57", sv10],
             ["58", sv10], ["59", sv10], ["60", sv10], ["61", sv10],
             ["62", sv10], ["63", sv10], ["64", sv10], ["65", sv10],
             ["66", sv10], ["68", sv2], ["71", sv12], ["72", sv12],
             ["73", sv12], ["74", sv12], ["75", sv12], ["76", sv12],
             ["77", sv12], ["78", sv12], ["79", sv12], ["80", sv12],
             ["81", sv12], ["82", sv12], ["83", sv12], ["84", sv12]]


def updatePath():
    absFilePath = os.path.abspath(__file__)  # Absolute Path of this module
    fileDir = os.path.dirname(absFilePath)  # Directory of this Module
    sys.path.append(fileDir)  # for imports
    return fileDir

def updateServers():
    route = os.path.join(path, 'megach.json')
    global updated
    if not os.path.exists(route):
        tmp = open(route, "a")
        tmp.write(json.dumps({'tsweights': tsweights, 'specials': specials}))
        tmp.close()
    with open(route) as file:
        dic = json.load(file)
    if not dic.get('tsweights'):
        dic['tsweights'] = tsweights
        dic['updated'] = updated
    else:
        # TODO analizar specials
        # specials=dic.get('specials') or specials
        updated = dic.get('updated') or updated
        tsweights.clear()
        tsweights.extend(dic.get('tsweights'))
    # Update every two weeks
    try:
        if updated < time.time() - 1209600 and autoupdate:
            import update_servers
            dic.update(update_servers.Updater().servers)
            dic.update({'updated': time.time()})
            with open(route, 'w') as file:
                file.write(json.dumps(dic))
    except ModuleNotFoundError as e1:
        print("External module not found, please search for update_servers.py", file=sys.stderr)
    except Exception as e:
        print('' + str(e))
    return updated


path = updatePath()
updated = updateServers()
_maxServernum = sum(x[1] for x in tsweights)

GroupFlags = {
    "LIST_TAXONOMY":      1, "NOANONS": 4, "NOFLAGGING": 8, "NOCOUNTER": 16,
    "NOIMAGES":           32, "NOLINKS": 64, "NOVIDEOS": 128,
    "NOSTYLEDTEXT":       256, "NOLINKSCHATANGO": 512,
    "NOBRDCASTMSGWITHBW": 1024, "RATELIMITREGIMEON": 2048,
    "CHANNELSDISABLED":   8192, "NLP_SINGLEMSG": 16384,
    "NLP_MSGQUEUE":       32768, "BROADCAST_MODE": 65536,
    "CLOSED_IF_NO_MODS":  131072, "IS_CLOSED": 262144,
    "SHOW_MOD_ICONS":     524288, "MODS_CHOOSE_VISIBLITY": 1048576,
    "HAS_XML":            268435456, "UNSAFE": 536870912
    }

ModFlags = {
    'DELETED':          1, 'EDIT_MODS': 2, 'EDIT_MOD_VISIBILITY': 4,
    'EDIT_BW':          8, 'EDIT_RESTRICTIONS': 16, 'EDIT_GROUP': 32,
    'SEE_COUNTER':      64, 'SEE_MOD_CHANNEL': 128, 'SEE_MOD_ACTIONS': 256,
    'EDIT_NLP':         512, 'EDIT_GP_ANNC': 1024, 'EDIT_ADMINS': 2048,
    'EDIT_SUPERMODS':   4096, 'NO_SENDING_LIMITATIONS': 8192, 'SEE_IPS': 16384,
    'CLOSE_GROUP':      32768, 'CAN_BROADCAST': 65536,
    'MOD_ICON_VISIBLE': 131072, 'IS_STAFF': 262144
    }

AdminFlags = (ModFlags["EDIT_MODS"] | ModFlags["EDIT_RESTRICTIONS"] |
              ModFlags["EDIT_GROUP"] | ModFlags["EDIT_GP_ANNC"])

Fonts = {
    'arial':    0, 'comic': 1, 'georgia': 2, 'handwriting': 3, 'impact': 4,
    'palatino': 5, 'papirus': 6, 'times': 7, 'typewriter': 8
    }

MessageFlags = {
    'IS_PREMIUM':  4, 'HAS_BG': 8, 'BADGE_SHIELD': 64, 'BADGE_STAFF': 128,
    'CHANNEL_RED': 256, 'CHANNEL_BLUE': 2048, 'CHANNEL_MOD': 32768
    }

Channels = {
    "white": 0, "red": 256, "blue": 2048, "mod": 32768
    }  # TODO darle uso

Badges = {
    "shield": 64, "staff": 128
    }  # TODO darle uso

ModChannels = Badges['shield'] | Badges['staff'] | Channels['mod']

PRINTLOCK = threading.Lock()
tprint = builtins.print

def printLock(*args, **kwargs):
    with PRINTLOCK:
        return tprint(*args, **kwargs)

builtins.print = printLock

def _savelog(message):
    try:
        with open(os.path.join(path, 'megach.log'), 'a') as f:
            f.writelines(str(message) + '\n')
    except Exception as e:
        print('Error al guardar log: ' + str(e), file = sys.stderr)


def _genUid() -> str:
    """
    Generar una uid ALeatoria de 16 dígitos.
    """
    return str(random.randrange(10 ** 15, 10 ** 16))


def _getAnonId(puid: str, ts: str) -> str:
    """
    Obtener una id de anon.
    @param puid: PUID del usuario de 4 cifras.
    @param ts: Tiempo de sesión en que se conectó el anon debe ser un string
    con un entero
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


def convertPM(msg: str) -> str:
    """
    Convertir las fuentes de un mensaje normal en fuentes para el PM
    Util para usar múltiples fuentes
    @param msg: Mensaje con fuentes incrustadas
    @return: Mensaje con etiquetas f convertidas a g
    """

    pattern = re.compile(
            r'<f x(\d{1,2})?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})=(.*?)>')

    def repl(match):
        s, c, f = match.groups()
        if s is None:
            s = 11
        else:
            s = int(s)
        if len(c) == 6:
            c = '{:X}{:X}{:X}'.format(
                    round(int(c[0:2], 16) / 17),  # r
                    round(int(c[2:4], 16) / 17),  # g
                    round(int(c[4:6], 16) / 17)  # b
                    )
        return '</g><g x{:02}s{}="{}">'.format(s, c, f[1:-1])

    return pattern.sub(repl, msg)


def getAnonName(puid: str, tssid: str) -> str:
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
    if group in specials:
        return specials[group]
    group = group.replace("_", "q").replace("-", "q")
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

def _clean_message(msg: str, pm: bool = False) -> [str, str, str]:
    """
    Clean a message and return the message, n tag and f tag.
    @type msg: str
    @param msg: the message
    @rtype: str, str, str
    @returns: cleaned message, n tag contents, f tag contents
    """
    # TODO check smileys for pm
    n = re.search("<n(.*?)/>", msg)
    tag = pm and 'g' or 'f'
    f = re.search("<" + tag + "(.*?)>", msg)
    msg = re.sub("<" + tag + ".*?>" + '|"<i s=sm://(.*)"', "", msg)

    wink = '<i s="sm://wink" w="14.52" h="14.52"/>'

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


def _parseFont(f: str, pm = False) -> (str, str, str):
    """
    Lee el contendido de un etiqueta f y regresa
    tamaño color y fuente (en ese orden)
    @param f: El texto con la etiqueta f incrustada
    @return: Tamaño, Color, Fuente
    """
    if pm:
        regex = r'x(\d{1,2})?s([a-fA-F0-9]{6}|[a-fA-F0-9]{3})="|\'(.*?)"|\''
    else:
        regex = r'x(\d{1,2})?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})="(.*?)"'
    match = re.search(regex, f)
    if not match:
        return None, None, None
    return match.groups()


def _parseNameColor(n: str) -> str:
    """Return the name color from message"""
    # probably is already the name
    return _clean_message(n)[1]


def _fontFormat(text):
    formats = {'/': 'I', '\*': 'B', '_': 'U'}
    for f in formats:
        f1, f2 = set(formats.keys()) - {f}
        # find = ' <?[BUI]?>?[{0}{1}]?{2}(.+?[\S]){2}'.format(f1, f2, f+'{1}')
        find = ' <?[BUI]?>?[{0}{1}]?{2}(.+?[\S]?[{2}]?){2}[{0}{1}]?[' \
               '\s]'.format(
                f1, f2, f)
        for x in re.findall(find, ' ' + text + ' '):
            original = f[-1] + x + f[-1]
            cambio = '<' + formats[f] + '>' + x + '</' + formats[f] + '>'
            text = text.replace(original, cambio)
    return text


def _videoImagePMFormat(text):
    for x in re.findall('(http[s]?://[^\s]+outube.com/watch\?v=([^\s]+))', text):
        original = x[0]
        cambio = '<i s="vid://yt:%s" w="126" h="96"/>' % x[1]
        text = text.replace(original, cambio)
    for x in re.findall('(http[s]?://[\S]+outu.be/([^\s]+))', text):
        original = x[0]
        cambio = '<i s="vid://yt:%s" w="126" h="96"/>' % x[1]
        text = text.replace(original, cambio)
    for x in re.findall("http[s]?://[\S]+?.jpg", text):
        text = text.replace(x, '<i s="%s" w="70.45" h="125"/>' % x)
    # print(text)
    return text


################################################################
# Utils
################################################################
class Struct:
    """
    Una clase dinámica que recibe sus propiedades como parámetros
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):  # TODO algo util aca
        return '<Struct>'


class Task:
    ALIVE = False
    _INSTANCES = set()
    _THREAD = None
    _LOCK = threading.Lock()

    @staticmethod
    def _manage():
        """Manage instances"""
        with Task._LOCK:
            if Task.ALIVE:
                # Only one call at a time for this method is allowed
                return
            Task.ALIVE = True
        while Task.ALIVE:
            time.sleep(0.01)
            Task._tick()

    @staticmethod
    def _tick():
        now = time.time()
        for task in list(Task._INSTANCES):
            try:
                if task.target <= now:
                    task.func(*task.args, **task.kw)
                    if task.isInterval:
                        task.target = task.timeout + now
                    else:
                        task.cancel()
            except Exception as e:
                print("Task error {}: {}".format(task.func, e))
                task.cancel()
        if not Task._INSTANCES:
            with Task._LOCK:
                Task.ALIVE = False

    def __init__(self, timeout, func = None, interval = False, *args, **kw):
        """
        Inicia una tarea nueva
        @param mgr: El dueño de esta tarea y el que la mantiene con vida
        """
        self.mgr = None
        self.func = func
        self.timeout = timeout
        self.target = time.time() + timeout
        self.isInterval = interval
        self.args = args
        self.kw = kw
        Task._INSTANCES.add(self)
        with Task._LOCK:
            if not Task.ALIVE:
                Task._THREAD = threading.Thread(target = Task._manage,
                                                name = 'Task Manager',
                                                )
                Task._THREAD.daemon = True
                Task._THREAD.start()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s Task: "%s" [%s]>' % (
            'Interval' if self.isInterval else 'Timeout',
            self.func.__name__, self.timeout)

    def cancel(self):
        """Cancel task"""
        with Task._LOCK:
            if self in Task._INSTANCES:
                Task._INSTANCES.remove(self)
            if self.mgr:
                self.mgr.removeTask(self)


################################################################
# Inicio del bot
################################################################

class WS:
    """
    Agrupamiento de métodos estáticos para encodear y chequear frames en
    conexiones del protocolo WebSocket
    """
    _BOUNDARY_CHARS = string.digits + string.ascii_letters
    FrameInfo = namedtuple("FrameInfo",
                           ["fin", "opcode", "masked", "payload_length"])
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
        ver = headers.get('version')
        if ver:
            ver = ver.split("/")[1]
            ver = tuple(int(x) for x in ver.split("."))
            if ver[0] < 1:
                return False
            if ver[1] < 1:
                return False
        if headers.get('upgrade', '').lower() != 'websocket':
            return False
        elif headers.get('connection', '').lower() != 'upgrade':
            return False
        elif 'sec-websocket-accept' not in headers:
            return False
        return headers['sec-websocket-accept']

    @staticmethod
    def encode(payload: object) -> bytes:
        """
        Encodea un mensaje y lo enmascara con las reglas obligatorias del
        protocolo websocket
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
    def encode_multipart(data, files, boundary = None):
        """
        Encodear información para peticiones multipart/form-data
        @param data: Datos a enviar (diccionario)
        @param files: Archivos a enviar en formato
         ({'filename':<name>,'content':<content>})
        @param boundary: Separador de los datos codificados
        @return: String encodeado
        """

        def escape_quote(s):
            return s.replace('"', '\\"')

        if boundary is None:
            boundary = ''.join(
                    random.choice(WS._BOUNDARY_CHARS) for x in range(30))
        lineas = []
        for nombre, valor in data.items():
            lineas.extend(('--%s' % boundary,
                           'Content-Disposition: form-data; name="%s"' % nombre,
                           '', str(valor)))
        for nombre, valor in files.items():
            filename = valor['filename']
            if 'mimetype' in valor:
                mimetype = valor['mimetype']
            else:
                mimetype = mimetypes.guess_type(filename)[
                               0] or 'application/octet-stream'
            lineas.extend(('--%s' % boundary,
                           'Content-Disposition: form-data; name="%s"; '
                           'filename="%s"' % (
                               escape_quote(nombre), escape_quote(filename)),
                           'Content-Type: %s' % mimetype, '', valor['content']))
        lineas.extend(('--%s--' % boundary, '',))
        body = '\r\n'.join(lineas)
        headers = {
            'Content-Type':   'multipart/form-data; boundary=%s' % boundary,
            'Content-Length': str(len(body))
            }
        return body, headers

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
        return WS.FrameInfo(bool(buffer[0] & 128), buffer[0] & 15,
                            bool(buffer[1] & 128), payload_length)

    @staticmethod
    def getHeaders(headers: bytes) -> dict:
        """
        Recibe una serie de datos, comprueba si es un handshake válido para
        websocket y retorna un diccionario
        @param headers: Los datos recibidos
        @return: Los headers en formato dict
        """
        if isinstance(headers, (bytes, bytearray)):
            if b"\r\n\r\n" in headers:
                headers, _ = headers.split(b"\r\n\r\n", 1)
            headers = headers.decode(errors = 'ignore')
        if isinstance(headers, str):
            headers = headers.splitlines()
        if isinstance(headers, list):
            # Convertirlo en diccionario e ignorar valores incorrectos
            headers = map((lambda x: x.split(':', 1) if len(
                    x.split(':')) > 1 else ('', '')), headers)
            headers = {z.lower().strip(): y.strip() for z, y in headers if
                       z and y}
        return headers

    @staticmethod
    def getPayload(buffer: bytes):
        """
        Decodifica un mensaje enviado por el servidor y lo vuelve legible
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
            return int.from_bytes(payload[:2], "big"), payload[2:].decode(
                    "utf-8", "replace")
        return payload

    @staticmethod
    def getServerSeckey(headers: bytes, key: bytes = b'') -> str:
        """
        Calcula la respuesta que debe dar el servidor según la clave de
        seguridad que se le envió
        @param headers: Los valores enviados al servidor. Si se recibe,
        se ignorará el parámetro key
        @param key: La clave que se le envió al servidor.
        @return: Clave que debería enviar el servidor (string)
        """
        if headers:
            key = WS.getHeaders(headers)['sec-websocket-key'].encode()
        sha = hashlib.sha1(key + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
        return base64.b64encode(sha.digest()).decode()

    @staticmethod
    def unmask_buff(buffer: bytes) -> bytes:
        """
        Recibe bytes con una mascara de websocket y la remueve para leerlos
        con fácilidad
        @param buffer: Los datos enmascarados
        @return: bytes Los mismos datos sin su máscara
        """
        mask = buffer[:4]
        return bytes(x ^ mask[i % 4] for i, x in enumerate(buffer[4:]))

    @staticmethod
    def RPOST(url, data = None, headers = None):
        """
        Enviar una petición post
        @param url: La url de la consulta
        @param data: Los datos enviados a la url
        @param headers: Las cabeceras de la petición post
        @return:
        """
        if type(data) is dict:
            data = urlparse.urlencode(data).encode('latin-1')
        elif type(data) is str:
            data = data.encode('latin-1')
        if not headers:
            headers = {
                "host": "chatango.com", "origin": "http://st.chatango.com"
                }
        pet = urlreq.Request(url, data = data, headers = headers)
        try:
            resp = urlreq.urlopen(pet)
            return resp
        except HTTPError as e:
            raise  # e.code
        except URLError as e:
            raise  # e.reason
        except Exception as e:
            raise  # TODO no controlada


class User:
    """
    Clase que representa a un usuario de chatango
    Iniciarlo sin el guion bajo para evitar inconvenientes
    """
    _users = {}
    _INFO = namedtuple('userinfo',
                       ['about', 'gender', 'age', 'country', 'bgtime',
                        'fullprofile'])
    _STYLE = namedtuple('style',
                        ['fontFamily', 'fontSize', 'bold', 'stylesOn', 'usebackground',
                         'italics', 'textColor', 'underline', 'nameColor'])

    def __new__(cls, name, **kwargs):
        # TODO obtener fuentes por defecto
        key = name.lower()
        if key in cls._users:
            for attr, val in kwargs.items():
                if attr == 'ip' and not val:
                    continue  # only valid ips
                setattr(cls._users[key], '_' + attr, val)
            return cls._users[key]
        self = super().__new__(cls)
        cls._users[key] = self
        self._info = None
        self._style = None
        self._fontColor = self.style.textColor or '000'
        self._fontFace = self.style.fontFamily or '000'
        self._fontSize = self.style.fontSize or 12
        self._nameColor = self.style.nameColor or '000'
        self._ip = ''
        self._isanon = not len(name) or name[0] in '!#'
        self._ispremium = None
        self._mbg = False
        self._history = deque(maxlen=5)  # TODO Mantener historial reciente de un usuario
        self._mrec = False
        self._name = key
        self._puids = dict()
        self._showname = name
        self._sids = dict()
        for attr, val in kwargs.items():
            # if val is None:
            #    continue
            setattr(self, '_' + attr, val)
        # TODO Más cosas del user
        return self

    def __dir__(self):
        return [x for x in
                set(list(self.__dict__.keys()) + list(dir(type(self)))) if
                x[0] != '_']

    def __radd__(self, other):
        return str(other) + self.showname

    def __add__(self, other):
        return self.showname + str(other)

    def __str__(self):
        return self.showname

    def __repr__(self):
        return "<User: %s>" % self.name

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
    def font(self) -> str:
        return '<f x%s%s="%s">' % (self.fontSize, self.fontColor, self.fontFace)

    @property
    def history(self):
        return list(self._history)[::-1]

    @history.setter
    def history(self, value):
        self._history.appendleft(value)

    @property
    def ip(self) -> str:
        """Ip del usuario, puede ser un string vacío"""
        return self._ip

    @property
    def isanon(self) -> bool:
        """Soy anon?"""
        return self._isanon

    @property
    def ispremium(self):
        return self._ispremium

    @property
    def name(self) -> str:
        """Nombre del usuario"""
        return self._name

    @property
    def nameColor(self) -> str:
        """El color del nombre que utiliza el usuario"""
        return self._nameColor

    @property
    def namecolor(self):
        """Color del nombre en formato html para chatango(hex3 compatible con PM)"""
        return '<n%s/>' % (
            self.nameColor[::2] if len(self.nameColor) == 6 else self.nameColor[
                                                                 :3])

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

    def getSessionIds(self, room = None):
        if room:
            return self._sids.get(room, set())
        else:
            return set.union(*self._sids.values())

    @property
    def info(self):
        if self._info:
            return self._info
        link = '/%s/%s/' % ('/'.join((self.name * 2)[:2]), self.name)
        urls = ('http://fp.chatango.com/profileimg' + link + 'mod1.xml',
                'http://fp.chatango.com/profileimg' + link + 'mod2.xml')
        misxml = []
        for x in urls:
            try:
                misxml.append(
                        ET.fromstring(
                                urlreq.urlopen(x).read().decode('latin-1')))
            except:
                misxml.append(None)
        buscar = 'body s b l d'
        encontrado = []
        for x in buscar.split():
            encontrado.append(misxml[0] and misxml[0].findtext(x) or '')
        encontrado.append(misxml[1] and misxml[1].findtext('body') or '')
        self._info = User._INFO(*encontrado)
        return self._info

    @property
    def age(self) -> int:
        if not self.info.age:
            return None
        hoy = datetime.now()
        birth = datetime.strptime(self.info.age, '%Y-%m-%d')
        return (hoy - birth).days // 365

    @property
    def about(self):
        return self.info.about and \
               _clean_message(urlreq.unquote(self.info.about))[
                   0] or None

    @property
    def country(self):
        return self.info.country or None

    @property
    def fullprofile(self):
        return urlreq.unquote(self.info.fullprofile) or None

    @property
    def gender(self):
        return self.info.gender.lower() or None

    @property
    def premiumtime(self):
        # TODO facilitar uso externo
        return self.info.bgtime or None

    @property
    def style(self):
        # TODO comentar
        if self._style:
            return self._style
        try:
            link = '/%s/%s/' % ('/'.join((self.name * 2)[:2]), self.name)
            url = 'http://ust.chatango.com/profileimg' + link + 'msgstyles.json'
            estilo = json.loads(urlreq.urlopen(url).read().decode('latin-1'))
            self._style = User._STYLE(*list(estilo.values()))
            return self._style
        except:
            return User._STYLE(*([None] * 9))



    sessionids = property(getSessionIds)

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
            if not sid:
                self._sids[room].clear()
            elif sid in self._sids[room]:
                self._sids[room].remove(sid)
            if len(self._sids[room]) == 0:
                del self._sids[room]

    def setName(self, value):
        """Reajusta el nombre de un usuario
        # TODO para uso en participant 2. Al cambiar aquí vigilar _users
        """
        self._name = value.lower()
        self._showname = value

    def get(name):
        return User._users.get(name) or User(name)


class Message:
    """
    Clase que representa un mensaje en una sala o en privado
    TODO revisar
    """

    def __init__(self, body = None, **kw):
        """
        :param kw:Parámetros del mensaje
        """
        self._msgid = None
        self._time = None
        self._user = None
        self._body = body
        self._room = None
        self._raw = ""
        self._hasbg = False
        self._ip = ""
        self._unid = ""
        self._puid = ""
        self._nameColor = "000"
        self._banword = None
        self._flash = None
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

    def __dir__(self):
        return [x for x in
                set(list(self.__dict__.keys()) + list(dir(type(self)))) if
                x[0] != '_']

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
    def banword(self):
        return self._banword

    @property
    def badge(self):
        """Insignia del mensaje, Ninguna, Mod, Staff son 0 1 o 2"""
        return self._badge

    @property
    def body(self):
        """
        Cuerpo del mensaje sin saltos de linea
        """
        return ' '.join(self._body.replace('\n', ' ').split(' '))

    @property
    def channel(self):
        return self._channel

    @property
    def flash(self):
        return self._flash

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
    def hasbg(self):
        return self._hasbg

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
        """Id del usuario del mensaje
        TODO comprobar significado y utilidad
        """
        return self._puid

    @property
    def unid(self):
        return self._unid

    @property
    def user(self) -> User:
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
        if self._msgid is not None:
            self._room = room
            self._msgid = msgid
            self._room.msgs.update({msgid: self})

    def detach(self):
        """Detach the Message."""
        if self._msgid is not None and self._msgid in self._room.msgs:
            self._room.msgs.pop(self._msgid)

    def delete(self):
        """Borrar el mensaje de la sala (Si es mod)"""
        self._room.deleteMessage(self)

    @classmethod
    def parse(cls, room, args):
        """Parse message from chatango args"""
        # TODO corregir self
        mtime = float(args[0]) - room._timecorrection
        name, tname, puid, unid, msgid, ip, channel = args[1:8]
        unknown2 = args[8]  # TODO examinar codigo de banned words
        if unknown2 and debug:  # Banned Message
            _savelog('[_rcmd_b][' + ':'.join(args) + ']' + unknown2)
        rawmsg = ":".join(args[9:])
        badge = 0
        ispremium, flash, banword = [None] * 3
        # TODO aplicar los flags
        if channel and channel.isdigit():
            channel = int(channel)
            badge = (channel & 192) // 64
            ispremium = channel & 4 > 0
            hasbg = channel & 8 > 0
            flash = channel & 16 > 0  # TODO asignar a user|message
            banword = channel & 32 > 0  # TODO asignar a message
            if debug and (channel & 3):
                print(
                    '[_rcmd_b][' + ':'.join(
                        args) + ']Encontrado un dato desconocido, '
                                'favor avisar al '
                                'desarrollador', file=sys.stderr)
                _savelog('[_rcmd_b][' + ':'.join(args) + ']')
                # TODO Descubrir y manupular canales 1|2 (3) y 16|32(48)
            channel = ((channel & 2048) | (channel & 256)) | (channel & 35072)
        body, n, f = _clean_message(rawmsg)
        nameColor = None
        if name == "":
            name = "#" + tname
            if name == "#":
                if n.isdigit():
                    name = "!" + getAnonName(puid, n)
                elif n and all(x in string.hexdigits for x in n):
                    name = "!" + getAnonName(puid, str(int(n, 16)))
                else:
                    name = "!" + getAnonName(puid, None)
                    # TODO fix anon bad messages
                    if debug:
                        _savelog('found bad message ' + ':'.join(args))
        else:
            if n:
                nameColor = n
            else:
                nameColor = None
        # TODO no reemplazar ip con vacio
        user = User(name, ip=ip, isanon=name[0] in '#!')
        # Detect changes on ip or premium data
        if user.ispremium != ispremium:
            evt = user._ispremium != None and ispremium != None and mtime > time.time() -5
            user._ispremium = ispremium
            if evt:
                room._callEvent("onPremiumChange", user)
            user._info = None
        if ip and ip != user.ip:
            user._ip = ip
        fontSize, fontColor, fontFace = _parseFont(f.strip())
        self = cls(badge=badge,
                   body=body,
                   channel=channel,
                   fontColor=fontColor,
                   fontFace=fontFace,
                   fontSize=fontSize or '11',
                   hasbg=hasbg,
                   msgid=msgid,
                   ip=ip,
                   ispremium=ispremium,
                   nameColor=nameColor,
                   puid=puid,
                   raw=rawmsg,
                   room=room,
                   time=mtime,
                   unid=unid,
                   unknown2=unknown2,
                   user=user,
                   flash=flash,
                   banword=banword
                   )
        return self


class WSConnection:
    """Clase base para gestopmar conexiones WebSocket y mantenerlas"""
    _WSLOCK = threading.Lock()  # Para manejar las conexiones una a la vez
    _SAFELOCK = threading.Lock()
    _INSTANCES = set()

    def __init__(self, server, port, origin, name = 'WSConnection'):
        self._connectiontime = 0  # Hora de inicio de la conexión
        self._correctiontime = 0  # Diferencia entre localtime y servertime
        self._connectattempts = 0
        self._connected = False
        self._firstCommand = True  # Si es el primer comando enviado
        self._headers = b''  # Las cabeceras que se enviaron en la petición
        self._origin = origin or server
        self._port = port or 443  # El puerto de la conexión
        self._server = server
        self._name = name
        self._serverheaders = b''  # Las caberceras de respuesta recibidas
        self._sock = None
        self._rbuf = b''  # El buffer de lectura  de la conexión
        self._wbuf = b''  # El buffer de escritura a la conexión
        self._wlock = False  # Si no se debe envíar nada al wbuf
        self._wlockbuf = b''  # Cuando no se manda al wbuf, viene acá
        self._tlock = threading.Lock()  # Para controlar esta conexion
        # TODO usar en comandos que retornan datos
        self._connlock = threading.Lock()
        self._terminator = ['\x00', '\r\n\x00']
        self._pingdata = ''
        self._fedder = None
        self._pingTask = None

    def __del__(self):
        self._disconnect()

    def _callEvent(self, evt, *args, **kw):
        try:
            if self.mgr and hasattr(self.mgr, evt):
                getattr(self.mgr, evt)(self, *args, **kw)
                self.mgr.onEventCalled(self, evt, *args, **kw)
            elif self.mgr:
                print('Evento no controlado ' + str(evt))
        except Exception as e:
            print("Error capturado en evento '%s':'%s'" % (evt, e),
                  file = sys.stderr)

    def _disconnect(self):
        """
        Privado: Solo usar para reconneción
        Cierra la conexión y detiene los pings, el objeto sigue existiendo
        """
        with self._tlock:
            if self._sock:
                self._sock.close()
            if self._name != 'PM':
                for x in self.userlist:
                    x.removeSessionId(self, 0)
            self._sock = None
            self._serverheaders = b''
            if self._pingTask:
                self._pingTask.cancel()
            self._connected = False

    def connect(self) -> bool:
        """ Iniciar la conexión con el servidor y llamar a _handshake() """
        with self._tlock:
            if not self._connected:

                self._connectattempts += 1
                self._sock = socket.socket()
                # TODO Comprobar, si no hay internet hay error acá
                self._sock.connect((self._server, self._port))
                self._sock.setblocking(False)
                self._handShake()
                self._pingTask = Task(90, self._ping, True)
                self._connected = True
                if not self._fedder:
                    self._fedder = threading.Thread(
                        target=self._feed,
                        name=self._name or 'WSConnection',
                            )
                    self._fedder.daemon = True
                    self._fedder.start()
                return True
            return False

    def _handShake(self):
        """
        Crea un handshake y lo guarda en las variables antes de enviarlo a
        la conexión
        """
        self._headers = ("GET / HTTP/1.1\r\n"
                         "Host: {}:{}\r\n"
                         "Origin: {}\r\n"
                         "Connection: Upgrade\r\n"
                         "Upgrade: websocket\r\n"
                         "Sec-WebSocket-Key: {}\r\n"
                         "Sec-WebSocket-Version: {}\r\n"
                         "\r\n").format(self._server, self._port, self._origin,
                                        WS.genseckey(), WS.VERSION).encode()
        self._wbuf = self._headers
        self._setWriteLock(True)

    def _feed(self):
        while self._connected:
            time.sleep(0.01)
            try:
                if not self._sock:
                    continue
                rd, wr, sp = select.select([self._sock],
                                           (self._wbuf and [
                                               self._sock] or []),
                                           [],
                                           0.2)
                for x in wr:
                    try:
                        with self._tlock:
                            size = self._sock.send(self._wbuf)
                            self._wbuf = self._wbuf[size:]
                    except Exception as e:
                        if debug:
                            print("Error sock.send " + str(e), sys.stderr)
                for x in rd:

                    chunk = None
                    # with self._tlock:
                    if self._sock:
                        chunk = self._sock.recv(1024)

                    if chunk:
                        self.onData(chunk)
                        # TODO calificar comandos de respuesta instantanea
                        # TODO separar esos _rcmd_ y usar un único thread para ellos
                        # threading.Thread(target=self.onData, name="Process", args=(chunk,)).start()
                    elif chunk is not None:
                        # Conexión perdida
                        with WSConnection._SAFELOCK:
                            if not self._serverheaders:  # Nunca se recibió
                                # comandos de la conexión
                                self.disconnect()
                            else:
                                self.reconnect()
                                # TODO este reconnect puede bloquearse
                                # ConnectionRefusedError
            except socket.error as cre:  # socket.error -
                # ConnectionResetError
                # TODO controlar tipo de error
                with WSConnection._WSLOCK:
                    self.test = cre  # variable de depuración para
                    # android
                    self._callEvent("onConnectionLost", cre)
                    attempts = 1  # Intentos de
                    self._connectattempts = 0
                    while attempts:
                        try:
                            self.reconnect()
                            attempts = 0
                            # TODO asegurar el reinicio del contador
                        except Exception as sgai:  # socket.gaierror:  #
                            # En caso de que no haya internet
                            self._callEvent('onConnectionAttempt', sgai)
                            attempts += 1
                            time.sleep(10)

    def _sendCommand(self, *args):
        """
        Envía un comando al servidor
        @type args: [str, str, ...]
        @param args: command and list of arguments
        """
        with self._connlock:
            if self._firstCommand:
                terminator = self._terminator[0]
                self._firstCommand = False
            else:
                terminator = self._terminator[1]
            cmd = ":".join(str(x) for x in args) + terminator
            self._write(WS.encode(cmd))

    def _ping(self):
        self._sendCommand('')
        self._callEvent('onPing')

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
            try:
                getattr(self, func)(args)
            except Exception as e:
                self._callEvent('onProcessError', func, e)
                print('[%s][%s] ERROR ON PROCESS "%s" "%s"' % (
                    time.strftime('%I:%M:%S %p'), self.name, func, e),
                      file = sys.stderr)
        elif debug:
            print('[{}][{:^10.10}]UNKNOWN DATA "{}"'.format(
                    time.strftime('%I:%M:%S %p'), self.name, ':'.join(data)),
                    file = sys.stderr)

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

    @property
    def attempts(self) -> int:
        """Los intentos de conexión antes de tener exito o rendirse"""
        return self._connectattempts

    @property
    def connected(self) -> bool:
        """Estoy conectado?"""
        return self._connected

    @property
    def localtime(self):
        """Tiempo del servidor"""
        return time.localtime(time.time() + self._correctiontime)

    @property
    def time(self):
        return time.time() + self._correctiontime

    @property
    def wbuf(self) -> bytes:
        """Buffer de escritura"""
        return self._wbuf

    def onData(self, data: bytes):
        """
        Al recibir datos del servidor
        @param data: Los datos recibidos y sin procesar
        """
        self._rbuf += data  # Agregar los datos al buffer de lectura
        if not self._serverheaders and b'\r\n' * 2 in data:
            self._serverheaders, self._rbuf = self._rbuf.split(b'\r\n' * 2, 1)
            clave = WS.checkHeaders(self._serverheaders)
            esperada = WS.getServerSeckey(self._headers)
            if clave != esperada and debug:
                if debug:
                    print('Un proxy ha enviado una respuesta en caché',
                          file = sys.stderr)
            self._setWriteLock(False)

        else:
            r = WS.checkFrame(self._rbuf)
            while r:  # Comprobar todos los frames en el buffer de lectura
                frame = self._rbuf[:r]
                self._rbuf = self._rbuf[r:]
                # Información sobre el frame recibido
                info = WS.frameInfo(frame)
                payload = WS.getPayload(frame)
                if info.opcode == WS.CLOSE:
                    # El servidor quiere cerrar la conexión
                    print(self._name + ' El servidor ha anulado la conexión',
                          file = sys.stderr)
                    self._disconnect()  # TODO reconectar
                elif info.opcode == WS.TEXT:
                    # El frame contiene datos
                    self._process(payload)
                elif debug:
                    print('Frame no controlado: "{}"'.format(payload),
                          file = sys.stderr)
                r = WS.checkFrame(self._rbuf)

    def reconnect(self):
        """
        Vuelve a iniciar la conexión a la Sala/PM
        """
        # with self._tlock:
        self._disconnect()
        self._reset()
        self.connect()

    def _rcmd_(self, pong = None):
        """Al recibir un pong"""
        self._callEvent('onPong')

    def _reset(self):
        self._serverheaders = b''
        self._wbuf = b''  # El buffer de escritura a la conexión
        self._wlock = False  # Bloquear el buffer de escritura
        self._wlockbuf = b''  # Buffer de escritura bloqueada
        self._firstCommand = False
        self._tlock = threading.Lock()
        self._connlock = threading.Lock()
        self._mods = dict()


class CHConnection(WSConnection):
    """
    Base para manejar las conexiones con Mensajes y salas.
    No Instanciar directamente
    """
    # True: cortar mensajes grandes, False: enviarlos en trozos
    BIGMESSAGECUT = False
    MAXLEN = 2700  # Room is 2900, PM IS 12000
    PINGINTERVAL = 90  # Intervalo para enviar pings, Si llega a 300 se

    def __radd__(self, other):
        return str(other) + self.name

    def __add__(self, other):
        return self.name + str(other)

    def __dir__(self):
        return [x for x in
                set(list(self.__dict__.keys()) + list(dir(type(self)))) if
                x[0] != '_']

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)

    def __init__(self, mgr, name, server, account):
        # Ports 8080 and 8081 ar http, 443 is https
        super().__init__(server, 8080, 'http://st.chatango.com', name)
        self._bgmode = 0
        self._currentaccount = account
        self._currentname = account and account[
            0]  # El usuario de esta conexión
        self._correctiontime = 0  # Diferencia entre la hora local y el server
        # Por que no guardar una configuración de esto por sala?
        self._maxHistoryLength = Gestor.maxHistoryLength
        self._history = deque(maxlen = self._maxHistoryLength)
        self._password = account[1]  # La clave de esta conexión
        self._user = User(account[0])
        self._logged = False
        self.mgr = mgr
        if mgr:  # Si el manager está activo iniciar la conexión directamente
            self._bgmode = int(self.mgr.bgmode)
            self.connect()

    def connect(self):
        super().connect()
        self._login()

    @property
    def account(self) -> str:
        """
        La cuenta que se está usando, evitar mostrar la password en público
        """
        cuenta = User(self._currentaccount[0])
        cuenta._password = self._currentaccount[1]
        return cuenta

    @property
    def currentname(self) -> str:
        """El nombre de usuario que está usando el bot en la conexión"""
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
    def user(self) -> User:
        """El usuario de esta conexión"""
        return self._user

    def disconnect(self):
        """Desconección completa de una sala"""
        self._disconnect()
        if not isinstance(self, PM):
            if self.mgr and self in self.mgr.rooms:
                self.mgr.leaveRoom(self)
            else:
                self._callEvent('onDisconnect')
        else:
            self._callEvent('onPMDisconnect')

    def _login(self):
        """Sobreescribir. PM y Room lo hacen diferente"""
        pass

    def _messageFormat(self, msg: str, html: bool):
        # TODO ajustar envío de texto con tabulaciones
        if len(msg) + msg.count(' ') * 5 > self.MAXLEN:
            if self.BIGMESSAGECUT:
                msg = msg[:self.MAXLEN]
            else:
                # partir el mensaje en pedacitos y formatearlos por separado
                espacios = msg.count(' ') + msg.count('\t')
                particion = self.MAXLEN
                conteo = 0
                while espacios * 6 + particion > self.MAXLEN:
                    particion = len(
                            msg[:particion - espacios])  # Recorrido máximo 5
                    espacios = msg[:particion].count(' ') + msg[
                                                            :particion].count(
                            '\t')
                    conteo += 1
                if debug:  # TODO eliminar
                    print(conteo)
                return self._messageFormat(msg[:particion],
                                           html) + self._messageFormat(
                        msg[particion:], html)
        fc = self.user.fontColor.lower()
        nc = self.user.nameColor
        if not html:
            msg = html2.escape(msg, quote = False)

        msg = msg.replace('\n', '\r').replace('~', '&#126;')
        for x in set(re.findall('<[biu]>|</[biu]>', msg)):
            msg = msg.replace(x, x.upper()).replace(x, x.upper())
        if self.name == 'PM':
            formt = '<n{}/><m v="1"><g x{:0>2.2}s{}="{}">{}</g></m>'
            fc = '{:X}{:X}{:X}'.format(*tuple(
                    round(int(fc[i:i + 2], 16) / 17) for i in
                    (0, 2, 4))).lower() if len(fc) == 6 else fc[:3].lower()
            msg = msg.replace('&nbsp;', ' ')  # fix
            msg = _videoImagePMFormat(msg)
            if not html:
                msg = _fontFormat(msg)
            msg = convertPM(msg)  # TODO No ha sido completamente probado
        else:  # Room
            if not html:
                # Reemplazar espacios múltiples
                # TODO mejorar sin alterar enlaces
                msg = msg.replace('\t', ' %s ' % ('&nbsp;' * 2))
                msg = msg.replace('   ', ' %s ''' % ('&nbsp;'))
                msg = msg.replace('&nbsp;  ', '&nbsp;&nbsp; ')
                msg = msg.replace('&nbsp;  ', '&nbsp;&nbsp; ')
                msg = msg.replace('  ', ' &#8203; ')
            formt = '<n{}/><f x{:0>2.2}{}="{}">{}'
            if not html:
                msg = _fontFormat(msg)
            if self.user.isanon:
                # El color del nombre es el tiempo de conexión y no hay fuente
                nc = str(self._connectiontime).split('.')[0][-4:]
                formt = '<n{0}/>{4}'

        if type(msg) != list:
            msg = [msg]
        return [
            formt.format(nc, str(self.user.fontSize), fc, self.user.fontFace,
                         unimsg) for unimsg in msg]

    @property
    def history(self):
        return list(self._history)

    def setBgMode(self, modo):
        """Activar el BG"""  # TODO modo por defecto
        self._bgmode = modo
        if self.connected and self.user.ispremium:
            self._sendCommand('msgbg', str(self._bgmode))

    def _rcmd_premium(self, args):
        # TODO el tiempo mostrado usa la hora del server
        # TODO usar args para definir el estado premium y el tiempo
        if self._bgmode and (args[0] == '210' or (
                isinstance(self, Room) and self._owner == self.user)):
            self._sendCommand('msgbg', str(self._bgmode))

    def _rcmd_show_fw(self, args = None):
        """Sin argumentos, manda una advertencia de flood en sala/pm"""
        self._callEvent('onFloodWarning')


class PM(CHConnection):
    """
    Clase Base para la conexiones con la mensajería privada de chatango
    """

    def __dir__(self):
        return [x for x in
                set(list(self.__dict__.keys()) + list(dir(type(self)))) if
                x[0] != '_']

    def __init__(self, mgr, name, password):
        """
        Clase que maneja una conexión con la mensajería privada de chatango
        TODO agregar posibilidad de anon
        @param mgr: Administrador de la clase
        @param name: Nombre del usuario
        @param password: Contraseña para la conexión
        """

        self._auth_re = re.compile(r"auth\.chatango\.com ?= ?([^;]*)",
                                   re.IGNORECASE)
        self._blocklist = set()
        self._contacts = set()
        self._name = 'PM'
        # TODO Si el puerto falla, aumentar en uno hasta cierto límte
        # self._server = 'i0.chatango.com'  # TODO server i0. para recibir mensajes
        self._status = dict()
        self.mgr = mgr
        self._trackqueue = queue.Queue()
        self._pmLock = threading.Lock()
        super().__init__(mgr, 'PM', 'c1.chatango.com', (name, password))

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
    def status(self):
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
            "user_id":     name, "password": password, "storecookie": "on",
            "checkerrors": "yes"
            }
        resp = WS.RPOST("http://chatango.com/login", data)
        if not resp:
            return None
        for header, value in resp.headers.items():
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
        r2 = ["tlogin", self._getAuth(self.mgr.name, self.mgr.password), "2"]
        if not r2[1]:
            self._callEvent("onLoginFail")
            self.disconnect()
            return False
        self._sendCommand(*r2)

    def addContact(self, user: str):
        """Add Contact to PM"""
        if isinstance(user, str):
            user = User.get(user)
        if user not in self._contacts:
            self._sendCommand("wladd", user.name)
            self._contacts.add(user)
            self._callEvent("onPMContactAdd", user)
            return True

    def removeContact(self, user: str):
        """Remove Contact from PM"""
        if isinstance(user, str):
            user = User.get(user)
        if user in self._contacts:
            self._sendCommand("wldelete", user.name)
            self._contacts.remove(user)
            self._callEvent("onPMContactRemove", user)

    def block(self, user):  # TODO
        """block a person"""
        if isinstance(user, User):
            user = user.name
        if user not in self._blocklist:
            self._sendCommand("block", user, user, "S")
            self._blocklist.add(User(user))
            self._callEvent("onPMBlock", User(user))

    def unblock(self, user):
        """Desbloquear a alguien"""
        if isinstance(user, User):
            user = user.name
        if user in self._blocklist:
            self._sendCommand("unblock", user)
            return True

    def track(self, user):
        """
        Obtener y almacenar el estado de un usuario
        @param user: str o User - Usuario
        @return: [laston,ison,status]
        """

        if isinstance(user, User):
            user = user.name
        if user == self.user.name:  # El usuario propio daría error
            return [self.user.name, '0',
                    self.connected and 'online' or 'offline']
        self._sendCommand('track', user)
        try:
            res = [None] * 3
            # TODO si esto falla habrán resultados huérfanos
            with self._pmLock:
                res = self._trackqueue.get()
            return res
        except:
            return [None] * 3

    def checkOnline(self, user):
        if isinstance(user, User):
            user = User.name  # TODO el track necesita esto?
        return self.track(user)[-1]

    def message(self, user, msg, html: bool = False):
        """
        Enviar un pm a un usuario
        @param html: Indica si se permite código html en el mensaje
        @param user: Usuario al que enviar el mensaje
        @param msg: Mensaje que se envia (string)
        """
        if msg and self.connected:
            if isinstance(user, User):
                user = user.name
            msg = self._messageFormat(str(msg), html)
            for unimsg in msg:
                self._sendCommand("msg", user, unimsg)
                body, nameColor, fontSize = _clean_message(unimsg, pm = True)
                tmsg = Message(
                                        body = body,
                                        nameColor = nameColor,
                                        fontSize = fontSize or '11',
                                        puid = None,
                                        raw = unimsg,
                                        room = self,
                                        time = time.time(),
                                        unid = None,
                                        user = self.user
                )
                self._callEvent('onPMMessageSend', User(user), tmsg)
                self._history.append(tmsg)
            return True
        return False

    def _write(self, data: bytes):
        if not self._wlock:
            self._wbuf += data
        else:
            self._wlockbuf += data

    def _rcmd_OK(self, args):
        self._connected = True
        self._sendCommand("wl")  # Obtener "amigos"
        self._sendCommand("getblock")  # Obtener mis "bloqueados"
        self._sendCommand("getpremium")
        self._callEvent('onPMConnect')

    def _rcmd_block_list(self, args):  # TODO
        self._blocklist = set()
        for name in args:
            if name == "":
                continue
            self._blocklist.add(User(name))

    def _rcmd_DENIED(self, args):
        self._callEvent("onLoginFail")
        self._disconnect()

    def _rcmd_idleupdate(self, args):  # TODO
        pass

    def _rcmd_kickingoff(self, args):
        # TODO desencadenar un evento al ser echado del pm
        self.disconnect()
        # self._callEvent("onKickedOff")

    def _rcmd_msglexceeded(self, args):
        # TODO terminar msglexceeded
        print("msglexceeded", file=sys.stderr)

    def _rcmd_msg(self, args):  # msg TODO unificar con Message.parse
        name = args[0] or args[1]  # Usuario o tempname
        if not name:
            name = args[2]  # Anon es unknown
        user = User(name)  # Usuario
        mtime = float(args[3]) - self._correctiontime
        unknown2 = args[4]  # 0 TODO what is this?
        if unknown2 and debug:
            _savelog('[_rcmd_msg][' + ':'.join(args) + ']')
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
        self._history.append(msg)
        user.history = msg
        self._callEvent("onPMMessage", user, msg)

    def _rcmd_msgoff(self, args):  # TODO msgoff a Message.Parse
        name = args[0] or args[1]  # Usuario o tempname
        if not name:
            name = args[2]  # Anon es unknown
        user = User(name)  # Usuario
        mtime = float(args[3]) - self._correctiontime
        unknown2 = args[4]  # 0 TODO what is this?
        if unknown2 and debug:
            _savelog('[_rcmd_msgoff][' + ':'.join(args) + ']')
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
                time = mtime, unid = None, unknown2 = unknown2, user = user)
        self._history.append(msg)
        self._callEvent("onPMOfflineMessage", user, msg)

    def _rcmd_reload_profile(self, args):
        user = User.get(args[0])
        user._info = None
        self._callEvent('onUpdateProfile', user)

    def _rcmd_seller_name(self, args):  # TODO completar _seller_name
        pass

    def _rcmd_status(self, args):
        # TODO completar _status
        # status:linkkg:1531458009.39:online:
        # status:linkkg:1531458452.5:app:
        """
        Estado de usuarios con charlas recientes
        """
        self._status[User.get(args[0])] = [args[1], args[2] in 'onlineapp', args[1]]

    def _rcmd_track(self, args):  # TODO completar _track
        # print("track "+str(args))
        if not self._trackqueue.empty():
            self._trackqueue.get()
        self._trackqueue.put(args)

    def _rcmd_time(self, args):
        """Recibir tiempo del server y corregirlo"""
        self._connectiontime = args[0]
        self._correctiontime = float(self._connectiontime) - time.time()

    def _rcmd_toofast(self, args):  # TODO esto solo debería parar un momento
        self.disconnect()

    def _rcmd_unblocked(self, args):
        """Se ha desbloqueado un usuario del pm"""
        user = User.get(args[0])
        if user in self._blocklist:
            self._blocklist.remove(user)
            self._callEvent("onPMUnblock", user)

    def _rcmd_wl(self, args):
        """Lista de contactos recibida al conectarse"""
        # TODO Revisar esta sección
        self._contacts = set()
        for i in range(len(args) // 4):
            name, last_on, is_on, idle = args[i * 4: i * 4 + 4]
            user = User(name)
            if last_on == "None":
                pass  # TODO in case chatango gives a "None" as data argument
            elif not is_on == "on":
                self._status[user] = [int(last_on), False, 0]
            elif idle == '0':
                self._status[user] = [int(last_on), True, 0]
            else:
                self._status[user] = [int(last_on), True,
                                      time.time() - int(idle) * 60]
            self._contacts.add(user)
        self._callEvent("onPMContactlistReceive")

    def _rcmd_wlapp(self, args):
        """Alguien ha iniciado sesión en la app"""
        # TODO [11:28:36 PM][_____PM______]:wlapp:megamaster12:1530768515.41
        user = User.get(args[0])
        last_on = float(args[1])
        self._status[user] = [last_on, False, last_on]
        self._callEvent("onPMContactApp", user)

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


class Room(CHConnection):
    """
    Base para manejar las conexiones con las salas. Hereda de WSConnection y
    tiene todas sus propiedades
    """
    _BANDATA = namedtuple('BanData', ['unid', 'ip', 'target', 'time', 'src'])
    _INFO = namedtuple('Info', ['title', 'about'])

    def __dir__(self):
        return [x for x in
                set(list(self.__dict__.keys()) + list(dir(type(self)))) if
                x[0] != '_']

    def __init__(self, name: str, mgr: object = None, account: tuple = None):
        # Configuraciones
        self._badge = 0
        self._channel = 0
        self._currentaccount = account or ('', '')

        # Datos del chat
        self._announcement = [0, 0, '']  # Estado, Tiempo, Texto
        self._banlist = dict()  # Lista de usuarios baneados
        self._flags = None

        self._mqueue = dict()
        self._mods = dict()
        self._msgs = dict()  # TODO esto y history es lo mismo?
        self._nameColor = ''
        self._port = 443  # TODO cambio a 8080 si no está disponible
        self._rbuf = b''
        self._connectiontime = 0
        self._recording = 0
        self._silent = False
        self._time = None
        self._timecorrection = 0
        self._info = None
        self._owner = None
        self._unbanlist = dict()
        self._unbanqueue = deque(maxlen = 500)
        self._user = None
        self._users = deque()
        self._userdict = dict()  # TODO {ssid:{user},}
        self._userhistory = deque(maxlen = 10)  # TODO {{time: <user>},}
        self._usercount = 0
        self._nomore = False  # Indica si el chat tiene más mensajes
        super().__init__(mgr, name, getServer(name), account or ('', ''))

    ####################
    # Propiedades
    ####################
    ##########
    # Lista de Usuarios
    @property
    def userlist(self):
        """
        Lista de usuarios en la sala, por defecto muestra todos los
        usuarios (no anons) sin incluir sesiones extras
        """
        return self._getUserlist()

    @property
    def anonlist(self):
        """Lista de anons detectados"""
        return list(set(self.alluserlist) - set(self.userlist))

    @property
    def alluserlist(self):
        """Lista de todos los usuarios en la sala (con anons)"""
        return sorted([x[1] for x in list(self._userdict.values())],
                      key = lambda z: z.name.lower())

    ##########
    # Nombres de Usuarios
    @property
    def usernames(self):
        """Nombres de usuarios en la sala (sin anons)"""
        return [x.name for x in self.userlist]

    @property
    def anonnames(self):
        """Nombres de los anons detectados"""
        return [x.showname for x in self.anonlist]

    @property
    def allusernames(self):
        """Nombres de usuarios y anons detectados"""
        return [x.name for x in self.alluserlist]

    @property
    def shownames(self):
        """Nombres para mostrar de los usuarios (sin anons)"""
        return list(set([x.showname for x in self.userlist]))

    @property
    def allshownames(self):
        """Todos los nombres de usuarios en la sala (con anons)"""
        return [x.showname for x in self.alluserlist]

    ##########
    # Bans
    @property
    def banlist(self):
        """La lista de usuarios baneados en la sala"""
        return list(self._banlist.keys())

    @property
    def bannames(self):
        """Nombres de usuarios baneados"""
        return [x.name for x in self.banlist]

    @property
    def unbanlist(self):
        """Lista de usuarios desbaneados"""
        return list(set(x.target.name for x in self._unbanqueue))

    ##########
    # Insignias y canales
    @property
    def badge(self):
        """Insignia usada en la sala"""
        return self._badge

    @badge.setter
    def badge(self, value):
        """Cambiamos la insignia usada en los mensajes"""
        if 0 <= value <= 2:  # 2 badges, 0=None
            self._badge = value

    @property
    def channel(self):
        """El canal que uso en la sala"""
        return self._channel

    @channel.setter
    def channel(self, value):
        if 0 <= value < 8:  # 8 channels from 0 to 7
            self._channel = value

    ##########
    # Otros ajustes
    @property
    def flags(self):
        return self._flags

    @flags.setter  # TODO ajustar flags.setter para cambiar la sala
    def flags(self, value):
        self._flags = value

    @property
    def botname(self):
        """Nombre del bot en la sala, """
        # TODO botname o currentname
        return self.user.name

    @property
    def about(self):
        return urlreq.unquote(self.info.about) or None

    @property
    def title(self):
        return urlreq.unquote(self.info.title)

    @property
    def announcement(self):
        return self._announcement

    @property
    def info(self):
        """Información de la sala, una lista [titulo,información]"""
        if self._info:
            return self._info
        link = '/%s/%s/' % ('/'.join((self.name * 2)[:2]), self.name)
        url = 'http://ust.chatango.com/groupinfo' + link + 'gprofile.xml'
        try:
            mixml = ET.fromstring(urlreq.urlopen(url).read().decode('utf-8'))
        except:
            return Room._INFO('', '')
        buscar = 'title desc'
        encontrado = []
        for x in buscar.split():
            encontrado.append(mixml.findtext(x, ''))
        self._info = Room._INFO(*encontrado)
        return self._info

    @property
    def mods(self):
        """Los mods de la sala"""
        return set(self._mods.keys())

    @property
    def modflags(self):
        """Flags de los mods en la sala. Se puede saber que permisos tienen"""
        return dict([(k.name, v) for k, v in self._mods.items()])

    @property
    def modnames(self):
        """Nombres de los moderadores en la sala"""
        return sorted([x.name for x in self.mods], key = lambda s: s.lower())

    @property
    def msgs(self):
        return self._msgs

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
    def user(self):
        """Mi usuario"""
        return self._user

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
    def userhistory(self):
        return self._userhistory

    def getSessionlist(self, mode = 0, memory = 0):
        """
        Regresa la lista de usuarios y su cantidad de sesiones en la sala
        @param mode: Modo 0 (User,int), 1 (name,int) 3 (showname,int)
        @param memory: int Mensajes que se verán si se revisará el historial
        @return: list[tuple,tuple,...]
        """
        # TODO Modo 2 para la otra opcion
        if mode < 2:
            return [(x.name if mode else x, len(x.getSessionIds(self))) for x in
                    self._getUserlist(1, memory)]
        else:
            return [(x.showname, len(x.getSessionIds(self))) for x in
                    self._getUserlist(1, memory)]

    def _addHistory(self, msg):
        """
        Agregar un mensaje al historial
        @param msg: El mensaje TODO
        """
        if len(self._history) == self._history.maxlen:
            rest = self._history.popleft()
            rest.detach()
        self._history.append(msg)

    def _getUserlist(self, unique = 1, memory = 0, anons = False):
        """
        Regresa una lista con los nombres de usuarios en la sala
        @param unique: bool indicando si la lista es única
        @param memory: int indicando que tan atrás se verá en el historial
        @param anons: bool indicando si se regresarán anons entre los usuarios
        @return: list
        """
        ul = []
        if not memory:
            ul = [x[1] for x in self._userdict.copy().values() if
                  anons or not x[1].isanon]
        elif type(memory) == int:
            ul = set(map(lambda x: x.user, list(self._history)[
                                           min(-memory, len(self._history)):]))
        if unique:
            ul = set(ul)
        return sorted(list(ul), key = lambda x: x.name.lower())

    ####################
    # Comandos de la sala
    ####################
    def addMod(self, user, powers = '82368'):
        """
        Agrega un moderador nuevo a la sala con los poderes básicos
        @param user: str. Usuario que será mod
        @param powers: Poderes del usuario mod, un string con números
        @return: bool indicando si se hará o no
        """
        # TODO los poderes serán recibidos de modflags
        if isinstance(user, User):
            user = user.name
        if self.user == self.owner or (
                self.user in self.mods and self.modflags.get(
                self.user.name).EDIT_MODS):
            self._sendCommand('addmod:{}:{}'.format(user, powers))
            return True
        return False

    def banMessage(self, msg: Message) -> bool:
        if self.getLevel(self.user) > 0:
            name = '' if msg.user.name[0] in '!#' else msg.user.name
            self._rawBan(msg.unid, msg.ip, name)
            return True
        return False

    def banUser(self, user: str) -> bool:
        """
        Banear un usuario (si se tiene el privilegio)
        @param user: El usuario, str o User
        @return: Bool indicando si se envió el comando
        """
        msg = self.getLastMessage(user)
        if msg and msg.user not in self.banlist:
            return self.banMessage(msg)
        return False

    def clearall(self):
        """Borra todos los mensajes"""
        mod = self._mods.get(self._user)
        if self.user == self._owner or (mod and mod.EDIT_GROUP):
            self._sendCommand("clearall")
            return True
        else:
            return False

    def clearUser(self, user):
        # TODO los anons cambian su nombre visible
        if self.getLevel(self.user) > 0:
            msg = self.getLastMessage(user)
            if msg:
                name = '' if msg.user.name[0] in '!#' else msg.user.name
                self._sendCommand("delallmsg", msg.unid, msg.ip, name)
                return True
        return False

    def deleteMessage(self, message):
        if self.getLevel(self.user) > 0 and message.msgid:
            self._sendCommand("delmsg", message.msgid)
            return True
        return False

    def deleteUser(self, user):
        if self.getLevel(self.user) > 0:
            msg = self.getLastMessage(user)
            if msg:
                self.deleteMessage(msg)
        return False

    def findUser(self, name):
        """Regresa un usuario si se encuentra, o None en caso contrario"""
        if isinstance(name, User):
            name = name.name
        if name.lower() in self.allusernames:
            return User.get(name)
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
            return self._history and self._history[-1] or None
        if isinstance(user, User):
            user = user.name
        for x in reversed(self.history):
            if x.user.name == user:
                return x
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
        # TODO login aunque tenga otra cuenta conectada?

        if not account:
            account = [self._currentaccount[0], self._currentaccount[1]]
        if uname:
            account = [uname, '']
            if password:
                account[1] = password
        if isinstance(account, str):
            cuenta = {k.lower(): [k, v] for k, v in self.mgr._accounts}.get(
                    account.lower(), self.mgr._accounts[0])
            cuenta[0] = account  # Poner el nombre tal cual
            account = cuenta
            self._currentaccount = [account[0], account[1]]
        self._currentname = account[0]
        self._sendCommand('blogin', account[0], account[1])

    def logout(self):
        """Salir de la cuenta y permanecer en la sala como Anon"""
        self._sendCommand("blogout")

    def message(self, msg, html: bool = False, canal = None, badge = 0):
        """TODO channel 5 para la combinacion esa y un badge
        TODO cola de mensajes
        Envía un mensaje
        @param msg: (str) Mensaje a enviar(str)
        @param html: (bool) Si se habilitarán los carácteres html, en caso
        contrario se reemplazarán los carácteres especiales
        @param canal: el número del canal. del 0 al 4 son normal,rojo,azul,
        azul+rojo,mod
        @param badge: (int) Insignia del mensaje
        """
        if canal is None:
            canal = self.channel
        if canal < 8:
            canal = (((canal & 1) | (canal & 2) << 2) << 8 | (canal & 4) << 13)
        if msg is None:
            return False

        msg = self._messageFormat(str(msg), html)
        badge = int(badge) if badge else self.badge
        for x in msg:
            self.rawMessage('%s:%s' % (canal + badge * 64, x))

    def rawMessage(self, msg):
        """
        Send a message without n and f tags.
        @type msg: str
        @param msg: message
        """
        if not self._silent:
            # TODO En lugar de "meme" enviar un string aleatorio en base 36
            self._sendCommand("bm", "meme", msg)

    def removeMod(self, user):
        if isinstance(user, User):
            user = user.name
        self._sendCommand('removemod', user)

    def setBannedWords(self, part = '', whole = ''):
        """
        Actualiza las palabras baneadas para que coincidan con las recibidas
        @param part: Las partes de palabras que serán baneadas (separadas por
        coma, 4 carácteres o más)
        @param whole: Las palabras completas que serán baneadas, (separadas
        por coma, cualquier tamaño)
        """
        permiso = self.modflags.get(self.user.name)
        if permiso and permiso.EDIT_BW:
            self._sendCommand('setbannedwords', urlreq.quote(part),
                              urlreq.quote(whole))
            return True
        return False

    def setRecordingMode(self, modo):
        self._recording = int(modo)
        if self.connected:
            self._sendCommand('msgmedia', str(self._recording))

    def setSilent(self, silent = True):
        """
        Silencia al bot en una sala
        @param silent: bool indica si activar o desactivar el silencio
        @return:
        """
        self._silent = silent

    def unbanUser(self, user):
        rec = self.banRecord(user)
        if rec:
            self.rawUnban(rec.target.name, rec.ip, rec.unid)
            return True
        else:
            return False

    def updateBannedWords(self, part = '', whole = ''):
        """
        Actualiza las palabras baneadas agregando las indicadas,
        ambos parámetros son opcionales
        @param part: Las partes de palabras que serán agregadas (separadas
        por coma,4 carácteres o más)
        @param whole: Las palabras completas que serán agregadas, (separadas
        por coma, cualquier tamaño)
        @return: bool TODO, comprobar si se dispone el nivel para el cambio
        """
        self._bwqueue = '%s:%s' % (part, whole)
        self._sendCommand('getbannedwords')

    def updateFlags(self, flag = None, enabled = True):
        if flag:
            if self.flags and flag in dir(self.flags):
                if flag in GroupFlags:
                    if enabled:
                        self._sendCommand("updategroupflags",
                                          str(GroupFlags[flag]), '0')
                    else:
                        self._sendCommand("updategroupflags", '0',
                                          str(GroupFlags[flag]))
                    return True
        return False

    def updateInfo(self, title = '', info = ''):
        title = title or self._info[0]
        info = info or self._info[1]
        data = {
            "erase":  0, "l": 1, "d": info, "n": title, "u": self.name,
            "lo":     self._currentaccount[0], "p": self._currentaccount[1],
            "origin": "st.chatango.com",
            }
        if WS.RPOST("http://chatango.com/updategroupprofile", data):
            return True
        return False

    def updateMod(self, user: str, powers: str = '82368', enabled = None):
        """
        Actualiza los poderes de un moderador
        @param user: Moderador al que se le actualizarán los privilegios
        @param powers: Poderes nuevos del mod. Si no se proporcionan se
        usarán los básicos
        @param enabled: bool indicando si los poderes están activados o no
        @return:
        """
        if isinstance(user, User):
            user = user.name

        if user not in self.modflags or (
                self.user not in self.mods and self.user != self.owner):
            return False
        if not self.modflags.get(self.user.name).EDIT_MODS:
            return False
        if isinstance(powers, str) and not powers.isdigit():
            powers = ModFlags.get(powers, None)
            if not powers:
                return False
        if isinstance(powers, int) or powers.isdigit():
            powers = int(powers)
            if enabled:
                powers = powers | self.modflags.get(user).value
            elif enabled == False:
                start = self.modflags.get(user).value
                powers = start > powers and start ^ powers or start
        else:
            return False
        self._sendCommand('updmod:{}:{}'.format(user, powers))
        return True

    def updateBg(self, bgc = '', ialp = '100', useimg = '0', bgalp = '100',
                 align = 'tl', isvid = '0', tile = '0', bgpic = None):
        """
        @param bgpic: Imagen de bg. si se envía se ignora lo demás.
        @param bgc: Color del bg Hexadecimal
        @param ialp: Opacidad de la imagen
        @param useimg: Usar imagen (0/1)
        @param bgalp: Opacidad del color de bg
        @param align: Alineacion de la imagen (tr,tl,br,bl)
        @param isvid: Si el bg contiene video (0/1) # TODO probar con gifs
        @param tile: Si la imagen se repite para cubrir el area de texto(0/1)
        @return: bool indicando exito o fracaso
        """
        data = {
            "lo":    self._currentaccount[0], "p": self._currentaccount[1],
            "bgc":   bgc, "ialp": ialp, "useimg": useimg, "bgalp": bgalp,
            "align": align, "isvid": isvid, "tile": tile, 'hasrec': '0'
            }
        headers = None
        if bgpic:
            data = {
                "lo": self._currentaccount[0], "p": self._currentaccount[1]
                }
            if bgpic.startswith("http:") or bgpic.startswith("https:"):
                archivo = urlreq.urlopen(bgpic)
            else:
                archivo = open(bgpic, 'rb')
            files = {
                'Filedata': {
                    'filename': bgpic,
                    'content':  archivo.read().decode('latin-1')
                    }
                }
            data, headers = WS.encode_multipart(data, files)
            headers.update({
                "host": "chatango.com", "origin": "http://st.chatango.com"
                })
        if WS.RPOST("http://chatango.com/updatemsgbg", data, headers):
            self._sendCommand("miu")
            return True
        else:
            return False

    def updateProfile(self, age = '', gender = '', country = '', about = '',
                      fullpic = None, show = False, **kw):
        """
        Actualiza el perfil del usuario
        NOTA: Solo es posible actualizar imagen o información por separado
        @param age: Edad
        @param gender: Género
        @param country: Nombre del país
        @param about: Acerca de mí
        @param fullpic: Dirección de una imagen(local o web). Si se envia
        esto se ignorará lo demás.
        @param show: Mostrar el perfil en la lista pública
        @param full_profile: Parte del perfil que incluye html
        @return: True o False
        """
        # TODO sacar la parte del archivo
        # TODO eliminar la variable **kw
        # TODO Evitar vaciar lo que no se manda
        data = {
            'u':    self._currentaccount[0], 'p': self._currentaccount[1],
            'auth': 'pwd', 'arch': 'h5', 'src': 'group', 'action': 'update',
            'age':  age, 'gender': gender, 'location': country, 'line': about
            }
        data.update(**kw)
        headers = {}
        if fullpic:
            if fullpic.startswith('http:') or fullpic.startswith('https:'):
                archivo = urlreq.urlopen(fullpic)
            else:
                archivo = open(fullpic, 'rb')
            data.update({'action': 'fullpic'})
            files = {
                'Filedata': {
                    'filename': fullpic,
                    'content':  archivo.read().decode('latin-1')
                    }
                }
            data, headers = WS.encode_multipart(data, files)
            headers.update({
                "host": "chatango.com", "origin": "http://st.chatango.com"
                })
        if WS.RPOST("http://chatango.com/updateprofile", data,
                    headers = headers):
            return True  # TODO comprobar resultado
        else:
            return False

    def uploadImage(self, img, url = False, **kw):
        """
        TODO sacar la parte del archivo
        Sube una imagen al servidor y regresa el número
        @param img: url de una imagen (local o web). También puede ser un
        archivo de bytes con la propiedad read()
        @param url: Indica si retornar una url o solo el número. Defecto(False)
        @return: string con url o número de la imagen
        """
        data = {
            'u': self._currentaccount[0], 'p': self._currentaccount[1]
            }
        if type(img) == str and (
                img.startswith("http:") or img.startswith("https:")):
            archivo = urlreq.urlopen(img).read()
        elif type(img) == str:
            archivo = open(img, 'rb').read()
        else:
            archivo = img.read()
        files = {
            'filedata': {'filename': img, 'content': archivo.decode('latin-1')}
            }
        files['filedata'].update(**kw)
        if hasattr(archivo, 'close'):
            archivo.close()
        data, headers = WS.encode_multipart(data, files)
        headers.update(
                {"host": "chatango.com", "origin": "http://st.chatango.com"})
        res = WS.RPOST("http://chatango.com/uploadimg", data, headers = headers)
        if res:
            res = res.read().decode('utf-8')
            if 'success' in res:
                if url:  # TODO enviar imágenes en distintas calidades
                    url = "http://ust.chatango.com/um/%s/%s/%s/img/t_%s.jpg"
                    url %= (
                        self.user.name[0], self.user.name[1],
                        self.user.name,
                        res.split(':', 1)[1])
                    return url
                else:
                    return res.split(':', 1)[1]
        return False

    ####################
    # Utilería del bot
    ####################
    def banRecord(self, user):
        if isinstance(user, User):  # TODO externalizar
            user = user.name
        if user.lower() in [x.name for x in self._banlist]:
            return self._banlist[User(user)]
        return None

    def _login(self, uname = None, password = None):
        """
        Autenticar. Logearse como uname con password. En caso de no haber
        ninguno usa la _currentaccount
        @param uname: Nombre del usuario (string)
        @param password: Clave del usuario (string)
        @return:
        """
        # TODO, Name y password no shilven
        __reg2 = ["bauth", self.name, _genUid(), self._currentaccount[0],
                  self._currentaccount[1]]  # TODO comando
        self._currenname = self._currentaccount[0]
        self._sendCommand(*__reg2)

    def _reload(self):
        # self._sendCommand("reload_init_batch")
        if self.userCount <= 1000:
            self._sendCommand("g_participants:start")
        else:
            self._sendCommand("gparticipants:start")
        self._sendCommand("getpremium", "l")
        self._sendCommand('getannouncement')
        self.requestBanlist()
        self.requestUnBanlist()

    @staticmethod
    def _parseFlags(flags: int, molde: dict) -> Struct:
        """
        Leer flags desde un número, y llenar un Molde con ellos
        @param flags: Flags int
        @param molde: Molde del cual rellenar
        @return: Struct
        """
        flags = int(flags)
        result = Struct(**dict([(mf, molde[mf] & flags != 0) for mf in molde]))
        result.value = flags
        return result

    def requestBanlist(self):  # TODO revisar
        self._sendCommand('blocklist', 'block',
                          str(int(time.time() + self._correctiontime)), 'next',
                          '500', 'anons', '1')

    def _rawBan(self, msgid, ip, name):
        """
        Ban user with received data
        @param msgid: Message id
        @param ip: user IP
        @param name: chatango user name
        @return: bool
        """
        self._sendCommand("block", msgid, ip, name)

    def rawUnban(self, name, ip, unid):
        self._sendCommand("removeblock", unid, ip, name)

    def requestUnBanlist(self):
        self._sendCommand('blocklist', 'unblock',
                          str(int(time.time() + self._correctiontime)), 'next',
                          '500', 'anons', '1')

    def setAnnouncement(self, anuncio = None, tiempo = 0,
                        enabled = True):  # TODO activar o desactivar solamente
        """Actualiza el anuncio por el indicado
        @param anuncio: El anuncio nuevo
        @param tiempo: Cada cuanto enviar el anuncio, en segundos (minimo 60)
        @param enabled: Si el anuncio está activado o desactivado (defecto True)
        Si solo se manda enabled, se cambia con el anuncio que ya estaba en
        la sala
        0=Off + No bg
        1=On  + No bg
        2=Off + BG
        3=On  + BG
        """
        # TODO usar fuentes por defecto del usuario
        if self.owner != self.user and (
                self.user not in self.mods or not self.modflags.get(
                self.user.name).EDIT_GP_ANNC):
            return False
        if anuncio is None:
            self._announcement[0] = int(enabled)
            self._sendCommand('updateannouncement', int(enabled),
                              *self._announcement[1:])
        else:
            self._sendCommand('updateannouncement', int(enabled), tiempo,
                              anuncio)
        return True

    ####################
    # Comandos recibidos
    ####################
    def _rcmd_aliasok(self, args):
        """
        Se ha iniciado sesión con el alias indicado
        """
        # TODO Cambiar el self.user por el alias usado en login
        self._user = User("#" + self._currentname)
        self._reload()

    def _rcmd_annc(self, args):
        self._announcement[0] = int(args[0])
        anc = ':'.join(args[2:])
        if anc != self._announcement[2]:
            self._announcement[2] = anc
            self._callEvent('onAnnouncementUpdate', args[0] != '0')
        self._callEvent('onAnnouncement', anc)

    def _rcmd_b(self, args):  # TODO reducir  y unificar con rcmd_i
        # TODO el reconocimiento de otros bots en anon está incompleto
        msg = Message.parse(self, args)
        self._mqueue[msg.msgid] = msg

    def _rcmd_badalias(self, args):
        """TODO _rcmd_badalias mal inicio de sesión sin clave"""
        # 4 ya hay un usuario con ese nombre en la sala
        # 2 ya tienes ese alias
        # 1 La palabra está baneada en el grupo
        pass

    def _rcmd_badlogin(self, args):
        """TODO inicio de sesión malo"""
        # 2 significa mal clave
        pass

    def _rcmd_badupdate(self, args):  # TODO completar rcmd_badupdate
        # announcement
        pass

    def _rcmd_blocked(self, args):  # TODO Que era todo esto?
        target = args[2] and User(args[2]) or ''
        user = User(args[3])
        if not target:
            msx = [msg for msg in self._history if msg.unid == args[0]]
            target = msx and msx[0].user or User('ANON')
            self._callEvent('onAnonBan', user, target)
        else:
            self._callEvent("onBan", user, target)
        self._banlist[target] = self._BANDATA(args[0], args[1], target,
                                              float(args[4]), user)

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
            self._banlist[user] = self._BANDATA(params[0], params[1], user,
                                                float(params[3]),
                                                User(params[4]))
        self._callEvent("onBanlistUpdate")

    def _rcmd_bw(self, args):  # Palabras baneadas en el chat
        # TODO, actualizar el registro del chat
        part, whole = '', ''
        if args:
            part = urlreq.unquote(args[0])
        if len(args) > 1:
            whole = urlreq.unquote(args[1])
        if hasattr(self, '_bwqueue'):
            self._bwqueue = [self._bwqueue.split(':', 1)[0] + ',' + args[0],
                             self._bwqueue.split(':', 1)[1] + ',' + args[1]]
            self.setBannedWords(*self._bwqueue)  # TODO agregar un callEvent
        self._callEvent("onBannedWordsUpdate", part, whole)

    def _rcmd_clearall(self, args):
        """
        Resultados del comando. Si se borró el chat args=ok, sino dará un error
        """
        self._callEvent("onClearall", args[0])

    def _rcmd_delete(self, args):
        """Borrar un mensaje de mi vista actual"""
        msg = self._msgs.get(args[0])
        if msg and msg in self._history:
            self._history.remove(msg)
            self._callEvent("onMessageDelete", msg.user, msg)
            msg.detach()
        # Si hay menos de 20 mensajes pero el chat tiene más, por que no
        # pedirle otros tantos?
        if len(self._history) < 20 and not self._nomore:
            self._sendCommand('get_more:20:0')

    def _rcmd_deleteall(self, args):
        """Mensajes han sido borrados"""
        user = None  # usuario borrado
        msgs = list()  # mensajes borrados
        for msgid in args:
            msg = self._msgs.get(msgid)
            if msg and msg in self._history:
                self._history.remove(msg)
                user = msg.user
                msg.detach()
                msgs.append(msg)
        if msgs:
            self._callEvent('onDeleteUser', user, msgs)

    def _rcmd_denied(self, args):
        """La sala posiblemente no existe"""
        self._callEvent("onLoginFail")
        self.disconnect()  # TODO regresar False en el onJoin

    def _rcmd_getannc(self, args):
        # ['3', 'pythonrpg', '5', '60', '<nE20/><f x1100F="1">hola']
        # Enabled, Room, ?, Time, Message
        # TODO que significa el tercer elemento?
        if len(args) < 4 or args[0] == 'none':
            return
        self._announcement = [int(args[0]), int(args[3]), ':'.join(args[4:])]
        if hasattr(self, '_ancqueue'):
            del self._ancqueue
            self._announcement[0] = args[0] == '0' and 3 or 0
            self._sendCommand('updateannouncement', self._announcement[0],
                              ':'.join(args[3:]))

    def _rcmd_g_participants(self, args):
        self._userdict = dict()
        args = ':'.join(args).split(";")
        if not args or not args[0]:
            return  # Fix
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
                    name = '!' + getAnonName(puid, contime)
            user = User(name, room = self, isanon = isanon, puid = puid)
            if user in ({self._owner} | self.mods):
                user.setName(name)
            user.addSessionId(self, ssid)
            self._userdict[ssid] = [contime, user]

    def _rcmd_gparticipants(self, args):
        """Comando viejo de chatango, ya no se usa, pero lo sigue enviando"""
        self._rcmd_g_participants(len(args) > 1 and args[1:] or '')

    def _rcmd_getpremium(self, args):
        # TODO
        if self._bgmode:
            self._sendCommand('msgbg', str(self._bgmode))

    def _rcmd_gotmore(self, args):
        # TODO COMPROBAR ESTABILIDAD
        num = args[0]  # if self._nomore and self._nomore < 6:  #
        # self._nomore =  #  int(num) + 1  # if len(self._history) <
        # self._history.maxlen and 0  #  < self._nomore < 6:  #
        # self._sendCommand("get_more:20:" + str(  #  self._nomore))

    def _rcmd_groupflagsupdate(self, args):
        flags = args[0]
        self._flags = self._parseFlags(flags, GroupFlags)
        self._callEvent('onFlagsUpdate')

    def _rcmd_i(self, args):  # TODO
        msg = Message.parse(self, args)
        if len(self._history) <= self._history.maxlen:
            self._history.appendleft(msg)
            self._callEvent("onHistoryMessage", msg.user, msg)

    def _rcmd_inited(self, args = None):
        """
        El historial y los comandos inicales se han recibido.
        """
        self._reload()
        if self.attempts <= 1:
            self._connectattempts = 1
            self._callEvent("onConnect")
        else:
            self._callEvent("onReconnect")
            self._connectattempts = 1
        # TODO, rellenar history hasta el límite indicado
        # self._sendCommand("get_more:20:" + str(self._waitingmore -  1))

    def _rcmd_logoutfirst(self, args):
        # TODO al intentar iniciar sesión sin haber cerrado otra
        pass

    def _rcmd_logoutok(self, args):
        """Me he desconectado, ahora usaré mi nombre de anon"""
        name = '!' + getAnonName(self._puid,
                                 str(self._connectiontime))
        self._user = User(name,
                          nameColor = str(self._connectiontime).split('.')[0][
                                      -4:])
        self._callEvent('onLogout', self._user, '?')  # TODO fail aqui

    def _rcmd_mods(self, args):
        pre = self._mods
        mods = self._mods = dict()
        # Load current mods
        for mod in args:
            name, powers = mod.split(',', 1)
            utmp = User.get(name)
            mods[utmp] = self._parseFlags(powers, ModFlags)
            mods[utmp].isadmin = int(powers) & AdminFlags != 0
        tuser = User(self.currentname)
        # TODO reducir
        if (self.user not in pre and self.user in mods) or (tuser not in pre and tuser in mods):
            # Si el bot no estaba en los mods
            if self.user == tuser:
                self._callEvent('onModAdd', self.user)
            return

        for user in self.mods - set(pre.keys()):  # Con Mod
            self._callEvent("onModAdd", user)
        for user in set(pre.keys()) - self.mods:  # Sin Mod
            self._callEvent("onModRemove", user)
        for user in set(pre.keys()) & self.mods:  # Cambio de privilegios
            privs = set(x for x in dir(mods.get(user)) if
                        not x.startswith('_') and getattr(mods.get(user),
                                                          x) != getattr(
                                pre.get(user), x))
            privs = privs - {'MOD_ICON_VISIBLE', 'value'}  # Let's Ignore these
            if privs:  # ¿Are there changes?
                self._callEvent('onModChange', user, privs)

    def _rcmd_miu(self, args):
        """Recarga la imagen y/o bg del usuario en cuestión"""
        self._callEvent('onBgChange', User(args[0]))

    def _rcmd_mustlogin(self, args = None):
        """Debes logearte para participar"""
        self._callEvent('onLoginRequest')

    def _rcmd_n(self, args):  # TODO aún hay discrepancias en el contador
        """Cambió la cantidad de usuarios en la sala"""
        if not self.flags.NOCOUNTER:
            self._usercount = int(args[0], 16)
            # assert not self._userdict or len(self._userdict) ==
            # self._usercount, 'Warning count doesnt match'  # TODO
            self._callEvent("onUserCountChange")

    def _rcmd_nomore(self, args):
        """No hay más mensajes por cargar en la sala"""
        self._waitingmore = 0  # TODO revisar

    def _rcmd_ok(self, args):
        self._owner = User(args[0])
        self._puid = args[1]  # TODO definir puid y sessionid
        self._authtype = args[2]  # TODO M=Ok, N= ? C= Anon
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
            self._user = User(
                '!' + getAnonName(self._puid, self._connectiontime))
            self._currenname = self._user.name  # TODO join as anon
        elif self._authtype == 'N':
            pass
        if self.mgr:
            # TODO remove private
            self._user._fontColor = self.mgr._fontColor
            self._user._fontFace = self.mgr._fontFace
            self._user._fontSize = self.mgr._fontSize
        if mods:
            for x in mods.split(';'):
                powers = x.split(',')[1]
                self._mods[User(x.split(',')[0])] = self._parseFlags(powers,
                                                                     ModFlags)
                self._mods[User(x.split(',')[0])].isadmin = int(
                        powers) & AdminFlags != 0

    def _rcmd_participant(self, args):
        """
        Cambio en la lista de participantes
        TODO _historysessions a un usuario para saber quien es
        """
        cambio = args[0]  # Leave Join Change
        ssid = args[
            1]  # Session ID, cambia por sesión (o pestaña del navegador).
        puid = args[2]  # Personal User ID (en la sala)
        name = args[3]  # Visible Name
        tname = args[4]  # Anon Name
        unknown = args[5]  #
        contime = args[6]  # Hora del cambio
        if name == 'None':
            if tname != 'None':
                name = '#' + tname
            else:
                name = '!' + getAnonName(puid, contime)
        user = User(name, puid = puid)
        before = None
        if ssid in self._userdict:
            before = self._userdict[ssid][1]
        if cambio == '0':  # Leave
            user.removeSessionId(self, ssid)  # Quitar la id de sesión activa

            if ssid in self._userdict:  # Remover el usuario de la sala
                usr = self._userdict.pop(ssid)[1]
                lista = [x[1] for x in self._userhistory]
                if usr not in lista:
                    self._userhistory.append([contime, usr])
                else:
                    self._userhistory.remove(
                            [x for x in self._userhistory if x[1] == usr][0])
                    self._userhistory.append([contime, usr])
            if user.isanon:
                self._callEvent('onAnonLeave', user, puid)
            else:
                self._callEvent('onLeave', user, puid)
        elif cambio == '1' or not before:  # Join
            user.addSessionId(self, ssid)  # Agregar la sesión al usuario
            if not user.isanon and user not in self.userlist:
                self._callEvent('onJoin', user, puid)
            elif user.isanon:
                self._callEvent('onAnonJoin', user, puid)
            # Agregar la sesión a la sala
            self._userdict[ssid] = [contime, user]
            lista = [x[1] for x in self._userhistory]
            if user in lista:
                self._userhistory.remove(
                        [x for x in self._userhistory if x[1] == user][0])
        else:  # 2 Account Change
            # Quitar la cuenta anterior de la lista y agregar la nueva
            # TODO conectar cuentas que han cambiado usando este método
            if before.isanon:  # Login
                if user.isanon:  # Anon Login
                    self._callEvent('onAnonLogin', user, puid)
                else:  # User Login
                    self._callEvent('onUserLogin', user, puid)
            elif not before.isanon:  # Logout
                if before in self.userlist:
                    lista = [x[1] for x in self._userhistory]

                    if before not in lista:
                        self._userhistory.append([contime, before])
                    else:
                        lst = [x for x in self._userhistory if before == x[1]]
                        if lst:
                            self._userhistory.remove(lst[0])
                        self._userhistory.append([contime, before])
                    self._callEvent('onUserLogout', before, puid)
            user.addPersonalUserId(self, puid)
            self._userdict[ssid] = [contime, user]

    def _rcmd_pwdok(self, args = None):
        """Login correcto"""
        self._user = User(self._currentname)
        self._callEvent("onLogin", self._user)
        self._reload()

    def _rcmd_show_tb(self, args):
        """Mostrar notificación de temporary ban"""
        self._callEvent("onFloodBan", int(args[0]))

    def _rcmd_tb(self, args):
        """Temporary ban sigue activo con el tiempo indicado"""
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
            if (msg.channel & ModChannels or msg.badge) and msg.user not in [
                self.owner] + list(self.mods):  # TODO reducir
                self._mods[msg.user] = self._parseFlags('0', ModFlags)
                self._mods[msg.user].isadmin = False
            msg.user.history = msg
            self._callEvent("onMessage", msg.user, msg)

    def _rcmd_ubw(self, args):  # TODO palabas desbaneadas ?)
        self._ubw = args
        pass

    # TODO _rcmd_proxybanned
    # TODO _rcmd_ratelimit

    def _rcmd_unblocked(self, args):
        """Se ha quitado el ban a un usuario"""
        unid = args[0]
        ip = args[1]
        # En caso de ban múltiple a misma cuenta, guardar solo el primer valor
        target = args[2].split(';')[0]
        # TODO verificar que otra accion se puede hacer con un ban multiple
        # args[3:-3] if len(args)>5
        bnsrc = args[-3]  # TODO utilidad del bnsrc (el que banea)
        ubsrc = User(args[-2])
        time = args[-1]
        self._unbanqueue.append(
                self._BANDATA(unid, ip, target, float(time), ubsrc))

        if target == '':
            # Si el baneado era anon, intentar otbener su nombre
            msx = [msg for msg in self._history if msg.unid == unid]
            target = msx and msx[0].user or User('anon')
            self._callEvent('onAnonUnban', ubsrc, target)
        else:
            target = User(target)
            if target in self._banlist:
                self._banlist.pop(target)
            self._callEvent("onUnban", ubsrc, target)

    def _rcmd_unblocklist(self, args):
        sections = ":".join(args).split(";")
        for section in sections[::-1]:
            params = section.split(":")
            if len(params) != 5:
                continue
            unid = params[0]
            ip = params[1]
            target = User(params[2] or 'Anon')
            time = float(params[3])
            src = User(params[4])
            self._unbanqueue.append(self._BANDATA(unid, ip, target, time, src))
        self._callEvent("onUnBanlistUpdate")

    def _rcmd_updatemoderr(self, args):
        """Ocurrió un error al enviar un comando para actualizar un mod"""
        self._callEvent("onUpdateModError", User(args[1]), args[0])

    def _rcmd_updateprofile(self, args):
        """Cuando alguien actualiza su perfil en un chat"""
        user = User.get(args[0])
        user._info = None
        self._callEvent('onUpdateProfile', user)

    def _rcmd_updgroupinfo(self, args):
        """Se ha actualizado la información de la sala"""
        self._info = Room._INFO(urlreq.unquote(args[0]),
                                urlreq.unquote(args[1]))
        self._callEvent('onUpdateInfo')


# TODO climited:1552105466643:
# climited:??:command

class Gestor:
    """
    Clase Base para manejar las demás conexiones
    """
    _TimerResolution = 0.2
    maxHistoryLength = 700
    PMHost = "c1.chatango.com"

    def __dir__(self):
        return [x for x in
                set(list(self.__dict__.keys()) + list(dir(type(self)))) if
                x[0] != '_']

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def __init__(self, name: str = '', password: str = None, pm: bool = None,
                 accounts = None):
        self._accounts = accounts
        self._colasalas = queue.Queue()
        self.connlock = threading.Lock()
        if accounts is None:
            self._accounts = [(name, password)]
        self._jt = None  # Join Thread
        self._name = self._accounts[0][0]
        self._password = self._accounts[0][1]
        self._rooms = dict()
        self._running = None
        self._user = User(self._name)
        self._tasks = set()
        self._pm = None
        self._badconns = queue.Queue()
        self._fontColor = '000000'
        self._fontSize = '12'
        self._fontFace = '0'
        self.bgmode = False
        self._pm = pm

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
    def easy_start(cls, rooms: list = None, name: str = None,
                   password: str = None, pm: bool = True,
                   accounts: [(str, str), (str, str), ...] = None):
        """
        Inicio rápido del bot y puesta en marcha
        @param rooms: Una lista de sslas
        @param name: Nombre de usuario
        @param password: Clave de conexión
        @param pm: Si se usará el PM o no
        @param accounts: Una lista/tupla de cuentas ((clave,usuario))
        """
        if not rooms:
            rooms = str(input('Nombres de salas separados por coma: ')).split(
                    ',')
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

    def findUser(self, name):
        """
        Regresa una lista con los nombres de salas en las que se encuentra el
        usuario
        """
        if isinstance(name, User):
            name = name.name
        return [x.name for x in list(self._rooms.values()) if x.findUser(name)]

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
        return self._rooms.get(room.lower())

    def joinRoom(self, room: str, account = None):
        """
        Unirse a una sala con la cuenta indicada
        @param room: Sala a la que unirse
        @param account:  Opcional, para entrar con otra cuenta str o ['','']
        """
        if account is None:
            account = self._accounts[0]
        if isinstance(account, str):
            cuenta = {k.lower(): [k, v] for k, v in self._accounts}.get(
                    account.lower(), self._accounts[0])
            cuenta[0] = account
            account = cuenta
        if room.lower() not in self._rooms:
            # self._rooms[room] = Room(room, self, account)
            # self._rooms[room.lower()]=Room(room.lower(),self,account)
            # self._rooms[room.lower()]=
            self._colasalas.put((room.lower(), account))
            return True
        else:
            return False

    def _joinThread(self):
        while True:
            room, account = self._colasalas.get()
            try:
                con = Room(room, self, account)
                self._rooms[room] = con
            except TimeoutError as fallo:
                print("[{0}][{1}] El servidor de la sala no responde".format(
                    time.strftime('%I:%M:%S %p'), room), file=sys.stderr)
                # TODO usar evento de sala cuando el server no responde

    def leaveRoom(self, room):
        if isinstance(room, Room):
            room = room.name
        if room.lower() in self._rooms:
            tmp = self._rooms.pop(room)
            tmp.disconnect()

    def main(self):
        """
        Poner en marcha al bot
        """
        while self._pm == True:
            try:
                self._pm = PM(mgr=self, name=self.name,
                              password=self.password)
            except socket.gaierror as malInicio:  # En caso de que no haya internet
                print("[{0}] No hay internet, Reintentando conexión en 10... ".format(
                    time.strftime('%I:%M:%S %p')
                ))
                time.sleep(10)

        self.onInit()
        if self._running == False:
            return
        self._running = True
        self._jt = threading.Thread(target = self._joinThread,
                                    name = "Join rooms")
        self._jt.daemon = True
        self._jt.start()
        while self._running:
            time.sleep(0.01)
            pass

        # Finish
        # Cerrar conexiones
        for conn in self.getConnections():
            conn.disconnect()
        # Cancelar tareas
        for x in list(self._tasks):
            x.cancel()

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
        self._fontColor = str(hexfont)
        for x in list(self.rooms):
            x.user._fontColor = str(hexfont)

    def setFontFace(self, facenum):
        """
        @param facenum: El número de la fuente en un string
        """
        fuente = str(Fonts.get(str(facenum).lower(), facenum))
        self._fontFace = fuente
        for x in list(self.rooms):
            x.user._fontFace = fuente

    def setFontSize(self, sizenum):
        """Cambiar el tamaño de la fuente
        TODO para la sala
        """
        size = str(sizenum)
        self._fontSize = size
        for x in list(self.rooms):
            x.user._fontSize = size

    def setInterval(self, tiempo, funcion, *args, **kwargs):
        """
        Llama a una función cada intervalo con los argumentos indicados
        @param funcion: La función que será invocada
        @type tiempo int
        @param tiempo:intervalo
        """
        task = Task(tiempo, funcion, True, *args, **kwargs)
        task.mgr = self
        self._tasks.add(task)  # TODO recuerda eliminar tasks obsoletos
        return task

    def setTimeout(self, tiempo, funcion, *args, **kwargs):
        """
        Llama a una función cada intervalo con los argumentos indicados
        @param tiempo: Tiempo en segundos hasta que se ejecute la función
        @param funcion: La función que será invocada
        """
        task = Task(tiempo, funcion, False, *args, **kwargs)
        self._tasks.add(task)
        return task

    def setNameColor(self, hexcolor):
        """
        Cambiar el color del nombre para todas las conexiones
        @param hexcolor: Color en hexadecimal tipo string
        """
        self.user._nameColor = hexcolor

    def onAnnouncement(self, room, announcement):
        """
        Al recibir anuncios de la sala
        @param room: Sala donde ocurre el evento
        @param announcement: Anuncio recibido
        """
        pass

    def onAnnouncementUpdate(self, room, active):
        """
        Se activa cuando un moderador cambia los anuncios automáticos de la sala
        @param room: Sala donde ocurre el evento
        @param active: Bool indicando si el annuncio está activo o no
        """
        pass

    def onBannedWordsUpdate(self, room, part, whole):
        """
        Al cambiar/recibir las palabras baneadas en la sala
        @param room: Sala donde ocurre el evento
        @param part: Partes de palabras baneadas
        @param whole: Palabras completas baneadas
        """
        pass

    def onAnonBan(self, room, user, target):
        """
        Al ser baneado un anon en la sala
        @param room: Sala donde ocurre
        @param user: Usuario que banea
        @param target: Usuario baneado
        """
        pass

    def onAnonUnban(self, room, user, target):
        """
        Al ser retirado el ban de un anon en la sala
        @param room: Sala donde ocurre
        @param user: Usuario que retira el ban
        @param target: Usuario baneado
        """
        pass

    def onAnonJoin(self, room, user, ssid):
        """
        Al unirse un Anon a la sala
        @param room: Sala en la que ocurre el evento
        @param user: Usuario(anon) que se ha unido
        @param ssid: Id de sesión del anon (es casi única por sala)
        """
        pass

    def onAnonLeave(self, room, user, ssid):
        """
        Al salir un Anon de la sala
        @param room: Sala en la que ocurre el evento
        @param user: Usuario que abandona la sala
        @param ssid: Id de sesión del anon que abandona la sala
        """
        pass

    def onAnonLogin(self, room, user, ssid):
        """
        Cuando un user se pone un nombre de Anon
        @param room: Sala en la que ocurre el evento
        @param user: Usuario que ha hecho login
        @param ssid: Id de sesión, con esto se puede saber que anon era
        """
        pass

    def onBan(self, room, user, target):
        """
        Al ser baneado un usuario en la sala
        @param room: Sala en la que ocurre el evento
        @param user: Usuario que banea
        @param target: Usuario baneado
        """
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
        @param result: Resultado, puede ser 'ok' o 'error'. El error solo
        aparece si el bot ha sido quien solicita el
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
        Al cargar un mensaje anterior a la conexión del bot en la sala. Util
        para mantener registrado hasta los
        momentos en los que no está el bot
        @param room: Sala donde se cargó el mensaje
        @param user: Usuario del mensaje
        @param message: El mensaje cargado
        """
        pass

    def onJoin(self, room, user, ssid):  # TODO comentar
        pass

    def onLeave(self, room, user, ssid):  # TODO comentar
        pass

    def onLogin(self, room, user):
        """
        Al loguearse como un usuario de chatango
        @param room: Sala donde ocurre el evento
        @param user: Mi usuario
        """
        pass

    def onLoginFail(self, room):
        """
        Al fracasar un intento de acceso
        @param room: Sala o PM
        """
        pass

    def onLoginRequest(self, room):
        """
        Cuando una sala solicita estar logeado para poder participar en ella
        @param room: Sala donde ocurre el evento
        """
        pass

    def onLogout(self, room, user, ssid):
        """
        Cuando un usuario sale de su cuenta en una sala
        @param room: Sala donde ocurre el evento
        @param user: Usuario que ha salido de su cuenta
        @param ssid: Id de sesión que está usando el usuario
        """
        # TODO incluir el anon del usuario
        pass

    def onMessage(self, room: Room, user: User, message: Message):
        """
        Al recibir un mensaje en una sala
        @param room: Sala en la que se ha recibido el mensaje
        @param user: Usuario que ha enviado (User)
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
        """
        Cuando se agrega un moderador nuevo a la sala
        @param room: Sala donde ocurre el evento
        @param user: Usuario que ha sido ascendido a moderador
        """
        pass

    def onModChange(self, room, user, privs):
        """
        Al cambiar los privilegios de un moderador
        @param room: Sala en la que ocurre el evento
        @param user: Usuario al que le han cambiado sus privilegios
        @param privs: Nombres de los privilegios modificados(nombres según
        modflags)
        """
        pass

    def onModRemove(self, room, user):
        """
        Cuando se remueve un moderador de la sala
        @param room: Sala donde ocurre el evento
        @param user: Usuario que ha perdido su mod
        """

    def onPMContactAdd(self, pm, user):
        """
        Al agregarse un contacto para el bot
        @param pm: El PM
        @param user: El usuario agregado a los contactos
        """
        pass

    def onPMBlock(self, pm, user):
        """
        Al bloquear a otro usuario en el PM
        @param pm: El PM
        @param user: usuario bloqueado
        """
        pass

    def onPMContactRemove(self, pm, user):
        """
        Al remover un contacto del PM
        @param pm: El pm
        @param user: contacto removido
        """
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

    def onPMContactApp(self, pm: PM, user: User):
        """
        Cuando un usuario se desconecta pero cuenta con la APP de chatango
        @param pm: El PM
        @param user: El usuario que se ha desconectado
        """
        pass

    def onPMContactOffline(self, pm: PM, user: User):
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
        """
        Al desconectarse del PM
        @param pm: El  PM
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

    def onPMMessageSend(self, pm, user, message):
        """
        Cuando se envía un mensaje al pm
        @param pm: El PM
        @param user: El usuario al que se envía el mensaje
        @param message: El mensaje enviado
        """
        pass

    def onBgChange(self, room, user):
        """
        Cuando un usuario cambia su BackGround[BG] en una sala
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

    def onPMOfflineMessage(self, pm, user, message):
        """
        Al recibir un mensaje cuando no se estuvo conectado
        @param pm: El PM
        @param user: El usuario que envió el mensaje
        @param message: El mensaje es de tipo (Message)
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

    def onUnban(self, room, user, target):
        """
        Al ser desbaneado un usuario
        @param room: Sala en la que ocurre el evento
        @param user: Usuario que quita el ban
        @param target: Usuaro que ha sido desbaneado
        """
        pass

    def onUnBanlistUpdate(self, room):
        """
        Cuando se actualiza el historial de ban de una sala
        @param room: Sala donde ocurre el evento
        """
        pass

    def onUpdateInfo(self, room):
        """
        Cuando se actualiza la información de una sala
        @param room: Sala donde ocurre el cambio
        """
        pass

    def onUpdateModError(self, room, user, reason):
        """
        Cuando ocurre un error al actualizar un moderador
        @param room: Sala donde ocurre el evento
        @param user: Mod que se intentó actualizar
        @param reason: Razón del error (2=Enviado código incorrecto/inválido)
        """
        # TODO Cambiar reason a algo más práctico
        pass

    def onUpdateProfile(self, room, user):
        """
        Cuando un usuario activa su perfil en una sala
        @param room: Sala donde ocurre el evento
        @param user: Usuario que actualiza su perfil
        """
        pass

    def onUserCountChange(self, room):
        """
        Al cambiar la cantidad de usuarios en una sala
        @param room: Sala en la que cambió la cantidad de usuarios
        """
        pass

    def onUserLogin(self, room, user, puid):
        """
        Al hacer login con una cuenta de chatango
        @param room: Sala donde ocurre
        @param user: Usuario que se ha conectado
        @param puid: Id personal del usuario
        """
        pass

    def onUserLogout(self, room, user, puid):
        """
        Al desloguearse de una sala, el usuario sigue como anon
        @param room: Sala en la que ocurre
        @param user: Usuario que se desconect+p
        @param puid: Id personal del usuario
        """
        pass

    def onConnectionLost(self, room, error):
        """
        Al perder la conexión a una sala o pm
        @param room: Sala o PM donde ocurre el evento
        @param error: Error de conexion que ocasionó la perdida
        @type error: Exception
        """
        print(
                "[{}][{}]: Conexión perdida, reintentando...[{}] ".format(
                        room,
                        time.strftime(
                                '%I:%M:%S %p'), error), file = sys.stderr)

    def onConnectionAttempt(self, room, error):
        """
        Al reinentar la conexión y volver a fallar
        @param room: Sala o PM donde ocurre el evento
        @param error: Error que ocasiona el fallo de conexión
        @type error: Exception
        """
        print('[{}][{}][{:^5}] Aún no hay internet.[{}]'.format(
                time.strftime(
                        '%I:%M:%S %p'),
                room,
                room._connectattempts, error),
                file = sys.stderr)

    def onPremiumChange(self, room, user):
        """
        Al detectar un cambio en el estado premium de un usuario
        @param room: Sala o  pm donde ocurre 
        @param user: Usuario que ha recibido o perdido estado premium
        """
        pass

class RoomManager(Gestor):
    """
    Compatibilidad con la ch
    """
    pass
