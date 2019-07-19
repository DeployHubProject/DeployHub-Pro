"""This module interfaces with the DeployHub RestAPIs to perform login, deploy, move and approvals."""

import os
import re
import subprocess
import tempfile
import time
import urllib
from pprint import pprint

import qtoml
import requests
import yaml


def get_json(url, cookies):
    """ Get URL as json string.
        Returns: json string"""

    try:
        res = requests.get(url, cookies=cookies)
        if (res is None):
            return None
        if (res.status_code != 200):
            return None
        return res.json()
    except requests.exceptions.ConnectionError as conn_error:
        print(str(conn_error))
    return None


def is_empty(my_string):
    """Is the string empty"""
    return not (my_string and my_string.strip())


def is_not_empty(my_string):
    """Is the string NOT empty"""
    return bool(my_string and my_string.strip())


def login(dhurl, user, password):
    """Login to DeployHub using the DH Url, userid and password.
    Returns: cookies to be used in subsequent API calls"""
    try:
        result = requests.post(dhurl + "/dmadminweb/API/login", data={'user': user, 'pass': password})
        cookies = result.cookies
        if (result.status_code == 200):
            return cookies
    except requests.exceptions.ConnectionError as conn_error:
        print(str(conn_error))
    return None


def deploy_application(app, env, dhurl, cookies):
    """Deploy the application to the environment
    Returns: deployment_id"""
    return get_json(dhurl + "/dmadminweb/API/deploy/" + urllib.parse.quote(app) + "/" + urllib.parse.quote(env), cookies)


def move_application(app, from_domain, task, dhurl, cookies):
    """Move an application from the from_domain using the task"""
    # Get appid
    data = get_json(dhurl + "/dmadminweb/API/application/" + urllib.parse.quote(app), cookies)
    appid = str(data['result']['id'])

    # Get from domainid
    data = get_json(dhurl + "/dmadminweb/API/domain/" + urllib.parse.quote(from_domain), cookies)
    fromid = str(data['result']['id'])

    # Get from Tasks
    data = get_json(dhurl + "/dmadminweb/GetTasks?domainid=" + fromid, cookies)
    taskid = "0"

    for atask in data:
        if (atask['name'] == task):
            taskid = str(atask['id'])

    # Move App Version
    data = get_json(dhurl + "/dmadminweb/RunTask?f=run&tid=" + taskid + "&notes=&id=" + appid + "&pid=" + fromid, cookies)
    return(data)


def approve_application(app, dhurl, cookies):
    """Approve the application for the current domain that it is in."""
    # Get appid
    data = get_json(dhurl + "/dmadminweb/API/application/" + urllib.parse.quote(app), cookies)
    appid = str(data['result']['id'])

    data = get_json(dhurl + "/dmadminweb/API/approve/" + appid, cookies)
    return data


def is_deployment_done(deployment_id, dhurl, cookies):
    """Check to see if the deployment has completed"""
    data = get_json(dhurl + "/dmadminweb/API/log/" + deployment_id + "?checkcomplete=Y", cookies)

    if (data is None):
        return [False, "Could not get log #" + deployment_id]

    if (is_empty(data.text)):
        return [False, "Could not get log #" + deployment_id]

    return [True, data]


def get_logs(deployment_id, dhurl, cookies):
    """Get the logs for the deployment.
    Returns: log as a String"""

    while (True):
        res = is_deployment_done(deployment_id, dhurl, cookies)

        if (res[0] and res[1]['success'] and res[1]['iscomplete']):
            url = dhurl + "/dmadminweb/API/log/" + deployment_id
            res = requests.get(url, cookies=cookies)
            return res.json()

        time.sleep(10)


