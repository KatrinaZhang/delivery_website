"""

My system has 3 kinds of user: regular ones, members and administrators.
Choose Register on the main page in order to register as a regular user.
But to login as an administrator and also a member, the user name is admin and the password is Y605j198
/admin is accessible on /profile when you logged in as admin

There are 2 coupon code:
1) USERBEST, win at /rps15 
2) LOVEFOOD, found at /terms

personally I think there are 2 cool stuff:
1) each dish is sold with dip and selected style, which makes the basic unit complicated
2) summary statistics in profile and admin panel, where includes many auto-generated charts via https://quickchart.io/

"""


# python3.10 -m flask run
from flask import Flask,render_template,request,url_for, g,session, redirect,request
from flask_session import Session
from forms import SelectorForm,SearchForm,RegistrationForm,LoginForm,ItemForm,CheckOutForm,HurdleForm,RpsForm,CheckOutForm_2,CouponAddForm
from wtforms import BooleanField,RadioField
from random import choice
from datetime import datetime,date
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from decimal import Decimal
import json
import urllib.request


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "this-is-katrina-secret-key"
app.config ["SESSION_PERMANENT"] = False
app.config ["SESSION_TYPE"] = "filesystem"
Session(app)


def calculate_cart_sum_quantity(cart_dic):
    sum_quantity=0
    for entry_tpl in cart_dic:
        quantity=cart_dic[entry_tpl]
        sum_quantity+=quantity
    return sum_quantity

def calculate_unit_price(entry_tpl):
    # 从database拿到该item信息
    db = get_db ()
    item = db.execute ("""SELECT * FROM items WHERE item_name = ?;""",(entry_tpl[0],)).fetchone()
    print("calculate_unit_price:",entry_tpl[0],item)
    # 拿到s和及其价格
    supplementary_dic={}
    price=item["item_price"]
    if item["supplementary_option"]:
        supplementary_dic=json.loads(item["supplementary_option"])
    for a in entry_tpl[2:]:
        price=price+supplementary_dic[a]
    return price

def getChoices():
    db = get_db()
    listOfCountry=db.execute("""SELECT DISTINCT country FROM winners ORDER BY country""").fetchall()
    choices=[]
    for dicLine in listOfCountry:
        choices.append(dicLine["country"])
    return choices

@app.before_request#This decorator registers a function to run before each request in your Flask application.
def load_logged_in_user():
    g.user = session.get("user_id", None)#Attempts to retrieve "user_id" from the Flask session. If not found, None is used. The result is stored in g.user, making it accessible app-wide during the request.
    # g.sum_quantity = session.get("sum_quantity", None)
    if "cart" in session:
        g.sum_quantity = calculate_cart_sum_quantity(session["cart"])
    g.is_admin = session.get("is_admin", None)

def login_required(view):
    @wraps(view)#原request对应的信息先“包起来”存着 This decorator from the functools module is used to preserve the original view's information, such as its name and docstring.
    def wrapped_view(*args, **kwargs):#Defines the actual wrapper function around the original view. It will check if a user is logged in before allowing access to the protected view.
        if g.user is None:#Checks if g.user is None, indicating no user is logged in.
            return redirect(url_for("login", next=request.url)) #If no user is logged in, redirects the user to the login page, potentially passing the original request URL as a parameter to return to after successful login.
        return view(*args, **kwargs)#对于已经登录的user来讲，把原本“包起来”存着的信息返回If a user is logged in (g.user is not None), executes the original view function with any provided arguments and keyword arguments.
    return wrapped_view#Returns the wrapped view function, effectively replacing the original view with the wrapped version when the decorator is applied.

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.is_admin is None:
            return redirect(url_for("login", next=request.url)) 
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/",methods=["GET","POST"])
def index(): 
    return redirect(url_for("homepage"))

