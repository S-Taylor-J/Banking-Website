# Admin and users login from the same route.

# Admin Account Details:
#       Username : admin   
#       password : admin1

# User Info to test website
# all user passwords are 123456789

# userName  : GeorgeGreen
# userId    : 156364
# cardNumber: 4600199748364425

# userName  : PeterPurple
# userId    : 952967
# cardNumber: 8742974552998954

# userName  : RubyRed
# userId    : 483877
# cardNumber: 3355317602240567

from flask import Flask, render_template, redirect, url_for, session, g, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from database import get_db, close_db
from forms import (
    registerForm,
    transactionForm,
    filterForm,
    loginForm,
    settingsForm,
    adminSenderInfo,
    adminReceiverInfo, 
)
from datetime import datetime
from flask_session import Session
from functools import wraps
import requests
import math

app = Flask(__name__)
app.config["SECRET_KEY"] = "hiuasdfihu23!!asdf2"

# Session Configurations
# Set session to not permanent
# Set session to store data to filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database Configuration.
# Calls the close_db function at the end of every route
app.teardown_appcontext(close_db)

# API configurations
# Used to get the current exchange rate
API_KEY = "UFRmmqpoPfb5SrFC8lwpfnFOfWyHMgBy"
API_URL = "https://api.currencybeacon.com/v1/convert"


def convert_currency(amount, from_currency, to_currency):

    try:
        params = {
            "api_key": API_KEY,
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
        }
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get("value", "Conversion Error")
        return "API Error"
    except:
        return 0

# Called at the start of Route
# Used to verify user session is still valid
@app.before_request
def load_logged_in_user():
    g.user = session.get("userId", None)


@app.before_request
def kickFrozenAccount():
    db = get_db()

    if g.user is not None:
        admin = db.execute(
            """
            SELECT *
            FROM adminAccounts
            WHERE userId = ?
            """,
            (g.user,),
        ).fetchone()
        if admin is None:
            account = db.execute(
                """
                SELECT *
                FROM users
                WHERE userId = ?
                """,
                (g.user,),
            ).fetchone()
            if account["freezeAccount"] == 1:
                session.clear()


