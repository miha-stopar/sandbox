#coding: utf8 
import pandas

col_names = ['doc_id', 'pub_year', 'year_sn', 'title', 'oj_ed', 'cpv_code', 'orig_cpv_code', 'pub_date', 'country', 'auth_type', 'auth_name', 'doc_type', 'contract_type', 'proc_type']
frame = pandas.read_csv('/home/miha/Desktop/opented.csv', names=col_names)

def is_same_name(prev_name, name):
    to_be_replaced = [",", "\\", "-", "–", ";"]
    if type(name) == float or type(prev_name) == float:
        return False
    cleaned_name = name.lower()
    for d in to_be_replaced:
        cleaned_name = cleaned_name.replace(d, " ") 
    tokens = cleaned_name.split()
    cleaned_prev = prev_name.lower()
    for d in to_be_replaced:
        cleaned_prev = cleaned_prev.replace(d, " ") 
    prev_tokens = cleaned_prev.split()
    a = set(tokens)
    b = set(prev_tokens)
    diff1 = a.difference(b)
    diff2 = b.difference(a)
    if (len(diff1) > 0 or len(diff2) > 0):
        return False
    else: 
        return True
   
count = 0
for ind, name in enumerate(frame['auth_name']):
    if ind == 0 or ind == 1:
        continue
    prev_name = frame['auth_name'][ind-1]
    is_same = is_same_name(prev_name, name)
    if is_same and name != prev_name: #it represents the same entity, but the names are slightly different
        #print "is the same ============================="
        print name
        print prev_name
        print "-----------------------------------"
        count += 1
        frame['auth_name'][ind] = prev_name
frame.to_csv("/home/miha/Desktop/new_opented.csv", index=False, header=False) # wait to be finished - this can take a while
print "number of duplicates: %s" % count
    









