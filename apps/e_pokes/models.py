from __future__ import unicode_literals
import re
import bcrypt
from django.db import models
from datetime import datetime, timedelta

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
NAME_REGEX = re.compile(r'^[A-Za-z]\w+$')

class UserManager(models.Manager):
    def validate_login(self, post_data):
        errors = []
        # check DB for post_data['email']
        if len(self.filter(email=post_data['email'])) > 0:
            # check this user's password
            user = self.filter(email=post_data['email'])[0]
            if not bcrypt.checkpw(post_data['password'].encode(), user.password.encode()):
                errors.append('email/password incorrect')
        else:
            errors.append('email/password incorrect')

        if errors:
            return errors
        return user

    def validate_registration(self, post_data):
        errors = []
        
        # check length of name fields
        if len(post_data['first_name']) < 2: 
            errors.append("first_name fields must be at least 3 characters")

        if len(post_data['alias']) < 2:
            errors.append("alias must be at least 3 characters")

        #check valid date of birth
        if post_data['birthday'] != '':
            date= datetime.strptime(post_data['birthday'], "%Y-%m-%d")
            now= datetime.now()
            if date > now:
              errors.append ("birthday can not be after today")
        else:
          errors.append('birthday cannot be empty')

        # check length of password
        if len(post_data['password']) < 8:
            errors.append("password must be at least 8 characters")

        # check first and last name for letter characters            
        if not re.match(NAME_REGEX, post_data['first_name']):
            errors.append('First name fields must be letter characters only')
        
         #check valid date of birth
        if post_data['birthday'] != '':
            date= datetime.strptime(post_data['birthday'], "%Y-%m-%d")
            now= datetime.now()
            if date > now:
              errors.append ("birthday can not be after today")
        else:
          errors.append('birthday cannot be empty')

        # check email with REGEX
        if not re.match(EMAIL_REGEX, post_data['email']):
            errors.append("invalid email")

        # check uniqueness of email
        if len(User.objects.filter(email=post_data['email'])) > 0:
            errors.append("email already in use")

        # check password == password_confirm
        if post_data['password'] != post_data['password_confirm']:
            errors.append("passwords do not match")


        if not errors:
            hashed = bcrypt.hashpw((post_data['password'].encode()), bcrypt.gensalt(5))

            new_user = self.create(
                first_name=post_data['first_name'],
                alias=post_data['alias'],
                birthday=post_data['birthday'],
                email=post_data['email'],
                password=hashed
            )
            return new_user
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)
    birthday = models.DateField(auto_now_add=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    objects = UserManager()
    def __str__(self):
        return self.email

class Poke(models.Model):
    sender= models.ForeignKey(User, related_name="sends_the_poke")
    receiver = models.ForeignKey(User, related_name="receives_the_poke")
    pokes = models.IntegerField(null=True)
    created_at = models.DateField(null=True)
