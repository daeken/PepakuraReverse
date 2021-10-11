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
- wstr - string data, prefixed with uint32 length in bytes
	- The value `key` (inside the first 'if format_ver') gets subtracted from each byte to "decrypt" it
	- On all fmtver's, the length in bytes covers the entirety of the string; it is not a count of characters and does not exclude the null terminator.
	- On fmtver <= 5, this data is encoded with the system encoding and is terminated by a zero *which is not encoded with the key*.
	- On fmtver >= 6, this data is UTF-16, and is terminated by an encoded UTF-16 zero.
- float, double - 32-bit and 64-bit floating point values, respectively; standard IEEE 754 floats
- bytes - Simply a C string for convenience
- array - This means there's a uint32 count, then that many children, one indent level in

Structure
=========

- bytes "version 3\n"
- uint32 format_ver - 4 is old unlocked format, 5 and 6 are locked and use slightly different formats.
- uint32 unknown
- uint32 version
- if format_ver > 4
	- wstr creator - This will be empty for en-us, "Pepakura Designer 3" elsewhere
	- uint32 key
- wstr locale - Empty for en-us
- wstr codepage - When this value contains the typo "Sfhit-JIS", force encoding CP932. Otherwise use the system's default multi-byte codepage (probably UTF-8).
- if format_ver > 5
	- uint32 unknown
	- bool unknown	
	- bool unknown
	- wstr hash - MD5 of "%s%d" filled with password & lock type. Empty password & 0 lock type = unlocked.
	- uint lock_type - lock type; 0: none, 1: allow changing textxure, 2: full locking
- else
	- uint lock_type
	- wstr hash - MD5 of "%d%s%d" filled with (face count + edge count), password (empty if unlocked), and lock type (0 if unlocked).
- if format_ver == 5
	- bool unknown
	- bool unknown
- double[4] unknown
- array Geometry
	- wstr name
	- bool unknown
	- array Vertices
		- double[3] vertex
	- array Faces
		- uint32 textureIdx - Index into Textures
		- uint32 part - This is the part number in Pepakura
		- double[4] plane - XYZ normal, perpendicular distance to origin
		- array Points - Both 2D point data, and edge data (edge between current point and next point)
			- uint32 index - Index into Vertices
			- double[2] coord - 2D coordinates
			- double[2] unknown - UV coordinates
			- bool may_need_tab - True if the edge should receive a tab if it is not contiguous with another shape
			- double tab_height - Height of tab in mm
			- double[2] tab_angles - Measured in radians
			- float[3] tab_edge_color - RGB
			- float[3] edge_color - RGB
	- array Edges
		- uint32[2] face_indices - Index into Faces
		- uint32[2] vertex_indices - Index into Vertices
		- bool internal - True if the edge is internal (contiguous w/ other shapes in the same part)
		- bool unknown
		- uint32 unknown
- array Textures
	- wstr name
	- float[4] unknown
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
	- array Parts
		- uint32 geom_index - Index into Geometry
		- double[4] bounds - x/y/w/h
		- if format_ver > 4
			- wstr partName
		- array PartEdge - Connections between faces
			- bool hidden - Whether this partedge is hidden
			- uint32 unknown
			- bool edge_side1_present - Logically always must be true
			- if edge_side1_present
				- uint32 face - Index into Geometry -> Faces
				- uint32 vertexIdx - Index into Geometry -> Vertices. Refers to an edge the same way Points do above.
			- bool edge_side2_present - False if this edge connects to no other face
			- if edge_side2_present
				- uint32 face - Index into Geometry -> Faces
				- uint32 vertexIdx - Index into Geometry -> Vertices
	- array Text - This holds text strings for rendering on the page
		- double x, y, width, height
		- double line_spacing
		- uint32 color - RR GG BB 00, 0xBBGGRR in little-endian
		- uint32 font_size
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
- if format_ver > 5 - Groups
	- array Groups
		- array GroupItems
			- uint32 elementIndex - 0: None, 1 + part index: Part, 1 + part count + text index: Text, likely can also reference images on the page (stored in the compressed data above)
- bool show_tabs;
- bool show_edge_ids
- bool unknown
- bool apply_materials - when 0, all faces are white
- bool ignore_flat_edges
- uint32 flat_edge_threshold - defaults to 175
- bool draw_white_lines_under_dotted_lines
- uint32 mountain_fold_style - 0: solid, 1: none, 3: mountain dotted
- uint32 valley_fold_style - 0: solid, 1: none, 2: valley dotted
- uint32 cut_style - 0: solid, 1: none
- uint32 unknown
- uint32 paper_type - 0: A4, 1: A3, 2: A2, 3: A1, 4: B5, 5: B4, 6: B3, 7: B2, 8: B1, 9: Letter, 10: Legal
- if paper_type == 11
	- double width, height
- uint32 page_orientation - 0 = Portrait, 1 = Landscape
- uint32 side_margin
- uint32 top_margin
- double[6] mountain_dashes - dash-blank spacing for mountain dotted lines
- double[6] valley_dashes - dash-blank spacing for valley dotted lines
- bool outline_padding - makes texture colors bleed out onto blank space
- double unknown
- if fmtver > 4
	- wstr creator
	- wstr description
- uint32 eof - Always 0x270F
