# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    ##db = DAL("postgres://w2p_user:your_password@localhost:5432/data_inventory_dbname", fake_migrate_all = False)    
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] # if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)


# joining (linking) tables for many-to-many relationships prefixed with 'j'
# except the accessor table for legacy reasons

# USERS ####
# CARDAT user record, person's details for access records
db.define_table(
    'cardat_user',
    Field('name', 'string', comment = "Full name", required = True, notnull = True),
    Field('name_alt', 'string', comment = "Preferred name or abbreviation"),
    Field('orcid', 'string', unique = True, comment = "Researcher ORCID (https://orcid.org/)"),
    Field('affiliation', 'list:string', comment = "Affiliation(s)"),
    Field('email', 'string', comment = "Primary email address"),
    Field('email_alt', 'list:string',
          comment = "Secondary email address(es)"),
    Field('website', 'string'),
    Field('notes', 'text', comment = "Misc notes"),
    auth.signature, 
    format = '%(name)s'
)
db.cardat_user.name.requires = IS_NOT_EMPTY()
db.cardat_user.orcid.requires = [IS_EMPTY_OR([
    IS_NOT_IN_DB(db, 'cardat_user.orcid'),
    IS_MATCH('^\d{4}(-\d{4}){3}$', error_message='Not an ORCID format')])] 
db.cardat_user.website.requires = [IS_EMPTY_OR(IS_URL())]
db.cardat_user.email.requires = IS_EMAIL()
db.cardat_user.email_alt.requires = IS_LIST_OF(IS_EMAIL())

# Show as link
db.cardat_user.email.represent = lambda val, row: None if val is None else A(val, _href="mailto:" + val, _target="_blank")
db.cardat_user.orcid.represent = lambda val, row: None if val is None else A(val, _href="https://orcid.org/" + val, _target="_blank")
db.cardat_user.website.represent = lambda val, row: None if val is None else A(val, _href=val, _target="_blank")


# PERSONNEL ####
# personnel details for data attribution in metadata (project/dataset owners, creators, other)
# may be organisations, not only individuals
db.define_table(
    'personnel',
    Field('name', 'string',
        required = True,
        notnull=True),
    Field('name_alt', 'string',
          comment = "Preferred name or abbreviation"),
    Field('user_type', 'string',
          requires = IS_IN_SET(['Person', 'Organisation']),
          widget = SQLFORM.widgets.radio.widget,
          default = "Person"),
    Field('orcid', 'string', unique = True, label = "ORCID", comment = 'ORCID as XXXX-XXXX-XXXX-XXXX'),
    Field('rorid', 'string', unique = True, label = "ROR", comment = 'ROR as 9 character string'),
    Field('affiliation', 'list:string', comment = "Affiliation(s)"),
    Field('email', 'string'),
    Field('email_alt', 'list:string', comment = "Secondary email address(es)"),
    Field('website', 'string'),
    Field('notes', 'text', comment = "Any other information linked to the person or organisation"),
    auth.signature, 
    format = '%(name)s'
)
db.personnel.name.requires = IS_NOT_EMPTY()
# require valid identifier formatting
db.personnel.orcid.requires = [IS_EMPTY_OR([
    IS_NOT_IN_DB(db, 'personnel.orcid'),
    IS_MATCH('^\d{4}(-\d{4}){3}$', error_message='Not a valid ORCID format (expect XXXX-XXXX-XXXX-XXXX)')])] 
db.personnel.rorid.requires = [IS_EMPTY_OR([
    IS_NOT_IN_DB(db, 'personnel.rorid'), 
    IS_MATCH('^[A-Za-z0-9]{9}$', error_message='Not a valid ROR format (expect 9-character alphanumeric string)')])] 
db.personnel.email.requires = IS_EMAIL()
db.personnel.email_alt.requires = IS_LIST_OF(IS_EMAIL())
db.personnel.website.requires = [IS_EMPTY_OR(IS_URL())]

# Show as link
db.personnel.email.represent = lambda val, row: None if val is None else A(val, _href="mailto:" + val, _target="_blank")
db.personnel.orcid.represent = lambda val, row: None if val is None else A(val, _href="https://orcid.org/" + val, _target="_blank")
db.personnel.rorid.represent = lambda val, row: None if val is None else A(val, _href="https://ror.org/" + val, _target="_blank")
db.personnel.website.represent = lambda val, row: None if val is None else A(val, _href=val, _target="_blank")



