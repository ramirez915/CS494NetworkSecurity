import hashlib
import itertools

#get the different combinations of salt numbers 0-9 for 5 spaces
def getSaltVals():
	combos = list(itertools.product(range(10),repeat = 5))
	combosAsStr = []
	for i in combos:
		combo = str(i[0]) + str(i[1]) + str(i[2]) + str(i[3]) + str(i[4])
		combosAsStr.append(combo)
	return combosAsStr

#---------------------
#how pass is found could be done differently did it like this
#with different funcitons
#---------------------
#checks the hash of the current word and target hash depending on the hashtype passed in
def getPassFromHashWithSalt(word,targetHash,saltDict,hashType):
	for salt in saltDict:
		saltWord = word + salt
		if hashType == "md5":
			md5hash = hashlib.md5(saltWord.encode()).hexdigest()
			if str(md5hash) == targetHash:
				return (targetHash,saltWord)
		elif hashType == "sha1":
			sha1Hash = hashlib.sha1(saltWord.encode()).hexdigest()
			if str(sha1Hash) == targetHash:
				return (targetHash,saltWord)
		elif hashType == "sha256":
			sha256hash = hashlib.sha256(saltWord.encode()).hexdigest()
			if str(sha256hash) == targetHash:
				return (targetHash,saltWord)
		elif hashType == "sha512":
			sha512hash = hashlib.sha512(saltWord.encode()).hexdigest()
			if str(sha512hash) == targetHash:
				return (targetHash,sha512hash)
#		print(len(md5hash))	#len is 32
#		print(len(sha1hash))	#len is 40
#		print(len(sha256hash))	#len is 64
#		print(len(sha384hash))	#len is 96
#		print(len(sha512hash))	#len is 128

	#if nothing was found return "none"
	return (targetHash,"none")

def convertWordsToLeet(dictContent):
	leetWordList = []
	for word in dictContent:
		if 'A' or 'a' in word:
			word = word.replace('A','4')
			word = word.replace('a','4')
			print(word)
		if 'B' or 'b' in word:
			word = word.replace('B',"13")
			word = word.replace('b',"13")
			print(word)
		if 'E' or 'e' in word:
			word = word.replace('E','3')
			word = word.replace('e','3')
			print(word)
		if 'G' or 'g' in word:
			word = word.replace('G','6')
			word = word.replace('g','9')
			print(word)
		if 'O' or 'o' in word:
			word = word.replace('O','0')
			word = word.replace('o','0')
			print(word)
		if 'S' or 's' in word:
			word = word.replace('S', '5')
			word = word.replace('s','5')
			print(word)
		if 'T' in word:
			word = word.replace('T','7')
			print(word)
		if 'Z' or 'z' in word:
			word = word.replace('Z','2')
			word = word.replace('z','2')
			print(word)
		if 'l' in word:
			word = word.replace('l','1')
			print(word)
		if 'I' or 'i' in word:
			word = word.replace('I', '1')
			word = word.replace('i','1')
			print(word)
		leetWordList.append(word)
	return leetWordList


def cipherCrack(word,targetHash):
	letterList = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o',
	'p','q','r','s','t','u','v','w','x','y','z']
	letterPos = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7,"i":8,"j":9,"k":10,"l":11,"m":12,
	"n":13,"o":14,"p":15,"q":16,"r":17,"s":18,"t":19,"u":20,"v":21,"w":22,"x":23,"y":24,"z":25}
	numberList = ['0','1','2','3','4','5','6','7','8','9']
	numberPos = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9}
	for i in range(26):
		newWord = ""
		for letter in word:
			lp = letterPos.get(letter)
			#case for lowercase letter
			if letter.islower() == True:
				pos = letterPos.get(letter)
				newPos = i + int(pos)
				#print("newpos is:",newPos)
				if newPos > 25:
					adjustedPos = newPos - 25 - 1
				#	print("adjusted pos",adjustedPos)
					newLetter = letterList[adjustedPos]
				else:
					newLetter = letterList[newPos]
				newWord = newWord + newLetter
			#case for uppercase letter
			if letter.isupper() == True:
				#print("UPPERCASE")
				lowercaseLetter = letter.lower()
				pos = letterPos.get(lowercaseLetter)
				newPos = i + pos
				#print("newPos is:",newPos)
				if newPos > 25:
					adjustedPos = newPos - 25 - 1
					#print("adjusted pos",adjustedPos)
					newLetter = letterList[adjustedPos].upper()
					newWord = newWord + newLetter
				else:
					newLetter = letterList[newPos].upper()
					newWord = newWord + newLetter
