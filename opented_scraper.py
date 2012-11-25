import requests
import json
from BeautifulSoup import BeautifulSoup, Tag
import os
import re, htmlentitydefs

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

baseurl = 'http://files.opented.org.s3.amazonaws.com/scraped/';
indexurl = 'http://files.opented.org.s3.amazonaws.com/scraped/index.json'
outdir = 'opented'
if not os.path.exists(outdir):
    os.makedirs(outdir)

def extract(text):
    soup = BeautifulSoup(text)
    grseq = soup.findAll("div", { "class" : "grseq" })
    info = []
    for seq in grseq:
        text = seq.text
        #print text
        if "Date of contract award" in text: # could be more winners
            entities = seq("div", {"class":"mlioccur"})
            contract_data = {}
            for ent in entities:
                if "NUMBER OF OFFERS RECEIVED" in ent.text:
                    divs = ent('div')
                    if divs:
                        number_of_offers = int(divs[0].text)
                        contract_data["number_of_offers"] = number_of_offers
                    else:
                        # empty information 
                        break
                if "NAME AND ADDRESS OF ECONOMIC OPERATOR" in ent.text:
                    contents = ent('div')[0]('p')[0].contents
                    winner_data = []
                    for c in contents:
                        if type(c) != Tag:
                            winner_data.append(c)
                    contract_data["winner"] = unescape(winner_data[0])
                    print unescape(winner_data[0])
                if "INFORMATION ON VALUE OF CONTRACT" in ent.text:
                    data = {}
                    data["value"] = "not available"
                    data["currency"] = "not available"
                    data["VAT"] = "not available"
                    try:
                        spans = ent('div')[0]('span')
                        for c in spans:
                            text = c.text
                            if "Value" in text:
                                vs = text.split(" ")
                                value = " ".join(vs[1:len(vs)-1]).strip()
                                data["value"] = value
                                currency = vs[len(vs)-1]
                                data["currency"] = currency
                                print "Value: %s" % value
                                print "Currency: %s" % currency
                            elif "VAT" in text:
                                data["VAT"] = text
                                print "VAT: %s" % text
                    except:
                        print "cannot extract value of contract"
                    contract_data["value"] = data
            info.append(contract_data)
    return info

r = requests.get(indexurl)
if(r.ok):
    rep = json.loads(r.text or r.content)
    for docid in rep:
        url = baseurl + docid + "/summary.html"
        print url
        rep = requests.get(url)
        if rep.ok:
            info = extract(rep.text)
            docdir = os.path.join(outdir, docid)
            if not os.path.exists(docdir):
                os.makedirs(docdir)
            path = os.path.join(docdir, '%s.json' % docid)
            json.dump(info, open(path, 'w'), indent=2, sort_keys=True)
            
"""
sample generated file:
[
  {
    "number_of_offers": 1, 
    "value": {
      "VAT": "Excluding VAT", 
      "currency": "EUR", 
      "value": "204 630,00"
    }, 
    "winner": "Fundaci\u00f3n CBD-Habitat"
  }, 
  {
    "number_of_offers": 1, 
    "value": {
      "VAT": "Excluding VAT", 
      "currency": "EUR", 
      "value": "62 800,00"
    }, 
    "winner": "Fundaci\u00f3n CBD-Habitat"
  }
]
"""

