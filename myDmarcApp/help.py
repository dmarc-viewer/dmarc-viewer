"""
This file contains several dictionaries of help topics.
Each topic has a:
    question (faq)
    long answer (long)
    short answer (short)
"""

from collections import OrderedDict

help_topics = OrderedDict([
    ("help-mydmarc", {
        "title" : "MyDmarc Tool",
        "items" : OrderedDict([
            ("mydmarc-what", {
                "faq": "What is the Open DMARC Anaylzer Tool?",
                "long": """Open DMARC Analyzer is a highly flexible tool that helps you analyze DMARC aggregate reports. The tool differs between incoming and outgoing reports. Incoming reports you RECEIVE from foreign domains (reporter) based on e-mail messages, the reporter received, purportedly from you. Outgoing reports on the other hand you SEND to foreign domains based on e-mail messages that you received, purportedly by them. To analyze reports you need to use the provided parser script and parse them into your database (see getting started). Below the different sections of the Open DMARC Analyzer are outlined.""",
                "short": """"""
                }),
            ("mydmarc-overview", {
                "faq": "Overview section",
                "long": """The Overview section shows general information about all incoming and outgoing reports to give you an idea about what is stored in your database. For both report types it shows the date ranges for which you have reports stored. These dates are based on the date range attribute of reports and can be faulty. Additionally it shows you the total amount of report receiver domains, reports and messages for incoming and outgoing reports. Also you can compare aligned DKIM, aligned SPF and evaluated DMARC disposition for all messages of both report types.""",
                "short": """"""
            }),       
            ("mydmarc-deep-analysis", {
                "faq": "Deep Analysis section",
                "long": """The Deep Analysis section is the heart of the Open DMARC Analyzer. Currently three analysis types are supported. A map - showing where messages came from, a time line - showing when messages came, and a table - showing DMARC records from DMARC reports. You can fully control what data, i.e. what reports are displayed by generating analysis views in the View Management section. On top of a view, you see its title and description, a list of the applied filters and the analysis types. Btw. you can also export your views (charts as PDF, table as CSV).""",
                "short": """"""
            }),             
            ("mydmarc-view-management", {
                "faq": "View Management section",
                "long": """In the View Management you can manage, i.e. create, edit, clone, delete and order the views for your Deep Analysis section. By dragging the arrow handles (left) you can move views up and down, which will be reflected in the Deep Analysis sidebar. By clicking "Add View", or "Edit" on a particular View you will enter the View Editor, this is where you control what data a view is based on.""",
                "short": """"""
            }),            
            ("mydmarc-view-editor", {
                "faq": "View Management section",
                "long": """The View Editor lets you edit a particular view. Each view has to be given a title and a description, so that you immediately know what you are looking at when you check out a view in the Deep Analysis section. Furthermore you can control if the view is displayed in the Deep Analysis sidebar. You can also select and de-select the various view types (map, table, line chart). Next thing is to decide whether this view should be based on incoming or outgoing reports and what time range you want data to be displayed for. You can select a fixed time range or a variable one (e.g. last N months). After you have filled out the general view info and filters you can define your data sets. You will need at least one data set to display any data at all in the view. Creating multiple data sets is especially useful if you want to compare two or more things in the line chart, eg. DKIM passes vs. DKIM fails. The map type shows each data set separately within a view and the table type merges all records of all data sets. Next to a label and a color for the data set, you can apply filters basically on all properties of a DMARC report. Beware, the select options for report receiver domain and report sender as well as raw DKIM domain and raw SPF domain depend on which report type you have selected above.""",
                "short": """"""
            }),
            ("mydmarc-view-editor", {
                "faq": "Help section",
                "long": """The help section, shows information on how to use the DMARC Analysis Tool, as well as Frequently Asked Questions concerning DMARC and its core technologies DKIM and SPF.""",
                "short": """"""
            }),
        ])
    }),
#    ("help-dmarc", {
#        "title" : "Domain-based Message Authentication, Reporting, and Conformance (DMARC)",
#        "items" : OrderedDict([
#            ("dmarc-what", { 
#                "faq": "What is DMARC?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-deploy", { 
#                "faq": "How can I deploy DMARC?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-configure", { 
#                "faq": "How should I configure DMARC?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-policy-disposition", { 
#                "faq": "What is a DMARC Policy and what is a Dispostion?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-alignment", { 
#                "faq": "What is a DMARC Policy and what is a Dispostion?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-incoming-outgoing", { 
#                "faq": "What is the difference between incoming and outgoing reports?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-report-sender", { 
#                "faq": "Who receives reports and who sends them?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-report-structure", { 
#                "faq": "How are aggregate reports structured?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dmarc-results", { 
#                "faq": "Can I rely on DMARC results?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#        ])
#    }),
#    ("help-dkim", {
#        "title" : "DomainKeys Identified Mail (DKIM)",
#        "items" : OrderedDict([
#            ("dkim-what", { 
#                "faq": "What is DKIM?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dkim-deploy", { 
#                "faq": "How can I deploy DKIM?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dkim-configure", { 
#                "faq": "How should I configure DKIM?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dkim-results-raw", { 
#                "faq": "What are raw DKIM results?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("dkim-results-aligned", { 
#                "faq": "What are aligned DKIM results?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            })
#        ])
#    }),
#    ("help-spf", {
#        "title" : "Sender Policy Framework (SPF)",
#        "items" : OrderedDict([
#            ("spf-what", { 
#                "faq": "What is SPF?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("spf-deploy", { 
#                "faq": "How can I deploy SPF?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("spf-configure", { 
#                "faq": "How should I configure SPF?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("spf-results-raw", { 
#                "faq": "What are raw SPF results?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            }),
#            ("spf-results-aligned", { 
#                "faq": "What are aligned SPF results?",
#                "long": """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
#quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
#consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
#cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#proident, sunt in culpa qui officia deserunt mollit anim id est laborum.""",
#                "short": """"""
#            })
#        ])
#    })
])
