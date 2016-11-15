# -*- coding: utf-8 -*-
from flask import flash, redirect, url_for
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView, tools
from flask_login import current_user
from sqlalchemy.sql import expression


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
        return redirect(url_for("login.index"))


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