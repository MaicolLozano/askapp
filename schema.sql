create database if not exists askapp;

use askapp;

create table if not exists users (
    id int primary key auto_increment,
    username varchar(255),
    email varchar(255),
    password varchar(255),
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp
);

create table if not exists questions (
    id int primary key auto_increment,
    title varchar(255),
    img varchar(255),
    body text,
    user_id int,
    author_name varchar(255),
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    foreign key (user_id) references users(id),
    foreign key (author_name) references users(username)
);

create table if not exists answers (
    id int primary key auto_increment,
    body text,
    user_id int,
    question_id int,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    foreign key (user_id) references users(id),
    foreign key (question_id) references questions(id)
);

create table if not exists contacts (
    id int primary key auto_increment,
    subject varchar(255),
    message text,
    user_id int,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    foreign key (user_id) references users(id)
);  