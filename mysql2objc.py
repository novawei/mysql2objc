#!/usr/bin/env python
# coding=utf-8

import MySQLdb
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

host = 'localhost'
port = 3306
user = 'root'
passwd = 'password'
db_name = 'mydb'
dir_name = 'mysql2objc-models'
cls_prefix = 'WN'

nsstring_types = ['char',
                  'varchar',
                  'tinyblob',
                  'tinytext',
                  'blob',
                  'text',
                  'mediumblob',
                  'mediumtext',
                  'longblob',
                  'longtext',
                  'date',
                  'time',
                  'datetime',
                  'timestamp']

nsinteger_types = ['tinyint',
                   'smallint',
                   'mediumint',
                   'int',
                   'integer',
                   'bigint']

double_types = ['double',
                'float',
                'decimal']

tpl_h_format = '''//
//  %s.h
//  QDG
//
//  Created by mysql2objc on 16/5/25.
//  Copyright © 2016年 nova. All rights reserved.
//

#import "WNModel.h"

/**
 *  %s
 */
@interface %s : WNModel
'''

tpl_m_format = '''//
//  %s.m
//  QDG
//
//  Created by mysql2objc on 16/5/25.
//  Copyright © 2016年 nova. All rights reserved.
//

#import "%s.h"

@implementation %s

@end
'''

tpl_end = '''

@end
'''

tpl_p_format = '''
@property (nonatomic, %s) %s%s; //%s'''

if os.path.exists(dir_name):
    filenames = os.listdir(dir_name)
    os.chdir(dir_name)
    for filename in filenames:
        os.remove(filename)
else:
    os.mkdir(dir_name)
    os.chdir(dir_name)

conn = MySQLdb.connect(
        host=host,
        port=port,
        user=user,
        passwd=passwd,
        db = db_name,
        charset='utf8')

cur = conn.cursor()
# list all tables
sql = "SELECT TABLE_NAME, TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='%s'" % db_name
count = cur.execute(sql)
tables = cur.fetchmany(count)
for table in tables:
    table_name = table[0]

    cls_name = cls_prefix;
    names = table_name.split('_')
    for name in names:
        if name == 't':
            continue
        cls_name += name.capitalize()

    # .h file
    h_file = open(cls_name + '.h', 'a')

    content = tpl_h_format % (cls_name, table[1], cls_name)

    sql = "SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='%s' and TABLE_NAME='%s'" % (db_name, table_name)
    count = cur.execute(sql)
    columns = cur.fetchmany(count)
    for column in columns:
        comment = column[2].replace('\r\n', '')
        data_type = column[1].lower()
        if data_type in nsstring_types:
            content += (tpl_p_format % ('strong', 'NSString *', column[0], comment))
        elif data_type in nsinteger_types:
            content += (tpl_p_format % ('assign', 'NSInteger ', column[0], comment))
        elif data_type in double_types:
            content += (tpl_p_format % ('assign', 'double ', column[0], comment))
        else:
            content += (tpl_p_format % ('assign', data_type+' ', column[0], comment))

    content += tpl_end

    h_file.writelines(content);
    h_file.close()

    # .m file
    m_file = open(cls_name + '.m', 'a')

    content = tpl_m_format % (cls_name, cls_name, cls_name)

    m_file.writelines(content)
    m_file.close()

cur.close()
conn.close()
