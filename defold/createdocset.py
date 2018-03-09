#!/usr/bin/env python3
from urllib.request import urlopen
from subprocess import call

import os
import re
import sys
import json
import shutil
import urllib
import sqlite3
import zipfile
import string

# path definitions
REF_PATH = "ref"
JSON_PATH = "json"

# filenames definitions
DOC_ZIP = "refdoc.zip"
DB_FILE = "docset.dsidx"

def get():
	sys.stdout.write("Downloading...")
	info_file = urlopen("http://d.defold.com/stable/info.json")
	info = json.loads(urlopen("http://d.defold.com/stable/info.json").read())
	info_file.close()
	os.remove(DOC_ZIP) if os.path.exists(DOC_ZIP) else None
	urllib.request.urlretrieve("http://d.defold.com/archive/" + info["sha1"] + "/engine/share/ref-doc.zip", DOC_ZIP)

def cleanup():
	sys.stdout.write("Cleaning...")
	shutil.rmtree(JSON_PATH) if os.path.exists(JSON_PATH) else None
	os.remove(DOC_ZIP) if os.path.exists(DOC_ZIP) else None
	os.remove(DB_FILE) if os.path.exists(DB_FILE) else None

def unzip():
	sys.stdout.write("Unpacking...")
	shutil.rmtree(JSON_PATH) if os.path.exists(JSON_PATH) else None
	with zipfile.ZipFile(DOC_ZIP) as zf: zf.extractall(JSON_PATH)

def create():
	sys.stdout.write("Creating...")

	# create all paths
	shutil.rmtree(REF_PATH) if os.path.exists(REF_PATH) else None
	os.makedirs(REF_PATH)

	# create sqlite db
	with sqlite3.connect("docset.dsidx") as db:

		cursor = db.cursor()
		try: cursor.execute('DROP TABLE searchIndex;')
		except: pass

		cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
		# make sure duplicates are ignored
		# cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

		index_html = ""

		for root, dir, files in os.walk(JSON_PATH):

			for file in files:

				with open(os.path.join(root, file), "r") as fh:

					if file.endswith(".json"):
						class_name = file.replace("_doc.json", "")
						class_path = class_name + ".html"
						class_doc = ""

						parsed_json = json.load(fh)
						info = parsed_json["info"]
						class_doc = class_doc + "<h1>" + info["name"] + "</h1>\n"
						class_doc = class_doc + "<p>" + info["description"] + "</p>\n"
						index_html = index_html + "<a class='index' href='ref/" + class_path + "'>" + class_name + "</a>" + info["brief"] + "</br>"

						for element in parsed_json["elements"]:
							function_name = element["name"]

							if function_name != "":
								entry_type = "Function"

								if element["type"] == "VARIABLE":
									entry_type = "Variable"

								elif element["type"] == "MESSAGE":
									entry_type = "Command"

								elif element["type"] == "PROPERTY":
									entry_type = "Property"

								elif element["type"] == "MACRO":
									entry_type = "Macro"

								elif element["type"] == "TYPEDEF":
									entry_type = "Type"

								elif element["type"] == "ENUM":
									entry_type = "Enum"

								function_path = class_path + "#" + function_name
								class_doc = class_doc + "<h1><a name='//apple_ref/cpp/" + entry_type + "/" + function_name + "' class='dashAnchor'></a><a class='entry' name='" + function_name + "'>" + function_name + ("()" if entry_type == "Function" else "") + "</a></h1>"
								class_doc = class_doc + "<div class='brief'>" + element["brief"] + "</div>"

								if element["description"] != "":
									class_doc = class_doc + "<p>" + element["description"] + "</p>"

								if element.get("note", "") != "":
									class_doc = class_doc + "<p>Note: " + element["note"] + "</p>"

								if len(element["parameters"]) > 0:
									class_doc = class_doc + "<h3>PARAMETERS</h3>"
									class_doc = class_doc + "<div class='params'>"

									for parameter in element["parameters"]:
										class_doc = class_doc + "<p class='param'>" + parameter["name"] + parameter["doc"] + "</p>"

									class_doc = class_doc + "</div>"

								if len(element["members"]) > 0:
									class_doc = class_doc + "<h3>MEMBERS</h3>"
									class_doc = class_doc + "<div class='params'>"

									for member in element["members"]:
										class_doc = class_doc + "<p class='param'>" + member["name"] + " - "  + member["doc"] + "</p>"

									class_doc = class_doc + "</div>"

								if len(element["returnvalues"]) > 0:
									class_doc = class_doc + "<h3>RETURN</h3>"
									class_doc = class_doc + "<div class='return'>"

									for returnvalue in element["returnvalues"]:
										class_doc = class_doc + "<p>" + returnvalue["name"] + " - " + returnvalue["doc"] + "</p>"

									class_doc = class_doc + "</div>"

								if element["examples"] != "":
									class_doc = class_doc + "<h3>EXAMPLES</h3>"
									class_doc = class_doc + "<div class='examples'>"
									class_doc = class_doc + "<p>" + element["examples"] + "</p>"
									class_doc = class_doc + "</div>"

								class_doc = class_doc + "<hr/>"
								cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (function_name, entry_type, "ref/" + function_path))

						with open(os.path.join(REF_PATH, class_path), "w") as out:
							out.write("<html><head><link rel='stylesheet' type='text/css' href='../defold.css'></head><body>")
							out.write("<div class='nav'>")
							out.write("<a class='chevron' href='../index.html'><img src='../svg/chevron-left.svg' alt='Home'></a>")
							out.write("</div>")
							out.write(class_doc.replace("<a href=\"/", "<a href=\"http://www.defold.com/"))
							out.write("</body></html>")

						cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (class_name, 'Module', "ref/" + class_path))

		with open(os.path.join(".", "index.html"), "w") as out:
			out.write("<html><head><link rel='stylesheet' type='text/css' href='defold.css'></head><body>")
			out.write(index_html)
			out.write("</body></html>")

get()
unzip()
create()
cleanup()
print("DONE!")