@app.route("/homepage",methods=["GET","POST"])
def homepage():  
    search_form=SearchForm()
    form=SelectorForm()
    db = get_db()
    searched_result=db.execute ("""SELECT * FROM items; """).fetchall()

    # search
    if 'submit_search' in request.form:
        if search_form.validate_on_submit():
            # print("a")
            item_name=search_form.search_bar.data
            db = get_db()
            searched_result=db.execute ("""SELECT * FROM items WHERE item_name LIKE ?; """,('%' + item_name + '%',)).fetchall()
            if searched_result==[]:
                search_form.search_bar.errors.append("the searched item is not in the database")
            return render_template("homepage.html",
                            search_form=search_form,form=form,searched_result=searched_result)        
    
    # sort&filter
    delivery_option=form.delivery_option.data
    is_all_offers=form.is_all_offers.data
    is_member_discount_allowed=form.is_member_discount_allowed.data
    is_coupon_allowed=form.is_coupon_allowed.data
    is_gluten_free=form.is_gluten_free.data
    is_vegan=form.is_vegan.data
    is_vegetarian=form.is_vegetarian.data
    sort_option=form.sort_option.data

    if 'submit_selector' in request.form:
        if form.validate_on_submit():
            query="SELECT * FROM items WHERE 1"
            # print("a",query)
            # delivery section
            if delivery_option == 'Delivery':
                query+=" AND is_delivery_allowed = 1"
            if delivery_option == 'Pickup':
                query+=" AND is_pickup_allowed = 1"
            # print("b",query)
            # offers section
            if is_all_offers:
                query=query
            elif is_member_discount_allowed or is_coupon_allowed:
                query+=" AND (0"
                if is_member_discount_allowed:
                    query+=" OR is_member_discount_allowed = 1"
                if is_coupon_allowed:
                    query+=" OR is_coupon_allowed = 1"
                query+=")"
            # print("c",query)
            # dietary section
            if is_gluten_free or is_vegan or is_vegetarian:
                query+=" AND (0"
                if is_gluten_free:
                    query+=" OR is_gluten_free = 1"
                if is_vegan:
                    query+=" OR is_vegan = 1"
                if is_vegetarian:
                    query+=" OR is_vegetarian = 1"
                query+=")"
            # print("d",query)
            #SORT
            if sort_option=="Price: Low to High":
                query+=" ORDER BY item_price"
            elif sort_option=='Price: High to Low':
                query+=" ORDER BY item_price DESC"
            elif sort_option=='Alphabet: A to Z':
                query+=" ORDER BY item_name"
            elif sort_option=='Alphabet: Z to A':
                query+=" ORDER BY item_name DESC"
            elif sort_option=='The Most Popular':
                query+=" ORDER BY number_of_sold DESC"
            #end
            query+=";"
            print(query)
            db = get_db()
            searched_result=db.execute (query).fetchall()
    return render_template("homepage.html",
                           search_form=search_form,form=form,searched_result=searched_result)    


@app.route("/item/<int:item_id>",methods=["GET","POST"])
def item(item_id):
    
    # 从database拿到该item信息
    db = get_db ()
    item = db.execute ("""SELECT * FROM items WHERE item_id = ?;""",(item_id,)).fetchone()
    # 建立s表
    supplementary_dic={}
    if item["supplementary_option"]:
        supplementary_dic=json.loads(item["supplementary_option"])
    if supplementary_dic:
        print("a")
        for option in supplementary_dic:
            setattr(ItemForm, option, BooleanField(option))
    
    # 建立c表
    compulsory_lst=[]
    if item["compulsory_option"]:
        compulsory_lst=json.loads(item["compulsory_option"])
    if compulsory_lst:
        print("b")
        choice_lst=[]
        for option in compulsory_lst:
            choice_lst.append(option)
        print(choice_lst)
        setattr(ItemForm,"compulsory_option",RadioField('Compulsory Option', choices=choice_lst,default=compulsory_lst[0]))



    form=ItemForm()
    print(form)
    entry_tpl=(item["item_name"],)
    entry_tpl_str=str(entry_tpl)
    price = Decimal(str(item["item_price"]))
    total_price=0
    quantity=0
    is_calculated=False
    # session["entry"] = {}
    if form.validate_on_submit():
        print("c")
        #get c, get s, compute entry tuple
        if compulsory_lst:
            compulsory_option=getattr(form,"compulsory_option").data    
            print(compulsory_option)
        supplementary_tpl=()
        for option in supplementary_dic:
            supplementary_option=getattr(form,option).data
            if supplementary_option:
                supplementary_tpl=supplementary_tpl+(option,)
                #calculate unit price
                price=price+supplementary_dic[option]
            print(f'{option}: {supplementary_option}')
        print(supplementary_tpl)
        #compute entry tuple
        if compulsory_lst:
            entry_tpl+=(compulsory_option,)
        else:
            entry_tpl+=("",)
        entry_tpl+=supplementary_tpl
        # print("1",entry_tpl)
        entry_tpl_str=json.dumps(entry_tpl)
        # print("2",entry_tpl_str)
        #get q
        quantity=Decimal(str(form.quantity.data))
        #calculate total_price
        total_price=price*quantity
        is_calculated=True
        print(entry_tpl_str)

    return render_template ("item.html",form=form,item=item,price=price,quantity=quantity,total_price=total_price,compulsory_lst=compulsory_lst,supplementary_dic=supplementary_dic,entry_tpl=entry_tpl,entry_tpl_str=entry_tpl_str,is_calculated=is_calculated)

