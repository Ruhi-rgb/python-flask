import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
print("Connecting to database..")

def main():

f = open("book.csv")
reader = csv.reader(f)
print("reading csv..")
count=0
for isbn, title, author, year in reader:
    if year.isdigit():
        #insert value in database
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn":isbn, "title":title, "author":author, "year":year})
        print(f"Added book {title} by {author}, ISBN{isbn}")
        count=count+1
    else:
        print(f"Did not add{title}. Year is not a number")
print(f"added book {title} to database")
        db.commit()
        print(f"{count} books successfully imported.")
    if __name__ == "__main__":
        main()
