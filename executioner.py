#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import logging
import time
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template, request
from socket import gethostname

"""
 Logging Level - Value
 #############   #####
 CRITICAL        50
 ERROR           40
 WARNING         30
 INFO            20
 DEBUG           10
 NOTSET          0
"""
LOG_FORMAT = '[%(levelname)s][%(filename)s:%(lineno)s][%(funcName)s()]:\t%(message)s'
LOG_LEVEL = logging.DEBUG

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(stdout_handler)
app = Flask(__name__)


class MyCommand:
    """
    """
    log_prefix = "COMMAND"
    FILE_PREFIX = "commandtab"
    GET_KEY = "command_name"

    def __init__(self, name, cmdline):
        self.name = name
        self.cmdline = cmdline
        self.last_output = ""
        logger.debug("[%s:%s] Created new command object [%s]" % (self.log_prefix, self.name, self.cmdline))

    def execute(self):
        logger.info("Executing command [%s]" % self.cmdline)
        logger.info("Working directory is [%s]" % my_cwd)
        self.last_output = subprocess.check_output(self.cmdline,
                                                   stderr=subprocess.STDOUT,
                                                   cwd=my_cwd,
                                                   shell=True).decode("utf-8")
        logger.info("Returned: [%s]" % self.last_output)
        return self.last_output


class MyService:
    log_prefix = "SERVICE"
    FILE_PREFIX = "servicetab"
    GET_KEY = "service_name"
    
    command_status = "systemctl status %s 2>&1 >/dev/null; echo $?"
    command_start = "systemctl start %s 2>&1 >/dev/null; echo $?"
    command_stop = "systemctl stop %s 2>&1 >/dev/null; echo $?"

    def __init__(self, name, conflicts_with):
        self.name = name

        if len(conflicts_with) == 0:
            self.conflicts_with = []
        else:
            self.conflicts_with = conflicts_with

        logger.debug("[%s:%s] Created new service object.  Conflicts with:" % (self.log_prefix, self.name))
        for conflict_element in self.conflicts_with:
            logger.debug("[%s:%s]\t\t\t%s" % (self.log_prefix, self.name, conflict_element))

    def get_status(self):
        logger.debug("[%s:%s] Retrieving status..." % (self.log_prefix, self.name))
        status = int(subprocess.check_output(self.command_status % self.name, stderr=subprocess.STDOUT,
                                             shell=True).decode("utf-8"))
        logger.debug("[%s:%s] Retrieved status is [%d]" % (self.log_prefix, self.name, status))
        return status

    def start(self):
        logger.info("[%s:%s] Starting service..." % (self.log_prefix, self.name))

        affected_services = self.stop_conflicting()

        subprocess.check_output(self.command_start % self.name, stderr=subprocess.STDOUT, shell=True)
        affected_services.append(self.name)
        return affected_services 

    def stop(self):
        logger.info("[%s:%s] Stopping service..." % (self.log_prefix, self.name))
        subprocess.check_output(self.command_stop % self.name, stderr=subprocess.STDOUT, shell=True)
        return [self.name]

    def stop_conflicting(self):
        stopped_conflicted_srvs = []
        for conflicting_srv in self.conflicts_with:
            service_elem, _ = find_elem_in_tabs(conflicting_srv, all_tabs)
            if (service_elem is not None) and service_elem.get_status() == 0:
                logger.info("[%s:%s] Stopping conflicting service: %s" % (self.log_prefix, self.name, conflicting_srv))
                service_elem.stop()
                stopped_conflicted_srvs.append(service_elem.name)
        return stopped_conflicted_srvs

    def restart(self):
        self.stop()
        self.start()


class MyTab:
    """
    """
    def __init__(self, name, elements, tab_type):
        self.name = name
        self.elements = elements
        self.tab_type = tab_type
        self.active = False

    def set_active(self):
        self.active = True

    def set_inactive(self):
        self.active = False


# Auxiliary functions
def find_elem_in_tabs(wanted_element_name, list_of_tabs):
    for tab in list_of_tabs:
        for element in tab.elements:
            if wanted_element_name == element.name:
                logger.debug("[%s] Found under tab [%s]" % (element.name, tab.name))
                return element, tab
    logger.debug("Element [%s] not found" % wanted_element_name)
    return None, None


