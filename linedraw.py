import yaml

def main(fn):
	data = yaml.load(file(fn, 'r'))
	scale = 5
	part = 0
	while True:
		minx = miny = 1000000
		maxx = maxy = -1000000
		found = False
		for obj in data['geometry']:
			for elem in obj['shapes']:
				if elem['part'] != part:
					continue
				found = True
				for point in elem['points']:
					point = point['coord']
					minx = min(minx, point[0])
					miny = min(miny, point[1])
					maxx = max(maxx, point[0])
					maxy = max(maxy, point[1])
		if not found:
			break
		offsetx = abs(minx) + 2
		offsety = abs(miny) + 2
		print '<canvas id="cvs%i" width=%i height=%i></canvas><br><br><script>' % (part, (abs(maxx) + abs(minx)) * scale + 4 * scale, (abs(maxy) + abs(miny)) * scale + 4 * scale)
		print 'cvs = document.getElementById("cvs%i");' % part
		print 'ctx = cvs.getContext("2d");'
		print 'ctx.strokeStyle = "black";'
		for obj in data['geometry']:
			for elem in obj['shapes']:
				if elem['part'] != part:
					continue
				points = []
				for sub in elem['points']:
					points.append(sub['coord'])
				print 'ctx.beginPath();'
				print 'ctx.moveTo(%f, %f);' % ((points[-1][0] + offsetx) * scale, (points[-1][1] + offsety) * scale)
				for point in points:
					print 'ctx.lineTo(%f, %f);' % ((point[0] + offsetx) * scale, (point[1] + offsety) * scale)
				print 'ctx.stroke();'
		print '</script>'
		part += 1

if __name__=='__main__':
	import sys
	main(*sys.argv[1:])