# METADATA ####
# records of data repository contents 
# in PROJECT-DATASET-ENTITY hierarchical tree

# PROJECT level 
db.define_table(
    'project',
    Field('title', 'string', required = True, 
    comment='Overarching project in format [Organisation]_[Project Title/Theme]_[Project Topic]',
    unique=True
    ),
    Field('abstract', 'text',
    comment='Descriptive abstract that summarizes information about the umbrella project context of the specific project'
    ),
    Field('study_extent','string', 
    comment='Short description of spatial and temporal coverage of the study'
    ),
    Field('funding', 'text',
    comment='Significant funding sources under which the data has been collected over the lifespan of the project'
    ),
    Field('project_established','date', 
    comment='Commencement date of overarching research project as a specific date'
    ),
    Field('project_citation','text', 
    comment='Citations relevant to the design of the overarching project'
    ),
    auth.signature,
    format = '%(title)s' 
)
# require unique and non-empty title
db.project.title.requires = IS_NOT_EMPTY()

# Project personnel
# join table with project id and personnel id
db.define_table(
    'j_project_personnel',
    Field('project_id', db.project, required = True, notnull=True),
    Field('personnel_id', db.personnel, required = True, notnull=True),
    Field('role', 'string', required = True), 
    Field('notes', 'string'),
    auth.signature,
    format = 'Project %(project_id)s personnel %(personnel_id)s' 
)
db.j_project_personnel.role.requires = IS_IN_SET(('Owner', 'Other'))
db.j_project_personnel._singular = "Project personnel"
db.j_project_personnel._plural = "Project personnel"




### ONE (project) TO MANY (dataset)
db.define_table(
    'dataset',
    ## title, personnel, identification of dataset
    Field('project_id', db.project, required = True, notnull=True),
    Field('shortname','string', unique = True, notnull=True, comment = 'A concise name indicating directory or repository name of dataset or tool'),
    Field('title','string', unique = True, notnull=True, comment = 'Descriptive, human-readable name'),
    Field('contact','string', comment = 'A contact name for general enquiries', default = "CARDAT Data Team"),
    Field('contact_email','string', comment = 'An email address for general enquiries.'),
    Field('associated_party','text', comment = 'A person, organisational role or organisation who has had an important role in the creation or maintenance of the data (i.e. parties who grant access to survey sites as landholder or land manager, or may have provided funding for the surveys)'),
    Field('repository_path' ,'string', comment='Dataset location in CARDAT repository - typically folder path from Environment_General or ResearchProjects_CAR. May be alternative storage location for restricted data.'),
    Field('repository_link' ,'string', comment='Link to dataset folder in data repository or code repository.'),
    Field('url_link' ,'string', comment = 'URL link or DOI to source if public. An additional, secondary identifier for this entity, possibly from different data management systems. DOI or other persistent URL preferred.'),
    Field('recommended_citation', 'text', comment='For example: 1. Creator (Publication Year): Title. Publisher. Identifier. 2. Creator (Publication Year): Title. Publisher. Date retrieved from website (URL). 3. Creator (Publication Year): Title. Publisher. Date received from data provider (name, role or organisation).'),

    ## description of data contained
    Field('abstract','text', comment = 'A brief overview of the resource that is being documented. The abstract should include basic information that summarizes the study data'),
    Field('studyextent' ,'text', comment= 'Both a specific sampling area and frequency (temporal boundaries, frequency of occurrence, spatial extent and spatial resolution).'),
    # spatial
    Field('geographicdescription','string',
    comment = 'A general description of the geographic area coverage of the dataset (this can be a simple place name, e.g. Kakadu National Park)'     
    ),
    Field('boundingcoordinates','string',
    comment = 'Bounding coordinates in order N, S, E, W (Optionally also add altitudeMinimum, altitudeMax)'
    ),
    # temporal
    Field('temporalcoverage_daterange','string', comment = "A text description of the temporal range that events were observed on"),
    Field('temporalcoverage_begindate','date', comment="A begin date.  The dates that events were observed on."),
    Field('temporalcoverage_enddate','date', comment="A end date. The dates that events were observed on."),

    # methodology
    Field('methods_protocol' , 'text', comment = 'The protocol field is used to either reference a protocol citation or describe the methods that were prescribed to define a study or dataset. Note that the protocol is intended to be used to document a prescribed procedure which may or may not have been performed (see Method Steps).'),
    Field('sampling_desc' ,'text', comment = 'Similar to a description of sampling procedures found in the methods section of a journal article.'),
    Field('method_steps','text', comment='Each method step to implement the measurement protocols and set up the study. Note that the method is used to describe procedures that were actually performed. The method may have diverged from the protocol purposefully, or perhaps incidentally, but the procedural lineage is still preserved and understandable'),
    # other
    Field('additional_info','text', comment = 'Additional information'),
    Field('publisher','string', comment = 'The publisher of this data set (e.g. repository, publishing house, any institution making the data available)'),

    # sharing
    # Field('access_rules','text', comment = "TO REMOVE"),
    # Field('distribution_methods','text', comment = "TO REMOVE"),
    # Field('metadataprovider','string', comment = 'TO REMOVE'),

    # publication process (in self repository)
    Field('request_date','date', comment = 'Date of request to data provider'),
    Field('provision_status','string', comment = 'The status of this data provision.'),
    Field('provision_date','date', comment = 'Date of dataset/tool received from data provider'),
    Field('pubdate','date', comment = 'Date published in repository'),
    Field('pub_notes','text', comment = 'Any relevant information regarding this dataset publication process (e.g. detail of request, reason for archival)'),
    auth.signature,
    format = '%(shortname)s'
)
# require unique and non-empty title
db.dataset.shortname.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'dataset.shortname')]
db.dataset.title.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'dataset.title')]

