"""
Parses data from a MAG API response (JSON format). There are modules to parse papers, affiliations journals, fields of study and authors.
"""
import json
import logging
import numpy as np
from ci_mapping.utils.utils import inverted2abstract


def parse_papers(response):
    """Parse paper information from a MAG API response.

    Args:
        response (json): Response from MAG API in JSON format. Contains paper information.

    Returns:
        d (dict): Paper metadata.

    """
    remappings = {
        "id": "Id",
        "prob": "prob",
        "title": "Ti",
        "publication_type": "Pt",
        "year": "Y",
        "date": "D",
        "citations": "CC",
    }

    d = {k: response[v] for k, v in remappings.items()}

    # Some MAG fields might be empty - replace empty values with np.nan
    try:
        d["doi"] = response["DOI"]
    except KeyError as e:
        # logging.info(f"{response['Id']}: {e}")
        d["doi"] = np.nan
    try:
        d["bibtex_doc_type"] = response["BT"]
    except KeyError as e:
        # logging.info(f"{response['Id']}: {e}")
        d["bibtex_doc_type"] = np.nan
    try:
        d["references"] = json.dumps(response["RId"])
    except KeyError as e:
        # logging.info(f"{response['Id']}: {e}")
        d["references"] = np.nan
    try:
        d["abstract"] = inverted2abstract(response["IA"])
    except KeyError as e:
        # logging.info(f"{response['Id']}: {e}")
        d["abstract"] = np.nan
    try:
        d["publisher"] = response["PB"]
    except KeyError as e:
        # logging.info(f"{response['Id']}: {e}")
        d["publisher"] = np.nan

    return d


def parse_conference(response, paper_id):
    """Parse conference information from a MAG API response.

    Args:
        response (json): Response from MAG API in JSON format. Contains all paper information.
        paper_id (int): Paper ID.

    Returns:
        d (dict): Conference details.

    """
    return {
        "id": response["C"]["CId"],
        "conference_name": response["C"]["CN"],
        "paper_id": paper_id,
    }


def parse_journal(response, paper_id):
    """Parse journal information from a MAG API response.

    Args:
        response (json): Response from MAG API in JSON format. Contains all paper information.
        paper_id (int): Paper ID.

    Returns:
        d (dict): Journal details.

    """
    return {
        "id": response["J"]["JId"],
        "journal_name": response["J"]["JN"],
        "paper_id": paper_id,
    }


def parse_authors(response, paper_id):
    """Parse author information from a MAG API response.

    Args:
        response (json): Response from MAG API in JSON format. Contains all paper information.
        paper_id (int): Paper ID.

    Returns:
        authors (:obj:`list` of :obj:`dict`): List of dictionaries with author information.
            There's one dictionary per author.
        paper_with_authors (:obj:`list` of :obj:`dict`): Matching paper and author IDs.

    """
    authors = []
    paper_with_authors = []
    for author in response["AA"]:
        # mag_paper_authors
        paper_with_authors.append(
            {"paper_id": paper_id, "author_id": author["AuId"], "order": author["S"]}
        )
        # mag_authors
        authors.append({"id": author["AuId"], "name": author["DAuN"]})

    return authors, paper_with_authors


def parse_fos(response, paper_id):
    """Parse the fields of study of a paper from a MAG API response.

    Args:
        response (json): Response from MAG API in JSON format. Contains all paper information.
        paper_id (int): Paper ID.

    Returns:
        fields_of_study (:obj:`list` of :obj:`dict`): List of dictionaries with fields of study information.
            There's one dictionary per field of study.
        paper_with_fos (:obj:`list` of :obj:`dict`): Matching fields of study and paper IDs.

    """
    # two outputs: fos_id with fos_name, fos_id with paper_id
    paper_with_fos = []
    fields_of_study = []
    for fos in response["F"]:
        # mag_fields_of_study
        fields_of_study.append(
            {"id": fos["FId"], "name": fos["DFN"], "norm_name": fos["FN"]}
        )
        # mag_paper_fields_of_study
        paper_with_fos.append({"field_of_study_id": fos["FId"], "paper_id": paper_id})

    return paper_with_fos, fields_of_study


def parse_affiliations(response, paper_id):
    """Parse the author affiliations from a MAG API response.

    Args:
        response (json): Response from MAG API in JSON format. Contains all paper information.
        paper_id (int): Paper ID.

    Returns:
        affiliations (:obj:`list` of :obj:`dict`): List of dictionaries with affiliation information.
            There's one dictionary per field of study.
       author_with_aff (:obj:`list` of :obj:`dict`): Matching affiliation and author IDs.

    """
    affiliations = []
    paper_author_aff = []
    for aff in response["AA"]:
        if aff["AfId"]:
            # mag_author_affiliation
            paper_author_aff.append(
                {
                    "affiliation_id": aff["AfId"],
                    "author_id": aff["AuId"],
                    "paper_id": paper_id,
                }
            )
            # mag_affiliation
            affiliations.append({"id": aff["AfId"], "affiliation": aff["AfN"]})
        else:
            paper_author_aff.append(
                {
                    "affiliation_id": None,
                    "author_id": aff["AuId"],
                    "paper_id": paper_id,
                }
            )
    return affiliations, paper_author_aff
