import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def initialize_firestore():
    """
    Create database connection
    
    """

    # Setup Google Cloud Key - The json file is obtained by going to 
    # Project Settings, Service Accounts, Create Service Account, and then
    # Generate New Private Key
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = "bucket_list_key.json"

    # Use the application default credentials.  The projectID is obtianed 
    # by going to Project Settings and then General.
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'bucket-list-3ab64',
    })

    # Get reference to database
    db = firestore.client()
    return db

def add_new_item(db):
    '''
    Prompt the user for a new item to add to the inventory database.  The
    item name must be unique (firestore document id).  
    '''

    name = input("Name: ")
    where = input("where: ")
    popular = input("Is it popular (Y/N): ")
    reason = input("reason: ")

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("my_list").document(name).get()
    if result.exists:
        print("Item already exists.")
        return

    # Build a dictionary to hold the contents of the firestore document.
    data = {"where" : where, 
            "popular" : popular,
            "reason" : reason}
    db.collection("my_list").document(name).set(data) 

    # Save this in the log collection in Firestore       
    log_transaction(db, f"Added {name} at the place {where}")

# display list
def show_list(db):
    results = db.collection("my_list").get()

    print("")
    print("Search Results")
    print(f"{'Name':<20}  {'Where':<10}  {'Popular':<10}  {'Reason':<20}")
    for result in results:
        item = result.to_dict()
        print(f"{result.id:<20}  {str(item['where']):<10}  {str(item['popular']):<10}  {str(item['reason']):<20}")
    print() 


#changes where the location is in list
def change_location(db):
    #asks for somthign that already exsists 
    name = input("Item Name: ")
    change_where = input("Where is the location? ")

    # Check for an already existing item by the same name.
    # The document ID must be unique in Firestore.
    result = db.collection("my_list").document(name).get()
    if not result.exists:
        print("Invalid Item Name")
        return

    # Convert data read from the firestore document to a dictionary
    data = result.to_dict()

    # Update the dictionary with the new quanity and then save the 
    # updated dictionary to Firestore.
    data["where"] = change_where
    db.collection("my_list").document(name).set(data)

    # Save this in the log collection in Firestore
    log_transaction(db, f"Added {change_where} {name}")

def log_transaction(db, message):
    '''
    Save a message with current timestamp to the log collection in the
    Firestore database.
    '''
    data = {"message" : message, "timestamp" : firestore.SERVER_TIMESTAMP}
    db.collection("log").add(data)    


def main():
    db = initialize_firestore()
    choice = None
    while choice != "0":
        print("0) exit")
        print("1) add Item to bucket List")
        print("2) show list")
        print("3) Change Location")
        print("4) check something off the list")
        choice = input(f"> ")
        print()

        if choice == "1":
            add_new_item(db)
        elif choice == "2":
            show_list(db)
        elif choice == "3":
            change_location(db)
        
    print("Come back soon!")


if __name__ == "__main__":
    main()