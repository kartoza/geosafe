# coding=utf-8
import json
import os

import shutil
import logging
import urlparse

from django.http.response import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from owslib.wcs import WebCoverageService

from geonode.layers.utils import file_upload
from geosafe.tasks.analysis import download_file
from owslib import fes
from owslib.csw import CatalogueServiceWeb, CswRecord

from geosafe.forms import MetaSearchForm
from geosafe.tasks import metasearch

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'

__date__ = '7/28/16'

LOGGER = logging.getLogger(__name__)


def index(request, *args, **kwargs):
    result = None
    if request.method == 'POST':
        form = MetaSearchForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['csw_url']
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            keywords = form.cleaned_data['keywords']
            keywords_query = [fes.PropertyIsLike(
                'csw:AnyText', '%%%s%%' % keywords)]
            try:
                csw = CatalogueServiceWeb(
                    url,
                    username=user,
                    password=password)
                result = csw.identification.type
                if result == 'CSW':
                    csw.getrecords2(
                        constraints=keywords_query)
                    result = []
                    for key in csw.records:
                        rec = csw.records[key]
                        if isinstance(rec, CswRecord):
                            # iterate Reference
                            for v in rec.references:
                                if 'OGC:WCS' in v['scheme']:
                                    rec.type = 'OGC:WCS'
                                    result.append(rec)
                                    break
                                if 'OGC:WFS' in v['scheme']:
                                    rec.type = 'OGC:WFS'
                                    result.append(rec)

                    template = 'geosafe/metasearch/metasearch_result.html'
            except Exception as e:
                LOGGER.exception(e)
                return HttpResponseServerError()

    else:
        form = MetaSearchForm()
        template = 'geosafe/metasearch/metasearch.html'

    context = {
        'form': form,
        'result': result
    }
    return render(request, template, context)


def show_add_layer_dialog(request, *args, **kwargs):
    if request.method == 'POST':
        csw_url = request.POST['csw_url']
        user = request.POST['user']
        password = request.POST['password']
        layer_id = request.POST['layer_id']
        try:
            csw = CatalogueServiceWeb(
                csw_url,
                username=user,
                password=password)
            constraints = [
                fes.PropertyIsEqualTo(
                    'dc:identifier', layer_id)
            ]
            result = csw.identification.type
            if result == 'CSW':
                csw.getrecords2(constraints=constraints)
                record = None
                for key in csw.records:
                    rec = csw.records[key]
                    for ref in rec.references:
                        if 'OGC:WCS' in ref['scheme']:
                            rec.type = 'WCS'
                            rec.endpoint = ref['url']
                            record = rec
                            break
                        if 'OGC:WFS' in ref['scheme']:
                            rec.type = 'WFS'
                            rec.endpoint = ref['url']
                            record = rec
                            break
                    if record:
                        break

                if record.type == 'WCS':
                    # get describe coverage
                    # find coverage id from references
                    coverage_id = None
                    version = None
                    for ref in record.references:
                        if 'service=WCS' in ref['url']:
                            url = ref['url']
                            parse_result = urlparse.urlparse(url)
                            query = parse_result.query
                            query_dict = urlparse.parse_qs(query)
                            coverage_id = query_dict['coverageid'][0]
                            version = query_dict['version'][0]
                            if coverage_id and version:
                                break
                    record.service_id = coverage_id
                    record.service_version = version
                elif record.type == 'WFS':
                    typename = None
                    version = None
                    for ref in record.references:
                        if 'service=WFS' in ref['url']:
                            url = ref['url']
                            parse_result = urlparse.urlparse(url)
                            query = parse_result.query
                            query_dict = urlparse.parse_qs(query)
                            typename = query_dict['typename'][0]
                            version = query_dict['version'][0]
                            if typename and version:
                                break

                    record.service_id = typename
                    record.service_version = version
                #     wcs = WebCoverageService(record.endpoint)
                #     result = wcs.getDescribeCoverage(coverage_id)
                context = {
                    'record': record
                }
                return render(
                    request,
                    'geosafe/metasearch/modal/add_layer.html',
                    context)
        except Exception as e:
            return HttpResponseServerError()


def add_layer(request, *args, **kwargs):
    result = {
        'success': False
    }
    if request.method == 'POST':
        endpoint = request.POST['endpoint']
        type = request.POST['type']
        user = request.POST['user']
        password = request.POST['password']
        identifier = request.POST['identifier']
        service_id = request.POST['service_id']
        service_version = request.POST['service_version']
        minx = request.POST['minx']
        miny = request.POST['miny']
        maxx = request.POST['maxx']
        maxy = request.POST['maxy']
        bbox = [
            minx, miny,
            maxx, maxy
        ]
        try:
            if type == 'WCS':
                metasearch.add_wcs_layer.delay(
                    endpoint,
                    service_version,
                    service_id,
                    bbox=bbox,
                    user=user, password=password)
            elif type == 'WFS':
                # bbox = (
                #     float(minx), float(miny),
                #     float(maxx), float(maxy)
                # )
                metasearch.add_wfs_layer.delay(
                    endpoint,
                    service_version,
                    service_id,
                    bbox=bbox,
                    user=user, password=password)
            result['success'] = True
        except Exception as e:
            pass
    return HttpResponse(
        json.dumps(result), content_type='application/json')
