import urllib
import lxml.html
from lxml.html import fromstring
import json
import re
import HTMLParser

URL = "http://ville.montreal.qc.ca/portal/page?_pageid=7317,78925591&_dad=portal&_schema=PORTAL"

def strip_tags(input):
    # unescape html entities
    html_parser = HTMLParser.HTMLParser()
    input = html_parser.unescape(input)
    # strip consecutive white spaces
    exp = re.compile(r'\s+')
    input = exp.sub(' ', input)
    # strip tags
    exp = re.compile(r'<.*?>')
    return exp.sub('', input)


def parse(elements):
    pools = []
    for e in elements:
        pool = {}
        pools.append(pool)

        i = 0
        header = e
        while i <= 2:
            header = header.getprevious()
            if header.text_content() != '':
                i += 1

        name = header.text_content()
        name = name.replace('\r\n', '')

        pool["name"] = name

        horaire = pool["horaire"] = []
        categorie = {}


        for row in e.find("tbody").cssselect("tr"):
            td = row.cssselect("td")

            if len(td) == 1:
                age = td[0].text_content().strip()

                if categorie:
                    horaire.append(categorie)
                categorie = {"age": age}

            elif len(td) == 2:
                jour = td[0].text_content().strip()
                heure = td[1]

                if heure.find('p') is not None:
                    heure = lxml.html.tostring(heure.find('p'))
                    heure = heure.replace('<br>', ', ')
                    heure = heure.replace('\r\n', '')
                    heure = strip_tags(heure)
                else:
                    heure = lxml.html.tostring(heure)
                    heure = heure.replace('<br>', ', ')
                    heure = heure.replace('\r\n', '')
                    heure = strip_tags(heure)

                categorie[jour] = heure

            elif len(td) == 3:
                age = td[0].text_content().strip()
                jour =  td[1].text_content().strip()
                heure = td[2].text_content().replace('\r\n', '').strip()


                if categorie:
                    horaire.append(categorie)

                categorie = {
                            "age": age,
                            jour: heure
                        }

        if categorie:
            horaire.append(categorie)

    return pools


def main():
    page = urllib.urlopen(URL)
    doc = fromstring(page.read())
    pools = parse(doc.cssselect(".tabDonnees"))
    with open('horaires.json', 'w') as out:
        out.write(json.dumps(pools, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
