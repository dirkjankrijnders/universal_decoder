from socket import socket, AF_INET, SOCK_STREAM
import asyncio


class RocrailClient(object):
    def __init__(self, hostname: str = "localhost", port: int = 8051):
        super(RocrailClient, self).__init__()
        self.hostname = hostname
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)

    def connect(self) -> bool:
        """
        Connect the Rocrail server using the details specified in the constructor
        :return:
            True if successful, False otherwise
        """
        return self.socket.connect((self.hostname, self.port))

    def disconnect(self):
        """
        Terminate the connection the Rocrail server
        :return:
        """
        self.socket.close()

    def send_message(self, msg_type: str, msg: str):
        """
        Send a message to the Rocrail server. The xml header is added by this function.
        :param msg_type: Type of the message
        :param msg: xml formatted message to send
        :return:
        """
        msg_string = "<xmlh><xml size=\"%d\" name=\"%s\"/></xmlh>%s" % (len(msg), msg_type, msg)
        self.socket.send(bytes(msg_string, 'ascii'))

    def power_on(self):
        """
        Tell Rocrail to power on
        :return:
        """
        self.send_message("sys", "<sys cmd=\"go\"/>")

    def power_off(self):
        """
        Tell Rocrail to power off
        :return:
        """
        self.send_message("sys", "<sys cmd=\"stop\"/>")

    def plan(self):
        """
        Get the current plan from Rocrail
        :return:
        """
        self.send_message("model", "<plan cmd=\"declst\"/>")


async def get_plan(host: str= "localhost"):
    from xml.etree.ElementTree import XMLPullParser, ElementTree, tostring
    from lxml import etree
    i = 0
    PRE = 0
    HEADER = 1
    MSG_START = 2
    MSG = 3
    state = PRE
    expected_msg = "asdfasdfasdf"
    reader, writer = await asyncio.open_connection(host, 8051)
    # connect = asyncio.open_connection("localhost", 8051)
    # reader, writer = yield from connect
    msg_type = "model"
    msg = "<%s cmd=\"plan\"/>" % msg_type
    msg_string = "<xmlh><xml size=\"%d\" name=\"%s\"/></xmlh>%s\n" % (len(msg), msg_type, msg)
    expected_no_messages = 2
    no_messages = 0
    writer.write(bytes(msg_string, 'ascii'))
    looping = True
    parser = None
    parser_lxml = None
    while looping:
        line = await reader.readline()
        line = line.strip(b'\x00')
        # print(line)
        if line.startswith(b"<?xml"):
            print("new message")
            parser = XMLPullParser(['start', 'end'])
            parser_lxml = etree.XMLPullParser()
            parser.feed("<root>")
        elif line:
            parser.feed(line)
            for event in parser.read_events():

                if event[0] == 'start':
                    if event[1].tag == 'xmlh':
                        state = HEADER
                    if state == MSG_START:
                        state = MSG
                        expected_msg = event[1].tag
                if event[0] == 'end':
                    if event[1].tag == 'xmlh':
                        state = MSG_START
                        line = line[7:]
                    if event[1].tag == expected_msg:
                        parser.feed("</root>")
                        print(line.decode())
                        parser_lxml.feed(line.decode())
                        try:
                            dom = parser_lxml.close()
                        except Exception as e:
                            print(e)
                        print("Closing message")
                        if no_messages == expected_no_messages:
                            looping = False
                        else:
                            i = 0
                            state = PRE
                            expected_msg = "asdfasdfasdf"

            if state > HEADER:
                string = line.decode()
                print(string)
                parser_lxml.feed(string)

        if not line:
            break

    # Ignore the body, close the socket
    writer.close()
    return dom
