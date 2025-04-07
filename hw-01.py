import pickle
from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, timedelta


class BaseView(ABC):
    """Abstract class for representing the user interface"""
    

    @abstractmethod
    def display_contacts(self, contacts):
        """Method for displaying a list of contacts"""
        pass


    @abstractmethod
    def display_commands(self, commands):
        """Method for displaying a list of available commands"""
        pass


    @abstractmethod
    def display_message(self, message):
        """Method for outputting any text"""
        pass


    @abstractmethod
    def display_notes(self, notes):
        """Method for displaying notes."""
        pass


    @abstractmethod
    def get_input(self, entry):
        """Method for receiving user input"""
        pass


class ConsoleView(BaseView):
    """Implementing an interface for the console"""


    def display_contacts(self, contacts):
        """Prints the contact list to the console"""
        if not contacts:
            print("No contacts saved.")
        else:
            print("Contacts: ")
            for record in contacts:
                phone = "; ".join(p.value for p in record.phones)
                birthday = f", birthday: {record.birthday.value.strftime('%d.%m.%Y')}" if record.birthday else ""
                print(f"Name: {record.name.value}, phone: {phone}{birthday}")



    def display_commands(self, commands):
        """Prints a list of available commands to the console"""
        print("\nCommands:")
        for command, desciption in commands.items():
            print(f"{command}: {desciption}")



    def display_message(self, message):
        """Prints a message to the console"""
        print(message)



    def display_notes(self, notes):
        """Prints a list of notes to the console."""
        print("Notes:")
        if not notes:
            print("No notes saved.")
        else:
            for note in notes:
                print(note)



    def get_input(self, entry):
        """Receives user input from the console"""
        return input(entry)
        

class Field:
    """Base class for record fields."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Class for storing the contact name."""
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """A class for storing a phone number."""
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must contain exactly 10 digits")
        super().__init__(value)


class Birthday(Field):
    """A class for storing birthdays."""
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Birthday must be in the format DD.MM.YYYY.")


class Record:
    """Class for storing contact information."""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None


    def add_phone(self, phone):
        """Adds a phone number to a contact."""
        if phone not in [p.value for p in self.phones]:
            self.phones.append(Phone(phone))


    def remove_phone(self, phone):
        """Deletes a phone number from the entry."""
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError('Phone not found')
        

    def edit_phone(self, old_phone, new_phone):
        """Edits the phone number."""
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            phone_obj.value = Phone(new_phone).value
        else:
            raise ValueError("Old phone not found")


    def find_phone(self, phone):
        """Searches for a phone number in a record."""
        for p in self.phones:
            if p.value == phone:
                return p
        return None


    def add_birthday(self, birthday):
        """Adds a birthday to the entry."""
        self.birthday = Birthday(birthday)


    def __str__(self):
        phone = "; ".join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Name: {self.name.value}, phone: {phone}{birthday}"


class AddressBook(UserDict):
    """A class for storing and managing records."""


    def add_record(self, record):
        self.data[record.name.value] = record


    def find(self, name):
        return self.data.get(name)


    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Contact not found")


    def get_upcoming_birthdays(self, days=7):
        """Returns a list of upcoming birthdays."""
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                    upcoming_birthdays.append(f"Name: {record.name.value}, birthday: {birthday_this_year.strftime('%d.%m.%Y')}")

        return upcoming_birthdays
    

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def save_data(book, filename="addressbook.pkl"):
    """Saves data to a file."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """Loads data from a file."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook()


def input_error(func):
    """Decorator to handle input errors and exceptions."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Enter the argument for the command."
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return inner


@input_error
def add_contact(args, book):
    """Adds a new contact or updates an existing one."""
    if len(args) < 2:
        return "Usage: add <name> <phone>"
    name, phone = args[0], args[1]
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact saved."
    else:
        message = "Contact updated."
    record.add_phone(phone)
    save_data(book)
    return message


@input_error
def change_contact(args, book):
    """Changes the phone number for an existing contact."""
    if len(args) < 3:
        return "Usage: change <name> <old_phone> <new_phone>"
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        save_data(book)
        return "Contact updated."
    return "Contact not found."


@input_error
def show_phone(args, book: AddressBook):
    """Displays the phone number for the specified contact."""
    if not args:
        return "Usage: phone <name>"
    name = args[0]
    record = book.find(name)
    if record:
        return f"The phone number for {name} is {', '.join([p.value for p in record.phones])}."
    return "Contact not found."


@input_error
def add_birthday(args, book):
    """Adds a birthday to an existing contact."""
    if len(args) != 2:
        return "Usage: add-birthday <name> <DD.MM.YYYY>"
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    save_data(book)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    """Displays the birthday of the specified contact."""
    if len(args) < 1:
        return "Usage: show-birthday <name>"
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if not record.birthday:
        return f"{name} has no birthday set."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}."


@input_error
def birthday(_, book):
    """Returns a list of upcoming birthdays."""
    upcoming = book.get_upcoming_birthdays()
    return "\n".join(upcoming) if upcoming else "No upcoming birthdays."


def main():
    book = load_data()
    # Створюємо екземпляр ConsoleView
    cv = ConsoleView()

    commands = {
            "hello": "Показати привітання",
            "add": "Додати контакт",
            "change": "Змінити контакт",
            "phone": "Показати номер телефону",
            "all": "Показати всі контакти",
            "delete": "Видалити контакт",
            "add-birthday": "Додати день народження",
            "show-birthday": "Показати день народження",
            "birthdays": "Показати найближчі дні народження",
            "commands": "Показати всі команди",
            "exit/close": "Вийти з програми\n"
        }

    cv.display_message("Welcome to the assistant bot!\n")    
    cv.display_contacts(book.data.values())
    cv.display_commands(commands)

    while True:
        command_input = cv.get_input("Enter a command: ").strip().lower()
        command_parts = command_input.split()
        if not command_parts:
            continue
        command, args = command_parts[0], command_parts[1:]

        if command in ["close", "exit"]:
            save_data(book)
            cv.display_message("Good bye!")
            break
        elif command == "hello":
            cv.display_message("Hello! How can I help you?")
        elif command == "add":
            cv.display_message(add_contact(args, book))
        elif command == "change":
            cv.display_message(change_contact(args, book))
        elif command == "delete" and args:
            try:
                book.delete(args[0])
                save_data(book)
                cv.display_message("Contact deleted.")
            except ValueError as e:
                cv.display_message(str(e))
        elif command == "phone":
            cv.display_message(show_phone(args, book))
        elif command == "all":
            cv.display_contacts(book.data.values())
        elif command == "add-birthday":
            cv.display_message(add_birthday(args, book))
        elif command == "show-birthday":
            cv.display_message(show_birthday(args, book))
        elif command == "birthdays":
            cv.display_message(birthday([], book))
        elif command == "commands":
            cv.display_commands(commands)
        else:
            cv.display_message("Invalid command.")


if __name__ == "__main__":
    main()