db.dataset.contact_email.requires = [IS_EMAIL()]
db.dataset.repository_link.requires = IS_EMPTY_OR(IS_URL())
db.dataset.url_link.requires = IS_EMPTY_OR(IS_URL())
db.dataset.provision_status.requires = IS_IN_SET(['','Identified', 'Requested', 'Provided', 'QC', 'Published', 'Archived', 'Working'])      

# show link as link
db.dataset.repository_link.represent = lambda val, row: None if val is None else A(val, _href=val, _target="_blank")
db.dataset.url_link.represent = lambda val, row: None if val is None else A(val, _href=val, _target="_blank")

# Dataset licencing 
#### ONE (dataset) to ONE (intellectualright)
db.define_table(
    'intellectualright',
    Field('dataset_id', db.dataset, unique = True, notnull=True),
    # intellectual rights - from CARDAT to User
    Field('licence_code', 'string', comment = "The licence to allow others to copy, distribute or display work and derivative works based upon it and define the way credit will be attributed. Common licences are 'CCBY', 'CCBYSA',  'CCBYND', 'CCBYNC', 'CCBYNCSA', 'CCBYNCND' or 'other'. For more information see http://creativecommons.org/licenses/."),
    Field('licence_text', 'string', comment = 'The name of the licence.'),
    Field('special_conditions', 'text', comment = 'Any restrictions to be placed on the access or use of this dataset, especially the timeframe if this is limited.'),
    Field('path_to_licence', 'string', comment = 'Optional.'),
    Field('accessibility', 'string', comment = 'Broad category of accessibility: Public (no special permission required), CARDAT (no special permission required for CARDAT members), Restricted (special permission required), Other.'),
    Field('notes', 'text', comment = 'Additional info (e.g. licencing of data sources)'),
    auth.signature,
    format = '%(licence_text)s (%(licence_code)s)'
    )
db.intellectualright.licence_code.requires = IS_IN_SET(['CCBY', 'CCBYSA',  'CCBYND', 'CCBYNC', 'CCBYNCSA', 'CCBYNCND', 'MIT',  'Apache-2.0', 'BSD-3-Clause', 'other'])    
db.intellectualright.accessibility.requires = IS_IN_SET(['Public', 'CARDAT', 'Restricted', 'Other'])

# Journal article (or other documentation) describing the methodology used to produce the dataset.
db.define_table(
    'dataset_publication',
    Field('dataset_id', db.dataset, required = True, notnull=True),
    Field('link', 'string', comment = 'Link to publication, DOI or other persistent URL preferred'),
    Field('title', 'string', comment = 'Title of publication', notnull=True),
    Field('author', 'string', comment = 'Author(s) of publication'),
    Field('citation', 'text', comment = 'Citation of publication'),
    auth.signature,
    format = '%(title)s'
    )
db.dataset_publication._singular = "Publication"
db.dataset_publication._plural = "Publications"
db.dataset_publication.title.requires = IS_NOT_EMPTY()
db.dataset_publication.link.requires = IS_EMPTY_OR(IS_URL())

