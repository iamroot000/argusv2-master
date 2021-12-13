
DB_HOST = "10.168.11.216"
DB_NAME = "yellowpages"
DB_USER = "bananaphone"
DB_PASS = "ringringringringringringring"

DEFAULT_ISOLATION_LEVEL = "SERIALIZABLE"

CREATE_TABLE_CONTACT = \
'''
CREATE TABLE IF NOT EXISTS Contacts(
    id int not null auto_increment,
    name varchar(64) not null,
    number bigint not null,
    primary key(id)
) ENGINE=InnoDB
'''

CREATE_TABLE_GROUP = \
'''
CREATE TABLE IF NOT EXISTS Groups(
    id int not null auto_increment,
    name varchar(64) not null,
    primary key(id)
) ENGINE=InnoDB
'''

CREATE_TABLE_MEMBERSHIP = \
'''
CREATE TABLE IF NOT EXISTS Membership(
    contact_id int not null,
    group_id int not null,
    foreign key (group_id) references Groups(id),
    foreign key (contact_id) references Contacts(id),
    unique(contact_id,group_id)
) ENGINE=InnoDB
'''


CREATE_TABLE_MESSAGEQUEUE = \
'''
CREATE TABLE IF NOT EXISTS MessageQueue(
    id int not null auto_increment,
    group_id int not null,
    message varchar(128) not null,
    lastSent datetime not null,
    freq_minutes int not null,
    flags int unsigned default 0,
    foreign key (group_id) references Groups(id),
    primary key(id)
) ENGINE=InnoDB
'''

SELECT_PHONE_NUMBER_BY_ID = \
'''
select number from Contacts where id = %s
'''
SELECT_GROUP_MEMBERS = \
'''
select Contacts.id,Contacts.name from Contacts inner join Membership on Contacts.id = Membership.contact_id inner join Groups on Membership.group_id = Groups.id where Groups.name = %s
'''
SELECT_GROUP_ID = \
'''
select id from Groups where name = %s
'''

SELECT_GROUP_NAMES_LIST = \
'''
select name from Groups
'''

INSERT_ANNOUNCEMENT = \
'''
insert into MessageQueue(group_id,message,lastSent,freq_minutes,flags) values (%s,%s,%s,%s,%s)
'''

DELETE_ANNOUNCEMENT_BY_ID = \
'''
delete from MessageQueue where id = %s
'''

SELECT_ANNOUNCEMENTS = \
'''
select MessageQueue.id, Groups.name, MessageQueue.message, MessageQueue.lastSent, MessageQueue.freq_minutes, MessageQueue.flags from MessageQueue inner join Groups where MessageQueue.group_id = Groups.id
'''

SELECT_ANNOUNCEMENTS_BY_ID = \
'''
select MessageQueue.id, Groups.name, MessageQueue.message, MessageQueue.lastSent, MessageQueue.freq_minutes, MessageQueue.flags from MessageQueue inner join Groups on MessageQueue.group_id = Groups.id where MessageQueue.id = %s
'''

SELECT_PENDING_ANNOUNCEMENTS = \
'''
select MessageQueue.id, Groups.id, Groups.name, MessageQueue.message, MessageQueue.freq_minutes, MessageQueue.flags from Groups inner join MessageQueue on MessageQueue.group_id = Groups.id where TIMESTAMPDIFF(MINUTE,MessageQueue.lastSent,NOW()) >= MessageQueue.freq_minutes
'''