def parse_tabs_from_xml(xmlfile):
    list_of_tabs = []

    tree = None
    try:
        tree = ET.parse(xmlfile)
    except ImportError:
        logger.error("File not found: [%s]" % xmlfile)
        exit(2)
        # logger.error("%s" % str(my_exception), exc_info=True)

    tree_root = tree.getroot()

    # Parse service tabs
    for service_tab in tree_root.findall(MyService.FILE_PREFIX):
        tab_caption = service_tab.get("caption")
        services = []

        for service in service_tab.findall("service"):
            service_name = service.get("name")

            conflicts = []
            for conflict in service.findall("conflict"):
                conflict_name = conflict.get("name")
                conflicts.append(conflict_name)

            my_service = MyService(service_name, conflicts)
            services.append(my_service)

        my_tab = MyTab(tab_caption, services, MyService.FILE_PREFIX)
        list_of_tabs.append(my_tab)

    # Parse command tabs
    for command_tab in tree_root.findall(MyCommand.FILE_PREFIX):
        tab_caption = command_tab.get("caption")
        commands = []

        for command in command_tab.findall("command"):
            command_caption = command.get("caption")
            command_line = command.get("line")
            my_command = MyCommand(command_caption, command_line)
            commands.append(my_command)

        my_tab = MyTab(tab_caption, commands, MyCommand.FILE_PREFIX)
        list_of_tabs.append(my_tab)
    return list_of_tabs


def affected_srvs_to_dict(service_list):
    result_dict = {}
    for my_service in service_list:
        service_elem, _ = find_elem_in_tabs(my_service, all_tabs)
        result_dict[my_service] = service_elem.get_status()
    return result_dict


# Flask paths
@app.route('/')
def executioner():
    return render_template('executioner.html')


# GET endpoints
@app.route('/srv_restart/', methods=['GET'])
def service_restart():
    restart_delay = 2
    service_name = request.args.get('service_name')
    logger.info("Received data [%s] from client" % service_name)
    
    found_element, found_tab = find_elem_in_tabs(service_name, all_tabs)
    
    affected_services = found_element.stop()
    logger.info(affected_srvs_to_dict(affected_services))

    logger.info("Waiting %d seconds(s) before starting service again..." % restart_delay)
    time.sleep(restart_delay)

    affected_services = found_element.start()
    logger.info(affected_srvs_to_dict(affected_services))

    return jsonify(affected_srvs_to_dict(affected_services))


@app.route('/srv_start/', methods=['GET'])
def service_start():
    service_name = request.args.get('service_name')
    logger.info("Received data [%s] from client" % service_name)
    
    found_element, found_tab = find_elem_in_tabs(service_name, all_tabs)
    affected_services = found_element.start()
    logger.info(affected_srvs_to_dict(affected_services))
    return jsonify(affected_srvs_to_dict(affected_services))


@app.route('/srv_stop/', methods=['GET'])
def service_stop():
    service_name = request.args.get('service_name')
    logger.debug("Received data [%s] from client" % service_name)
    
    found_element, found_tab = find_elem_in_tabs(service_name, all_tabs)
    affected_services = found_element.stop()
    logger.info(affected_srvs_to_dict(affected_services))
    return jsonify(affected_srvs_to_dict(affected_services))


@app.route('/cmd_exec/', methods=['GET'])
def command_execute():
    command_name = request.args.get('command_name')
    logger.debug("Received data execute=[%s] from client" % command_name)
    found_element, found_tab = find_elem_in_tabs(command_name, all_tabs)
    execution_result = found_element.execute()
    return jsonify({command_name: execution_result})


@app.route('/cmd_last_output/', methods=['GET'])
def command_last_output():
    command_name = request.args.get('command_name')
    logger.debug("Received data last_output=[%s] from client" % command_name)
    found_element, found_tab = find_elem_in_tabs(command_name, all_tabs)
    return jsonify({command_name: found_element.last_output})


@app.route('/cmd_clear/', methods=['GET'])
def command_clear():
    command_name = request.args.get('command_name')
    logger.debug("Received data clear=[%s] from client" % command_name)
    found_element, found_tab = find_elem_in_tabs(command_name, all_tabs)
    found_element.last_output = ""
    return jsonify({command_name: found_element.last_output})


# Main logic
if __name__ == '__main__':
    app_host = ""
    app_port = 9000

    my_cwd = os.path.dirname(os.path.realpath(__file__))
    all_tabs = parse_tabs_from_xml("%s/tabs/%s.xml" % (my_cwd, gethostname()))
    all_tabs[0].set_active()

    # Functions and variables accessed by the HTML templates
    app.jinja_env.globals['gethostname'] = gethostname
    app.jinja_env.globals['all_tabs'] = all_tabs

    # Run the server
    app.run(host=app_host, port=app_port, debug=True)
