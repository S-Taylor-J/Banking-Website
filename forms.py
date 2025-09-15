from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    DateField,
    RadioField,
    DecimalField,
    SubmitField,
    SelectField,
    IntegerField,
    BooleanField,
)
from wtforms.validators import InputRequired, EqualTo, Length
from datetime import date


def verifyAge(form, field):
    dob = form.dob.data
    today = date.today()
    minAgeDate = today.replace(year=today.year - 16)
    if dob > minAgeDate:
        form.dob.errors.append("You must be at least 16 years old to register")


def verifyPhoneNumber(form, field):
    phoneNum = form.phoneNum.data
    if not phoneNum.isdigit():
        form.phoneNum.errors.append("Please enter a valid phone number.")


class loginForm(FlaskForm):
    userName = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class registerForm(FlaskForm):
    firstName = StringField(
        "First Name", validators=[InputRequired()], render_kw={"placeholder": "John"}
    )
    lastName = StringField(
        "Last Name", validators=[InputRequired()], render_kw={"placeholder": "Smith"}
    )
    userName = StringField(
        "User Name",
        validators=[InputRequired()],
        render_kw={"placeholder": "JohnSmith"},
    )
    dob = DateField("Date of Birth", validators=[InputRequired(), verifyAge])
    phoneNum = StringField(
        "Phone Number",
        validators=[InputRequired(), Length(min=10, max=10), verifyPhoneNumber],
        render_kw={"placeholder": "0801531990"},
    )
    email = StringField(
        "Email",
        validators=[InputRequired()],
        render_kw={"placeholder": "johnsmith@umail.ie"},
    )
    currency = RadioField(
        "Currency",
        choices=["EUR", "USD", "GBP", "JPY", "CNY"],
        validators=[InputRequired()],
    )
    homeAddress = StringField(
        "Home Address",
        validators=[InputRequired()],
        render_kw={"placeholder": "1045 S State St"},
    )
    city = StringField(
        "City",
        validators=[InputRequired()],
        render_kw={"placeholder": "Salt Lake City"},
    )
    county = StringField(
        "County",
        validators=[InputRequired()],
        render_kw={"placeholder": "Utah"},
    )
    postalCode = StringField(
        "Postal Code",
        validators=[InputRequired()],
        render_kw={"placeholder": "UT 84111"},
    )
    country = SelectField(
        "Country",
        choices=["Ireland", "Portugal", "England", "United States", "Japan", "China"],
        default="Ireland"
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=20)]
    )
    confirmPassword = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class transactionForm(FlaskForm):
    userName = StringField(
        "Recipient's name",
        validators=[InputRequired()],
        render_kw={"placeholder": "Recipient's Username"},
    )
    destinationCountry = SelectField(
        "Destination country",
        choices=["Ireland", "Portugal", "England", "United States", "Japan", "China"],
        default="Ireland"
    )
    userId = StringField(
        "User ID",
        validators=[InputRequired()],
        render_kw={"placeholder": "User ID"},
    )
    amount = DecimalField(
        "Amount", validators=[InputRequired()], render_kw={"placeholder": "Amount"}
    )
    currency = SelectField(
        "Currency",
        validators=[InputRequired()],
        choices=["EUR", "USD", "GBP", "JPY", "CNY"],
        default="EUR",
    )
    description = StringField(
        "Transfer Reason", render_kw={"placeholder": "Description - Opcional"}
    )
    additionalInfo = StringField(
        "Additional information ",
        render_kw={"placeholder": "Additional information - Opcional"},
    )
    recipientEmail = StringField(
        "Recipient email", render_kw={"placeholder": "Recipient email - Opcional"}
    )
    submit = SubmitField("Next Step")


