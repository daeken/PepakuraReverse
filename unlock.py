import math, sys
import struct, zlib
from PIL import Image
import codecs

codepages = {
	'Sfhit-JIS' : 'shift_jis', 
}

class ParseBuffer(object):
	def __init__(self, data):
		self.data = data
		self.i = 0
		self.key = None
		self.codepage = None
		self.outdata = ''
		self.ignore = False

	@property
	def end(self):
		return self.i == len(self.data)
	def peek(self, size):
		return self.data[self.i:self.i+size]
	def read(self, size):
		self.i += size
		cdata = self.data[self.i-size:self.i]
		if not self.ignore:
			self.outdata += cdata
		return cdata
	def write(self, data, sized=False):
		if sized:
			self.outdata += struct.pack('I', len(data))
		self.outdata += data
	def unpack(self, fmt):
		fmt = '<' + fmt
		ret = struct.unpack(fmt, self.read(struct.calcsize(fmt)))
		if len(ret) == 1:
			return ret[0]
		return ret

	@property
	def byte(self):
		return self.unpack('B')
	def bytes(self, size):
		return map(ord, self.read(size))
	@property
	def bool(self):
		return {0:False, 1:True}[self.byte] # Throws an exception if the byte is non 0/1
	@property
	def int16(self):
		return self.unpack('h')
	@property
	def uint16(self):
		return self.unpack('H')
	@property
	def int32(self):
		return self.unpack('i')
	@property
	def uint32(self):
		return self.unpack('I')
	@property
	def float(self):
		return self.unpack('f')
	@property
	def double(self):
		return self.unpack('d')
	def str(self, size=None):
		return self.read(self.uint32 if size is None else size).split('\0', 1)[0]
	@property
	def wstr(self):
		if self.key is not None:
			#saved = self.ignore
			#self.ignore = True
			data = ''.join(chr((ord(x) - self.key + 256) % 256) for x in self.str())
			#self.write(data, sized=True)
			#self.ignore = saved
		else:
			data = self.str()
		if self.codepage is None or self.codepage not in codepages:
			return data

		return codecs.decode(data, codepages[self.codepage]).encode('utf-8')

def arr(*x):
	return '[%s]' % (', '.join(map(repr, x)))

