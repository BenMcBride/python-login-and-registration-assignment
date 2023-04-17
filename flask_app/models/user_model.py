from flask_app.config.mysqlconnection import connectToMySQL 
from flask_bcrypt import Bcrypt
from flask_app import app
from flask import flash, request
import re
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    DB = "users_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

# class methods

    @classmethod
    def save(cls, data ): 
        query = """
            INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) 
            VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW() );
            """
        data = {
            **data,
            'password': bcrypt.generate_password_hash(data['password'])
            }
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result

    @classmethod
    def get_one(cls, data):
        data = {
            'id': data
            }
        query = """
            SELECT *
            FROM users
            WHERE id = %(id)s;
            """
        result = connectToMySQL(cls.DB).query_db(query, data)
        return cls( result[0] )

# static methods

    @staticmethod
    def validate_user(user):
        query = """
            SELECT *
            FROM users
            WHERE email = %(email)s;
            """
        result = connectToMySQL('users_schema').query_db(query,user)
        is_valid = True
        if len(user['first_name']) < 2:
            is_valid = False
            flash("First name must be at least 2 characters.")
        if not user['first_name'].isalpha():
            is_valid = False
            flash("First name can contain letters only.")
        if len(user['last_name']) < 2:
            is_valid = False
            flash("Last name must be at least 2 characters.")
        if not user['last_name'].isalpha():
            is_valid = False
            flash("Last name can contain letters only.")
        if len(user['email']) == 0:
            is_valid = False
            flash("Email is a required for registration.")
        if not EMAIL_REGEX.match(user['email']): 
            is_valid = False
            flash("Invalid email address!")
        if result:
            is_valid = False
            flash("Email already registered.")
        if len(user['password']) < 2:
            is_valid = False
            flash("Password must be at least 8 characters")
        if user['confirm_password'] != user['password']:
            is_valid = False
            flash("Password fields do not match")
        return is_valid

    @staticmethod
    def validate_login(data):
        print(data)
        query = """
            SELECT * 
            FROM users 
            WHERE email = %(email)s;
            """
        result = connectToMySQL('users_schema').query_db(query, data)
        user_id = User(result[0])
        if not EMAIL_REGEX.match(data['email']):
            flash('Email/Password not valid')
            return False
        if len(data['login_password']) < 8:
            flash('Email/Password not valid')
            return False
        if not result:
            flash('Email/Password not valid')
            return False
        if not bcrypt.check_password_hash(user_id.password, data['login_password']):
            flash('Email/Password not valid')
            return False
        return user_id