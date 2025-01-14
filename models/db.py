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





# USERS ####
# CARDAT user record, person's details for access records
db.define_table(
    'cardat_user',
    Field('name', 'string',
        required = True,
        requires = IS_NOT_EMPTY()),
    Field('name_alt', 'string',
          comment = "Preferred name or abbreviation"),
    Field('orcid', 'string',
          requires = IS_EMPTY_OR(IS_NOT_IN_DB(db, 'cardat_user.orcid')),
          unique = True),
    Field('affiliation', 'text',
          comment = "Semi-colon separated list of affiliations"),
    Field('email', 'string',
          requires = IS_EMPTY_OR(IS_EMAIL())),
    Field('email_alt', 'string',
          comment = "Secondary email address(es), semicolon-separated"),
    Field('website', 'string'),
    Field('notes', 'text', comment = "Misc notes"),
    auth.signature, 
    format = '%(name)s'
)

# PERSONNEL ####
# personnel details for data attribution in metadata (project/dataset owners, creators, other)
# may be organisations, not only individuals
db.define_table(
    'personnel',
    Field('name', 'string',
        required = True,
        requires = IS_NOT_EMPTY()),
    Field('name_alt', 'string',
          comment = "Preferred name or abbreviation"),
    Field('user_type', 'string',
          requires = IS_IN_SET(['Person', 'Organisation']),
          widget = SQLFORM.widgets.radio.widget,
          default = "Person"),
    Field('id_type', 'string',
          requires = IS_IN_SET(['ORCID', 'ROR', 'Other']),
          widget = SQLFORM.widgets.radio.widget,
          comment = 'ORCID for individuals, ROR for organisations, mark as Other if none available'),
    Field('idvalue', 'string',
          requires = IS_EMPTY_OR(IS_NOT_IN_DB(db, 'personnel.idvalue')),
          unique = True),
    Field('affiliation', 'text',
          comment = "Semi-colon separated list of affiliations"),
    Field('email', 'string',
          requires = IS_EMPTY_OR(IS_EMAIL())),
    Field('email_alt', 'string',
          comment = "Secondary email address(es), semicolon-separated"),
    Field('website', 'string'),
    Field('notes', 'text', comment = "Any other information linked to the person or organisation"),
    auth.signature, 
    format = '%(name)s'
)




# METADATA ####
# records of data repository contents
db.define_table(
    'project',
Field('title', 'string', required = True,
comment= XML(T('Overarching project in format [Organisation]_[Project Title/Theme]_[Project Topic].%s',
A('More', _href=XML(URL('static','index.html',  anchor='sec-2-1-1', scheme=True, host=True)), _target='new'))),
unique=True
),
# Field('data_owner','list:reference cardat_user',
# comment= XML(T('This is the data owner (or project originator). It is a compulsory field. %s',
# A('More', _href=XML(URL('static','index.html',  anchor='sec-2-1-2', scheme=True, host=True)), _target='new'))),
# ),
# Field('data_owner_affiliation','string', 
# comment= XML(T('This is the data owner organisation. %s',
# A('More', _href=XML(URL('static','index.html',  anchor='sec-2-1-2', scheme=True, host=True)), _target='new')))
# ),
Field('abstract', 'text',
comment= XML(T('Descriptive abstract that summarizes information about the umbrella project context of the specific project. %s',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-1-3', scheme=True, host=True)))))
),
Field('study_extent','string', 
comment= XML(T('This can include descriptions of the geographic, temporal, and taxonomic coverage of the research location. %s', 
A('More', _href=XML(URL('static','index.html', anchor='sec-5-1-4', scheme=True, host=True)))))
),
# Field('personnel','string', 
# comment= XML(T('This is for key people etc that are not the owner. %s',
# A('More', _href=XML(URL('static','index.html',  anchor='sec-2-1-2', scheme=True, host=True)), _target='new')))
# ),
Field('funding', 'text',
comment= XML(T('Significant funding sources under which the data has been collected over the lifespan of the project. %s',
A('More', _href=XML(URL('static','index.html',  anchor='sec-2-1-3', scheme=True, host=True)), _target='new')))
),
Field('project_established','date', 
comment= XML(T('Commencement date of overarching research project as a specific date or year. %s', 
A('More', _href=XML(URL('static','index.html', anchor='sec-5-1-4', scheme=True, host=True)))))
),
Field('project_citation','text', 
comment= XML(T('Citations relevant to the design of the overarching project., %s'))
),
auth.signature,
format = '%(title)s' 
)
# require unique and non-empty title
db.project.title.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'project.title')]
# require a project data owner
# db.project.data_owner.requires = IS_NOT_EMPTY()

