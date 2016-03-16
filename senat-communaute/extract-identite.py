#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re

path = "/home/sylvain/Dropbox/jeux de données/Archives du Sénat/"
filename = "senateurs_communaute_wd-identite.csv"


def date_qs(date):
    date_fields = date.split('/')
    if len(date_fields) == 1:
        return "+0000000{}-00-00T00:00:00Z/09".format(date_fields[0])
    elif len(date_fields) == 3:
        return "+0000000{}-{}-{}T00:00:00Z/11".format(date_fields[2],
                                                      date_fields[1],
                                                      date_fields[0])
    else:
        return ""


def cleaner(text):
    text = text.title()
    text = text.replace('Republique', 'République')
    text = text.replace('Senat', 'Sénat')
    text = text.replace('Assemblee', 'Assemblée')
    text = text.replace('Legislative', 'législative')
    text = text.replace('Nationale', 'nationale')
    text = text.replace('Centrafricain', 'centrafricain',)
    text = text.replace('Francais', 'français',)
    text = text.replace('Gabonais', 'gabonais',)
    text = text.replace('Islamique', 'islamique',)
    text = text.replace('Malgache', 'malgache',)
    text = text.replace("Cote D'Ivoire", "Côte d'Ivoire",)
    text = text.replace(' Du ', ' du ')
    text = text.replace(' De ', ' de ')
    text = text.replace(' La ', ' la ')
    text = text.replace(' Et ', ' et ')
    text = text.replace('-Et-', '-et-')
    text = re.compile('France (.*)').sub('France', text)
    return text

with open(path + filename, 'r') as csv_input:
    with open(path + 'out.csv', 'w') as csv_output:
        reader = csv.DictReader(csv_input)
        fieldnames = reader.fieldnames[:]
        fieldnames.remove("Année de naissance")
        fieldnames.remove("NOM TRI")
        writer = csv.DictWriter(csv_output,
                                fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()
        for row in reader:
            row["NOM"] = row['NOM'].title()
            row["SENATEUR DELEGUE PAR"] = cleaner(row["SENATEUR DELEGUE PAR"])
            row["PAYS"] = cleaner(row['PAYS'])
            row["DEPARTEMENT"] = cleaner(row['DEPARTEMENT'])
            row["GROUPE"] = cleaner(row['GROUPE'])
            row["Date de désignation"] = date_qs(row["Date de désignation"])
            row["Fin de mandat"] = date_qs(row["Fin de mandat"])
            if row["Année de naissance"].strip() != "null":
                row["Date de naissance"] = date_qs(row["Année de naissance"])
            else:
                row["Date de naissance"] = date_qs(row["Date de naissance"])
            writer.writerow(row)
