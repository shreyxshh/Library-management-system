import json
import random
import string 
from pathlib import Path
from datetime import datetime

class Library:

    #creating a json database to store info
    database = 'database.json'
    data = {"book" : [], "member" : []}

    #if database exists then adding it in dummy data
    if Path(database).exists():
        with open(database , 'r') as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)

    else:
        with open(database, 'w') as f:
            data = json.dump(data, f, indent = 4)

    @classmethod
    def gen_id(Prefix = 'B'): #default paremeter
        #itll be used to generate random ids for books with prefix = 'B'
        # B - books
        random_id = ""
        for i in range(5):
            random_id += random.choices(string.ascii_letters+string.digits)

        return Prefix + '-' + random_id

    @classmethod
    def save_file(cls):
        with open(Library.database, 'w') as f:
            json.dump(cls.data, f, indent=4, default=str) #formating the dictionary internally
    
    def add_book(self):
        title = input('enter title of the book : ')
        author = input('enter the author of the book : ')
        copies = int(input('enter the no of copies : '))

        book = {
            'id' : Library.gen_id(),
            'title' : title,
            'author' : author,
            'total_copies' : copies,
            'available_copies' : copies,
            'added on' : datetime.now().strftime('%Y--%m-%d, %H:%M:%S') 
            #now() -> brings the current time from the system 
            #strftime('%Y--%m-%d %H:%M:%S') -> string format time - year-month-day, hour:minutes:seconds
        }
        Library.data['book'].append(book)
        Library.save_file()

    def list_book(self):
        #if no books are present  
        if not Library.data['book']: 
            print('no books found!')
            return
        for b in Library.data['book']:
        #looping in all the dictionaries in the (data['book'])
            print(f'{b['id']:12} {b['title'][:24]:25} {b['author'][:19]:20} {b['total_copies']}/{b['available_copies']:>3}')
        

    def add_member(self):
        name = input('Enter your name : ')
        email = input('Enter your email : ')
        member = {
            'id' : Library.gen_id('M'), #'M' means id for members 
            'name' : name,
            'email' : email,
            'borrowed' : [] #list the books which member will borrow
        }
        Library.data['member'].append(member)
        Library.save_file()
        print('Member added successfully!')
    
    def list_member(self):
        if not Library.data['member']:
            print('No members found!')
            return 
        for m in Library.data['member']: #looping the member dictionary
            print(f'{m['id']}, {m['name']}, {m['email']}, ')
            print(f'this guy currently : ', m['borrowed'], 'borrowes')

    def borrow_book(self):
        #getting member and book which he needs
        member_id = input('Enter your id : ').strip()#strips the words after spaces 
        members = [m for m in Library.data['member'] if m['id'] == member_id]
        if not members:
            print('Not such user found!')
            return
        member = members[0]#for ease to use in code

        book_id = input('Enter the book id : ')
        books = [b for b in Library.data['book']if b['id'] == book_id]
        if not books:
            print('No such book found!')
            return
        book = books[0]#for ease to use in code

        if book['available_copies'] <= 0:
            print('NO more book available!')
            return 
        
        #this will contain all the borrowes for any specific member
        borrowed_entry = {
            'book_id' : book['id'],
            'title' : book['title'],
            'borrow_on' : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        member['borrowed'].append(borrowed_entry)
        book['available_copies'] -= 1
        Library.save_file()

    def return_book(self):
        member_id = input('Enter your id : ').strip()
        members = [m for m in Library.data['member'] if m['id'] == member_id]
        if not members:
            print('Not such user found!')
            return
        member = members[0]#for ease to use in code

        if not member['borrowed']:
            print('No borrows are done by the user!')
            return 
        
        print("borrowed books")
        for i, b in enumerate(member['borrowed']):
            print(f"{i+1}. {b['title']} ({b['book_id']})")
        
        try:
            choice = int(input("enter number to return : "))
            selected = member['borrowed'].pop(choice - 1)
        except Exception as err:
            print("invalid value")
        
        books = [bk for bk in Library.data['book'] if bk['id'] == selected['book_id']]
        if books:
            books[0]['available_copies'] += 1
        
        Library.save_file()

hello = Library()

print("="*50) #this will print '=' - 50 times
print("Library Management System")
print("="*50)
print("1. Add Book")
print("2. List Books")
print("3. Add Members")
print("4. List members")
print("5. Borrow Book")
print("6. Return Book")
print("0. Exit the portal")
print("-"*50)

choice = input("Enter task you want to do : ")
while True:

    if choice == 1:
        hello.add_book()
    if choice == 2:
        hello.list_book()
    if choice == 3:
        hello.add_member()
    if choice == 4:
        hello.list_member()
    if choice == 5:
        hello.borrow_book()
    if choice == 6:
        hello.return_book()
    if choice == 0:
        exit(0)
    