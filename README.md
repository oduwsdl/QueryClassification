# QueryClassification
(Implementation associated with: [A Supervised Learning Algorithm for Binary Domain Classification of Web Queries using SERPs, Alexander C. Nwala and Michael L. Nelson])

Here is the source code to classify a web query as belonging to either the scholar or non-scholar class. See tech report for full explanation: [Tech Report]

## Short explanation
We leverage the work of Search Engines as part of our effort to route domain specific queries to local Digital Libraries. To detect queries that should be routed to local, specialized
Digital Libraries, we first send the queries to Google and then examine
the features in the resulting Search Engine Result Pages, and then classify the query as belonging to either
the scholar or non-scholar domain. Using 400,000 AOL
queries for the non-scholar domain and 400,000 queries
from the NASA Technical Report Server for the
scholar domain, our classifier achieved a precision of 0.809
and F-measure of 0.805.

## Installation
```
$ git clone https://github.com/oduwsdl/QueryClassification.git
$ cd QueryClassification
$ sudo pip install -r requirements.txt
```

## Prerequisite
* [Python 2.7+]
* [Requests]

## Usage
```
$ python classifyQuery.py query 
```

e.g.

```
$ python classifyQuery.py "fluid dynamics"
```

## Support

anwala@cs.odu.edu

[Tech Report]: <https://arxiv.org/abs/1605.00184>
[A Supervised Learning Algorithm for Binary Domain Classification of Web Queries using SERPs, Alexander C. Nwala and Michael L. Nelson]: <https://arxiv.org/abs/1605.00184>
[Python 2.7+]: <https://www.python.org/downloads/>
[Requests]: <http://docs.python-requests.org/en/master/user/install/#install>