class filterForm(FlaskForm):
    minAmount = IntegerField("Min Amount")
    maxAmount = IntegerField("Max Amount")
    country = SelectField(
        "Destination Country",
        choices=[
            " ",
        ],
    )
    recipientId = IntegerField("Recipient ID")
    senderId = IntegerField("Sender ID")
    currency = SelectField(
        "Currency Type ", choices=[" ", "EUR", "USD", "GBP", "JPY", "CNY"]
    )
    country = SelectField(
        "Country",
        choices=[
            " ",
            "Ireland",
            "Portugal",
            "England",
            "United States",
            "Japan",
            "China",
        ],
    )
    startDate = DateField("Start Date")
    endDate = DateField("End Date")
    amountAsc = BooleanField("Amount Increasing")
    amountDec = BooleanField("Amount decreasing")
    countryAsc = BooleanField("Country Ascending A-Z")
    countryDec = BooleanField("Country Descending Z-A")
    dateAsc = BooleanField("Date Ascending")
    dateDes = BooleanField("Date Descending")
    submit = SubmitField("Apply Filters")


class settingsForm(FlaskForm):
    firstName = StringField(
        "First Name", validators=[InputRequired()], render_kw={"placeholder": "John"}
    )
    lastName = StringField(
        "Last Name", validators=[InputRequired()], render_kw={"placeholder": "Smith"}
    )
    userName = StringField(
        "User Name",
        validators=[InputRequired()],
        render_kw={"placeholder": "JohnSmith"},
    )
    dob = DateField("Date of Birth", validators=[InputRequired(), verifyAge])
    phoneNum = StringField(
        "Phone Number",
        validators=[InputRequired(), Length(min=10, max=10), verifyPhoneNumber],
        render_kw={"placeholder": "0801531990"},
    )
    email = StringField(
        "Email",
        validators=[InputRequired()],
        render_kw={"placeholder": "johnsmith@umail.ie"},
    )
    currency = RadioField(
        "Currency",
        choices=["EUR", "USD", "GBP", "JPY", "CNY"],
        validators=[InputRequired()],
    )
    homeAddress = StringField(
        "Home Address",
        validators=[InputRequired()],
        render_kw={"placeholder": "1045 S State St"},
    )
    city = StringField(
        "City",
        validators=[InputRequired()],
        render_kw={"placeholder": "Salt Lake City"},
    )
    county = StringField(
        "County",
        validators=[InputRequired()],
        render_kw={"placeholder": "Utah"},
    )
    postalCode = StringField(
        "Postal Code",
        validators=[InputRequired()],
        render_kw={"placeholder": "UT 84111"},
    )
    country = StringField(
        "Country",
        validators=[InputRequired()],
        render_kw={"placeholder": "United States"},
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=20)]
    )
    confirmPassword = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Save Changes")

class adminSenderInfo(FlaskForm):
    userName = StringField(
        "Recipient's name",
        validators=[InputRequired()],
        render_kw={"placeholder": "Username"},
    )
    cardDetails = IntegerField("Bank Card Details", validators=[InputRequired()], render_kw={"placeholder": "Bank Card Details"})
    userId = StringField(
        "User ID",
        validators=[InputRequired()],
        render_kw={"placeholder": "User ID"},
    )
    amount = DecimalField(
        "Amount", validators=[InputRequired()], render_kw={"placeholder": "Amount"}
    )
    currency = SelectField(
        "Currency",
        validators=[InputRequired()],
        choices=["EUR", "USD", "GBP", "JPY", "CNY"],
        default="EUR",
    )
    destinationCountry = SelectField(
        "Destination country",
        choices=["Ireland", "Portugal", "England", "United States", "Japan", "China"],
        default="Ireland"
    )
    description = StringField(
        "Transfer Reason", render_kw={"placeholder": "Description - Opcional"}
    )
    additionalInfo = StringField(
        "Additional information ",
        render_kw={"placeholder": "Additional information - Opcional"},
    )

    submit = SubmitField("Next Step")

class adminReceiverInfo(FlaskForm):
    userName = StringField(
        "Recipient's name",
        validators=[InputRequired()],
        render_kw={"placeholder": "Username"},
    )
    cardDetails = IntegerField("Bank Card Details", validators=[InputRequired()], render_kw={"placeholder": "Bank Card Details"})
    userId = StringField(
        "User ID",
        validators=[InputRequired()],
        render_kw={"placeholder": "User ID"},
    )
    recipientEmail = StringField(
        "Recipient email", render_kw={"placeholder": "Recipient email - Opcional"}
    )
    submit = SubmitField("Next Step")
    