def get_attrs(app, comp, env, srv, dhurl, cookies):
    """Get the attributes for this deployment base on app version and env.
    Returns: json of attributes"""

    data = get_json(dhurl + "/dmadminweb/API/environment/" + urllib.parse.quote(env), cookies)
    envid = str(data['result']['id'])
    servers = data['result']['servers']

    data = get_json(dhurl + "/dmadminweb/API/getvar/environment/" + envid, cookies)
    env_attrs = data['attributes']

    for a_srv in servers:
        if (srv == a_srv['name']):
            srvid = str(a_srv['id'])
            data = get_json(dhurl + "/dmadminweb/API/getvar/server/" + srvid, cookies)
            srv_attrs = data['attributes']
            break

    data = get_json(dhurl + "/dmadminweb/API/application/" + app, cookies)

    if (app == data['result']['name']):
        appid = str(data['result']['id'])
    else:
        for a_ver in data['result']['versions']:
            if (app == a_ver['name']):
                appid = str(a_ver['id'])
                break

    data = get_json(dhurl + "/dmadminweb/API/getvar/application/" + appid, cookies)
    app_attrs = data['attributes']

    data = get_json(dhurl + "/dmadminweb/API/component/" + comp, cookies)
    compid = str(data['result']['id'])

    data = get_json(dhurl + "/dmadminweb/API/getvar/component/" + compid, cookies)
    comp_attrs = data['attributes']

    result = {}
    for entry in env_attrs:
        result.update(entry)

    for entry in srv_attrs:
        result.update(entry)

    for entry in app_attrs:
        result.update(entry)

    for entry in comp_attrs:
        result.update(entry)

    return result


def find_domain(findname, dhurl, cookies):
    """Get the domain name and id that matches best with the passed in name"""

    data = get_json(dhurl + "/dmadminweb/GetAllDomains", cookies)
    for dom in data:
        child = dom['name'].split('.')[-1]
        if (child == findname):
            return dom
        else:
            child = child.replace(" ", "").lower()
            if (child == findname):
                dom['name'] = 'GLOBAL.Chasing Horses LLC.' + dom['name']
                return dom
    return None


def get_component(compname, compvariant, compversion, dhurl, cookies):
    """Get the component object based on the component name and variant.
    Returns: component id of the found component otherwise None"""

    data = get_json(dhurl + "/dmadminweb/API/component/" + urllib.parse.quote(compname) + "?compvariant=" + urllib.parse.quote(compvariant), cookies)

    if ('.' in compname):
        parts = compname.split('.')
        compname = parts[-1]
    parent = (None, None)

    if ('result' in data and 'versions' in data['result']):
        versions = data['result']['versions']

        # find latest component that matches the compname;compvariant
        for ver in versions:
            if ((ver['name'].count(';') == 2 and (compname + ";" + compvariant + ";") in ver['name']) or (ver['name'].count(';') == 1 and (compname + ";" + compvariant) in ver['name'])):
                parent = (ver['id'], ver['name'])

            if (compversion is not None):
                if ((compname + ";" + compvariant + ";" + compversion) == ver['name']):
                    parent = (ver['id'], ver['name'])
                    break

    if (parent is None and ('result' in data and 'id' in data['result'])):
        parent = (data['result']['id'], data['result']['name'])

    return parent


def update_name(compname, compvariant, compversion, compid, dhurl, cookies):
    if ('.' in compname):
        parts = compname.split('.')
        compname = parts[-1]

    if (compversion is None):
        data = get_json(dhurl + "/dmadminweb/UpdateSummaryData?objtype=23&id=" + str(compid) + "&change_1=" + urllib.parse.quote(compname + ";" + compvariant), cookies)
    else:
        data = get_json(dhurl + "/dmadminweb/UpdateSummaryData?objtype=23&id=" + str(compid) + "&change_1=" + urllib.parse.quote(compname + ";" + compvariant + ";" + compversion), cookies)

    return data


def new_component_item(compid, kind, dhurl, cookies):
    """Create the component item for the component.
    Returns: component item id of the new component otherwise None"""
    data = get_json(dhurl + "/dmadminweb/UpdateAttrs?f=inv&c=" + str(compid) + '&xpos=100&ypos=100&kind=' + kind, cookies)
    return data


