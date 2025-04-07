def home():
    response.flash = T("Welcome to the CARDAT data inventory!")
    return dict()

def guide():

    return dict()

@auth.requires_login()
def data_dictionary():
    form = SQLFORM.factory(
        Field('select_table', 'string', requires=IS_IN_DB(db, 'tbl_description.tbl_nm', distinct = True)),
        table_name = "select_table",
        submit_button='Show'
    )
    table_name = ""
    rows = []
    grid = None

    if form.validate():
        redirect(URL(#c='manage', f='browse', 
            args=form.vars.select_table))

    if len(request.args) != 0:
        table_name = request.args[0]

        rows = db(db.tbl_description.tbl_nm == request.args[0]).select(
                    db.tbl_description.col_nm,
                    db.tbl_description.data_type,
                    db.tbl_description.description, orderby = db.tbl_description.col_order)

    return dict(form=form,
    table_name=table_name,
    rows=rows,
    grid=grid)

@auth.requires_login()
def edit_data_dictionary():
    grid = SQLFORM.grid(db.tbl_description,
        fields = [db.tbl_description.tbl_nm, 
                db.tbl_description.col_nm, 
                db.tbl_description.data_type],
        orderby = [db.tbl_description.tbl_nm, 
                db.tbl_description.col_order
        ],
        user_signature=True
        )
    return dict(grid=grid)