# show link as link
db.dataset_publication.link.represent = lambda val, row: None if val is None else A(val, _href=val, _target="_blank")

# Dataset personnel
db.define_table(
    'j_dataset_personnel',
    Field('dataset_id', db.dataset, required = True, notnull=True),
    Field('personnel_id', db.personnel, required = True, notnull=True),
    Field('role', 'string', required = True), 
    Field('role_description', 'string'),
    Field('notes', 'text'),
    auth.signature,
    format = 'Dataset %(dataset_id)s personnel %(personnel_id)s' 
)
db.j_dataset_personnel.role.requires = IS_IN_SET(('Owner', 'Creator', 'Contact', 'Analyst', 'Other'))
db.j_dataset_personnel._singular = "Dataset personnel"
db.j_dataset_personnel._plural = "Dataset personnel"


#### ONE (dataset) TO MANY (entity)
# equivalent of a 'resource' in other metadata schemas
db.define_table(
      'entity',
Field('dataset_id', db.dataset, required = True, notnull=True),
Field('entityname','string', required = True, comment = "The file name, name of database table, etc. It should identify the entity in the dataset. Example: SpeciesAbundance1996.csv", requires = IS_NOT_EMPTY()),
Field('entitytype', 'string', comment = "General format of the data"),
Field('entitydescription', 'string', comment = "Text generally describing the content of the entity."),
Field('physical_distribution', 'string',
comment= 'Information required for retrieving the resource.'),
Field('physical_distribution_additionalinfo', 'text',
comment= 'Additional Information about the storage of the resource, including backup regime.'),
Field('entity_temporalcoverage_daterange','string', comment = "A text description of the temporal range that events were observed on"),
Field('entity_methods', 'text', comment = "Information on the specific methods used to collect information in this entity."),
Field('numberofrecords', 'integer', comment = 'The number of rows in a table.'),
auth.signature,
format = '%(entityname)s'
)
db.entity.entityname.requires = IS_NOT_EMPTY()

# Entity attributes
#### ONE (entity) TO MANY (attributes/variables)
# Attributes of entities
db.define_table(
    'attr',
    Field('entity_id', db.entity, required = True, notnull=True),
    Field('variable_name', 'string', required = True, comment = 'The name of the variable'),
    Field('variable_definition', 'string', comment = 'Definition of the variable.'),
    Field('measurement_scales', 'string', comment = 'One of nominal, ordinal, interval, ratio or datetime'),
    Field('units', 'string', comment = 'Standard Unit of Measurement'),
    Field('value_labels', 'string', comment = 'Factor labels and meaning'),
    auth.signature,
    format = '%(variable_name)s'     
    )
db.attr.variable_name.requires = IS_NOT_EMPTY()
db.attr.measurement_scales.requires = IS_IN_SET(['nominal', 'ordinal', 'interval', 'ratio', 'datetime'])





# ACCESS REQUESTS TO DATA ####
# Unique access requests
db.define_table(
    'accessrequest',
    Field('title', 'string', required = True, 
    comment = "A short (two or three word) title of the project for which the data are to be used"),
    Field('date_of_request', 'date', required = True,
    comment = "Date request received."),
    Field('description', 'text', comment = "A description of the project for which the data are to be used. Include description of any ethics committee approvals and the intended publication strategy."),
    Field('category_access', 'text', 
    comment = "Category of access - request is for access to the dataset (Data sharing service), for data wrangling to produce a dataset (Data science service), for working on the dataset/project itself (Project personnel) or for training purposes (Training)"),
    Field('primary_purpose', 'string', comment = "Sector from which request is made - choose the most appropriate"),
    Field('other_info', 'text', comment = "Additional info or notes"),
    auth.signature,
    format = '%(title)s'
    )
db.accessrequest.title.requires = [IS_NOT_EMPTY()]    
db.accessrequest.category_access.requires = IS_IN_SET(['Project personnel', 'Data sharing service','Data science service', 'Data training'])
db.accessrequest.primary_purpose.requires = IS_IN_SET(['', 'Research', 'Government', 'Training', 'Education (postgraduate)', 'Education (undergraduate)', 'Commercial/Industry', 'Other'])

