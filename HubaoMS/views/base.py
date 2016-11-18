# -*- coding: utf-8 -*-
from math import ceil
from flask import flash, request
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView, tools
from flask_login import current_user
from sqlalchemy.sql import expression
from sqlalchemy.orm import joinedload

from utils.functions import abs_redirect

class AuthenticatedBaseView(BaseView):
    # Various settings
    page_size = 20
    """
        Default page size for pagination.
    """

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        flash(u"请先登录", category='error')
        return abs_redirect("login.index")


class AuthenticatedModelView(ModelView, AuthenticatedBaseView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    """
       Override this property for sorting by sum of columns, for example:
            extra_sorting = {
                "col_name": "col_1 + col_2"
            }
    """
    extra_sorting = None

    def _get_default_order(self):
        if isinstance(self.column_default_sort, list):
            attrs = []
            joins = []
            directions = []
            for item in self.column_default_sort:
                if isinstance(item, tuple):
                    directions.append(item[1])
                    field = tools.get_field_with_path(self.model, item[0])
                    attrs.append(field[0])
                    joins.append(field[1])
                else:
                    directions.append(False)
                    field = tools.get_field_with_path(self.model, item)
                    attrs.append(field[0])
                    joins.append(field[1])
            return attrs, joins, directions
        else:
            return super(AuthenticatedModelView, self)._get_default_order()

    # Override this method to support:  1.Sort by sum of multiple columns; 2.Sort by multiple columns
    def _apply_sorting(self, query, joins, sort_column, sort_desc):
        if sort_column is not None:
            if sort_column in self._sortable_columns:
                sort_field = self._sortable_columns[sort_column]
                sort_joins = self._sortable_joins.get(sort_column)

                query, joins = self._order_by(query, joins, sort_joins, sort_field, sort_desc)
            elif sort_column in self.extra_sorting:
                sort_field = self.extra_sorting[sort_column]
                if "+" in sort_field:
                    sum_columns = [tools.get_field_with_path(self.model, item.strip())[0] for item in sort_field.split('+')]

                    if sort_desc:
                        query = query.order_by(expression.desc(sum(sum_columns)))
                    else:
                        query = query.order_by(sum(sum_columns))
        else:
            order = self._get_default_order()

            if order:
                sort_field, sort_joins, sort_desc = order
                if isinstance(sort_field, list):
                    for f, j, d in zip(sort_field, sort_joins, sort_desc):
                        query, joins = self._order_by(query, joins, j, f, d)
                else:
                    query, joins = self._order_by(query, joins, sort_joins, sort_field, sort_desc)

        return query, joins

    def is_sortable(self, name):
        return True if self.extra_sorting and name in self.extra_sorting \
            else super(AuthenticatedModelView, self).is_sortable(name)


class IndexView(AdminIndexView):
    @expose()
    def index(self):
        authenticated = current_user.is_authenticated
        username = current_user.username if authenticated else None
        return self.render("index.html", authenticated=authenticated, current_user=username)


class BaseRobotToggleView(AuthenticatedModelView):
    def _get_list_extra_args(self):
        view_args = super(BaseRobotToggleView, self)._get_list_extra_args()
        view_args.extra_args["robot"] = request.args.get('robot', "1")
        return view_args

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None, robot=True):
        """
            Return records from the database.

            :param page:
                Page number
            :param sort_column:
                Sort column name
            :param sort_desc:
                Descending or ascending sort
            :param search:
                Search query
            :param execute:
                Execute query immediately? Default is `True`
            :param filters:
                List of filter tuples
            :param page_size:
                Number of results. Defaults to ModelView's page_size. Can be
                overriden to change the page_size limit. Removing the page_size
                limit requires setting page_size to 0 or False.
        """

        # Will contain join paths with optional aliased object
        joins = {}
        count_joins = {}

        query = self.get_query(robot)
        count_query = self.get_count_query(robot) if not self.simple_list_pager else None

        # Ignore eager-loaded relations (prevent unnecessary joins)
        # TODO: Separate join detection for query and count query?
        if hasattr(query, '_join_entities'):
            for entity in query._join_entities:
                for table in entity.tables:
                    joins[table] = None

        # Apply search criteria
        if self._search_supported and search:
            query, count_query, joins, count_joins = self._apply_search(query,
                                                                        count_query,
                                                                        joins,
                                                                        count_joins,
                                                                        search)

        # Apply filters
        if filters and self._filters:
            query, count_query, joins, count_joins = self._apply_filters(query,
                                                                         count_query,
                                                                         joins,
                                                                         count_joins,
                                                                         filters)

        # Calculate number of rows if necessary
        count = count_query.scalar() if count_query else None

        # Auto join
        for j in self._auto_joins:
            query = query.options(joinedload(j))

        # Sorting
        query, joins = self._apply_sorting(query, joins, sort_column, sort_desc)

        # Pagination
        query = self._apply_pagination(query, page, page_size)

        # Execute if needed
        if execute:
            query = query.all()

        return count, query

    @expose("/")
    def index_view(self, **kwargs):
        """
            List view
        """
        if self.can_delete:
            delete_form = self.delete_form()
        else:
            delete_form = None

        # Grab parameters from URL
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        display_robot = view_args.extra_args.get("robot") != "0"

        # Get count and data
        count, data = self.get_list(view_args.page, sort_column, view_args.sort_desc,
                                    view_args.search, view_args.filters,
                                    robot=display_robot)

        list_forms = {}
        if self.column_editable_list:
            for row in data:
                list_forms[self.get_pk_value(row)] = self.list_form(obj=row)

        # Calculate number of pages
        if count is not None and self.page_size:
            num_pages = int(ceil(count / float(self.page_size)))
        elif not self.page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None

            return self._get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False):
            desc = None

            if invert and not view_args.sort_desc:
                desc = 1

            return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

        def robot_url(display):
            return self._get_list_url(view_args.clone(extra_args={"robot":display}))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        clear_search_url = self._get_list_url(view_args.clone(page=0,
                                                              sort=view_args.sort,
                                                              sort_desc=view_args.sort_desc,
                                                              search=None,
                                                              filters=None))

        return self.render(
            self.list_template,
            data=data,
            list_forms=list_forms,
            delete_form=delete_form,

            # List
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            list_row_actions=self.get_list_row_actions(),

            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            page=view_args.page,
            page_size=self.page_size,

            # Sorting
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,

            # Search
            search_supported=self._search_supported,
            clear_search_url=clear_search_url,
            search=view_args.search,

            # Filters
            filters=self._filters,
            filter_groups=self._get_filter_groups(),
            active_filters=view_args.filters,

            # Actions
            actions=actions,
            actions_confirmation=actions_confirmation,

            # Misc
            enumerate=enumerate,
            get_pk_value=self.get_pk_value,
            get_value=self.get_list_value,
            return_url=self._get_list_url(view_args),

            # Robot
            robot=1 if display_robot else 0,
            robot_url=robot_url,
            **kwargs
        )