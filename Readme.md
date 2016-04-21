Introduction
============

Pepakura is a very popular piece of software for translating a 3d model into a series of paper elements that can be printed and cut out, to rebuild said model.  Unfortunately, it's Windows-only and the file format has thus far been completely unknown.

I've reverse-engineered the entire file structure, but most of the contents of the data are currently unknown.  Feel free to look through the files I've included, along with the structure, and figure things out.

Pull requests are appreciated!

Scripts
=======

There are a number of scripts included in the repo:

- loader.py - Takes a PDO file and outputs YAML
- unlock.py - Takes a locked PDO file and outputs a (currently broken) unlocked PDO file
- stl.py - Takes a generated YAML file and outputs an STL model (I think this is fully functional?)
- linedraw.py - Takes a generated YAML file and outputs an HTML file that draws the shapes (Partially functional)

Data Types
==========

All content is little endian

- uint8, uint16, uint32 - Unsigned integers of various bit lengths
- wstr - UTF-8 string, prefixed with uint32 length in bytes
	- For "locked" files, the value `key` (inside the first 'if locked') gets subtracted from each byte to "decrypt" it
- float, double - 32-bit and 64-bit floating point values, respectively; standard IEEE 754 floats
- bytes - Simply a C string for convenience
- array - This means there's a uint32 count, then that many children, one indent level in

Structure
=========

- bytes "version 3\n"
- uint32 locked - 4 is unlocked, 5 is locked, all others undefined
- uint32 unknown
- uint32 version
- if locked == 5
	- wstr creator - This will be empty for en-us, "Pepakura Designer 3" elsewhere
	- uint32 key
- wstr locale - Empty for en-us
- wstr codepage
- uint32 unknown
- wstr hexstring
- if locked == 5
	- bool unknown
	- bool unknown
- double[4] unknown
- array Geometry
	- wstr name
	- bool unknown
	- array Vertices
		- double[3] vertex
	- array Shapes
		- uint32 unknown
		- uint32 part - This is the part number in Pepakura
		- double[4] unknown
		- array Points
			- uint32 index - Index into Vertices
			- double[2] coord - 2D coordinate
			- double[2] unknown
			- bool unknown
			- double[3] unknown
			- uint32[3] unknown
			- float[3] edge_color - RGB
	- array Unknown
		- uint32[4] unknown
		- bool[2] unknown
		- uint32 unknown
- array Textures
	- wstr name
	- float[4] unknown
	- float[4] unknown
	- float[4] unknown
	- float[4] unknown
	- bool has_image
	- if has_image
		- uint32 width - In pixels
		- uint32 height - In pixels
		- uint32 compressed_size
		- bytes[compressed_size] image - Zlib deflated image data, RGB, nothing special
- bool some_flag
- if some_flag
	- double unknown
	- bool unknown
	- double[4] unknown
	- array Unknown
		- uint32 unknown
		- double[4] unknown
		- if locked == 5
			- wstr unknown
		- array Unknown
			- bool unknown
			- uint32 unknown
			- bool flag1
			- if flag1
				- uint32[2] unknown
			- bool flag2
			- if flag2
				- uint32[2] unknown
	- array Text - This holds text strings for rendering on the page
		- double[5] unknown
		- uint32[2] unknown
		- wstr font
		- array Lines
			- wstr line
	- array Unknown
		- double[4] unknown
		- uint32[2] unknown
		- uint32 compressed_size
		- bytes[compressed_size] unknown - Zlib deflated
	- array Unknown
		- double[4] unknown
		- uint32[2] unknown
		- uint32 compressed_size
		- bytes[compressed_size] unknown - Zlib deflated
- bool[5] unknown
- uint32 unknown
- bool unknown
- uint32[4] unknown
- uint32 some_flag
- if some_flag == 0x0b
	- double[2] unknown
- uint32[3] unknown
- double[6] unknown
- double[6] unknown
- bool unknown
- double unknown
- if locked == 5
	- wstr unknown
	- wstr unknown
- uint32 eof - Always 0x270F
