create DATABASE USER_TRACKING_SYSTEM;
GO

USE USER_TRACKING_SYSTEM;
GO

create table roles (
    role_id INT primary key,
    role_name varcHar(50)
);
GO

create table users (
    user_id INT primary key,
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    role_id INT NOT NULL,
    created_at DATE,
    username varchar(50) NOT NULL UNIQUE,
    [password] varchar(50) NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);
GO

create table customers (
    customer_id INT primary key,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table address (
    address_id INT primary key,
    user_id INT,
    address_type VARCHAR(20)
        CONSTRAINT CK_ADDRESS_TYPE CHECK (address_type IN ('office', 'home', 'school')),
    country_id INT ,
    city_id INT,
    district_id INT,
    neighborhood_id INT,
    street varchar(50),
    building_no INT,
    apartment_no INT,
    postal_code INT,
    -- isdefault,
    -- created_at
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table countries (
    country_id INT primary key,
    country_name varchar(50)  
);
GO

create table cities (
    city_id INT primary key,
    city_name varchar(50),
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
);
GO

create table districts (
    district_id INT primary key,
    district_name varchar(50),
    city_id INT,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
GO

create table neighborhood (
    neighborhood_id INT primary key,
    neighborhood_name varchar(50),
    district_id INT,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);
GO

create table products (
    product_id INT primary key,
    product_name varchar(50),
    vendor_id INT,
    quantity INT,
    category VARCHAR(20)
        CONSTRAINT CK_PRODUCTS_CATEGORY CHECK (category IN ('food', 'drink', 'tech')),
    unit_price INT,
    total_price INT
);
GO

create  table branchs (
    branch_id INT primary key,
    branch_name varchar(50),
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES address(address_id)
);
GO

create table couriers (
    courier_id INT primary key,
    branch_id INT,
    salary DECIMAL(10,2),
    FOREIGN KEY (branch_id) REFERENCES branchs(branch_id)
);
GO

create table contacts (
    contact_id INT primary key,
    user_id INT,
    phone varchar(13),
    --email varchar(50)
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table orders (
    order_id INT primary key,
    user_id INT,
    address_id INT,
    branch_id INT,
    order_status VARCHAR(20) NOT NULL
        CONSTRAINT CK_ORDERS_STATUS CHECK (order_status IN ('pending','shipped','delivered','cancelled')),
    payment_method VARCHAR(20) NOT NULL
        CONSTRAINT CK_ORDERS_PAYMENT CHECK (payment_method IN ('cash','credit_card','eft')),    
    total_amount DECIMAL(10, 2),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id),
    FOREIGN KEY (branch_id) REFERENCES branchs(branch_id)

);
GO

create table vendors (
    vendor_id INT primary key,
    vendor_name varchar(50),
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
);
GO

create table shippings (
    shipping_id INT primary key,
    order_id INT NOT NULL,
    courier_id INT NOT NULL,
    tracking_number VARCHAR(20) NOT NULL,
    shipping_status VARCHAR(20) NOT NULL
        CONSTRAINT CK_SHIPPINGS_STATUS CHECK (shipping_status IN ('preparing','on_the_way','delivered')),
    shipped_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    delivered_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    -- shipping_cost float
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (courier_id)  REFERENCES couriers(courier_id)
);
GO

create table sales_logs (
    sales_log_id INT primary key,
    order_id INT,
    product_id INT,
    user_id INT,
    branch_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),   
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (branch_id) REFERENCES branchs(branch_id)
);
GO

create table customer_representive (
    customer_representive_id INT primary key,
    customer_name varchar(50),
    salary DECIMAL(10, 2),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

create table db_administrator (
    db_administrator_id INT primary key,
    db_administrator_name varchar(50),
    salary DECIMAL(10, 2),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

ALTER TABLE products
ADD CONSTRAINT FK_PRODUCTS_VENDORS
FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
GO


