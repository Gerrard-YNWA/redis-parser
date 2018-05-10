#!/bin/python
#-*-coding:utf8-*-

import socket

READ_BUFFER=1024 #1K
S_SIMPLE_STRING="+"
S_ERRORS="-"
S_INTEGERS=":"
S_BULK_STRINGS="$"
S_ARRAYS="*"
CRLF="\r\n"

BAD_REPLY=-1
STATUS_REPLY=0
ERROR_REPLY=1
INTEGER_REPLY=2
BULK_REPLY=3
MULTI_BULK_REPLY=4

def parse_cmd(*cmd):
    raw_data="%s%d%s" % (S_ARRAYS, len(cmd), CRLF)
    output = ["redis-cli>"]
    for v in cmd:
        raw_data = "%s%s%d%s%s%s" %(raw_data, S_BULK_STRINGS, len(v), CRLF, v, CRLF)
        output.append(v)
    print " ".join(output[i] for i in range(len(output)))
    return raw_data

def read_resp(s):
    data = []
    while True:
        block = s.recv(READ_BUFFER)
        data.append(block)
        if len(block) < READ_BUFFER:
            break
    #print len(''.join(data))
    return ''.join(data)


def parse_single_line_reply(data):
    i = 1
    seen_cr = 0
    dst_len = -2
    while i < len(data):
        if data[i] == '\r':
            seen_cr = 1
        elif seen_cr == 1:
            if data[i] == '\n':
                dst_len = i - 2
                return data[1:], dst_len
            seen_cr = 0
        i = i+1    
    return None, dst_len

def parse_bulk_reply(data):
    #print bytes.decode(data)
    if data == '$-1\r\n': #"$-1\r\n" represent None/NULL/nil
        return None, -1
    i = 1
    dst_len = 0
    seen_cr = 0
    while i < len(data):
        if data[i] != '\r':
            if data[i] > '9' or data[i] < '0':
                return None, -2
            dst_len = dst_len*10 + int(data[i])
        else:
            seen_cr = 1
            break
        i = i+1
    i = i+1
    if i >= len(data):
        return None, -2
    if seen_cr == 1 and data[i] != '\n':
        return None, -2
    if data[dst_len+i+1:dst_len+i+3] != '\r\n':
        return None, -2
    return data[1+len(str(dst_len))+2:], dst_len

def parse_multi_bulk_reply(data):
    #print "parse_multi_bulk_reply"
    if data == '*-1\r\n': #"*-1\r\n" represent None/NULL/nil
        return None, -1
    i = 1
    count = 0
    seen_cr = 0
    while i < len(data):
        if data[i] != '\r':
            if data[i] > '9' or data[i] < '0':
                return None, -2
            count = count*10 + int(data[i])
        else:
            seen_cr = 1
            break
        i = i+1
    i = i+1
    if seen_cr == 1 and data[i] != '\n':
        return None, -2
    bulks = []
    i = i+1
    for j in range(count):
        l = 0
        if data[i] == S_SIMPLE_STRING or data[i] == S_ERRORS or data[i] == S_INTEGERS:
            dst, dst_len = parse_single_line_reply(data[i:])

        elif data[i] == S_BULK_STRINGS:
            dst, dst_len = parse_bulk_reply(data[i:])
            l = len(str(dst_len))
            if dst_len > -1:
                l = l+2 #additional \r\n

        #elif data[i+1] == S_BULK_STRINGS:
            #dst, dst_len = parse_multi_bulk_reply(data[i:])
        else:
            return None, -2 #BAD REPLY

        if dst_len == -2:
            return None, -2
        elif dst_len == -1: #None
            bulks.append(None)
        else:
            #print dst[:dst_len]
            bulks.append(dst[:dst_len])
        i = i + dst_len + 3 + l #3 means [$+-:]\r\n, l means additional length for BULK_STRING 
    return bulks, len(bulks)

def parse_resp(data):
    if data[0] == S_SIMPLE_STRING:
        dst, dst_len = parse_single_line_reply(data)
        if dst_len == -2:
            return None, BAD_REPLY
        return dst[:dst_len], STATUS_REPLY
    elif data[0] == S_INTEGERS:
        dst, dst_len = parse_single_line_reply(data)
        if dst_len == -2:
            return None, BAD_REPLY
        return dst[:dst_len], INTEGER_REPLY
    elif data[0] == S_ERRORS:
        dst, dst_len = parse_single_line_reply(data)
        if dst_len == -2:
            return None, BAD_REPLY
        return dst[:dst_len], ERROR_REPLY
    elif data[0] == S_BULK_STRINGS:
        dst, dst_len = parse_bulk_reply(data)
        if dst_len == -2:
            return None, BAD_REPLY
        elif dst_len == -1:
            return None, BULK_REPLY
        return dst[:dst_len], BULK_REPLY
    elif data[0] == S_ARRAYS:
        bulks, dst_len = parse_multi_bulk_reply(data)
        if dst_len == -2:
            return None, BAD_REPLY
        return "\n".join(v for v in bulks), MULTI_BULK_REPLY

# TEST
address = ("127.0.0.1", 6379)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(address)

# status
t = ("SET", "name", "gerrard","EX", "10")
raw_data = parse_cmd(*t)
s.send(raw_data)
print parse_resp(read_resp(s))[0]

# error
t = ("HGETALL", "name")
raw_data = parse_cmd(*t)
s.send(raw_data)
print parse_resp(read_resp(s))[0]

# integer
t = ("TTL", "name")
raw_data = parse_cmd(*t)
s.send(raw_data)
print parse_resp(read_resp(s))[0]

# bulk string
t = ("GET", "name")
raw_data = parse_cmd(*t)
s.send(raw_data)
print parse_resp(read_resp(s))[0]

# arrays
#t = ("CONFIG", "GET", "*")
t = ("KEYS", "*")
raw_data = parse_cmd(*t)
s.send(raw_data)
print parse_resp(read_resp(s))[0]

s.close()