@app.route("/cart")
@login_required#################################
def cart():
    if "cart" not in session:
        session["cart"] = {}
    names ={}
    prices = {}
    total_prices = {}
    sub_total=0
    db = get_db()
    print(session["cart"])
    for entry_tpl in session["cart"]:
        item = db.execute("""SELECT * FROM items WHERE item_name = ?;""", (entry_tpl[0],)).fetchone()
        #生成names
        names[entry_tpl]=entry_tpl
        #生成prices
        unit_price=Decimal(str(calculate_unit_price(entry_tpl)))
        prices[entry_tpl] = Decimal(str(unit_price))
        #计算每一行的单价total_price,记录所有单价total_prices，记录扣税前总价格sub_total
        quantity = Decimal(str(session["cart"][entry_tpl]))
        total_price = unit_price * quantity
        total_prices[entry_tpl]=total_price
        sub_total+=total_price
        session["sub_total"]=sub_total

    return render_template ("cart.html", cart=session["cart"], names=names,prices=prices,total_prices=total_prices,sub_total=sub_total)


@app.route("/add_to_cart/<entry_tpl_str>/<int:quantity>")
@login_required#################################
def add_to_cart(entry_tpl_str,quantity):
    print(entry_tpl_str,quantity)
    entry_tpl=tuple(json.loads(entry_tpl_str))
    print(entry_tpl)
    if "cart" not in session:
        session["cart"] = {}
    if entry_tpl not in session["cart"]:
        session["cart"][entry_tpl] = quantity
    else:
        session["cart"][entry_tpl] = session["cart"][entry_tpl]+quantity
    session.modified = True
    # print(session["cart"])
    return redirect(url_for("cart"))


@app.route("/deduct_from_cart/<entry_tpl_str>/<int:quantity>")
@login_required#################################
def deduct_from_cart(entry_tpl_str,quantity):
    print("a")
    entry_tpl=tuple(json.loads(entry_tpl_str))
    if "cart" not in session:
        print("b")
        session["cart"] = {}
    if entry_tpl in session["cart"]:
        print("c")
        if session["cart"][entry_tpl] >= quantity:
            print("d")
            session["cart"][entry_tpl] = session["cart"][entry_tpl]-quantity
    print("e")
    session.modified = True
    # print(session["cart"])
    return redirect(url_for("cart"))


@app.route("/remove_from_cart/<entry_tpl_str>")
@login_required#################################
def remove_from_cart(entry_tpl_str):
    entry_tpl=tuple(json.loads(entry_tpl_str))
    if "cart" not in session:
        session["cart"] = {}
    if entry_tpl in session["cart"]:
        (session["cart"]).pop(entry_tpl)
    session.modified = True
    # print(session["cart"])
    return redirect(url_for("cart"))


