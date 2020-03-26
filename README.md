# shoppero

[![Build Status](https://travis-ci.com/Haj-Res/shoppero.svg?branch=dev)](https://travis-ci.com/Haj-Res/shoppero)

Shoppero is a shopping list management application. It allows you to easily
build and edit your shopping lists, as well as share it with other users on
the internet.

As you use Shoppero, it will build up your item database improving the apps
usability and speed of list creation with item suggestions and field
population.

Shoppero works on two levels. Shopping lists and Items. You can directly add
edit and delete items from your database. Items in your database are suggested
to you while creating a shopping list. Adding any item that does not exists in
your database to your shopping list will will add a base item with those
stats to your database and improve future list creation and editing.

Lists can be created, edited and shared. Each lists consists of a name and a
list of items it contains. Items can be added, edited and deleted from the
list, as well as marked as complete or not complete allowing for ast list
updating. When sharing a list, you can choose the access level of the user by
allowing them to only read the list, read list and mark items as (not) complete
or give them full read and write access.

The site will allow you to scan bar codes from items to add items to your
database or to your shopping lists. If items exists in your database and you
scan it's bar code during the shopping list creation/editing process, it will
populate the item addition form with known data. If no item with the scanned
code exists, just the code field will be populated. 

## Getting started
Create a .env file based on the included .env.example file.
Navigate to folder that contains this file

    docker build .
    docker-compose build
    docker-compose up -d

When the ENVIRONMENT variable in the .env file is set to `production`, the app
will require a higher quality password while registering.