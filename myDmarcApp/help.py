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
                "faq": "What is the MyDMARC Tool?",
                "long": """""",
                "short": """"""
                }),
            ("mydmarc-deploy", {
                "faq": "How can I deploy the MyDmarc Tool?",
                "long": """""",
                "short": """"""
            }),
            ("mydmarc-datainput", {
                "faq": "How can feed the tool with data?",
                "long": """""",
                "short": """"""
            }),        
            ("mydmarc-overview", {
                "faq": "What's on the overview page?",
                "long": """""",
                "short": """"""
            }),        
            ("mydmarc-deep-analysis", {
                "faq": "What's on the deep analysis page?",
                "long": """""",
                "short": """"""
            }),        
            ("mydmarc-views-filtersets", {
                "faq": "What are views, filtersets and filters?",
                "long": """""",
                "short": """"""
            }),        
            ("mydmarc-view-management", {
                "faq": "How can I manage my views?",
                "long": """""",
                "short": """"""
            }),
        ])
    }),
    ("help-dmarc", {
        "title" : "Domain-based Message Authentication, Reporting, and Conformance (DMARC)",
        "items" : OrderedDict([
            ("dmarc-what", { 
                "faq": "What is DMARC?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-deploy", { 
                "faq": "How can I deploy DMARC?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-configure", { 
                "faq": "How should I configure DMARC?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-policy-disposition", { 
                "faq": "What is a DMARC Policy and what is a Dispostion?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-alignment", { 
                "faq": "What is a DMARC Policy and what is a Dispostion?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-incoming-outgoing", { 
                "faq": "What is the difference between incoming and outgoing reports?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-report-sender", { 
                "faq": "Who receives reports and who sends them?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-report-structure", { 
                "faq": "How are aggregate reports structured?",
                "long": """""",
                "short": """"""
            }),
            ("dmarc-results", { 
                "faq": "Can I rely on DMARC results?",
                "long": """""",
                "short": """"""
            }),
        ])
    }),
    ("help-dkim", {
        "title" : "DomainKeys Identified Mail (DKIM)",
        "items" : OrderedDict([
            ("dkim-what", { 
                "faq": "What is DKIM?",
                "long": """""",
                "short": """"""
            }),
            ("dkim-deploy", { 
                "faq": "How can I deploy DKIM?",
                "long": """""",
                "short": """"""
            }),
            ("dkim-configure", { 
                "faq": "How should I configure DKIM?",
                "long": """""",
                "short": """"""
            }),
            ("dkim-results-raw", { 
                "faq": "What are raw DKIM results?",
                "long": """""",
                "short": """"""
            }),
            ("dkim-results-aligned", { 
                "faq": "What are aligned DKIM results?",
                "long": """""",
                "short": """"""
            })
        ])
    }),
    ("help-spf", {
        "title" : "Sender Policy Framework (SPF)",
        "items" : OrderedDict([
            ("spf-what", { 
                "faq": "What is SPF?",
                "long": """""",
                "short": """"""
            }),
            ("spf-deploy", { 
                "faq": "How can I deploy SPF?",
                "long": """""",
                "short": """"""
            }),
            ("spf-configure", { 
                "faq": "How should I configure SPF?",
                "long": """""",
                "short": """"""
            }),
            ("spf-results-raw", { 
                "faq": "What are raw SPF results?",
                "long": """""",
                "short": """"""
            }),
            ("spf-results-aligned", { 
                "faq": "What are aligned SPF results?",
                "long": """""",
                "short": """"""
            })
        ])
    })
])
