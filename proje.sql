create DATABASE USER_TRACKING_SYSTEM;
GO

USE USER_TRACKING_SYSTEM;
GO

create table roles (
    role_id INT IDENTITY(1,1) primary key,
    role_name nvarchar(50)
);
GO

create table users (
    user_id INT IDENTITY(1,1) primary key,
    first_name nvarchar(50) NOT NULL,
    last_name nvarchar(50) NOT NULL,
    role_id INT NOT NULL,
    created_at nvarchar(30),
    username nvarchar(50) NOT NULL UNIQUE,
    email nvarchar(50) NOT NULL UNIQUE,
    [password] nvarchar(50) NOT NULL,
    phone nvarchar(50) NOT NULL UNIQUE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);
GO

create table customers (
    customer_id INT IDENTITY(1,1) primary key,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table cities (
    city_id INT IDENTITY(1,1) primary key,
    city_name nvarchar(50)
);
GO

create table districts (
    district_id INT IDENTITY(1,1) primary key,
    district_name nvarchar(50),
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
GO

create table address (
    address_id INT IDENTITY(1,1) primary key,
    customer_id INT,
    address_type nvarchar(20),
    city_id nvarchar(50),
    district_id INT,
    address_description nvarchar(255),
    postal_code INT,
    -- isdefault,
    -- created_at
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
GO

create table products (
    product_id INT IDENTITY(1,1) primary key,
    product_name nvarchar(50),
    vendor_id INT,
    quantity INT,
    category nvarchar(20),
    unit_price INT,
    total_price INT
);
GO
/*
create  table branchs (
    branch_id INT primary key,
    branch_name nvarchar(50),
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES address(address_id)
);
GO
*/
create table couriers (
    courier_id INT IDENTITY(1,1) primary key,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO
/*
create table contacts (
    contact_id INT primary key,
    user_id INT,
    phone nvarchar(13),
    --email nvarchar(50)
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO
*/
create table orders (
    order_id INT IDENTITY(1,1) primary key,
    customer_id INT,
    address_id INT,
    product_id INT,
    order_status nvarchar(20),
    --payment_method nvarchar(20),  
    quantity INT,
    total_price DECIMAL(10, 2),
    created_at nvarchar(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
GO

create table vendors (
    vendor_id INT IDENTITY(1,1) primary key,
    vendor_name nvarchar(50)
);
GO
/*
create table shippings (
    shipping_id INT primary key,
    order_id INT NOT NULL,
    courier_id INT NOT NULL,
    tracking_number nvarchar(20) NOT NULL,
    shipping_status nvarchar(20) NOT NULL
        CONSTRAINT CK_SHIPPINGS_STATUS CHECK (shipping_status IN ('preparing','on_the_way','delivered')),
    shipped_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    delivered_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    -- shipping_cost float
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (courier_id)  REFERENCES couriers(courier_id)
);
GO
*/
create table sales_logs (
    sales_log_id INT IDENTITY(1,1) primary key,
    order_id INT,
    product_id INT,
    user_id INT,
    vendor_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    created_at varchar(50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),   
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
GO

create table customer_representive (
    customer_representive_id INT IDENTITY(1,1) primary key,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table db_administrator (
    db_administrator_id INT IDENTITY(1,1) primary key,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table messages (
    message_id INT IDENTITY(1,1) primary key,
    customer_id INT,
    complain_topic nvarchar(50),
    message nvarchar(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
GO

ALTER TABLE products
ADD CONSTRAINT FK_PRODUCTS_VENDORS
FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
GO


