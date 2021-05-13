# Food Stock
#### Video Demo: https://youtu.be/JPu4Ztlmj_8
#### Description:
App for pantry management
## Problem Statement:
In 2020 Covid 19 hit the globe prompting the world to stockpile on food and essentials to the point of insanity.

In 2021, many households see a problem in which they are unable to easily monitor the current situation in their pantries

This Web App aims to allow households to monitor the situation in their pantries by showing the expiry dates as well as amount
to reduce food waste and ensure food security.

## The design(database):
Each family is given an id.

Users must first register a family only adding members once logged in only.

This was choosen over just registering individually to ensure simplicity in user_id as different families can have users of the same name.

In addition we can also easily display the family food supply by just querying the unique family_id.


## The design(login):
The login page was designed to be as simple as possible for design.

We also implemented a reset function for the forgetful who can easily reset their password via 2FA auth.

This ensures only reset can be done by intended individual.

Login does not need 2FA as it is too troublesome and information in app is not too sensitive.


## The design(console):
A table shows all brought products
Once used, the products can be removed with the click of a button

I did not include a text bar in the same page to reduce clutter


## The design(history):
This allows for users to track past purchases allowing them to make more responsible choices ahead

Users can observe what they have purchased before


## Future improvements:
- Transition to a mobile app
- Use celery to automate expiry date notification to users
- Migration to postgresdb

## Main logic of the app:
Application.py has 10 routes:
- login
- console
- brought
- delete
- history
- logout
- register
- reset
- reset_confirmed
- add

## Login:
Login checks database for the credentials entered by user running SQL queries to ensure that the user in question exists

## Console:
Console gets all important data needed by user such as item name and the expiry date, displaying the data in the table using jinja 2 for loop

Data presented is only that with same family_id as user

There is a ate button which is assigned an item_id

When pressed, it submits the item_id to the delete route

## Delete:
Delete route uses sql to delete entry in items database, before redirecting user back to console

## Brought:
When item is brought, a sql query is run adding to both items and history databases.

Quantity is updated using a for loop

## History:
Displays all items that have been brought by family of user.

## Register:
Register new family only

Adds to database of existing users

## Reset:
Prompts user to enter family and user id.

Email is sent via flask mail to user of code

## Reset_confirmed:
Allows user to enter their verification code and new password

## Add:
Adds new members in family by updating the users table by SQL


