@app.route("/checkout",methods=["GET","POST"])
@login_required
def checkout():
    print("a")
    form=CheckOutForm()
    form_2=CheckOutForm_2()

    exchanged=0
    selectedCurrency=""
    sub_total=session["sub_total"]
    org_sub_total=sub_total
    sub_total_1=sub_total
    db = get_db()
    is_member=db.execute ("""SELECT is_member FROM users WHERE user_id = ?;""",(session["user_id"],)).fetchone()
    if is_member is None:
        is_member_str=""
    else:
        is_member_str=is_member['is_member']
    if is_member_str:
        sub_total=Decimal(str(sub_total))*Decimal(str(0.5))
        sub_total_1=sub_total
    rate=0
    coupon_message=""
    is_exchanged=False

    if 'submit_a' in request.form and form.validate_on_submit():
        print("b")
        coupon_code=form.coupon.data
        coupon_amount=db.execute ("""SELECT discount_amount FROM coupons WHERE code = ?;""",(coupon_code,)).fetchone()
        # print("hi")
        # print(coupon_amount,type(coupon_amount))
        if coupon_code=="" or coupon_amount is None:
            if coupon_code=="":
                coupon_message="You don't have a coupon? It hides in the terms!"
            else:
                coupon_message="There is no such coupon"
        else:
            coupon_amount=coupon_amount['discount_amount']
            if sub_total>=coupon_amount+10:
                sub_total=sub_total-coupon_amount
                coupon_message="€"+str(coupon_amount)+" deducted by coupon"
            elif sub_total<10:
                coupon_message="coupon is not allowed under subtotal € 10"
            else:
                sub_total=10
                coupon_message="deducted to minimum amount € 10"
        URL="http://api.exchangeratesapi.io/v1/latest?access_key=4f57a9eda8882e5a44d9d61bdb5d9766"
    # URL="https://api.currencybeacon.com/v1/latest?api_key=5mtbEv1PIk90xGVPAIf70r2gJvWX9bN0"
        response = urllib.request.urlopen(URL)
        data = response.read().decode('utf-8') # Decode bytes to string
        data = json.loads(data) 
        # print("hihi",data,data['rates'])
        selectedCurrency=form.currency.data
        session["selectedCurrency"]=selectedCurrency
        rate=Decimal(str(data['rates'][selectedCurrency]))
        # sub_total
        exchanged=rate*sub_total
        session["sub"]=sub_total
        session["exchanged"]=exchanged
        is_exchanged=True

        
    if 'submit_b' in request.form and form_2.validate_on_submit():
        print("c")
        selectedCurrency=session["selectedCurrency"]
        sub_total=session["sub"]
        exchanged=session["exchanged"]

        order_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        receive_timestamp=form_2.datetime.data.strftime('%Y-%m-%d %H:%M:%S')
        delivery_option=form_2.delivery_option.data
        cart=session["cart"]
        for entry_tpl in cart.keys():
            item_name=entry_tpl[0]
            number_of_sold=db.execute ("""SELECT number_of_sold FROM items WHERE item_name = ?;""",(item_name,)).fetchone()
            number_of_sold_value = number_of_sold['number_of_sold']
            number_of_sold_value=number_of_sold_value+cart[entry_tpl]
            print("number_of_sold_value",number_of_sold_value)
            db.execute('''UPDATE items SET number_of_sold = ? WHERE item_name = ?;''',
                (number_of_sold_value,item_name,))#这里有一个配置问题，我自己安装了python3.10解决了
            db.commit()



        # print(cart)
        # order_content=str(cart)
        cart_str_keys = {json.dumps(key): value for key, value in cart.items()}
        # print(type(cart_str_keys),cart_str_keys)
        order_content = json.dumps(cart_str_keys)
        # print(type(order_content),order_content)
        # cart_str_keys = json.loads(cart_json)
        paid_amount=float(exchanged)
        currency=selectedCurrency
        paid_eur=float(sub_total)
        note=str(form_2.note.data)
        # print(receive_timestamp,delivery_option,note)
        # print((session["user_id"],order_timestamp,receive_timestamp,delivery_option,order_content,paid_amount,currency,paid_eur,note))
        # print((type(session["user_id"]),type(order_timestamp),type(receive_timestamp),type(delivery_option),type(order_content),type(paid_amount),type(currency),type(paid_eur),type(note)))
        db = get_db()
        db.execute("""
        INSERT INTO orders (real_user_id,order_timestamp,receive_timestamp,delivery_option,order_content,paid_amount,currency,paid_eur,note)
        VALUES (?,?,?,?,?,?,?,?,?);""",
            (session["real_user_id"],order_timestamp,receive_timestamp,delivery_option,order_content,paid_amount,currency,paid_eur,note))#这里有一个配置问题，我自己安装了python3.10解决了
        db.commit()
        
        '''
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            order_timestamp DATETIME NOT NULL,
            receive_timestamp DATETIME NOT NULL,
            delivery_option TEXT NOT NULL,
            order_content TEXT NOT NULL,
            paid_amount NUMERIC NOT NULL,
            currency TEXT NOT NULL,
            note TEXT
        '''
        session.pop("cart", None)
        session.pop("exchanged", None)
        session.pop("selectedCurrency", None)
        session.pop("sub", None)
        session.pop("sub_total", None)
        return redirect(url_for('profile'))
    print("d")
    return render_template("checkout.html",is_exchanged=is_exchanged,form_2=form_2,is_member_str=is_member_str,org_sub_total=org_sub_total,sub_total=sub_total,sub_total_1=sub_total_1,form=form,exchanged=exchanged,selectedCurrency=selectedCurrency,rate=rate,coupon_message=coupon_message)

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/register", methods= ["GET", "POST"])
def register():
    form = RegistrationForm()
    form.country.choices=getChoices()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        country=form.country.data
        address=form.address.data

        db = get_db()
        conflict_user = db.execute(
            """SELECT * FROM users
                WHERE user_id = ?;""",(user_id,)).fetchone()
        if conflict_user is not None:
            form.user_id.errors.append("User name already taken")
        else:
            db.execute("""
                INSERT INTO users (user_id, password,country,address)
                VALUES (?, ?,?,?);""",
                  (user_id, generate_password_hash(password),country,address,))#这里有一个配置问题，我自己安装了python3.10解决了
            db.commit()
            return redirect(url_for("login"))
    return render_template ("register.html", form=form)


