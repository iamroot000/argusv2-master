


DEFAULT_ISOLATION_LEVEL = "SERIALIZABLE"

CREATE_TABLE_CONTACT = \
'''
CREATE TABLE IF NOT EXISTS smsalerts_contact(
    id int not null auto_increment,
    name varchar(64) not null,
    number bigint not null,
    primary key(id)
) ENGINE=InnoDB
'''

CREATE_TABLE_GROUP = \
'''
CREATE TABLE IF NOT EXISTS smsalerts_group(
    id int not null auto_increment,
    name varchar(64) not null,
    primary key(id)
) ENGINE=InnoDB
'''

CREATE_TABLE_MEMBERSHIP = \
'''
CREATE TABLE IF NOT EXISTS smsalerts_membership(
    contact_id int not null,
    group_id int not null,
    foreign key (group_id) references smsalerts_group(id),
    foreign key (contact_id) references smsalerts_contact(id),
    unique(contact_id,group_id)
) ENGINE=InnoDB
'''


CREATE_TABLE_MESSAGEQUEUE = \
'''
CREATE TABLE IF NOT EXISTS smsalerts_message_queue(
    id int not null auto_increment,
    group_id int not null,
    message varchar(128) not null,
    last_sent datetime not null,
    freq_minutes int not null,
    flags int unsigned default 0,
    foreign key (group_id) references smsalerts_group(id),
    primary key(id)
) ENGINE=InnoDB
'''

SELECT_PHONE_NUMBER_BY_ID = \
'''
select number from smsalerts_contact where id = %s
'''
SELECT_GROUP_MEMBERS = \
'''
select smsalerts_contact.id,smsalerts_contact.name from smsalerts_contact inner join smsalerts_membership on smsalerts_contact.id = smsalerts_membership.contact_id inner join smsalerts_group on smsalerts_membership.group_id = smsalerts_group.id where smsalerts_group.name = %s
'''
SELECT_GROUP_ID = \
'''
select id from smsalerts_group where name = %s
'''

SELECT_GROUP_NAMES_LIST = \
'''
select name from smsalerts_group
'''

INSERT_ANNOUNCEMENT = \
'''
insert into smsalerts_message_queue(group_id,message,last_sent,freq_minutes,flags) values (%s,%s,%s,%s,%s)
'''

DELETE_ANNOUNCEMENT_BY_ID = \
'''
delete from smsalerts_message_queue where id = %s
'''

SELECT_ANNOUNCEMENTS = \
'''
select smsalerts_message_queue.id, smsalerts_group.name, smsalerts_message_queue.message, smsalerts_message_queue.last_sent, smsalerts_message_queue.freq_minutes, smsalerts_message_queue.flags from smsalerts_message_queue inner join smsalerts_group where smsalerts_message_queue.group_id = smsalerts_group.id
'''

SELECT_ANNOUNCEMENTS_BY_ID = \
'''
select smsalerts_message_queue.id, smsalerts_group.name, smsalerts_message_queue.message, smsalerts_message_queue.last_sent, smsalerts_message_queue.freq_minutes, smsalerts_message_queue.flags from smsalerts_message_queue inner join smsalerts_group on smsalerts_message_queue.group_id = smsalerts_group.id where smsalerts_message_queue.id = %s
'''

SELECT_PENDING_ANNOUNCEMENTS = \
'''
select smsalerts_message_queue.id, smsalerts_group.id, smsalerts_group.name, smsalerts_message_queue.message, smsalerts_message_queue.freq_minutes, smsalerts_message_queue.flags from smsalerts_group inner join smsalerts_message_queue on smsalerts_message_queue.group_id = smsalerts_group.id where TIMESTAMPDIFF(MINUTE,smsalerts_message_queue.last_sent,NOW()) >= smsalerts_message_queue.freq_minutes
'''
