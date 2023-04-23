import hashlib 

kkas = input("ievadi paroli:")
hashed = hashlib.md5(kkas.encode()).hexdigest()
print(hashed)