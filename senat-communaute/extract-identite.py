#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
from SPARQLWrapper import SPARQLWrapper, JSON

path = "/home/sylvain/Dropbox/jeux de données/Archives du Sénat/"
filename = "senateurs_communaute_wd-identite.csv"


def wikidata_sparql_query(query):
    """
    Queries WDQS and returns the result
    """
    endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results


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
    text = text.replace('Correze', 'Corrèze')
    text = text.replace('Correze', 'Corrèze')
    text = re.compile('France (.*)').sub('France', text)
    return text


def get_qids():
    results = wikidata_sparql_query(
        """
        SELECT DISTINCT ?senateur ?senateurLabel ?idSenat ?dateNaissance
        ?debutMandat ?finMandat ?delegueparLabel ?groupeLabel {
        ?senateur wdt:P31 wd:Q5 .
        ?senateur wdt:P39 wd:Q20177062 .
        ?senateur wdt:P1808 ?idSenat .
        FILTER (SUBSTR(str(?idSenat), 1, 19) = "senateur-communaute")

        SERVICE wikibase:label {
        bd:serviceParam wikibase:language "fr" .
        }
        } ORDER BY ?idSenat
        """)

    senateurs = {}
    for r in results['results']['bindings']:
        name = r['senateurLabel']['value']
        idSenat = r['idSenat']['value']
        entity = r['senateur']['value']
        qid = (entity).split('/')[-1]
        senateurs[name] = {'qid': qid, 'idSenat': idSenat}

    return senateurs

senateurs = get_qids()
with open(path + filename, 'r') as csv_input:
    with open(path + 'out.csv', 'w') as csv_output:
        reader = csv.DictReader(csv_input)
        fieldnames = reader.fieldnames[:]
        fieldnames.remove("Année de naissance")
        fieldnames.remove("NOM TRI")
        fieldnames.append('qid')
        fieldnames.append('idSenat')
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

            name = "{} {}".format(row["PRENOM"], row["NOM"])
            if name in senateurs.keys():
                row['qid'] = senateurs[name]['qid']
                row['idSenat'] = senateurs[name]['idSenat']

            writer.writerow(row)
