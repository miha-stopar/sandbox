#coding: utf8 
import pandas

frame = pandas.read_csv('/home/miha/Desktop/opented.csv', names=['doc_id', 'pub_year', 'year_sn', 'title', 'oj_ed', 'cpv_code', 'orig_cpv_code', 'pub_date', 'country', 'auth_type', 'auth_name', 'doc_type', 'contract_type', 'proc_type'])

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
    #print "blaa: %s, %s" % (count1, len(tokens))
    #print "blaa: %s, %s" % (count2, len(prev_tokens))
    a = set(tokens)
    b = set(prev_tokens)
    diff1 = a.difference(b)
    diff2 = b.difference(a)
    #print diff1
    #print diff2
    s1, s2 = False, False # if difference contains at least one capitalized word 
    for i in diff1:
        cap = i[0].upper() + i[1:]
        if cap in name or i.upper() in name:
            s1 = True
            break
    for i in diff2:
        cap = i[0].upper() + i[1:]
        if cap in prev_name or i.upper() in prev_name:
            s2 = True
            break
    # diff_cap means that both names contain at least one capitalized word that is not in the other one
    # change or -> and to find more duplicates - but some might won't be the proper duplicates - 
    # for example "EDF" and "EDF SA" - I don't know if this is the same or not
    diff_cap = s1 or s2
    # diff_cap = diff_cap or max(len(diff1), len(diff2)) > 1): # this makes less restrictive condition
    if (len(diff1) > 0 or len(diff2) > 0):# and diff_cap:
        return False
    else: 
        return True
   
count = 0
for ind, name in enumerate(frame['auth_name']):
    if ind == 0:
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
print "number of duplicates: %s" % count
frame.to_csv("new_opented.csv")    
    