@app.route("/login", methods= ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute(
            """SELECT * FROM users
            WHERE user_id = ?;""", (user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("No such user name!")
        elif not check_password_hash(user["password"],password):
            form.password.errors.append("Incorrect password!")
        else:
            session.clear()######################################
            session["user_id"] = user_id
            real_user_id = db.execute(
                """SELECT real_user_id FROM users
                WHERE user_id = ?;""", (user_id,)).fetchone()
            # print("session-user-if:"+session["user_id"])
            session["real_user_id"] = int(real_user_id['real_user_id']) 
            # print(type(session["real_user_id"]),session["real_user_id"])
            is_admin = db.execute(
                """SELECT is_admin FROM users
                WHERE user_id = ?;""", (user_id,)).fetchone()
            session["is_admin"] = is_admin['is_admin']
            print("session is_admin ",session["is_admin"])

            next_page = request.args.get("next")
            # print(next_page)
            if not next_page:
                next_page = url_for("homepage")
            return redirect(next_page)
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("homepage"))


@app.route("/profile")
@login_required
def profile():
    user_id=session["user_id"]
    real_user_id= session["real_user_id"]
    db = get_db()
    user = db.execute(
    """SELECT * FROM users
    WHERE real_user_id = ?;""", (real_user_id,)).fetchone()
    orders = db.execute(
    """SELECT * FROM orders
    WHERE real_user_id = ? ORDER BY order_id DESC;""", (real_user_id,)).fetchall()
    orders_dicts = [dict(order) for order in orders]
    sum=0
    for order in orders_dicts:
        cart_json=order["order_content"]
        cart_str_keys = json.loads(cart_json)
        cart = {tuple(json.loads(key)): value for key, value in cart_str_keys.items()}
        order["order_content"]=cart
        sum=sum+order["paid_eur"]
    q_v=0
    q_sum=0
    items = db.execute(
    """SELECT item_name,is_vegetarian FROM items;""").fetchall()
    vegetarian_dic={}
    for item in items:
        vegetarian_dic[item["item_name"]]=item["is_vegetarian"]
    q_order=0
    for order in orders_dicts:
        q_order=q_order+1
        for entry_tpl in order["order_content"]:
            q_sum=q_sum+order["order_content"][entry_tpl]
            if vegetarian_dic[entry_tpl[0]]:
                q_v=q_v+order["order_content"][entry_tpl]
    
    if q_sum !=0:
        r=f"{q_v/q_sum * 100:.2f}%"
        q_n=q_sum-q_v
    else:
        r=None
        q_n=None
    return render_template("profile.html",user=user,orders=orders_dicts,sum=sum,q_sum=q_sum,r=r,label1="Vegetarian",label2="Non-vegetarian",value1=q_v,value2=q_n,q_order=q_order)

@app.route("/change_profile", methods= ["GET", "POST"])
@login_required
def change_profile():
    form=RegistrationForm()
    form.country.choices=getChoices()
    user_id=session["user_id"]
    db = get_db()
    user = db.execute("""SELECT * FROM users WHERE user_id = ?;""", (user_id,)).fetchone()
    if request.method == "GET":
        form.user_id.data=user["user_id"]
        form.address.data=user["address"]
        form.country.default=user["country"]
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        country=form.country.data
        address=form.address.data
        
        real_user_id=user["real_user_id"]
        db = get_db()
        conflict_user = None
        if user_id != session["user_id"]:
            conflict_user = db.execute(
                """SELECT * FROM users
                    WHERE user_id = ?;""",(user_id,)).fetchone()
        if conflict_user is not None:
            form.user_id.errors.append("User name already taken")
        else:
            db.execute('''UPDATE users SET user_id = ?,password=?, country = ?, address = ? WHERE real_user_id = ?;''',
                (user_id, generate_password_hash(password),country,address,real_user_id,))#这里有一个配置问题，我自己安装了python3.10解决了
            db.commit()
            session["user_id"]=user_id
            return redirect(url_for("profile"))
    return render_template("change_profile.html",form=form)

def Score(guessedWord,secret):
    lstScore=[]
    indexG=0
    for charG in guessedWord:
        indexS=0
        for charS in secret:
            if charG==charS:
                if indexG==indexS:
                    lstScore.append((charG,"green"))
                    break
                else:
                    lstScore.append((charG,"yellow"))
                    break
            indexS+=1
        if len(lstScore)<indexG+1:
            lstScore.append((charG,"grey"))
        indexG+=1
    return lstScore

lstWords=[]
fin=open("five_letter_words.txt","r") 
for word in fin:
    word=word.strip()
    lstWords.append(word)
fin.close() 

@app.route("/whurdle",methods=["GET","POST"])
@login_required
def whurdle():
    db = get_db()
    is_member=db.execute ("""SELECT is_member FROM users WHERE user_id = ?;""",(session["user_id"],)).fetchone()
    if is_member is None:
        is_member_str=False
    else:
        is_member_str=is_member['is_member']
    print(is_member_str)
    if is_member_str:
        message="You already win the membership"
        return render_template("hurdle_result.html",message=message,win=1)
    failed_date = db.execute ("""SELECT failed_day FROM users WHERE user_id = ?;""",(session["user_id"],)).fetchone()
    if failed_date is None:
        failed_date_str=0
    else:
        failed_date_str = failed_date['failed_day']  # Get the date string from the row
    # failed_date_obj = datetime.strptime(failed_date_str, '%Y-%m-%d').date()  # Convert to date object
    date_today=date.today()
    print("u",session["user_id"],"f",failed_date_str,"d",date_today)
    if failed_date_str == date_today:
        message="You used up the chance today, comeback tomorrow to win the membership"
        return render_template("hurdle_result.html",message=message,win=0)
    fin=open("theDay.txt","r")
    theDay=fin.read()
    fin.close() 
    # print(theDay)
    now=str(datetime.now().date())
    if now!=theDay:
        theDay=now
        # print(theDay)
        fout=open("theDay.txt","w")
        fout.write(theDay)
        fout.close() 
        secret=choice(lstWords)
        fout=open("secret.txt","w")
        fout.write(secret)
        fout.close() 
    fin=open("secret.txt","r")
    secretOfDay=fin.read()
    fin.close() 
    # print(secretOfDay)
    form=HurdleForm()
    message=""
    scoreDic={}
    if "scoreDic" not in session:
        session["scoreDic"]={}
    # print("0")
    if form.validate_on_submit():
        # print("1")
        guessedWord=form.guessedWord.data
        if guessedWord in lstWords:
            # print("2")
            if guessedWord==secretOfDay:
                # print("a")
                message="Good guess, the secret word is "+guessedWord+", you win the member!"
                db = get_db()
                # print("b")
                db.execute("""
                    UPDATE users SET is_member= 1 WHERE user_id=(?);""",
                    (session["user_id"],))#这里有一个配置问题，我自己安装了python3.10解决了
                # print("c")
                print("good guess",session["user_id"])
                db.commit()
                # session.clear()#######
                return render_template("hurdle_form.html",form=form,message=message,scoreDic=scoreDic)
            else:
                if "numberOfWrongGuesses" not in session:
                    session["numberOfWrongGuesses"]=0
                session["numberOfWrongGuesses"]+=1
                score=Score(guessedWord,secretOfDay)
                session["scoreDic"][session["numberOfWrongGuesses"]]=score
                scoreDic=session["scoreDic"]
                if 1<=session["numberOfWrongGuesses"]<=5:
                    print("hihi")
                    message="Wrong guess, the secret word is not "+guessedWord
                else:
                    message="you run out of 6 guesses, the secret word is actually "+secretOfDay
                    date_today=date.today()
                    # UPDATE  [TABLE] SET [ATTRIBUTES]=200 WHERE playerno=44;
                    db = get_db()
                    db.execute("""
                        UPDATE users SET failed_day= (?) WHERE user_id=(?);""",
                        (date_today, session["user_id"],))#这里有一个配置问题，我自己安装了python3.10解决了
                    db.commit()
                    # session.clear()
                return render_template("hurdle_form.html",form=form,message=message,scoreDic=scoreDic)
        else:
            message="What a poor guess, "+guessedWord+" is not even a word"
            scoreDic=session["scoreDic"]
            return render_template("hurdle_form.html",form=form,message=message,scoreDic=scoreDic)
    message=str(form.guessedWord.errors)
    message=message[1:-1]    
    scoreDic=session["scoreDic"]
    return render_template("hurdle_form.html",form=form,message=message,scoreDic=scoreDic)


@app.route("/rps15",methods=['GET', 'POST'])
def rps15():
    form=RpsForm()
    game=["rock","fire","scissors","snake","human","tree","wolf","sponge","paper","air","water","dragon","devil","lightning","gun"]
    form.rps_choice.choices=game
    player=""
    computer=""
    result=""
    if form.validate_on_submit():
        player=form.rps_choice.data
        computer=choice(game)    
        if game.index(player)-game.index(computer)==0:
            result="It's a draw!"
        if game.index(player)-game.index(computer)>7 or 0<game.index(computer)-game.index(player)<=7:
                result="Player wins! The coupon code is USERBEST"
        if 0<game.index(player)-game.index(computer)<=7 or game.index(computer)-game.index(player)>7:
                result="Computer wins!"
    return render_template("rps.html",form=form,player=player,computer=computer,result=result) 
        

@app.route("/attribution")
def attribution():
    return render_template("attribution.html")

@app.route("/admin")
@login_required
@admin_required
def admin():
    db= get_db ()
    sums = db.execute("""
            SELECT 
                DATE(order_timestamp) as OrderDate, 
                SUM(paid_eur) as TotalPaidEur
            FROM 
                orders
            WHERE 
                order_timestamp >= DATE('now', '-10 days')
            GROUP BY 
                DATE(order_timestamp)
            ORDER BY 
                OrderDate DESC;
            """).fetchall()
    label_lst=[]
    data_lst=[]
    for sum in sums:
        label_lst.append(sum["OrderDate"])
        data_lst.append(sum["TotalPaidEur"])

    top5_user_sums = db.execute("""
        SELECT 
            u.user_id, 
            SUM(o.paid_eur) as TotalPaidEur
        FROM 
            orders o
        JOIN 
            users u ON o.real_user_id = u.real_user_id
        GROUP BY 
            u.user_id
        ORDER BY 
            TotalPaidEur DESC
        LIMIT 5;
    """).fetchall()
    label2_lst=[]
    data2_lst=[] 
    for sum in top5_user_sums:
        label2_lst.append(sum["user_id"])
        data2_lst.append(sum["TotalPaidEur"])



    orders = db.execute(
                """SELECT * FROM orders ORDER BY order_id DESC;""").fetchall()
    orders_dicts = [dict(order) for order in orders]
    sum=0
    for order in orders_dicts:
        cart_json=order["order_content"]
        cart_str_keys = json.loads(cart_json)
        cart = {tuple(json.loads(key)): value for key, value in cart_str_keys.items()}
        order["order_content"]=cart
    item_sale_label=[]
    item_sale_data=[]
    item_sale_dic={}
    entry_sale_label=[]
    entry_sale_data=[]
    entry_sale_dic={}

    for order in orders_dicts:
        for entry_tpl in order["order_content"]:
            entry_sale_dic[entry_tpl]=0
            item_sale_dic[entry_tpl[0]]=0
    for order in orders_dicts:
        for entry_tpl in order["order_content"]:
            entry_sale_dic[entry_tpl]+=order["order_content"][entry_tpl]
            item_sale_dic[entry_tpl[0]]+=order["order_content"][entry_tpl]
    entry_sale_dic = dict(sorted(entry_sale_dic.items(), key=lambda item: item[1], reverse=True)[:3])
    item_sale_dic = dict(sorted(item_sale_dic.items(), key=lambda item: item[1], reverse=True)[:3])
    for entry_tpl in entry_sale_dic:
        entry_sale_label.append(str(entry_tpl))
        entry_sale_data.append(entry_sale_dic[entry_tpl])
    for item_name in item_sale_dic:
        item_sale_label.append(item_name)
        item_sale_data.append(item_sale_dic[item_name])




    return render_template("admin.html",label_lst=label_lst,data_lst=data_lst,label2_lst=label2_lst,data2_lst=data2_lst,label3_lst=item_sale_label,data3_lst=item_sale_data,label4_lst=entry_sale_label,data4_lst=entry_sale_data)

@app.route("/admin/user")
@login_required
@admin_required
def admin_user():
    db= get_db ()
    users = db.execute("""SELECT * FROM users;""").fetchall()
    return render_template("admin_user.html",users=users)

@app.route("/admin/user/delete/<user_id>")
@login_required
@admin_required
def admin_user_delete(user_id):
    db= get_db ()
    db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    db.commit()
    return redirect(url_for("admin_user")) 

@app.route("/admin/user/make_admin/<user_id>")
@login_required
@admin_required
def admin_user_make_admin(user_id):
    db= get_db ()
    db.execute("UPDATE users SET is_admin=1 WHERE user_id = ?", (user_id,))
    db.commit()
    return redirect(url_for("admin_user")) 

@app.route("/admin/user/stepdown_admin/<user_id>")
@login_required
@admin_required
def admin_user_stepdown_admin(user_id):
    db= get_db ()
    db.execute("UPDATE users SET is_admin=0 WHERE user_id = ?", (user_id,))
    db.commit()
    return redirect(url_for("admin_user")) 

@app.route("/admin/user/make_member/<user_id>")
@login_required
@admin_required
def admin_user_make_member(user_id):
    db= get_db ()
    db.execute("UPDATE users SET is_member=1 WHERE user_id = ?", (user_id,))
    db.commit()
    return redirect(url_for("admin_user")) 

@app.route("/admin/user/stepdown_member/<user_id>")
@login_required
@admin_required
def admin_user_stepdown_member(user_id):
    db= get_db ()
    db.execute("UPDATE users SET is_member=0 WHERE user_id = ?", (user_id,))
    db.commit()
    return redirect(url_for("admin_user")) 

@app.route("/admin/product")
@login_required
@admin_required
def admin_product():
    db= get_db ()
    items = db.execute("""SELECT * FROM items;""").fetchall()
    return render_template("admin_product.html",items=items)

@app.route("/admin/coupon")
@login_required
@admin_required
def admin_coupon():
    db= get_db ()
    coupons = db.execute("""SELECT * FROM coupons;""").fetchall()
    return render_template("admin_coupon.html",coupons=coupons)

@app.route("/admin/coupon/add",methods=["GET","POST"])
@login_required
@admin_required
def admin_coupon_add():
    form=CouponAddForm()
    if form.validate_on_submit():
        code=form.code.data
        discount_amount=form.discount_amount.data
        description=form.description.data
        db = get_db()
        conflict_coupon = db.execute(
            """SELECT * FROM coupons
                WHERE code = ?;""",(code,)).fetchone()
        if conflict_coupon is not None:
            form.code.errors.append("Code already taken,choose another one")
        else:
            db.execute("""
                INSERT INTO coupons (code,discount_amount,description)
                VALUES (?,?,?);""",
                  (code,discount_amount,description,))#这里有一个配置问题，我自己安装了python3.10解决了
            db.commit()
            return redirect(url_for("admin_coupon")) 
    return render_template("admin_coupon_add.html",form=form)