def new_component_version(compname, compvariant, compversion, kind, dhurl, cookies):
    # Get latest version of compnent variant
    (compid, found_compname) = get_component(compname, compvariant, compversion, dhurl, cookies)

    # Create base component variant if one is not found
    # Get the new compid of the new component variant
    if (compid is None):
        compid = new_component(compname, compvariant, None, None, compid, dhurl, cookies)

    if ('.' in compname):
        parts = compname.split('.')
        short_compname = parts[-1]
    # Create new version of component variant base on latest comp variant
    # Get the new compid for the new version of the component variant
    if (found_compname is None or found_compname != (short_compname + ";" + compvariant + ";" + compversion)):
        compid = new_component(compname, compvariant, compversion, kind, compid, dhurl, cookies)

    return compid


def new_component(compname, compvariant, compversion, kind, parent_compid, dhurl, cookies):
    """Create the component object based on the component name and variant.
    Returns: component id of the new component otherwise None"""

    # Create base version
    if (parent_compid is None):
        data = get_json(dhurl + "/dmadminweb/API/new/compver/" + urllib.parse.quote(compname + ";" + compvariant), cookies)
        compid = data['result']['id']
    else:
        data = get_json(dhurl + "/dmadminweb/API/new/compver/" + str(parent_compid), cookies)
        compid = data['result']['id']

    update_name(compname, compvariant, compversion, compid, dhurl, cookies)

    if (kind is not None):
        new_component_item(compid, kind, dhurl, cookies)

    return compid


def update_component_attrs(compid, compattr, dhurl, cookies):
    attr_str = ""

    data = None
    count = 0
    for attr in (compattr):
        (key, value) = attr.split('=')

        if (count == 0):
            attr_str = attr_str + "name=" + urllib.parse.quote(key) + "&value=" + urllib.parse.quote(value)
        else:
            attr_str = attr_str + "&name" + str(count) + "=" + urllib.parse.quote(key) + "&value" + str(count) + "=" + urllib.parse.quote(value)

        count = count + 1

    if (attr_str):
        data = get_json(dhurl + "/dmadminweb/API/setvar/component/" + str(compid) + "?" + attr_str, cookies)

    return data


def clone_repo(project):
    print("### Grabbing features.toml ###")

    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)
    print(tempdir)

    pid = subprocess.Popen('git clone -q git@github.com:' + project + '.git .', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in pid.stdout.readlines():
        print(line)
        pid.wait()

    data = None
    if (not os.path.exists("features.toml")):
        print("features.toml not found")
        return data

    with open("features.toml", "r") as fin:
        tmpstr = fin.read()
        data = qtoml.loads(tmpstr)
    return data


def import_cluster(kubeyaml, defaultdomain, dhurl, cookies):
    newvals = {}
    complist = []

    if (os.path.exists(kubeyaml)):
        stream = open(kubeyaml, 'r')
        values = yaml.load(stream)
        newvals.update(values)
        stream.close()

        for item in newvals['items']:
            appname = item['metadata']['namespace']
            if ('default' in appname):
                appname = defaultdomain.split('.')[-1] + ' App'
            compname = item['metadata']['name']
            dom = find_domain(compname, dhurl, cookies)
            if (dom is None):
                compname = defaultdomain + '.' + compname
            else:
                compname = dom['name'] + '.' + compname
            image_tag = item['spec']['template']['spec']['containers'][0]['image']
            if ('@' in image_tag):
                (image, image_sha) = image_tag.split('@')
                image_sha = image_sha.split(':')[-1]
                (image, tag) = image.split(':')
                version = ""
                gitcommit = ""

                if ('-g'in tag):
                    (version, gitcommit) = re.split(r'-g', tag)

                compattr = []
                compattr.append('DockerRepo=' + image)
                compattr.append('DockerSha=' + image_sha)
                compattr.append('GitCommit=' + gitcommit)
                comp = {'project': appname, 'compname': compname, 'compvariant': version, 'compversion': 'g' + gitcommit, 'compattr': compattr}
                complist.append(comp)

    return complist


def update_versions(project, compname, compvariant, compversion):
    # Clone apprepo
    data = clone_repo(project)
    if (data is not None):
        pprint(data)
