import hashlib as hl
#converts the dictionary word according to found mapping
def convertWord(word,mapping):
	newWord = ""
	for letter in word:
#		print("original letter",letter)
		newletter = mapping.get(letter)
		if newletter == None:
			newWord = newWord + letter
		else:
#			print("mapped letter",letter)
			newWord = newWord + newletter
#	print("new word",newWord)
	return newWord

#open the shadow to get the last hash
with open('shadow') as f:
	content = f.readlines()
f.close()

targethash = content[-1].split(':')[1][:-1]
print("target hash",targethash)

with open('encrypted.txt') as ef:
	encryptedStuff = ef.readlines()
ef.close()

#print("encrypted",encryptedStuff)

letterCount = {}
for word in encryptedStuff:
#	print("word in file",word)
	for c in word:
#		print("char in word",c)
		# if the letter is not in dictionary yet add it
		if letterCount.get(c,-1) == -1:
			letterCount[c] = 1
		else:
			letterCount[c] = letterCount[c] + 1
#remove the space
letterCount.pop(" ")
letterCount.pop(".")
letterCount.pop(",")
print("letter count",letterCount)

#sort the counts
sortedPair = []
for pair in letterCount.items():
	sortedPair.append(pair)
sortedPair.sort(key=lambda tup: tup[1], reverse=True)
print("\n",sortedPair)

#create list accroding to the most common letters in English
# I played around with this list in order to decrypt the file
commonLetList = ["t","e","a","i","o","n","h","l","d","s","r","u",
"c","m","b","y","w","f","p","g","k","v","z","q","x","j"]
print("list of common letters \n",commonLetList)


mappedDict = {}
pos = 0
print("\nmapped letters")
for pair in sortedPair:
	mappedDict[pair[0]] = commonLetList[pos]
	pos = pos + 1
print(mappedDict)

#add in back the '.' ',' and space
mappedDict['.'] = '.'
mappedDict[','] = ','
mappedDict[' '] = ' '
print("\nnew dict",mappedDict)


#use the mapped dictionary to map the letters from the text file
newText = " "
for word in encryptedStuff:
	newWord = " "
	for c in word:
#		print("c is",c)
		if c != ' ' or c != ',' or c != '.':
			newWord = newWord + mappedDict[c]
		else:
			newWord = newWord + c
	newText = newText + newWord
print("\nfinal\n",newText)

#take out if need to write to file again
#write to file the decryption
#file = open("plaintext.txt","w+")
#file.write(newText)


#reverse the mapping to encrypt
revMap = {}
for key,value in mappedDict.items():
	revMap[value] = key
print("rev map",revMap)


with open('dictionary.txt') as dictionary:
	words = dictionary.readlines()
dictionary.close()
passwordList = []
for word in words:
	word = word[:-1]
#	print("\nword before",word)
	#convert word according to mapping
	mappedWord = convertWord(word,revMap)
#	print("mapped word",mappedWord)
	mappedhash = hl.md5(mappedWord.encode()).hexdigest()
	if mappedhash == targethash:
		passwordList.append((targethash,word))
#print("len targethash",len(targethash))
print(passwordList)
