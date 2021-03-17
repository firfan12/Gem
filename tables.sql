use gem_db;
'''
Where is comments (a three-way relationship among buyer, seller and
item) shown in the ER diagram? Doesnt seem to be.'''

drop table if exists comments; 
drop table if exists favorites;
drop table if exists tags;
drop table if exists items;
drop table if exists person;  

create table person(
   name varchar (30) not null,
   email varchar (30) not null,
   password varchar (30) not null,
   phone varchar (10),
   admin boolean,
   location varchar(30),
   primary key (email)
)
ENGINE = InnoDB;
 
create table item(
   item_id int not null auto_increment,
   item_name varchar(30) not null,
   category set(‘Clothing’, ‘Accessories’, ‘Dorm Essentials’, ‘Beauty’, ‘School Supplies’, ‘Tech’, ‘Furniture’, ‘Textbooks’, ‘Food’, ‘Other’) not null, 
   free boolean not null,
   status enum(‘Still Available’, ‘Awaiting Pickup’, ‘Sold’) not null,
   image varchar(30) not null, 
   item_condition  enum(‘Brand New’, ‘Gently Used’, ‘Well Loved’) not null,
   item_description varchar(200) not null,
   price double not null,
   primary key (item_id),
   index (email),
   foreign key (email) references person(email)
       on update cascade
       on delete cascade
)
ENGINE = InnoDB;
 
create table tags(
   seller_id int not null,
   tag varchar(15) not null,
   index (seller_id)
   foreign key (seller_id) references person(email)
       on update cascade
       on delete cascade,
    foreign key (item_id) references item(item_id)
       on update cascade
       on delete cascade
)
ENGINE = InnoDB;
 
create table favorites( 
   buyer_id varchar(30) not null,
   item_id int not null,
   index (buyer_id)
   primary key(buyer, item),
   foreign key (buyer_id) references person(email)
       on update cascade
       on delete cascade,
   foreign key (item_id) references item(item_id)
       on update cascade
       on delete cascade
);
ENGINE = InnoDB;
 
create table comments(
   buyer_id varchar(30) not null,
   item_id int not null, 
   seller_id varchar(30) not null,
   comment varchar(200) not null, 
   primary key(buyer_id, seller_id, item_id, comment)
   foreign key (buyer_id) references buyer(email)
       on update cascade
       on delete cascade,
   foreign key (seller_id) references seller(email)
       on update cascade
       on delete cascade,
   foreign key (item_id) references item(item_id)
       on update cascade
       on delete cascade  
);
ENGINE = InnoDB;