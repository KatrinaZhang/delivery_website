from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,BooleanField,RadioField,SelectMultipleField,SubmitField,FieldList, FormField, PasswordField,SelectField,DateTimeField,DateTimeLocalField
from wtforms.validators import InputRequired, EqualTo, NumberRange, Length,DataRequired
from datetime import datetime, timedelta

class SearchForm(FlaskForm):
    search_bar=StringField("",validators=[InputRequired()])
    submit_search=SubmitField("Search")


class SelectorForm(FlaskForm):
    delivery_option = RadioField('', choices=[('Delivery', 'Delivery'), ('Pickup', 'Pickup')],default='Pickup')
    # offerOption=SelectMultipleField('Offers', choices=[('all_offer', 'All Offers'), ('member_discount_allowed', 'Member Discount Allowed'), ('coupon_allowed', 'Coupon Allowed')])
    is_all_offers=BooleanField("All Offers")
    is_member_discount_allowed=BooleanField("Member Discount Allowed")
    is_coupon_allowed=BooleanField("Coupon Allowed")
    is_gluten_free=BooleanField("Gluten Free")
    is_vegan=BooleanField("Vegan Friendly")
    is_vegetarian=BooleanField("Vegetarian")
    sort_option = RadioField('Sort', 
                             choices=[('Price: Low to High', 'Price: Low to High'), ('Price: High to Low', 'Price: High to Low'), 
                                      ('Alphabet: A to Z', 'Alphabet: A to Z'), ('Alphabet: Z to A', 'Alphabet: Z to A'), 
                                      ('The Most Popular', 'The Best Seller')],default='Price: High to Low')
    submit_selector=SubmitField("Submit")

class RegistrationForm(FlaskForm):
    user_id = StringField("User id:", validators= [InputRequired()])
    password = PasswordField("Password:", validators= [InputRequired()])
    password2 = PasswordField("Confirm password:",
                              validators= [InputRequired(), EqualTo("password")])
    address = StringField("Address:", validators= [InputRequired()])
    country = SelectField("Country:",choices=["Netherlands","Ireland"])
    
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField ("User id:",validators= [InputRequired()])
    password = PasswordField("Password:",validators= [InputRequired()])
    submit = SubmitField("Submit")

class ItemForm(FlaskForm):
    # compulsory_option = RadioField('Compulsory Option', choices=[('', ''), ('', '')],default='',validators= [InputRequired()])
    # offerOption=SelectMultipleField('Offers', choices=[('all_offer', 'All Offers'), ('member_discount_allowed', 'Member Discount Allowed'), ('coupon_allowed', 'Coupon Allowed')])
    # is_all_offers=BooleanField("All Offers")
    # is_member_discount_allowed=BooleanField("Member Discount Allowed")
    quantity=IntegerField("Quantity:",validators=[NumberRange(min=1, max=100)],default=1)
    submit = SubmitField("Calculate")

def default_datetime():
    return datetime.now() + timedelta(hours=1)

class CheckOutForm(FlaskForm):
    currency=SelectField("Currency:",choices=["EUR","CNY","GBP","JPY","USD"])
    coupon = StringField("Coupon Code:")
    submit_a = SubmitField("Submit to Calculate")

class CheckOutForm_2(FlaskForm):
    delivery_option = RadioField('', choices=[('Delivery', 'Delivery'), ('Pickup', 'Pickup')],default='Pickup')
    datetime = DateTimeLocalField('Pick a Date and Time', format='%Y-%m-%dT%H:%M', 
                                       validators=[DataRequired()], default=default_datetime())
    note = StringField("Note:")
    agree_to_terms = BooleanField("I agree to the terms and conditions")
    submit_b=SubmitField("Pay")


class HurdleForm(FlaskForm):
    guessedWord = StringField("Make a Guess of 5-letter-word ;)",
                                 validators=[InputRequired(),Length(5, 5)])
    submit=SubmitField("Submit")

class RpsForm(FlaskForm):
    rps_choice = SelectField("Choose your weapon:",choices=["rock","scissors"])
    
    submit = SubmitField("Submit")

class CouponAddForm(FlaskForm):
    code = StringField("code:)",validators=[InputRequired(),Length(8, 8)])
    discount_amount = IntegerField("discount_amount(euro integer):)",validators=[InputRequired(),NumberRange(min=1, max=99)])
    description = StringField("description:")
    submit=SubmitField("Submit")