#		print(word)
#		print(newWord)
		if len(targetHash) == 32:
			resulthash = hashlib.md5(newWord.encode()).hexdigest()
			if resulthash == targetHash:
				return (targetHash,word)
		elif len(targetHash) == 40:
			resulthash = hashlib.sha1(newWord.encode()).hexdigest()
			if resulthash == targetHash:
				return (targetHash,word)
		elif len(targetHash) == 64:
			resulthash = hashlib.sha256(newWord.encode()).hexdigest()
			if resulthash == targetHash:
				return (targetHash,word)
		elif len(targetHash) == 128:
			resulthash = hashlib.sha512(newWord.encode()).hexdigest()
			if resulthash == targetHash:
				return (targetHash,word)
	return (targetHash,"none")





#------------------------------------------------------------START OF SCRIPT HERE

#open shadow file
with open('shadow') as f:
	content = f.readlines()
f.close()
hashedPassList = []
#get the hash by itself from file and put in a list
for line in content:
	wantedLine = line.split(':')[1][:-1]	#taking out the \n at the end
#	print(wantedLine)
	hashedPassList.append(wantedLine)

#for i in hashedPassList:
#	print(i)
#	print(len(i))

saltValsList = getSaltVals()		#will contain all the salt numbers

#get dictionary contents
with open('dictionary.txt') as dict:
	dictContent = dict.readlines()
dict.close()

#print("dictionary len")
#print(len(dictContent))

passList = []

#MAKE LIST WITHOUT LAST ONE
hashesWOLast = []
for x in range(6):
	hashesWOLast.append(hashedPassList[x])
print("hash list without the last one")
print(hashesWOLast)

#get the words in the dictionary in leet speak
leetWords = convertWordsToLeet(dictContent)

#check first by hashing regular word for all
for hash in hashesWOLast:
	for word in dictContent:
		word = word[:-1]
		if len(hash) == 32:
			regularhash = hashlib.md5(word.encode()).hexdigest()
			if hash == regularhash:
				passList.append((hash,word))
		elif len(hash) == 40:
			regularhash = hashlib.sha1(word.encode()).hexdigest()
			if hash == regularhash:
				passList.append((hash,word))
		elif len(hash) == 64:
			regularhash = hashlib.sha256(word.encode()).hexdigest()
			if hash == regularhash:
				passList.append((hash,word))
		elif len(hash) == 128:
			regularhash = hashlib.sha512(word.encode()).hexdigest()
			if hash == regularhash:
				passList.append((hash,word))

#remove the hashes for the passwords found
for pair in passList:
	if pair[0] in hashesWOLast:
		hashesWOLast.remove(pair[0])
print("reduced hash list")
print(hashesWOLast)
#check the left over ones now using the leet speak
for hash in hashesWOLast:
	for word in leetWords:
		word = word[:-1]
		if len(hash) == 32:
			leethash = hashlib.md5(word.encode()).hexdigest()
			if hash == leethash:
				passList.append((hash,word))
		elif len(hash) == 40:
			leethash = hashlib.sha1(word.encode()).hexdigest()
			if hash == leethash:
				passList.append((hash,word))
		elif len(hash) == 64:
			leethash = hashlib.sha256(word.encode()).hexdigest()
			if hash == leethash:
				passList.append((hash,word))
		elif len(hash) == 128:
			leethash = hashlib.sha512(word.encode()).hexdigest()
			if hash == leethash:
				passList.append((hash,word))

#remove the hashes found
for pair in passList:
	if pair[0] in hashesWOLast:
		hashesWOLast.remove(pair[0])

print("reduced list again")
print(hashesWOLast)

#check with cipher
for hash in hashesWOLast:
	for word in dictContent:
		word = word[:-1]
		result = cipherCrack(word,hash)
		if result[1] != "none":
			passList.append(result)

#reduce list once more to get the last one needed for the salt check
for pair in passList:
	if pair[0] in hashesWOLast:
		hashesWOLast.remove(pair[0])


#this will get the password with the salt
#takes a while but works

for hash in hashesWOLast:
	for word in dictContent:
		word = word[:-1]
		if len(hash) == 32:
			result = getPassFromHashWithSalt(word,hash,saltsValsList,"md5")
			if result[1] != "none":
				passList.append(result)
		elif len(hash) == 40:
			result = getPassFromHashWithSalt(word,hash,saltValsList,"sha1")
			if result[1] != "none":
				passList.append(result)
		elif len(hash) == 64:
			result = getPassFromHashWithSalt(word,hash,saltValsList,"sha256")
			if result[1] != "none":
				passList.append(result)
		elif len(hash) == 128:
			result = getPassFromHashWithSalt(word,hash,saltValsList,"sha512")
			if result[1] != "none":
				passList.append(result)

print("passlist",passList)
for i in passList:
	print(i)