# Link access request to dataset
db.define_table(
    'request_dataset',
    Field('accessrequest_id', db.accessrequest, required = True, notnull=True),
    Field('dataset_id', db.dataset, required = True, notnull=True),
    Field('approval_date', 'date', required = True, comment = "Date request approved"),
    Field('approval_documentation', 'string', comment = 'Location of record of approval'),
    auth.signature,
    format = '%(accessrequest_id)s - %(dataset_id)s'
    )

## Secondary to access request
# record of outputs from access requests
db.define_table(
    'request_output',
    Field('accessrequest_id', db.accessrequest, required = True, notnull=True),
    Field('title', 'string', required = True),
    Field('author', 'string'),
    Field('output_category', 'string', comment = "Type of output - conference/journal paper, dataset, report, thesis, etc."),
    Field('publication', 'string', comment = 'Specific output type, e.g. book, newspaper, etc.'),
    Field('publication_date', 'date'),
    Field('link', 'string', comment = "URL link to output if exists - DOI or similar permanent link where possible.'"),
    Field('status', 'string', default = "Pending"),
    Field('additional_notes', 'text', comment = 'Additional notes about output'),
    auth.signature,
    format = '%(title)s'
    )
db.request_output.requires = IS_IN_SET(["Journal Article", "Dataset", "Report", "Media Article", "Thesis", "Other"])
db.request_output.status.requires = IS_IN_SET(['Unknown (lapsed)', 'No output', 'Pending', 'Published'])
db.request_output.status.link = IS_EMPTY_OR(IS_URL())

# show link as link
db.request_output.link.represent = lambda val, row: None if val is None else A(val, _href=val, _target="_blank")

# MANY (accessors) TO ONE (accessrequest)
# Persons that are part of the access request
db.define_table(
    'accessor',
    Field('accessrequest_id', db.accessrequest, required = True, notnull=True),
    Field('cardat_user_id', db.cardat_user, required = True, notnull=True),
    Field('begin_date', 'date', comment = "Access granted via CARDAT repository on this date"),
    Field('end_date', 'date', comment = "Access revoked via CARDAT repository on this date"),
    Field('key_contact', 'boolean', default = True, 
        comment = "Study lead or contact person for request. Typically one person per request but may be multiple (e.g. study lead and data analyst)"),
    Field('role', 'string', comment = "The role that this person will have in the project, specifically in relation to the data"),
    Field('role_description', 'text', comment = "Further description of the role"),
    auth.signature,
    format = '%(cardat_user_id)s'
)
db.accessor.role.widget = SQLFORM.widgets.autocomplete(
     request, db.accessor.role, limitby=(0, 10), min_length=2, distinct = True)

# KEYWORDS ####
# tags for datasets
db.define_table(
    'keyword',
    Field('thesaurus', required = True, default = "Collections", comment = "Source thesaurus of keywords"),
    Field('keyword', 'string', required = True),
    auth.signature,
    format = '%(thesaurus)s: %(keyword)s'
    )
db.keyword.thesaurus.widget = SQLFORM.widgets.autocomplete(
    request, db.keyword.thesaurus, limitby=(0, 10), min_length=2, distinct = True)
# unique keywords for each thesaurus
db.keyword.keyword.requires = [
    IS_NOT_IN_DB(db(db.keyword.thesaurus == request.vars.thesaurus), 'keyword.keyword'), 
    IS_NOT_EMPTY()]

db.define_table(
    'j_dataset_keyword',
    Field('dataset_id', db.dataset, required = True, notnull=True),
    Field('keyword_id', db.keyword, required = True, notnull=True),
    auth.signature,
    format = '%(dataset_id)s: %(keyword_id)s'
)
db.j_dataset_keyword._singular = "Dataset-keyword"
db.j_dataset_keyword._plural = "Dataset-keyword"



# DATASET LINKAGES ####

db.define_table(
    'dataset_linkage',
    Field('parent_dataset', db.dataset, required = True, notnull=True),
    Field('child_dataset', db.dataset, required = True, notnull=True),
    Field('linkage', 'string', comment = 'Parent-child relationship of dataset', notnull=True),
    auth.signature,
    format = '%(linkage)s: %(parent_dataset)s -> %(child_dataset)s'
    )
db.dataset_linkage.linkage.requires = IS_IN_SET(("Subset/Extraction", "Derivation"))
db.dataset_linkage.child_dataset.requires = IS_IN_DB(db(db.dataset.id != request.post_vars.parent_dataset),
                            'dataset.id', db.dataset._format)