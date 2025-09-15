DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS savingsAccount;
DROP TABLE IF EXISTS debitAccount;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS adminAccounts;

CREATE TABLE users (
  userId INTEGER PRIMARY KEY,
  userName VARCHAR(20) NOT NULL,
  firstName VARCHAR(20) NOT NULL,
  lastName VARCHAR(20) NOT NULL,
  dob DATE NOT NULL,
  phoneNum VARCHAR(10) NOT NULL CHECK (LENGTH(phoneNum) = 10),
  email VARCHAR(50) NOT NULL,
  currency VARCHAR(5) NOT NULL,
  homeAddress VARCHAR(100) NOT NULL,  
  city VARCHAR(50) NOT NULL,          
  county VARCHAR(50) NOT NULL,        
  postalCode VARCHAR(10) NOT NULL,
  country VARCHAR(50) NOT NULL,
  freezeAccount BOOLEAN DEFAULT 0,
  createdAccount DATE NOT NULL,       
  password VARCHAR(25) NOT NULL, 
);

CREATE TABLE debitAccount (
  userId INTEGER NOT NULL,
  cardNumber INTEGER NOT NULL,
  expiryDate DATE NOT NULL,
  CVC INTEGER NOT NULL,
  balance DECIMAL(10, 2) NOT NULL,  
  pin INTEGER NOT NULL,
  currency VARCHAR(5) NOT NULL,
  FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    senderId INTEGER NOT NULL, 
    receiverId INTEGER NOT NULL, 
    recipientName VARCHAR(30) NOT NULL,
    destinationCountry VARCHAR(40) NOT NULL,
    amount REAL NOT NULL, 
    currency VARCHAR(5) NOT NULL,    
    descriptionText TEXT,
    additionalInfo TEXT,
    recipientEmail TEXT,
    transactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (senderId) REFERENCES users(usersId), 
    FOREIGN KEY (receiverId) REFERENCES users(usersId)  
);

CREATE TABLE adminTransactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    senderId INTEGER NOT NULL, 
    receiverId INTEGER NOT NULL, 
    recipientName VARCHAR(30) NOT NULL,
    destinationCountry VARCHAR(40) NOT NULL,
    amount REAL NOT NULL, 
    currency VARCHAR(5) NOT NULL,    
    descriptionText TEXT,
    additionalInfo TEXT,
    recipientEmail TEXT,
    transactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (senderId) REFERENCES users(usersId), 
    FOREIGN KEY (receiverId) REFERENCES users(usersId)  
);

create TABLE adminAccounts (
  userId INTEGER PRIMARY KEY AUTOINCREMENT,
  userName VARCHAR(20) NOT NULL,
  email VARCHAR(50) NOT NULL,
  password VARCHAR(25) NOT NULL
);
