from Utils import *
from scapy.all import *

from displayPacket import *

class Rule:
    """A NIDS rule"""

    def __init__(self, string, action, protocol, srcIp, srcPorts, dstIp, dstPorts):
        """Constructor"""
        # TODO : include options in the constructor, make it easier (input string)
        self.string = string
        self.action = action
        self.protocol = protocol
        self.srcIps = srcIp
        self.srcPorts = srcPorts
        self.dstIps = dstIp
        self.dstPorts = dstPorts

    def addOption(self, option, value):
        if (option == "msg"):
            self.msg = value
        elif (option == "tos"):
            self.tos = int(value)
        elif (option == "len"):
            self.len = int(value)
        elif (option == "offset"):
            self.offset = int(value)
        elif (option == "seq"):
            self.seq = int(value)
        elif (option == "ack"):
            self.ack = int(value)
        elif (option == "flags"):
            self.flags = value
        elif (option == "http_request"):
            self.http_request = value
            # remove starting and ending ["]
            if (self.http_request.endswith('"')):
                self.http_request = self.http_request[:-1]
            if (self.http_request.startswith('"')):
                self.http_request = self.http_request[1:]
        elif (option == "content"):
            self.content = value;
            # remove starting and ending ["]
            if (self.content.endswith('"')):
                self.content = self.content[:-1]
            if (self.content.startswith('"')):
                self.content = self.content[1:]

    def __repr__(self):
        """Returns the string representing the Rule"""
        # simply use initialization string
        return self.string

    def match(self, pkt):
        """
        Returns True if and only if the rule is matched by given packet,
        i.e. if every part of the rule is met by the packet.
        """
        # check protocol
        if (not self.checkProtocol(pkt)):
            return False

        # check IP source and destination
        if (not self.checkIps(pkt)):
            return False

        # check source Port
        if (not self.checkPorts(pkt)):
            return False

        # check options
        if (not self.checkOptions(pkt)):
            return False

        # otherwise the rule is met
        return True

    def checkProtocol(self, pkt):
        """ Returns True if and only if the rule concerns packet's protocol """
        f = False
        if (self.protocol == Protocol.TCP and TCP in pkt):
            f = True
        elif (self.protocol == Protocol.UDP and UDP in pkt):
            f = True
        elif (self.protocol == Protocol.HTTP and TCP in pkt):
            # HTTP packet has to be TCP
            # check payload to determine if this is a HTTP packet
            if (isHTTP(pkt)):
                f = True
        return f

    def checkIps(self, pkt):
        """Returns True if and only if the rule's IPs concern the pkt IPs"""
        f = False
        if (IP not in pkt):
            f = False
        else:
            srcIp = pkt[IP].src
            dstIp = pkt[IP].dst
            ipSrc = ip_address(unicode(srcIp))
            ipDst = ip_address(unicode(dstIp))
            if (self.srcIps.contains(ipSrc) and self.dstIps.contains(ipDst)):
                # ipSrc and ipDst match rule's source and destination ips
                f = True
            else:
                f = False
        return f

    def checkPorts(self, pkt):
        """Returns True if and only if the rule's Ports concern packet's Ports"""
        f = False
        if (UDP in pkt):
            srcPort = pkt[UDP].sport
            dstPort = pkt[UDP].dport
            if (self.srcPorts.contains(srcPort) and self.dstPorts.contains(dstPort)):
                f = True
        elif (TCP in pkt):
            srcPort = pkt[TCP].sport
            dstPort = pkt[TCP].dport
            if (self.srcPorts.contains(srcPort) and self.dstPorts.contains(dstPort)):
                f = True
        return f

    def checkOptions(self, pkt):
        """ Return True if and only if all options are matched """

        # TODO : change hasattr to try except
        if (hasattr(self, "tos")):
            if (IP in pkt):
                if (self.tos != int(pkt[IP].tos)):
                    return False
            else:
                return False

        if (hasattr(self, "len")):
            if (IP in pkt):
                if (self.len != int(pkt[IP].ihl)):
                    return False
            else:
                return False

        if (hasattr(self, "offset")):
            if (IP in pkt):
                if (self.offset != int(pkt[IP].frag)):
                    return False
            else:
                return False

        if (hasattr(self, "seq")):
            if (TCP not in pkt):
                return False
            else:
                if (self.seq != int(pkt[TCP].seq)):
                    return False

        if (hasattr(self, "ack")):
            if (TCP not in pkt):
                return False
            else:
                if (self.ack != int(pkt[TCP].ack)):
                    return False

        if (hasattr(self, "flags")):
            # match if and only if the received packet has all the rule flags set
            if (TCP not in pkt):
                return False
            else:
                for c in self.flags:
                    pktFlags = pkt[TCP].underlayer.sprintf("%TCP.flags%")
                    if (c not in pktFlags):
                        return False

        if (hasattr(self, "http_request")):
            if (not isHTTP(pkt)):
                return False
            elif (TCP in pkt and pkt[TCP].payload):
                data = str(pkt[TCP].payload)
                words = data.split(' ')
                if ((len(words) < 1) or (words[0].rstrip() !=  self.http_request)):
                    return False
            else:
                return False

        if (hasattr(self, "content")):
            payload = None
            if (TCP in pkt):
                payload = pkt[TCP].payload
            elif (UDP in pkt):
                payload = pkt[UDP].payload
            if (payload):
                if (self.content not in str(payload)):
                    return False
            else:
                return False

        return True


    def printOptions(self):
        # TODO : hasattr -> try / except
        if (hasattr(self, "msg")):
            print self.msg
        if (hasattr(self, "tos")):
            print self.tos
        if (hasattr(self, "len")):
            print self.len
        if (hasattr(self, "offset")):
            print self.offset
        if (hasattr(self, "seq")):
            print self.seq
        if (hasattr(self, "ack")):
            print self.ack
        if (hasattr(self, "flags")):
            print self.flags
        if (hasattr(self, "http_request")):
            print self.http_request
        if (hasattr(self, "content")):
            print self.content
