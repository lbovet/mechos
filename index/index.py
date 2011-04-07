import unicodedata
import re

def strip_accents(input):
   return  unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')

s = dict()
ig = set(("mp3", "and", "is", "the", "out", "best", "back", "from", "you", "vous", "love", "very", "was", "with", "me", "your", "what", "for", "toi", "moi"))

a = list()
n = 0

for i in open('itunes.txt', 'r'):
	line = strip_accents(unicode(i.lower(), 'utf-8'))
	line = re.sub(" +", " ", line)
	string_tokens = re.split("[^a-z^0-9^'^ ]+", line)
	all_tokens = set()
	for t in string_tokens:
		t = re.sub("^[0-9]+", "", t)
		t = re.sub("[^a-z^0-9'^ ]", "", t).strip() 
		if len(t) > 2:
			w_tokens = list(re.split("([ '])", t))
			w_tokens.reverse()
			suffix = ""
			for j in w_tokens:
				suffix = (j + suffix)
				if not re.match("[ ']", j):				
					all_tokens.add(suffix)
		
#	word_tokens = set(re.split("[^a-z^0-9^']+", line))
#	for t in word_tokens:
#		for nt in t.split("'"):
#			all_tokens.add(nt)
	for t in all_tokens:
		m = re.sub("[^a-z^0-9'^ ]", "", t).strip()
		if len(m) > 2 and not m in ig:
			if not s.has_key(m):
				l = list((n,))
				s[m]=l			
			else:
				l = s[m]	
				l.append(n)			
		
	n=n+1
	a.append(i.strip())	

for i in sorted(s):
	if len(s[i]) > 100:
		print i +" : "+ str(len(s[i]))

#print sorted(s)
print len(s)

class Entry:
	children = None
	ids = None

	def __repr__(self):
		return repr(self.children)

root = Entry()
root.children = {}

for k,v in s.iteritems():
	p = root
	for c in k:
		if not p.children.has_key(c):
			f = Entry()	
			f.children = {}		
			p.children[c] = f
		else:
			f = p.children[c]
		p = f
	p.ids = v

#print repr(root)

import pickle
f = open("index.idx", "w")
pickle.dump(root, f)
f.close()

def all_ids(item):
	e=item
	if e.ids:
		r = e.ids
	else:
		r = list()	
	for v in e.children.values():
		r.extend(all_ids(v))
	return r

def search(item, s):
	
	if item.children.has_key(s[0]):
		e = item.children[s[0]]		

		if len(s) == 1:
			r = all_ids(e)
		else:
			r = search(e, s[1:])
	else:
		return []

	return sorted(set(r))				

import sys

while True:
	sys.stdout.write("> ")
	l = sys.stdin.readline()
	if l:
		for i in search(root, l.strip()):
			print a[i]
	else:
		break