#### ONE (project) TO MANY (dataset)
db.define_table(
    'dataset',
    Field('project_id',db.project),
Field('shortname','string', comment = XML(T('A concise name, eg. vernal-data-1999. %s.',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2-1', scheme=True, host=True)),  _target='new')))
),
Field('title','string', comment = XML(T('Structure eg: project, data type, location, temporal tranches. %s',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2', scheme=True, host=True)))))
),
Field('creator','string', comment='The name of the person, organization, or position who created the data'),
Field('contact','string', comment = 'A contact name for general enquiries.  This field defaults to creator.'),
Field('contact_email','string', comment = 'An email address for general enquiries.'),
Field('abstract','text', comment = XML(T('A brief overview of the resource that is being documented. The abstract should include basic information that summarizes the study/data. %s', A('More', _href=XML(URL('static', 'index.html',  anchor='sec-5-2', scheme=True, host=True)))))),
Field('additional_metadata' ,'string', comment="Any additional metadata such as folder path or URL links to related webpages."),
Field('alternate_identifier' ,'string', comment = XML(T('An additional, secondary identifier for this entity, possibly from different data management systems. This might be a DOI, or other persistent URL. %s', A('More', _href=XML(URL('static', 'index.html',  anchor='sec-5-2', scheme=True, host=True)))))),
Field('recommended_citation', 'text', comment="For example: 1. Creator (Publication Year): Title. Publisher. Identifier. 2. Creator (Publication Year): Title. Publisher. Date retrieved from website (URL). 3. Creator (Publication Year): Title. Publisher. Date received from data provider (name, role or organisation)."),
Field('studyextent' ,'text', comment="Both a specific sampling area and frequency (temporal boundaries, frequency of occurrence, spatial extent and spatial resolution)."),
Field('temporalcoverage_daterange','string', comment = "A text description of the temporal range that events were observed on"),
Field('temporalcoverage_begindate','date', comment="A begin date.  The dates that events were observed on."),
Field('temporalcoverage_enddate','date', comment="A end date. The dates that events were observed on."),
Field('methods_protocol' , 'text', comment = XML(T('The protocol field is used to either reference a protocol citation or describe the methods that were prescribed to define a study or dataset. Note that the protocol is intended to be used to document a prescribed procedure which may or may not have been performed (see Method Steps). %s', A('More', _href=XML(URL('static', 'index.html',  anchor='sec-5-2-9', scheme=True, host=True)))))),
Field('sampling_desc' ,'text', comment = XML(T('Similar to a description of sampling procedures found in the methods section of a journal article. %s', A('More', _href=XML(URL('static', 'index.html',  anchor='sec-5-2-10', scheme=True, host=True)))))),
Field('method_steps','text', comment=XML(T('EACH method step to implement the measurement protocols and set up the study. Note that the method is used to describe procedures that were actually performed. The method may have diverged from the protocol purposefully, or perhaps incidentally, but the procedural lineage is still preserved and understandable. %s', A('More', _href=XML(URL('static', 'index.html',  anchor='sec-5-2-11', scheme=True, host=True)))))),
Field('associated_party','text', comment = XML(T('A person, organisational role or organisation who has had an important role in the creation or maintenance of the data (i.e. parties who grant access to survey sites as landholder or land manager, or may have provided funding for the surveys). %s.',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2', scheme=True, host=True)))))
  ),
Field('geographicdescription','string',
comment = XML(T('A general description of the geographic area in which the data were collected. This can be a simple place name (e.g. Kakadu National Park). %s',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2', scheme=True, host=True)))))     
),
Field('boundingcoordinates','string',
comment = XML(T('bounding coordinates in order N, S, E, W (Optionally also add altitudeMinimum, altitudeMax). %s',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2', scheme=True, host=True)))))     
),
Field('taxonomic_coverage','string', comment="List of scientific names."),
Field('additionalinfo','string', comment = XML(T('Any information that is not characterised well by EML metadata. Example is a group id for grouping datasets apart from EML-project (such as a funding stream, or a particular documentation such as provision agreement). %s.',
A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2-15', scheme=True, host=True)),  _target='new')))
  ),
Field('publisher','string',
comment = XML(T('The publisher of this data set (e.g. repository, publishing house, any institution making the data available). %s.',
A('More', _href=XML(URL('static','index.html',  anchor='sec-2-2-18', scheme=True, host=True)), _target='new')))     
),
Field('pubdate','date'),
Field('access_rules','text', comment = "The eml-access module describes the level of access that is to be allowed or denied to a resource for a particular user or group of users"),
Field('distribution_methods','text', comment = "The methods of distribution used for others to access the software, data, and documentation."),
Field('metadataprovider','string', comment = 'The name of the person who produced the metadata.'),
Field('provision_status','string', comment = 'The status of this data provision (Identified, Requested or Provided).'),
Field('provision_date','date', comment = 'The date provided.'),
Field('request_notes','text', comment = 'Any relevant information regarding this data provision request.'),
Field('request_date','date', comment = 'Date provision requested.'),
format = '%(shortname)s'
    )

db.dataset.contact_email.requires = [IS_EMAIL()]
db.dataset.creator.requires = [IS_NOT_EMPTY()]
db.dataset.provision_status.requires = IS_IN_SET(['','Identified', 'Requested', 'Provided', 'QC', 'Published'])      
# db.dataset.metadataprovider.requires = [IS_EMAIL(), IS_NOT_IN_DB(db, 'dataset.metadataprovider')]
#### ONE (dataset) TO MANY (entity)
  
db.define_table(
      'entity',
Field('dataset_id',db.dataset),
Field('entityname','string', comment = "The file name, name of database table, etc. It should identify the entity in the dataset. Example: SpeciesAbundance1996.csv", requires = IS_NOT_EMPTY()),
Field('entitydescription', 'string', comment = "Text generally describing the entity, its type, and relevant information about the data in the entity. Example: Species abundance data for 1996 at the VCR LTER site"),
Field('physical_distribution', 'string',
comment= XML(T('Information required for retrieving the resource. %s',    
      A('More', _href=XML(URL('static','index.html',  anchor='sec-5-3-4', scheme=True, host=True)))))
      ),
      Field('physical_distribution_additionalinfo', 'text',
comment= XML(T('Additional Information about the storage of the resource, including backup regime. %s',    
      A('More', _href=XML(URL('static','index.html',  anchor='sec-5-3-4', scheme=True, host=True)))))
      ),
Field('entity_temporalcoverage_daterange','string', comment = "A text description of the temporal range that events were observed on"),
Field('entity_methods', 'text', comment = "Information on the specific methods used to collect information in this entity."),
Field('numberofrecords', 'integer', comment = 'The number of rows in a table.'),
format = '%(entityname)s'
)
#### ONE (entity) TO MANY (attributes/variables)

db.define_table(
    'attr',
    Field('entity_id',db.entity),
    Field('variable_name', 'string', comment = 'The name of the variable'),
    Field('variable_definition', 'string', comment = 'Definition of the variable.'),
    Field('measurement_scales', 'string', comment = 'One of nominal, ordinal, interval, ratio or datetime', requires = IS_IN_SET(['nominal', 'ordinal', 'interval', 'ratio', 'datetime'])),
    Field('units', 'string', comment = 'Standard Unit of Measurement'),
    Field('value_labels', 'string', comment = 'Labels for levels of a factor.  For example a=bud, b=flower, c=fruiting')      
    )


#### ONE (intellectualright) TO one (dataset)
db.define_table(
    'intellectualright',
    Field('dataset_id',db.dataset),
    Field('data_owner', 'string', comment = 'The person or organisation with authority to grant permissions to access data.'),
    Field('data_owner_contact', 'string', comment = 'Optional.'),
    Field('accessibility', 'string', comment = XML(T("The data can be 1) public, 2) only a group or 3) restricted to a person %s",     A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2', scheme=True, host=True)))))
    ),
    Field('licencee', comment = 'Optional.'),    
    Field('licence_code', 'string', comment = XML(T("The licence to allow others to copy, distribute or display work and derivative works based upon it and define the way credit will be attributed. Common licences are 'CCBY', 'CCBYSA',  'CCBYND', 'CCBYNC', 'CCBYNCSA', 'CCBYNCND' or 'other'. For more information see http://creativecommons.org/licenses/. %s",     A('More', _href=XML(URL('static','index.html',  anchor='sec-5-2', scheme=True, host=True)))))
    ),
    Field('licence_text', 'string', comment = 'The name of the licence.'),
    Field('special_conditions', 'text', comment = 'Any restrictions to be placed on the access or use, especially the timeframe if this is limited.'),
    Field('path_to_licence', 'string', comment = 'Optional.')
    )
    
db.intellectualright.licence_code.requires = IS_IN_SET(['CCBY', 'CCBYSA',  'CCBYND', 'CCBYNC', 'CCBYNCSA', 'CCBYNCND', 'other'])    
db.intellectualright.accessibility.requires = IS_IN_SET(['Public', 'CAR', 'CERAPH',  'Restricted', 'other'])




# ACCESS REQUESTS TO DATA ####
# Unique access request
db.define_table(
    'accessrequest',
    Field('title', 'string', comment = "A short (two or three word) title of the project for which the data are to be used",
            required = True),
    Field('date_of_request', 'date', comment = "Date request received by CARDAT.",
            required = True),
    Field('description', 'text', comment = "A description of the project for which the data are to be used. Include description of any ethics committee approvals and the intended publication strategy."),
    Field('category_access', 'text', comment = "Category of access."),
    Field('primary_purpose', 'string', comment = ""),
    Field('other_info', 'text', comment = "Additional info or notes"),
    auth.signature,
    format = '%(title)s'# %(accessdataset_id)s -> %(dataset_id)s'
    )

db.accessrequest.title.requires = [IS_NOT_EMPTY()]    
db.accessrequest.category_access.requires = IS_IN_SET(['Project personnel', 'Data sharing service','Data science service', 'Data training'])
db.accessrequest.primary_purpose.requires = IS_IN_SET(['', 'Research','Government', 'Teaching', 'Education (postgraduate)', 'Education (undergraduate)', 'Commercial/Industry', 'Other'])

## Secondary to access request
# record of outputs from access requests
db.define_table(
    'request_output',
    Field('accessrequest_id', db.accessrequest),
    Field('output_category', 'string', requires = IS_IN_SET(["Journal Article", "Dataset", "Report", "Media Article", "Thesis", "Other"])),
    Field('link', 'string', requires = IS_URL()),
    Field('title', 'string'),
    Field('author', 'string'),
    Field('publication', 'string', comment = 'Journal, data portal/repository, book, newspaper, etc.'),
    Field('publication_date', 'date'),
    Field('status', 'string', default = "Pending"),
    Field('additional_notes', 'text', comment = 'Additional notes about output'),
    auth.signature,
    format = '%(title)s'
    )
db.request_output.accessrequest_id.requires = IS_IN_DB(db, 'accessrequest.id', db.accessrequest.title)
db.request_output.status.requires = IS_IN_SET(['Unknown (lapsed)', 'No output', 'Pending', 'Published'])

#### MANY (accessors) TO ONE (accessrequest)
# Persons that are part of the access request
db.define_table(
    'accessor',
    Field('accessrequest_id', db.accessrequest),
    Field('cardat_user_id', db.cardat_user),
    Field('begin_date', 'date', comment = "Access granted on this date (direct access)"),
    Field('end_date', 'date', comment = "Access revoked on this date (direct access)"),
    Field('key_contact', 'boolean', comment = "Study lead or contact person for request. Typically one person per request but may be multiple (e.g. study lead and data analyst)."),
    Field('role', 'string', comment = "The role that this person will have in the project, specifically in relation to the data."),
    Field('role_description', 'text', comment = "Description of the role."),
    auth.signature,
    format = '%(cardat_user_id)s'
)
db.accessor.accessrequest_id.requires = IS_IN_DB(db, 'accessrequest.id', db.accessrequest.title)
db.accessor.cardat_user_id.requires = IS_IN_DB(db, 'cardat_user.id', db.cardat_user.name)

# KEYWORDS ####
# tags for datasets
db.define_table(
    'keyword',
    Field('thesaurus',
        required = True,
        requires = IS_IN_SET("CARDAT"),
        default = "CARDAT"),
    Field('keyword', 'string', 
        required = True,
        requires = (IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'keyword.keyword'))),
    auth.signature,
    format = '%(thesaurus)s: %(keyword)s'
    )
# unique keywords for each thesaurus
db.keyword.keyword.requires = IS_NOT_IN_DB(
    db(db.keyword.thesaurus == request.vars.thesaurus),
    'keyword.keyword')
