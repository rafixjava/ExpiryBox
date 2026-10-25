# App 1: Accounts
#
# The class diagram's USER (pk, name, email, password, createdAt) is covered by
# Django's built-in User model (django.contrib.auth.models.User):
#
#   diagram       ->  built-in User field
#   pk            ->  id
#   name          ->  first_name   (labelled "Name" on our forms)
#   email         ->  email
#   password      ->  password     (stored as a secure hash, never plain text)
#   createdAt     ->  date_joined
#
# Because the built-in model already has everything we need, this app does
# not define a model of its own. Users log in with their username.
