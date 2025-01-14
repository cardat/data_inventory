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
#### accessdatasets
  
db.define_table(
    'accessdataset',
    Field('name','string',
comment= XML(T('A person or group. Keep this to a short (two or three word) title as it is used to specify access requests in the acessrequest table). %s',    
    A('More', _href=XML(URL('static','index.html',  anchor='sec-5-3-4', scheme=True, host=True)))))
    ),
    Field('email'),
    Field('bio', 'string', comment = "A short description of this person/group."),
    format = '%(name)s'
    )
db.accessdataset.name.requires = IS_NOT_EMPTY()
db.accessdataset.email.requires = [IS_EMAIL(), IS_NOT_EMPTY()]
#### MANY (accessors) TO MANY (accessdataset members)

db.define_table(
    'accessor',
    Field('accessdataset_id',db.accessdataset),
    Field('name'),
    Field('email'),
    Field('role', 'string', comment = "The role that this person will have in the project, specifically in relation to the data."),
    Field('role_description', 'text', comment = "Description of the role."),
    Field('begin_date', 'date', comment = "Access granted on this date"),
    Field('end_date', 'date', comment = "Access revoked on this date"),
    format = '%(name)s'
    )
db.accessor.email.requires = [IS_EMAIL()]
# , IS_NOT_IN_DB(db, 'accessor.email')]
#### MANY (datasets) TO MANY (accessors)

db.define_table(
    'accessrequest',
    Field('dataset_id',db.dataset),
    Field('accessdataset_id',db.accessdataset),
    Field('title', 'string', comment = "A short (two or three word) title of the project for which the data are to be used"),
    Field('description', 'text', comment = "A description of the project for which the data are to be used. Include description of any ethics committee approvals and the intended publication strategy."),
    Field('begin_date', 'date', comment = "Access granted on this date"),
    Field('end_date', 'date', comment = "Access revoked on this date"),
    format = '%(title)s %(accessdataset_id)s -> %(dataset_id)s'
    )
#### MANY (keywords) TO one (dataset)

