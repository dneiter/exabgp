# encoding: utf-8
"""
rt.py

Created by Thomas Mangin on 2014-06-20.
Copyright (c) 2014-2014 Orange. All rights reserved.
Copyright (c) 2014-2014 Exa Networks. All rights reserved.
"""


import socket
from struct import pack,unpack

from exabgp.bgp.message.open.asn import ASN
from exabgp.bgp.message.update.attribute.community.extended import ExtendedCommunity


# ================================================================== RouteTarget


class RouteTarget (ExtendedCommunity):
	COMMUNITY_SUBTYPE = 0x02

	def __hash__ (self):
		return hash(self.community)

	def __cmp__ (self,other):
		if not isinstance(other,RouteTarget):
			return -1
		if self.asn != other.asn:
			return -1
		if self.ip != other.ip:
			return -1
		return 0


# ================================================================ RouteTargetIP


class RouteTargetIPASN (RouteTarget):
	COMMUNITY_TYPE = 0x01

	# XXX: FIXME: Decide between IP and number and keep one

	def __init__ (self,asn,ip,community=None):
		self.ip = ip if '.' in str(ip) else socket.inet_ntop(socket.AF_INET,pack('!L',ip))
		self.asn = asn
		self.community = community if community is not None else self.pack()

	def __str__ (self):
		return "target:%s:%d" % (self.ip, self.ip)

	def pack (self):
		ip = socket.inet_pton(socket.AF_INET,self.ip)
		return pack('!BB4sH',0x01,0x02,ip,self.asn)

	@staticmethod
	def unpack (data):
		ip = socket.inet_ntop(socket.AF_INET,data[2:6])
		asn = unpack('!4sH',data[6:8])[0]
		return RouteTargetIPASN(ip,asn,data[:8])

RouteTargetIPASN._known[chr(RouteTargetIPASN.COMMUNITY_TYPE)+chr(RouteTargetIPASN.COMMUNITY_SUBTYPE)] = RouteTargetIPASN


# =============================================================== RouteTargetASN


class RouteTargetASNIP (RouteTarget):
	COMMUNITY_TYPE = 0x00

	# XXX: FIXME: Decide between IP and number and keep one

	def __init__ (self,asn,ip,community=None):
		self.asn = asn
		self.ip = ip if '.' in str(ip) else socket.inet_ntop(socket.AF_INET,pack('!L',ip))
		self.community = community if community is not None else self.pack()

	def __str__ (self):
		return "target:%s:%d" % (str(self.asn), self.ip)

	def pack (self):
		ip = socket.inet_pton(socket.AF_INET,self.ip)
		return pack('!BBH4s',0x00,0x02,self.asn,ip)

	@staticmethod
	def unpack(data):
		asn = unpack('!H',data[2:4])
		ip = socket.inet_ntop(socket.AF_INET,data[4:8])
		return RouteTargetASNIP(ASN(asn),ip,data[:8])

RouteTargetASNIP._known[chr(RouteTargetASNIP.COMMUNITY_TYPE)+chr(RouteTargetASNIP.COMMUNITY_SUBTYPE)] = RouteTargetASNIP