def parse(data):
	buf = ParseBuffer(data)
	assert buf.str(10) == 'version 3\n'
	#buf.ignore = True
	locked = buf.uint32 # 4 == unlocked, 5 == locked
	#buf.write('\x04\0\0\0')
	#buf.ignore = False
	print 'locked:', locked
	print 'unk1:', buf.uint32
	print 'version:', buf.uint32
	print
	
	if locked == 5:
		#buf.ignore = True
		print 'unk2:', buf.wstr # Empty for en-us
		buf.key = buf.uint32
		print 'key:', buf.key
		print
		#buf.ignore = False

	print 'locale:', buf.wstr # Should always be empty for en-us, according to the codepage bug
	codepage = buf.wstr
	print 'codepage:', buf.codepage
	buf.ignore = True
	print 'unk3:', buf.uint32
	buf.write('\0\0\0\0')
	buf.ignore = False
	print 'hexstring:', buf.wstr
	print

	if locked == 5:
		#buf.ignore = True
		print 'unk4:', buf.bool
		print 'unk5:', buf.bool
		print
		#buf.ignore = False

	print 'unk6:', arr(buf.double, buf.double, buf.double, buf.double)
	print 'unk7:'
	for i in xrange(buf.uint32):
		print '  - name:', buf.wstr
		print '    unk8:', buf.bool
		print '    unk9:'
		for j in xrange(buf.uint32):
			print '      -', arr(buf.double, buf.double, buf.double)
		print
		print '    unk10:'
		for j in xrange(buf.uint32):
			print '      - unk11:', arr(buf.uint32, buf.uint32, buf.double, buf.double, buf.double, buf.double)
			print '        unk12:'
			for k in xrange(buf.uint32):
				print '          - unk13:', arr(buf.uint32, buf.double, buf.double, buf.double, buf.double)
				print '            unk14:', buf.bool
				print '            unk15:', arr(buf.double, buf.double, buf.double)
				print '            unk16:', arr(buf.uint32, buf.uint32, buf.uint32, buf.float, buf.float, buf.float) # last three contain RGB values (x / 256)
			print
		print
		print '    unk17:'
		for j in xrange(buf.uint32):
			print '      -', arr(buf.uint32, buf.uint32, buf.uint32, buf.uint32, buf.bool, buf.bool, buf.uint32)
		print
	print

	print 'textures:'
	for i in xrange(buf.uint32):
		print '  - unk19:', buf.wstr
		print '    unk20:', arr(buf.float, buf.float, buf.float, buf.float)
		print '    unk21:', arr(buf.float, buf.float, buf.float, buf.float)
		print '    unk22:', arr(buf.float, buf.float, buf.float, buf.float)
		print '    unk23:', arr(buf.float, buf.float, buf.float, buf.float)
		print '    unk24:', arr(buf.float, buf.float, buf.float, buf.float)
		print '    unk25:', buf.bool
		w, h = buf.uint32, buf.uint32
		print '    width:', w
		print '    height:', h
		cbuf = buf.read(buf.uint32)
		dbuf = zlib.decompress(cbuf)
		im = Image.frombuffer('RGB', (w, h), dbuf)
		#im.save('texture-%i.png' % i)
		print
	print

	if buf.bool:
		print 'unk26:', buf.double
		print 'unk27:', buf.bool
		print 'unk28:', arr(buf.double, buf.double, buf.double, buf.double)
		
		print 'unk29:'
		for i in xrange(buf.uint32):
			print '  - unk30:', arr(buf.uint32, buf.double, buf.double, buf.double, buf.double)
			if locked == 5:
				#buf.ignore = True
				print '    unk31:', buf.wstr
				#buf.ignore = False
			print '    unk32:'
			for j in xrange(buf.uint32):
				print '      - unk33:', arr(buf.bool, buf.uint32)
				if buf.bool:
					print '        unk34:', arr(buf.uint32, buf.uint32)
				if buf.bool:
					print '        unk35:', arr(buf.uint32, buf.uint32)
			print
		print

		print 'text_display:'
		for i in xrange(buf.uint32):
			print '  - unk37:', arr(buf.double, buf.double, buf.double, buf.double, buf.double)
			print '    unk38:', arr(buf.uint32, buf.uint32)
			print '    font:', buf.wstr
			print '    lines:'
			for j in xrange(buf.uint32):
				print '      -', buf.wstr
			print
		
		print 'unk39:'
		for i in xrange(buf.uint32):
			print '  - unk40:', arr(buf.double, buf.double, buf.double, buf.double)
			print '    unk41:', arr(buf.uint32, buf.uint32)
			cbuf = buf.read(buf.uint32)
			dbuf = zlib.decompress(cbuf)
			print '    decompressed_size:', len(dbuf)
			print
		print


		print 'unk42:'
		for i in xrange(buf.uint32):
			print '  - unk43:', arr(buf.double, buf.double, buf.double, buf.double)
			print '    unk44:', arr(buf.uint32, buf.uint32)
			cbuf = buf.read(buf.uint32)
			dbuf = zlib.decompress(cbuf)
			print '    decompressed_size:', len(dbuf)
			print

	print 'unk45:', arr(buf.bool, buf.bool, buf.bool, buf.bool, buf.bool)
	print 'unk46:', arr(buf.uint32, buf.bool, buf.uint32, buf.uint32, buf.uint32, buf.uint32)

	unk = buf.uint32
	if unk == 0x0B:
		print 'unk47:', arr(buf.double, buf.double)
	else:
		print 'unk48:', unk
	print

	print 'unk49:', arr(buf.uint32, buf.uint32, buf.uint32)
	print 'unk50:', arr(buf.double, buf.double, buf.double, buf.double, buf.double, buf.double)
	print 'unk51:', arr(buf.double, buf.double, buf.double, buf.double, buf.double, buf.double)

	print 'unk52:', arr(buf.bool, buf.double)
	if locked == 5:
		#buf.ignore = True
		print 'unk53:', '"' + buf.wstr + '"'
		print 'unk54:', '"' + buf.wstr + '"'
		#buf.ignore = False

	assert buf.uint32 == 0x270f
	assert buf.end
	return buf.outdata

if __name__=='__main__':
	data = file(sys.argv[1], 'r').read()
	out = parse(data)
	file(sys.argv[2], 'wb').write(out)
