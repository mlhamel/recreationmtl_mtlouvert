import urllib
import lxml.html
from lxml.html import fromstring
import json

URL = "http://ville.montreal.qc.ca/portal/page?_pageid=7317,78925591&_dad=portal&_schema=PORTAL"

def parse(elements):
    pools = []
    for e in elements:
        pool = {}
        pools.append(pool)

        #i = 0
        #header = e
        #while i <= 3:
            #header = header.getprevious()
            #print header.tag
            #if header.tag != "p":
                #i += 1
        #name = header.text_content()

        name = e.getprevious().getprevious().getprevious().text_content()

        pool["name"] = name

        horaire = pool["horaire"] = []
        categorie = {}


        for row in e.find("tbody").cssselect("tr"):
            td = row.cssselect("td")

            if len(td) == 1:
                age = td[0].text_content().strip()

                print age
                if categorie:
                    horaire.append(categorie)
                categorie = {"age": age}

            elif len(td) == 2:
                jour = td[0].text_content().strip()
                #TODO separer les plage horraies quand il y en a plus qu'une
                heure = td[1].text_content().strip()
                #heure = lxml.html.tostring(td[1].find('p')).replace('<br>', ',')
                categorie[jour] = heure

            elif len(td) == 3:
                age = td[0].text_content().strip()
                jour =  td[1].text_content().strip()
                heure = td[2].text_content().strip()

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
    #print pools
    with open('horaires.json', 'w') as out:
        out.write(json.dumps(pools, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    main()
