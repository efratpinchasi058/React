
class User:
    def __init__(self, name, ID, password, countP,wins,word):
        self.name = name
        self.ID = ID
        self.password = password
        self.countP = countP
        self.word = word
        self.wins = wins
    def __str__(self):
        return f"Name: {self.name}; ID number: {self.ID}; Password: {self.password}; Count: {self.countP}; Word: {self.word}; Wins: {self.wins}"