# Redirect user to login page if they aren't logged in
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        db = get_db()
        admin = db.execute(
            """
            SELECT *
            FROM adminAccounts
            WHERE userId = ?""",
            (g.user,),
        ).fetchone()
        if admin is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return render_template("user/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    errorMessage = ""
    form = loginForm()
    if form.validate_on_submit():
        userName = form.userName.data
        password = form.password.data
        db = get_db()
        try:
            # Check if login credentials are a user and valid
            validUser = db.execute(
                """
                SELECT * 
                FROM users 
                WHERE userName = ?""",
                (userName,),
            ).fetchone()
        except Exception as e:
            return render_template("user/login.html", form=form)
        try:
            # Check if login credentials are an admin and valid
            adminAccount = db.execute(
                """
                SELECT *
                FROM adminAccounts
                WHERE userName = ?
                """,
                (userName,),
            ).fetchone()
        except Exception as e:
            return render_template("user/login.html", form=form)

        if adminAccount is not None and check_password_hash(
            adminAccount["password"], password
        ):
            session.clear()
            session["userId"] = adminAccount["userId"]
            session.modified = True
            return redirect(url_for("adminDashboard"))
        elif validUser is None:
            form.userName.errors.append("Invalid Username. Username doesn't exist")
        elif not check_password_hash(validUser["password"], password):
            form.password.errors.append("Incorrect password.")
        else:
            if validUser["freezeAccount"] == 0:
                session.clear()
                session["userId"] = validUser["userId"]
                session.modified = True
                return redirect(url_for("dashboard"))
            else:
                errorMessage = "Your Account has been Frozen"
                return render_template(
                    "user/login.html", form=form, errorMessage=errorMessage
                )
    return render_template("user/login.html", form=form, errorMessage=errorMessage)


# Clear user login session
@app.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = registerForm()
    if form.validate_on_submit():
        try:
            # Generate a unique 6-digit ID
            userId = idNum()
            # Get data from the form
            firstName = form.firstName.data
            lastName = form.lastName.data
            userName = form.userName.data
            dob = form.dob.data
            phoneNum = form.phoneNum.data
            email = form.email.data
            currency = form.currency.data
            homeAddress = form.homeAddress.data
            city = form.city.data
            county = form.county.data
            postalCode = form.postalCode.data
            country = form.country.data
            createdAccount = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            password = form.password.data

            db = get_db()
            # Check if the username, email and phone number are already in use
            validUserName = db.execute(
                """
                SELECT *
                FROM users 
                WHERE userName = ?""",
                (userName,),
            ).fetchone()
            validEmail = db.execute(
                """
                SELECT *
                FROM users 
                WHERE email = ?""",
                (email,),
            ).fetchone()
            validPhoneNum = db.execute(
                """
                SELECT *
                FROM users 
                WHERE phoneNum = ?""",
                (phoneNum,),
            ).fetchone()

            if validUserName is not None:
                form.userName.errors.append("Invalid Username. Username already exist")
            elif validEmail is not None:
                form.email.errors.append("Invalid email. Email already used.")
            elif validPhoneNum is not None:
                form.phoneNum.errors.append(
                    "Invalid phone number. Phone number already used."
                )
            else:

                # Insert user into the database
                db.execute(
                    """ 
                    INSERT INTO users (
                    userID, 
                    firstName, 
                    lastName, 
                    userName, 
                    dob, 
                    phoneNum, 
                    email, 
                    currency, 
                    homeAddress, 
                    city, 
                    county, 
                    postalCode, 
                    country,
                    createdAccount, 
                    password) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        userId,
                        firstName,
                        lastName,
                        userName,
                        dob,
                        phoneNum,
                        email,
                        currency,
                        homeAddress,
                        city,
                        county,
                        postalCode,
                        country,
                        createdAccount,
                        generate_password_hash(password),
                    ),
                )
                db.commit()

                # Create Debit Card for user
                cardNumber = generateCard()
                eDate = expiryDate()
                cvc = cvcNum()
                balance = convert_currency(10000, "EUR", currency)
                pin = cardPin()
                db.execute(
                    """
                    INSERT INTO debitAccount(
                        userId, 
                        cardNumber, 
                        expiryDate, 
                        CVC, 
                        balance, 
                        pin, 
                        currency
                        )
                    VALUES (?,?,?,?,?,?,?)""",
                    (userId, cardNumber, eDate, cvc, balance, pin, currency),
                )
                db.commit()

                return redirect(url_for("login"))

        except Exception as e:
            return render_template("user/register.html", form=form)

    return render_template("user/register.html", form=form)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    averageAmounts = 0
    db = get_db()

    # Get user information
    user = db.execute(
        """
        SELECT * 
        FROM users 
        WHERE userId = ?
        """,
        (g.user,),
    ).fetchone()
    
    # Get user account information
    userAccount = db.execute(
        """
        SELECT * 
        FROM debitAccount 
        WHERE userId = ?""",
        (g.user,),
    ).fetchone()

    cardNumber = str(userAccount["cardNumber"])
    endCardNumber = "****" + cardNumber[-4:]

    transactions = db.execute(
        """
    SELECT t.*, u1.firstName AS receiverName, u1.lastName AS receiverLastName, u2.firstName AS senderName, u2.lastName as senderLastName
    FROM transactions t
    JOIN users u1 ON u1.userId = t.receiverId 
    JOIN users u2 ON u2.userId = t.senderId  
    WHERE t.senderId = ? OR t.receiverId = ?
    ORDER BY transactionDate DESC
    LIMIT 3
    """,
        (g.user, g.user),
    ).fetchall()
    
    transferIn = db.execute("""
        SELECT *
        FROM transactions 
        WHERE receiverId = ?""", (g.user, )
        ).fetchall()
    transferOut = db.execute("""
        SELECT *
        FROM transactions 
        WHERE senderId = ?""", (g.user, )
        ).fetchall()
    countryStats = db.execute("""
        SELECT destinationCountry, COUNT(*) AS count
        FROM transactions
        GROUP BY destinationCountry
        ORDER BY count DESC
        LIMIT 1;"""
        ).fetchone()
    averageIn = db.execute("""
        SELECT *
        FROM transactions
        WHERE receiverId = ?
        """,(g.user,)).fetchall()
    averageOut = db.execute("""
        SELECT *
        FROM transactions
        WHERE senderId = ?
        """,(g.user,)).fetchall()

    userStats = db.execute(   """
    SELECT firstName, lastName, t.receiverId, COUNT(*) AS count
    FROM transactions AS t JOIN users AS u
    ON t.receiverId = u.userId
    WHERE t.senderId = ?
    GROUP BY t.receiverId
    ORDER BY count DESC
    LIMIT 1;
    """,(g.user,)
    ).fetchone()
    
    moneyIn = "{:,.2f}".format(dbCalc(transferIn, user, False))
    numInTransfers = len(transferIn)
        
    moneyOut = "{:,.2f}".format(dbCalc(transferOut, user, False))
    numOutTransfers = len(transferOut)
    
    inAmount = "{:,.2f}".format(dbCalc(averageIn,user,True))
    outAmount = "{:,.2f}".format(dbCalc(averageOut,user, True))

        
    return render_template(
        "user/dashboard.html",
        user=user,
        userAccount=userAccount,
        transactions=transactions,
        endCardNumber=endCardNumber,
        moneyIn=moneyIn,
        numInTransfers=numInTransfers,
        moneyOut=moneyOut,
        numOutTransfers=numOutTransfers,
        transferOut=transferOut,
        countryStats=countryStats,
        inAmount=inAmount,
        outAmount=outAmount,
        userStats=userStats
    )

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    # Progress bar
    step = 1
    session["step"] = step
    message = ""
    form = transactionForm()

    if form.validate_on_submit():
        # Get data from form
        userName = form.userName.data
        destinationCountry = form.destinationCountry.data
        userId = form.userId.data
        amount = form.amount.data
        currency = form.currency.data
        description = form.description.data
        additionalInfo = form.additionalInfo.data
        recipientEmail = form.recipientEmail.data

        if "transaction" not in session:
            session["transaction"] = {}

        # Store transaction Information in a session
        session["transaction"]["userName"] = userName
        session["transaction"]["destinationCountry"] = destinationCountry
        session["transaction"]["description"] = description
        session["transaction"]["userId"] = userId
        session["transaction"]["amount"] = amount
        session["transaction"]["toCurrency"] = currency
        session["transaction"]["description"] = description
        session["transaction"]["additionalInfo"] = additionalInfo
        session["transaction"]["recipientEmail"] = recipientEmail
        session.modified = True

        db = get_db()
        validUser = db.execute(
            """
                SELECT *
                FROM users
                WHERE userName = ? AND userId = ?
            """,
            (userName, userId),
        ).fetchone()
        senderAccount = db.execute(
            """
            SELECT * 
            FROM debitAccount 
            WHERE userId = ?
            """,
            (g.user,),
        ).fetchone()

        amountExc = convert_currency(amount, senderAccount["currency"],currency )
        
        
        if amountExc <= 0:
            message = "Invalid amount"
            return render_template(
                "user/transfer.html", form=form, message=message, step=session["step"]
            )
        if validUser is None:
            message = "Invalid username or userID"
            return render_template(
                "user/transfer.html", form=form, message=message, step=session["step"]
            )
        if validUser["freezeAccount"] == 1:
            message = "User account is frozen and cannot receive funds"
            return render_template(
                "user/transfer.html", form=form, message=message, step=session["step"]
            )
        if senderAccount["balance"] < amount:
            message = "You do not have the funds to support this transaction"
            return render_template(
                "user/transfer.html", form=form, message=message, step=session["step"]
            )
        else:
            session["step"] += 1
            currentTime = datetime.now()
            session["transaction"]["fromCurrency"] = senderAccount["currency"]
            fee = convert_currency(amount,currency , senderAccount["currency"]) *0.05
            print(fee)
            if fee < 5:
                fee = 5
            session["transaction"]["fee"] = fee

            currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
            session["transaction"]["transactionDate"] = currentTime

            return render_template(
                "user/transfer.html",
                form=form,
                transaction=session["transaction"],
                validUser=validUser,
                senderAccount=senderAccount,
                step=session["step"],
            )
    return render_template(
        "user/transfer.html", form=form, message=message, step=session["step"]
    )

@app.route("/confirmTransfer", methods=["GET", "POST"])
@login_required
def confirmTransfer():
    try:
        userName = session["transaction"]["userName"]
        destinationCountry = session["transaction"]["destinationCountry"]
        userId = session["transaction"]["userId"]
        amount = float(session["transaction"]["amount"])
        toCurrency = session["transaction"]["toCurrency"]
        description = session["transaction"]["description"]
        additionalInfo = session["transaction"]["additionalInfo"]
        recipientEmail = session["transaction"]["recipientEmail"]
        fee = session["transaction"]["fee"]
        transactionDate = datetime.now()
        session["step"] += 1
    except:        
        session.pop("transaction", None)
        return redirect(url_for("transfer"))
    
    db = get_db()
    senderAccount = db.execute(
        """
            SELECT * 
            FROM debitAccount 
            WHERE userId = ?
            """,
        (g.user,),
    ).fetchone()
    receiverAccount = db.execute(
        """
            SELECT * 
            FROM debitAccount 
            WHERE userId = ?
            """,
        (userId,),
    ).fetchone()
    senderBalance = float(senderAccount["balance"])
    receiverBalance = float(receiverAccount["balance"])
    fee = float(session["transaction"]["fee"])
    fee = convert_currency(fee, senderAccount["currency"], toCurrency)
    print("toCurrency", fee)

    if receiverAccount["currency"] != toCurrency:
        rAmount = convert_currency(
            amount,
            toCurrency,
            receiverAccount["currency"],
        )
        receiverBalance += rAmount
    else:
        receiverBalance += amount

    if senderAccount["currency"] != toCurrency:
        amount += fee
        sAmount = convert_currency(amount, toCurrency, senderAccount["currency"])
        senderBalance -= sAmount

    else:
        amount += fee
        senderBalance -= amount

    db.execute(
        """
            UPDATE debitAccount
            SET balance = ?
            WHERE userId = ?
            """,
        (receiverBalance, userId),
    )
    db.commit()
    db.execute(
        """
            UPDATE debitAccount
            SET balance = ?
            WHERE userId = ?
            """,
        (senderBalance, g.user),
    )
    db.commit()

    db.execute(
        """
            INSERT INTO transactions
            (
                senderId, 
                receiverId,
                recipientName,
                destinationCountry,
                amount, 
                currency,
                descriptionText,
                additionalInfo,
                recipientEmail,
                transactionDate
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
        (
            g.user,
            userId,
            userName,
            destinationCountry,
            amount,
            toCurrency,
            description,
            additionalInfo,
            recipientEmail,
            transactionDate,
        ),
    )
    db.commit()
    amount = convert_currency(amount, toCurrency, "EUR")
    db.execute(
        """
            INSERT INTO adminTransactions
            (
                senderId, 
                receiverId,
                recipientName,
                destinationCountry,
                amount, 
                currency,
                descriptionText,
                additionalInfo,
                recipientEmail,
                transactionDate
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
        (
            g.user,
            userId,
            userName,
            destinationCountry,
            amount,
            toCurrency,
            description,
            additionalInfo,
            recipientEmail,
            transactionDate,
        ),
    )
    db.commit()
    session.pop("transaction")
    session.modified = True
    return redirect ("confirmTransfer")


@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():
    page = request.args.get("page", 1, type=int)
    limit = 5
    offset = (page - 1) * limit
    
    form = filterForm()
    parameter = [g.user, g.user]

    db = get_db()
    user = db.execute("""SELECT * FROM users WHERE userId = ?""", (g.user,)).fetchone()
    query = """
    SELECT t.*, u1.firstName AS receiverName, u1.userName AS receiverUsername, u2.firstName AS senderName, u2.userName AS senderUsername
    FROM transactions t
    JOIN users u1 ON u1.userId = t.receiverId 
    JOIN users u2 ON u2.userId = t.senderId  
    WHERE (t.senderId = ? OR t.receiverId = ?)
    """    
    
    if form.submit():
        minAmount = form.minAmount.data
        maxAmount = form.maxAmount.data
        currency = form.currency.data
        recipientId = form.recipientId.data
        country = form.country.data
        currency = form.currency.data
        startDate = form.startDate.data
        endDate = form.endDate.data
        amountAsc = form.amountAsc.data
        amountDec = form.amountDec.data
        countryAsc = form.countryAsc.data
        countryDec = form.countryDec.data
        dateAsc = form.dateAsc.data
        dateDes = form.dateDes.data

        if minAmount is None or minAmount == "":
            minAmount = 0
        if maxAmount is None or maxAmount == "":
            maxAmount = 9999999999999999

        query += "AND amount BETWEEN ? AND ?"

        parameter.append(minAmount)
        parameter.append(maxAmount)

        if currency and currency != " ":
            query += " AND t.currency = ?"
            parameter.append(currency)

        if country and country != " ":
            query += " AND t.destinationCountry = ?"
            parameter.append(country)

        if recipientId:
            query += " AND senderId = ?"
            parameter.append(recipientId)

        if startDate:
            query += " AND transactionDate >= ?"
            parameter.append(startDate)

        if endDate:
            query += " AND transactionDate <= ?"
            parameter.append(endDate)

        orderParameters = []

        if amountAsc:
            orderParameters.append("amount ASC")

        if amountDec:
            orderParameters.append("amount DESC")

        if countryAsc:
            orderParameters.append("destinationCountry ASC")

        elif countryDec:
            orderParameters.append("destinationCountry DESC")

        if dateAsc:
            orderParameters.append("transactionDate ASC")

        elif dateDes:
            orderParameters.append("transactionDate DESC")

        if orderParameters:
            orderParameters = "ORDER BY " + ", ".join(orderParameters)
            query += orderParameters
            
        query += " LIMIT ? OFFSET ?"
        parameter.append(limit)
        parameter.append(offset)
        
        transactions = db.execute(query, parameter).fetchall()
        
        pageAmount = db.execute("""
            SELECT COUNT(id) AS totalPages
            FROM transactions t
            JOIN users u1 ON u1.userId = t.receiverId 
            JOIN users u2 ON u2.userId = t.senderId  
            WHERE (t.senderId = ? OR t.receiverId = ?)
            """,(g.user,g.user)).fetchone()
        
        if pageAmount['totalPages'] > limit:
            totalPages = math.ceil(pageAmount["totalPages"] / limit)
        else: 
            totalPages = 1 
            
        return render_template(
            "user/transaction.html",
            transactions=transactions,
            user=user,
            form=form,
            totalPages=totalPages,
            page=page
            
        )

    
    return render_template(
        "user/transaction.html",
        transactions=transactions,
        user=user,
        form=form,
    )


@app.route("/card", methods=["GET", "POST"])
@login_required
def card():
    db = get_db()

    user = db.execute(
        """
        SELECT * 
        FROM users 
        WHERE userId = ?""",
        (g.user,),
    ).fetchone()
    userAccount = db.execute(
        """
        SELECT * 
        FROM debitAccount 
        WHERE userId = ?""",
        (g.user,),
    ).fetchone()
    
    userBalance = userAccount["balance"]
    balance = "{:,.2f}".format(userBalance)
    cardExpiryDate = userAccount["expiryDate"]
    expiryDate = cardExpiryDate.strftime("%d/%m")
    cardNumber = str(userAccount["cardNumber"])
    part1, part2, part3, part4 = [
        cardNumber[:4],
        cardNumber[4:8],
        cardNumber[8:12],
        cardNumber[12:],
    ]
    cardNumber = part1 + " " + part2 + " " + part3 + " " + part4

    return render_template(
        "user/card.html",
        user=user,
        userAccount=userAccount,
        balance=balance,
        expiryDate=expiryDate,
        cardNumber=cardNumber,
    )


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = settingsForm()

    db = get_db()
    user = db.execute(
        """
        SELECT * 
        FROM users 
        WHERE userId = ?""",
        (g.user,),
    ).fetchone()

    if request.method == "GET":
        form.firstName.data = user["firstName"]
        form.lastName.data = user["lastName"]
        form.userName.data = user["userName"]
        form.dob.data = user["dob"]
        form.phoneNum.data = user["phoneNum"]
        form.email.data = user["email"]
        form.currency.data = user["currency"]
        form.homeAddress.data = user["homeAddress"]
        form.city.data = user["city"]
        form.county.data = user["county"]
        form.postalCode.data = user["postalCode"]
        form.country.data = user["country"]

    if form.validate_on_submit():
        firstName = form.firstName.data
        lastName = form.lastName.data
        userName = form.userName.data
        dob = form.dob.data
        phoneNum = form.phoneNum.data
        email = form.email.data
        currency = form.currency.data
        homeAddress = form.homeAddress.data
        city = form.city.data
        county = form.county.data
        postalCode = form.postalCode.data
        country = form.country.data
        password = form.password.data

        validUserName = db.execute(
            """
            SELECT *
            FROM users 
            WHERE userName = ?
            EXCEPT 
            SELECT *
            FROM users
            WHERE userId = ?
            """,
            (userName, g.user),
        ).fetchone()
        validEmail = db.execute(
            """
            SELECT *
            FROM users 
            WHERE email = ?
            EXCEPT 
            SELECT *
            FROM users
            WHERE userId = ?""",
            (email, g.user),
        ).fetchone()
        validPhoneNum = db.execute(
            """
            SELECT *
            FROM users 
            WHERE phoneNum = ?
            EXCEPT 
            SELECT *
            FROM users
            WHERE userId = ?""",
            (phoneNum, g.user),
        ).fetchone()

        if validUserName is not None:
            form.userName.errors.append("Invalid Username. Username already exist")
        elif validEmail is not None:
            form.email.errors.append("Invalid email. Email already used.")
        elif validPhoneNum is not None:
            form.phoneNum.errors.append(
                "Invalid phone number. Phone number already used."
            )
        else:
            userAccount = db.execute(
                """
                SELECT *
                FROM debitAccount 
                WHERE userId = ?""",
                (g.user,),
            ).fetchone()
            amount = convert_currency(
                userAccount["balance"], userAccount["currency"], currency
            )
            db.execute(
                """
                UPDATE debitAccount
                SET balance = ?
                WHERE userId = ?""",
                (amount, g.user),
            )
            db.commit()
            
            db.execute(
                """
                UPDATE users 
                SET userName = ?,
                    firstname = ?,
                    lastName = ?,
                    dob = ?, 
                    phoneNum = ?,
                    email = ?,
                    currency = ?,
                    homeAddress = ?,
                    city = ?, 
                    county = ?,
                    postalCode = ?,
                    country = ?
                WHERE userId = ?
                """,
                (
                    userName,
                    firstName,
                    lastName,
                    dob,
                    phoneNum,
                    email,
                    currency,
                    homeAddress,
                    city,
                    county,
                    postalCode,
                    country,
                    g.user,
                ),
            )
            db.commit()
            db.execute(
                """
                UPDATE debitAccount 
                SET currency = ?
                WHERE userId = ?;""",(
                    currency, g.user
                )
            )
            db.commit()

            
            flash("Account Information Updated.")
    return render_template("user/settings.html", user=user, form=form)


@app.route("/admin/dashboard", methods=["GET", "POST"])
@login_required
@admin_required
def adminDashboard():

    db = get_db()
    totalUsers = db.execute(
        """
        SELECT COUNT(*) as totalUsers
        FROM users
        """
    ).fetchone()
    activeUsers = db.execute(
        """
        SELECT COUNT(*) as activeUsers
        FROM users
        WHERE freezeAccount = ?""",
        (0,),
    ).fetchone()
    frozenUsers = db.execute(
        """
        SELECT COUNT(*) as frozenUsers
        FROM users
        WHERE freezeAccount = ?""",
        (1,),
    ).fetchone()

    monthlyTransactions = db.execute(
        """
        SELECT SUM(amount) AS monthlyBalance, COUNT(*) as numTransactions
        FROM adminTransactions
        WHERE strftime('%Y-%m', transactionDate) = strftime('%Y-%m', 'now');
        """
    ).fetchone()
    lastMonthTransactions = db.execute(
        """
        SELECT SUM(amount) AS monthlyBalance, COUNT(*) as numTransactions
        from adminTransactions
        WHERE strftime('%Y-%m', transactionDate) = strftime('%Y-%m', date('now','-1 month'));
        """
    ).fetchone()
    weeklyTransaction = db.execute(
        """
        SELECT SUM(amount) AS weeklyBalance, COUNT(*) as numTransactions
        FROM adminTransactions
        WHERE strftime('%Y-%W', transactionDate) = strftime('%Y-%W', 'now')"""
    ).fetchone()
    transaction = db.execute(
        """
        SELECT COUNT(*) AS totalTransactions, SUM(amount) AS totalBalance, *
        FROM adminTransactions
        """
    ).fetchone()
    user = db.execute(
        """
        SELECT COUNT(*) AS registeredUser
        FROM users
        WHERE strftime('%Y-%m', createdAccount) = strftime('%Y-%m', 'now');
        """
    ).fetchone()

    return render_template(
        "admin/dashboard.html",
        totalUsers=totalUsers,
        activeUsers=activeUsers,
        frozenUsers=frozenUsers,
        monthlyTransactions=monthlyTransactions,
        lastMonthTransactions=lastMonthTransactions,
        weeklyTransaction=weeklyTransaction,
        transaction=transaction,
        user=user,
    )


@app.route("/admin/view/allUsers", methods=["GET", "POST"])
@login_required
@admin_required
def adminUsers():
    db = get_db()
    users = db.execute(
        """
        SELECT *
        FROM users
        """
    )

    return render_template("admin/userList.html", users=users)


@app.route("/admin/freeze/user/<int:userId>", methods=["GET", "POST"])
@login_required
@admin_required
def adminFreezeUser(userId):
    db = get_db()
    db.execute(
        """
        UPDATE users 
        SET freezeAccount = ?
        WHERE userId = ?""",
        (1, userId),
    )
    db.commit()

    return redirect(url_for("adminUsers"))


@app.route("/admin/unfreeze/user/<int:userId>", methods=["GET", "POST"])
@login_required
@admin_required
def adminUnfreezeUser(userId):
    db = get_db()
    db.execute(
        """
        UPDATE users 
        SET freezeAccount = ?
        WHERE userId = ?""",
        (0, userId),
    )
    db.commit()

    return redirect(url_for("adminUsers"))


@app.route("/admin/view/transactions", methods=["GET", "POST"])
@login_required
@admin_required
def adminTransactions():
    page = request.args.get("page", 1, type=int)
    limit = 5
    offset = (page - 1) * limit
    
    print(offset)
    
    parameter = []
    orderParameters = [] 

    form = filterForm()

    db = get_db()
    query = """
        SELECT *
        FROM adminTransactions
        """
    transactions = db.execute(query, parameter).fetchall()

    query += "WHERE amount BETWEEN ? AND ?"

    if form.submit():
        minAmount = form.minAmount.data
        maxAmount = form.maxAmount.data
        currency = form.currency.data
        recipientId = form.recipientId.data
        senderId = form.senderId.data
        country = form.country.data
        currency = form.currency.data
        startDate = form.startDate.data
        endDate = form.endDate.data
        amountAsc = form.amountAsc.data
        amountDec = form.amountDec.data
        countryAsc = form.countryAsc.data
        countryDec = form.countryDec.data
        dateAsc = form.dateAsc.data
        dateDes = form.dateDes.data

        if minAmount is None or minAmount == "":
            minAmount = 0
        if maxAmount is None or maxAmount == "":
            maxAmount = 9999999999999999

        parameter.append(minAmount)
        parameter.append(maxAmount)

        if currency and currency != " ":
            query += " AND currency = ?"
            parameter.append(currency)

        if country and country != " ":
            query += " AND destinationCountry = ?"
            parameter.append(country)

        if senderId:
            query += " AND receiverId = ?"
            parameter.append(senderId)

        if recipientId:
            query += " AND receiverId = ?"
            parameter.append(recipientId)

        if startDate:
            query += " AND transactionDate >= ?"
            parameter.append(startDate)

        if endDate:
            query += " AND transactionDate <= ?"
            parameter.append(endDate)

        if amountAsc:
            orderParameters.append("amount ASC")

        if amountDec:
            orderParameters.append("amount DESC")

        if countryAsc:
            orderParameters.append("destinationCountry ASC")

        elif countryDec:
            orderParameters.append("destinationCountry DESC")

        if dateAsc:
            orderParameters.append("transactionDate ASC")

        elif dateDes:
            orderParameters.append("transactionDate DESC")

        if orderParameters:
            orderParameters = "ORDER BY " + ", ".join(orderParameters)
            query += orderParameters

        query += " LIMIT ? OFFSET ?"
        parameter.append(limit)
        parameter.append(offset)
        
        transactions = db.execute(query, parameter).fetchall()
        pages = db.execute("""
            SELECT COUNT(id) AS totalPages
            FROM adminTransactions""").fetchone()
        
        if pages['totalPages'] > limit:
            totalPages = math.ceil(pages["totalPages"] / limit)
        else: 
            totalPages = 1 



    return render_template(
        "admin/transactions.html", transactions=transactions, form=form, page=page, totalPages=totalPages
    )


@app.route("/admin/view/user/<int:userId>", methods=["GET", "POST"])
@login_required
@admin_required
def viewUser(userId):
    db = get_db()
    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE userId = ?""",
        (userId,),
    ).fetchone()
    userAccount = db.execute(
        """
        SELECT *
        FROM debitAccount 
        WHERE userId = ?""",
        (userId,),
    ).fetchone()

    return render_template("admin/viewUser.html", user=user, userAccount=userAccount)


@app.route("/admin/sender/transfer", methods=["GET", "POST"])
@login_required
@admin_required
def adminSenderTransfer():
    step = 1 
    session["adminStep"] = step
    message = ""
    sForm = adminSenderInfo()

    if sForm.validate_on_submit():
        # Get data from form
        sUserName = sForm.userName.data
        sCardDetails = sForm.cardDetails.data
        sUserId = sForm.userId.data
        sAmount = sForm.amount.data
        sCurrency = sForm.currency.data
        sDestinationCountry = sForm.destinationCountry.data
        sDescription = sForm.description.data
        sAdditionalInfo = sForm.additionalInfo.data
        
        db = get_db()
        
        if sAmount <= 0:
            message = "Invalid amount"
            return render_template(
            "admin/transferSender.html", sForm=sForm, message=message, step=session["adminStep"])
        
        sSenderUsername = db.execute("""
            SELECT *
            FROM users 
            WHERE userName = ? """, (sUserName,)).fetchone()
        
        sBankCardInfo = db.execute("""
            SELECT *
            FROM debitAccount
            WHERE cardNumber = ?""", (sCardDetails, )).fetchone()
        
        sSenderId = db.execute("""
            SELECT *
            FROM users 
            WHERE userID = ?""", (sUserId, )).fetchone()
        
        if sSenderUsername is None:
            message = "Invalid Username"
            return render_template("admin/transferSender.html",sForm=sForm,  step=session["adminStep"], message=message)
            
        if sBankCardInfo is None:
            message = "Card Details do not exist"
            return render_template("admin/transferSender.html",sForm=sForm, step=session["adminStep"], message=message)

        
        if sSenderId is None:
            message = "Invalid UserID "
            return render_template("admin/transferSender.html", sForm=sForm,step=session["adminStep"], message=message)

            
        validSender = db.execute("""
            SELECT *
            FROM users AS u JOIN debitAccount AS d
            ON u.userId = d.userId
            WHERE u.userId = ? AND u.userName = ? AND d.cardNumber = ?""",
            (sUserId, sUserName, sCardDetails)).fetchone()
        
        if validSender is None:
            message = "User information does not match."
            return render_template("admin/transferSender.html",sForm=sForm, step=session["adminStep"], message=message)
        
        if validSender["freezeAccount"] ==1:
            message = "Account is frozen. No transfer can be made"
            return render_template("admin/transferSender.html",sForm=sForm, step=session["adminStep"], message=message)
        
        else:
            if "adminSenderTransaction" not in session:
                session["adminSenderTransaction"] = {}

            # Store transaction Information in a session
            session["adminSenderTransaction"]["userName"] = sUserName
            session["adminSenderTransaction"]["cardDetails"] = sCardDetails
            session["adminSenderTransaction"]["userId"] = sUserId
            session["adminSenderTransaction"]["amount"] = sAmount
            session["adminSenderTransaction"]["toCurrency"] = sCurrency
            session["adminSenderTransaction"]["destinationCountry"] = sDestinationCountry
            session["adminSenderTransaction"]["description"] = sDescription
            session["adminSenderTransaction"]["additionalInfo"] = sAdditionalInfo
            session.modified = True
            session["adminStep"] += 1
            return redirect(url_for("adminReceiverTransfer"))

    return render_template("admin/transferSender.html", sForm=sForm, step=session["adminStep"], message=message)

@app.route("/admin/receiver/transfer", methods=["GET", "POST"])
@login_required
@admin_required
def adminReceiverTransfer():
    rForm = adminReceiverInfo()
    message = ""
    
    if session["adminStep"] == 2:
        print(session["adminStep"])
        if rForm.validate_on_submit():
            rUserName = rForm.userName.data
            rCardDetails = rForm.cardDetails.data
            rUserId = rForm.userId.data
            rEmail = rForm.recipientEmail.data
            
            db = get_db()
            
            rSenderUsername = db.execute("""
                SELECT *
                FROM users 
                WHERE userName = ? """, (rUserName,)).fetchone()
            
            rBankCardInfo = db.execute("""
                SELECT *
                FROM debitAccount
                WHERE cardNumber = ?""", (rCardDetails, )).fetchone()
            
            rSenderId = db.execute("""
                SELECT *
                FROM users 
                WHERE userID = ?""", (rUserId, )).fetchone()
            
            if rSenderUsername is None:
                message = "Invalid Username"
                return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)
                
            if rBankCardInfo is None:
                message = "Card Details do not exist"
                return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)

            
            if rSenderId is None:
                message = "Invalid UserID "
                return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)
            
            validReceiver = db.execute("""
                SELECT *
                FROM users AS u JOIN debitAccount AS d
                ON u.userId = d.userId
                WHERE u.userId = ? AND u.userName = ? AND d.cardNumber = ?""",
                (rUserId, rUserName, rCardDetails)).fetchone()
            
            if validReceiver is None:
                message = "User information does not match."
                return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)
            
            if rUserName == session["adminSenderTransaction"]["userName"]:
                rForm.userName.errors.append("Sender cannot send money to self")
                return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)

            if validReceiver["freezeAccount"] ==1 :
                message = "Account is frozen. No transfer can be made"
                return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)

                

            
            else:
                if "adminReceiverTransaction" not in session:
                    session["adminReceiverTransaction"] = {}
                
                session["adminReceiverTransaction"]["userName"] = rUserName
                session["adminReceiverTransaction"]["cardDetails"] = rCardDetails
                session["adminReceiverTransaction"]["userId"] = rUserId
                session["adminReceiverTransaction"]["email"] = rEmail
                session.modified = True
                session["adminStep"] += 1
                return redirect(url_for("adminDetailsTransfer"))

    return render_template("admin/transferReceiver.html", rForm=rForm, step=session["adminStep"], message=message)


