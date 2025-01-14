
def access_dataset():
    form = SQLFORM.factory(
        Field('accessdataset_id',requires=IS_IN_DB(db,db.accessdataset.id,'%(name)s')),
        Field('dataset_id',requires=IS_IN_DB(db,db.dataset.id,'%(shortname)s')),
        Field('title','string',requires=IS_NOT_EMPTY()),
        Field('description','text',requires=IS_NOT_EMPTY()),
        Field('begin_date','date'),
        Field('end_date','date')).process()

    
    if form.accepted:
        # get previous access for same dataset
        access = db((db.accessrequest.accessdataset_id == form.vars.accessdataset_id)&
            (db.accessrequest.dataset_id==form.vars.dataset_id)).select().first()

        db.accessrequest.insert(accessdataset_id=form.vars.accessdataset_id,
                         dataset_id=form.vars.dataset_id,
                         title=form.vars.title,
                         description=form.vars.description,
                         begin_date =form.vars.begin_date,
                         end_date   =form.vars.end_date
                         )

        response.flash = 'dataset accessed!'
    elif form.errors:
        response.flash = 'invalid values in form!'

    
    # now get a list of all accesses
    accessing = (db.accessdataset.id==db.accessrequest.accessdataset_id)&(db.dataset.id==db.accessrequest.dataset_id)
    records = SQLTABLE(db(accessing).select(),headers='fieldname:capitalize')
    return dict(form=form, records=records)
def manage_projects():
    grid = SQLFORM.smartgrid(db.project,linked_tables=['dataset', 'entity', 'publication', 'intellectualright', 'attr','accessrequest', 'authorship_approval'
                                                      ],
                             fields = [db.project.title, db.project.personnel_data_owner,
                                       db.dataset.shortname,


                                       db.dataset.additional_metadata,                                          

                                       db.entity.entityname, db.entity.entitydescription, db.entity.physical_distribution,
                                       db.attr.variable_name, db.attr.variable_definition,
                                       db.accessrequest.accessdataset_id, 
                                       db.accessrequest.dataset_id,
                                       db.accessrequest.title, 

                                       db.intellectualright.licence_code,
                                       db.publication.bibtex_key, db.publication.title,  
                                       db.publication.google_scholar_cites, db.publication.impact_factor,
                                       db.authorship_approval.id, db.authorship_approval.name, db.authorship_approval.date_request_sent,
                                       db.authorship_approval.date_approval_given],
                                       orderby = dict(project=db.project.title, dataset=db.dataset.shortname,authorship_approval=db.authorship_approval.id),
                             user_signature=True,maxtextlength =200, csv=False, paginate=50)
    return dict(grid=grid)
def manage_datasets():
    grid = SQLFORM.smartgrid(db.dataset,linked_tables=[ 'entity', 'keyword', 'intellectualright', 'attr','accessrequest', 'publication', 'authorship_approval'
                                                      ],
                             fields = [
                                       db.dataset.shortname,
                                       db.dataset.id,
                            
                                       db.dataset.additional_metadata,                                          
                                       db.dataset.contact_email,
                                       db.entity.entityname, db.entity.entitydescription, db.entity.physical_distribution,
                                       db.attr.variable_name, db.attr.variable_definition,
                                       db.accessrequest.accessdataset_id, 
                                       db.accessrequest.dataset_id,
                                       db.accessrequest.title, 
                                       db.keyword.keyword,
                                       db.intellectualright.licence_code,
                                       db.publication.bibtex_key, db.publication.title,  
                                       db.publication.google_scholar_cites, db.publication.impact_factor,
                                       db.authorship_approval.id, db.authorship_approval.name, db.authorship_approval.date_request_sent,
                                       db.authorship_approval.date_approval_given],
                                       orderby = dict(dataset=db.dataset.title,authorship_approval=db.authorship_approval.id),
                             user_signature=True,maxtextlength =200, csv=False, paginate=50)
    return dict(grid=grid)
def manage_publications():
    grid = SQLFORM.smartgrid(db.publication,linked_tables=['publication', 'authorship_approval'
                                                      ],
                             fields = [
                                       db.publication.bibtex_key, db.publication.citation,  
                                       db.publication.thesis_section, 
                                       db.authorship_approval.id, db.authorship_approval.name, db.authorship_approval.date_request_sent,
                                       db.authorship_approval.date_approval_given],
                                       orderby = dict(thesis_section=db.publication.thesis_section, authorship_approval=db.authorship_approval.id),
                             user_signature=True,maxtextlength =200)
    return dict(grid=grid)
def manage_accessors_or_groups():
    grid = SQLFORM.smartgrid(db.accessdataset,linked_tables=['accessor'],
                             fields = [
                                       db.accessdataset.name,
                                       db.accessdataset.email,
                                       db.accessor.name, db.accessor.email],
                                       orderby = dict(accessdataset=[db.accessdataset.name]),
                             user_signature=True,maxtextlength =200, csv=False, paginate=35)

    return dict(grid=grid)
    # db.accessor.email.requires = [IS_IN_DB(db,db.accessor.id,'%(email)s')]
def manage_crosswalk():
    grid = SQLFORM.smartgrid(db.crosswalk,
                             fields = [db.crosswalk.transfer2new,   
                                       db.crosswalk.eml_node,
                                       db.crosswalk.datinv,
                                       db.crosswalk.ltern_name,
                                       db.crosswalk.portal_ddf_qaf,
                                       db.crosswalk.ddi_node,
                                       db.crosswalk.aekos_shared
                                       ],
                                       orderby = dict(crosswalk=[db.crosswalk.transfer2new, db.crosswalk.portal_ddf_qaf, db.crosswalk.eml_node]),
                             user_signature=True,maxtextlength =200)

    return dict(grid=grid)
def manage_thesaurus_ltern():
    grid = SQLFORM.smartgrid(db.thesaurus_ltern,
                             fields = [   
                                       db.thesaurus_ltern.keyword
                                       ],
                                       orderby = dict(thesaurus_ltern=[ db.thesaurus_ltern.keyword]),
                             user_signature=True,maxtextlength =200)

    return dict(grid=grid)