db.define_table(
    'keyword',
    Field('dataset_id',db.dataset),
    Field('thesaurus', 'string', comment = 'source of authoritative definitions'),
    Field('keyword', 'string', requires=IS_IN_DB(db, 'thesaurus_ltern.keyword'))
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
#### ONE (checklist) TO one (dataset)
db.define_table(
    'checklist',
    Field('dataset_id',db.dataset),
Field('checked_by','string'),
Field('check_date','date'),
Field('notes_comments','text'),
Field('data_package_title_check','boolean'),
Field('data_set_citation_check','boolean'),
Field('data_package_owner_check','boolean'),
Field('data_package_owner_check_individual_name','boolean'),
Field('data_package_owner_check_position_role','boolean'),
Field('data_package_owner_check_organization','boolean'),
Field('data_package_owner_check_address','boolean'),
Field('data_package_owner_check_phone','boolean'),
Field('data_package_owner_check_email_address','boolean'),
Field('associated_parties','boolean'),
Field('associated_parties_individual_name','boolean'),
Field('associated_parties_position','boolean'),
Field('associated_parties_organization','boolean'),
Field('associated_parties_physical_address','boolean'),
Field('associated_parties_phone','boolean'),
Field('associated_parties_email_address','boolean'),
Field('abstract','boolean'),
Field('keywords_and_subject_categories','boolean'),
Field('gcmd_science_keywords','boolean'),
Field('anzsrc_for_codes','boolean'),
Field('ltern_monitoring_themes','boolean'),
Field('keywords_free_text','boolean'),
Field('geographic_coverage','boolean'),
Field('geographic_description','boolean'),
Field('bounding_coordinates','boolean'),
Field('temporal_coverage','boolean'),
Field('contacts_individual_names','boolean'),
Field('contacts_positions','boolean'),
Field('contacts_organizations','boolean'),
Field('contacts_addresses','boolean'),
Field('contacts_phone','boolean'),
Field('contacts_email_addresses','boolean'),
Field('methods_and_sampling_information','boolean'),
Field('method_step_titles','boolean'),
Field('method_step_description','boolean'),
Field('instrumentation_details','boolean'),
Field('sampling_area_and_frequency','boolean'),
Field('sampling_description','boolean'),
Field('research_project_title','boolean'),
Field('research_project_funding_sources','boolean'),
Field('research_project_personnel_information','boolean'),
Field('research_project_individual_name','boolean'),
Field('research_project_position_role','boolean'),
Field('research_project_organization','boolean'),
Field('research_project_address','boolean'),
Field('research_project_phone','boolean'),
Field('research_project_email_address','boolean'),
Field('research_project_role','boolean'),
Field('additional_metadata','boolean'),

Field('access_control','boolean'),

Field('usage_rights','boolean'),
Field('special_conditions','boolean'),
Field('entity_metadata','boolean'),
Field('homepage_content','boolean'),
Field('eml_homepage_links','boolean'),
Field('can_the_plot_network_or_data_package_be_filtered_in_the_search_bar_of_the_portal','boolean'),
Field('draft_publication_checklist_passed','boolean'),
Field('metacat_publication_checklist_check_public_or_mediated_access','boolean'),
Field('metacat_publication_checklist_add_publication_date_to_data_inventory','boolean'),
Field('metacat_publication_checklist_passed','boolean'),
Field('reporting_checklist_licenced','boolean'),
Field('reporting_checklist_described_with_metadata_','boolean'),
Field('reporting_checklist_doi_minted','boolean'),
Field('reporting_checklist_metadata_feed_to_tddp_and_rda','boolean'),
Field('reporting_checklist_passed','boolean')
    )
    
db.checklist.checked_by.requires = IS_IN_SET(['Claire', 'Karl'])
db.checklist.check_date.requires = IS_NOT_EMPTY()
#### ONE (errors) TO one (dataset)
db.define_table(
    'error',
    Field('dataset_id',db.dataset),
Field('logged_by','string'),
Field('date_logged','date'),
Field('date_actioned','date'),
Field('error','text'),
Field('addenda','text')
    )
    
db.error.logged_by.requires = IS_NOT_EMPTY()
db.error.date_logged.requires = IS_NOT_EMPTY()
#### ONE (biblio) TO one (entity)
db.define_table(
'publication',
Field('dataset_id',db.dataset),
Field('bibtex_key', 'string', requires = IS_NOT_EMPTY(),  comment = "For eg from mendeley, use ctrl-k or copy as.  it will be like \cite{xyz}.  COMPULSORY."),
Field('publication_type','string', requires = IS_IN_SET(['Papers', 'Conference Presentations', 'Reports', 'Policy Briefs', 'Data Packages', 'Software', 'Media'])),
Field('publication_status','string', requires = IS_IN_SET(['Wishlist','Draft', 'Submitted', 'Revision', 'Accepted', 'Published (peer-reviewed)', 'Published (not peer-reviewed)', 'Self-published (not peer-reviewed)'])),
Field('publication_status_deadline','date', comment = 'This is the date that the current phase will finish and the next phase of publication starts'),
Field('title','string'),
Field('citation', 'string', comment = 'At a minimum author-date-journal, perhaps DOI?'),
Field('key_results', 'text', comment = 'Include both effect estimates and uncertainty'),
Field('background_to_study', 'string', comment = ''),
Field('research_question', 'string', comment = ''),
Field('study_extent', 'string', comment = ''),
Field('outcomes','string', comment = ''),
Field('exposures','string', comment = ''),
Field('covariates','string', comment = 'Include covariates, effect modifiers, confounders and subgroups'),
Field('method_protocol', 'text', comment = ''),
Field('general_comments', 'text', comment = ''),
Field('publication_description', 'string'),
Field('google_pubid','string', comment = 'The unique ID used by google scholar'),
Field('journal','string'),
Field('year_published','integer'),
Field('impact_factor','double'),
Field('date_impact_factor_checked','date'),
Field('google_scholar_cites','integer'),
Field('date_gs_cites_checked','date'),
Field('web_of_science_cites','integer'),
Field('date_wos_cites_checked','date'),
Field('contribution','text'),
Field('thesis_section','string'),
Field('thesis_context_statement','text'),
Field('thesis_publication_status','string')
)
#### many approval_to_share TO one paper
db.define_table(
    'authorship_approval',
    Field('publication_id',db.publication),
Field('name','string'),
Field('email','string'),
Field('organisation', 'string'),
Field('date_request_sent','date'),
Field('date_approval_given','date'),
Field('times_contacted','integer'),
Field('notes','text'),
Field('extra_details', 'text')
    )
db.define_table(
    'crosswalk',
    Field('eml_module','string'),
    Field('eml_table','string'),
    Field('datinv','string'),
    Field('eml_node','string'),
    Field('help_comment','text'),
    Field('eml_desc','text'),
    Field('eml_standard_link','string'),
    Field('eml_local_link','string'),
    Field('ddi_module','string'),
    Field('ddi_node','string'),
    Field('morpho','string'),
    Field('ltern_table','string'),
    Field('ltern_name','string'),
    Field('portal_ddf_qaf','string'),
    Field('ltern_desc','text'),
    Field('aekos_shared','string'),
    Field('aekos_desc','text'),
    Field('asn','string'),
    Field('tern','string'),
    Field('ala','string'),
    Field('psql_type','string'),
    Field('w2p_code','string'),
    Field('constraint_text','string'),
    Field('lter_manual_page','string'),
    Field('transfer2new','string')
    )


# KEYWORDS ####
# tags for datasets
db.define_table(
    'thesaurus',
    Field('keyword', 'string', 
        required = True,
        requires = (IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'thesaurus.keyword'))),
    auth.signature,
    format = '%(keyword)s'
    )