@app.route("/admin/details/transfer", methods=["GET", "POST"])
@login_required
@admin_required
def adminDetailsTransfer():
    
    sender=session["adminSenderTransaction"]
    receiver=session["adminReceiverTransaction"]
    
    db = get_db()
    senderAccount = db.execute("""
        SELECT *
        FROM debitAccount
        WHERE userId = ?""", (sender["userId"],)).fetchone()

    receiverAccount = db.execute("""
        SELECT *
        FROM debitAccount
        WHERE userId = ?""", (receiver["userId"],)).fetchone()

    currentTime = datetime.now()
    currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")

    fee = convert_currency(sender["amount"], sender["toCurrency"], senderAccount["currency"] ) * 0.05
    if fee < 5:
        fee = 5
    session["adminSenderTransaction"]["fee"] = fee

    session["adminSenderTransaction"]["transactionDate"] = currentTime

    return render_template("admin/transferDetails.html", sender=sender, receiver=receiver, step=session["adminStep"], senderAccount=senderAccount, receiverAccount=receiverAccount)

@app.route("/admin/confirm/transfer", methods=["GET", "POST"])
@login_required
@admin_required
def adminConfirm():
    sender=session["adminSenderTransaction"]
    receiver=session["adminReceiverTransaction"]
    
    db = get_db()
    senderAccount = db.execute(
        """
            SELECT * 
            FROM debitAccount 
            WHERE userId = ?
            """,
        (sender["userId"],),
    ).fetchone()
    receiverAccount = db.execute(
        """
            SELECT * 
            FROM debitAccount 
            WHERE userId = ?
            """,
        (receiver["userId"],),
    ).fetchone()
    receiverInfo = db.execute("""
        SELECT *
        FROM users 
        WHERE userId = ?""", (sender["userId"], )).fetchone()
    senderBalance = float(senderAccount["balance"])
    receiverBalance = float(receiverAccount["balance"])
    fee = float(session["adminSenderTransaction"]["fee"])
    amount = float(sender["amount"])

    if receiverAccount["currency"] != sender["toCurrency"]:
        rAmount = convert_currency(
            amount,
            sender["toCurrency"],
            receiverAccount["currency"],
        )
        receiverBalance += rAmount
    else:
        receiverBalance += amount

    if senderAccount["currency"] != sender["toCurrency"]:
        amount += fee
        sAmount = convert_currency(amount, sender["toCurrency"], senderAccount["currency"])
        senderBalance -= sAmount

    else:
        amount += fee
        senderBalance -= amount

    db.execute(
        """
            UPDATE debitAccount
            SET balance = ?
            WHERE userId = ?
            """,
        (receiverBalance, receiver["userId"]),
    )
    db.commit()
    db.execute(
        """
            UPDATE debitAccount
            SET balance = ?
            WHERE userId = ?
            """,
        (senderBalance, sender["userId"]),
    )
    db.commit()

    db.execute(
        """
            INSERT INTO transactions
            (
                senderId, 
                receiverId,
                recipientName,
                destinationCountry,
                amount, 
                currency,
                descriptionText,
                additionalInfo,
                recipientEmail,
                transactionDate
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
        (
            sender["userId"],
            receiver["userId"],
            receiverInfo["userName"],
            sender["destinationCountry"],
            amount,
            sender["toCurrency"],
            sender["description"],
            sender["additionalInfo"],
            receiver["email"],
            sender["transactionDate"],
        ),
    )
    
    db.commit()
    amount = convert_currency(amount, sender["toCurrency"], "EUR")
    db.execute(
        """
            INSERT INTO adminTransactions
            (
                senderId, 
                receiverId,
                recipientName,
                destinationCountry,
                amount, 
                currency,
                descriptionText,
                additionalInfo,
                recipientEmail,
                transactionDate
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
        (
            sender["userId"],
            receiver["userId"],
            receiverInfo["userName"],
            sender["destinationCountry"],
            amount,
            sender["toCurrency"],
            sender["description"],
            sender["additionalInfo"],
            receiver["email"],
            sender["transactionDate"],
        ),
    )
    db.commit()
    session.pop("adminSenderTransaction")
    session.modified = True
    session.pop("adminReceiverTransaction")
    session.modified = True
        
    return redirect(url_for("adminSenderTransfer"))

@app.route("/credits")
def credits():
    
    
    return render_template("credits.html")

def idNum():
    while True:
        newId = randint(100000, 999999)
        db = get_db()
        clash = db.execute(
            """
            SELECT userID 
            FROM users 
            WHERE userID = ?""",
            (newId,),
        ).fetchone()
        if clash is None:
            return newId


def generateCard():
    while True:
        newSCard = randint(1000000000000000, 9999999999999999)
        db = get_db()
        clash = db.execute(
            """
            SELECT cardNumber 
            FROM debitAccount 
            WHERE cardNumber = ?""",
            (newSCard,),
        ).fetchone()
        if clash is None:
            return newSCard

def expiryDate():
    today = datetime.today().date()
    expiryDate = today.replace(year=today.year + 4)
    return expiryDate

def cvcNum():
    cvc = randint(100, 999)
    return cvc

def cardPin():
    pin = randint(1000, 9999)
    return pin

def dbCalc(tuple, userDict, average):
    total = 0
    amount = 0
    if tuple != []:
        for row in tuple:
            if row["currency"] != userDict["currency"]:
                amount = convert_currency(row["amount"], row["currency"], userDict["currency"])
                total += amount
            else:
                total += row["amount"]
        if average:
            average = total/len(tuple)
            return average
        else:
            return total
    return 0
