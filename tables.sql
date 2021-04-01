use gem_db;

drop table if exists comments; 
drop table if exists favorites;
drop table if exists tags;
drop table if exists item;
drop table if exists person;  

create table person(
   name varchar (30) not null,
   email varchar (30) not null,
   password varchar (30) not null,
   phone varchar (10),
   admin boolean,
   location varchar(30),
   primary key (email)
);
 
create table item(
   item_id int not null auto_increment,
   item_name varchar(30) not null,
   seller_id varchar (30) not null,
   category set('Clothing','Accessories','Dorm Essentials','Beauty','School Supplies','Tech','Furniture','Textbooks','Food','Other') not null, 
   free boolean not null,
   status enum('Still Available','Awaiting Pickup','Sold') not null,
   sellmode set('For Sale','For Rent','For Trade'),
   image varchar(30) not null, 
   item_condition set('Brand New','Gently Used','Well Loved') not null,
   item_description varchar(200) not null,
   price double,
   timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   primary key (item_id),
   index (seller_id),
   foreign key (seller_id) references person(email)
       on update cascade
       on delete cascade
)
ENGINE = InnoDB; 
 
create table favorites( 
   buyer_id varchar(30) not null,
   item_id int not null,
   index (buyer_id),
   foreign key (buyer_id) references person(email)
       on update cascade
       on delete cascade,
   foreign key (item_id) references item(item_id)
       on update cascade
       on delete cascade,
   primary key(buyer_id, item_id)
)
ENGINE = InnoDB;

create table comments(
   buyer_id varchar(30) not null,
   item_id int not null, 
   seller_id varchar(30) not null,
   comment varchar(200) not null, 
   primary key(buyer_id, seller_id, item_id, comment),
   foreign key (buyer_id) references person(email)
       on update cascade
       on delete cascade,
   foreign key (seller_id) references person(email)
       on update cascade
       on delete cascade,
   foreign key (item_id) references item(item_id)
       on update cascade
       on delete cascade  
)
ENGINE = InnoDB;

create table tags(
   seller_id varchar(30) not null,
   tag varchar(15) not null,
   item_id int not null,
   foreign key (seller_id) references person(email)
       on update cascade
       on delete cascade,
   foreign key (item_id) references item(item_id)
       on update cascade
       on delete cascade
)
ENGINE = InnoDB;
