# coding=utf-8
from owslib.csw import CatalogueServiceWeb
from owslib import fes

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/14/16'


def csw_query_metadata_by_id(
        csw_url, identifier, username=None, password=None):
    csw = CatalogueServiceWeb(
        csw_url,
        username=username,
        password=password)
    result = csw.identification.type
    record = None
    if result == 'CSW':
        constraints = [
            fes.PropertyIsEqualTo(
                'dc:identifier', identifier)
        ]
        csw.getrecords2(
            typenames='gmd:MD_Metadata',
            esn='full',
            outputschema='http://www.isotc211.org/2005/gmd',
            constraints=constraints)
        for key in csw.records:
            record = csw.records[key]
    return record
