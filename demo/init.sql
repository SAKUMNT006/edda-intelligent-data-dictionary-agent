-- Demo relational schema with PK/FK + some nulls + skew for profiling
create table if not exists customers (
  customer_id varchar(20) primary key,
  full_name text not null,
  email text,
  phone text,
  created_at timestamp not null default now()
);

create table if not exists products (
  product_id varchar(20) primary key,
  category text,
  product_name text not null,
  price numeric(10,2) not null
);

create table if not exists orders (
  order_id varchar(20) primary key,
  customer_id varchar(20) not null references customers(customer_id),
  order_status text not null,
  order_date timestamp not null,
  delivered_date timestamp,
  total_amount numeric(10,2)
);

create table if not exists order_items (
  order_item_id serial primary key,
  order_id varchar(20) not null references orders(order_id),
  product_id varchar(20) not null references products(product_id),
  qty int not null,
  unit_price numeric(10,2) not null
);

create table if not exists payments (
  payment_id serial primary key,
  order_id varchar(20) not null references orders(order_id),
  payment_method text,
  payment_status text not null,
  paid_amount numeric(10,2),
  paid_at timestamp
);

-- seed customers (with some missing email/phone)
insert into customers(customer_id, full_name, email, phone, created_at) values
  ('C001','Asha Verma','asha@example.com','9999911111', now() - interval '90 days'),
  ('C002','Rohit Singh',null,'9999922222', now() - interval '40 days'),
  ('C003','Neha Kumar','neha@example.com',null, now() - interval '10 days'),
  ('C004','Vikram Mehta',null,null, now() - interval '5 days')
on conflict do nothing;

insert into products(product_id, category, product_name, price) values
  ('P001','electronics','Wireless Mouse',599.00),
  ('P002','electronics','Keyboard',1299.00),
  ('P003','home','Water Bottle',299.00),
  ('P004','home','Desk Lamp',899.00)
on conflict do nothing;

insert into orders(order_id, customer_id, order_status, order_date, delivered_date, total_amount) values
  ('O1001','C001','DELIVERED', now() - interval '60 days', now() - interval '57 days', 1898.00),
  ('O1002','C002','SHIPPED',   now() - interval '12 days', null,  599.00),
  ('O1003','C003','PLACED',    now() - interval '2 days',  null,  299.00),
  ('O1004','C004','CANCELLED', now() - interval '20 days', null,  null)
on conflict do nothing;

insert into order_items(order_id, product_id, qty, unit_price) values
  ('O1001','P001',1,599.00),
  ('O1001','P002',1,1299.00),
  ('O1002','P001',1,599.00),
  ('O1003','P003',1,299.00)
on conflict do nothing;

insert into payments(order_id, payment_method, payment_status, paid_amount, paid_at) values
  ('O1001','CARD','PAID',1898.00, now() - interval '60 days'),
  ('O1002','UPI','PENDING',null, null),
  ('O1003','COD','PENDING',null, null)
on conflict do nothing;

create index if not exists idx_orders_customer on orders(customer_id);
create index if not exists idx_payments_order on payments(order_id);
